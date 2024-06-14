<template>
  <div id="map"/>
  <div id="popup" class="ol-popup">
    <a href="#" id="popup-closer" class="ol-popup-closer"></a>
    <div id="popup-content"></div>
  </div>
</template>

<script setup lang="ts">
import Map from 'ol/Map';
import View from 'ol/View';
import TileLayer from 'ol/layer/Tile';
import {onMounted, Ref, ref, watch} from "vue";
import {GeoTIFF, OSM} from "ol/source";
import 'ol/ol.css';
import {fromLonLat, transform} from 'ol/proj';
import {useCommonStore, useVesselsStore} from "../store";
import {storeToRefs} from "pinia";
import VectorLayer from "ol/layer/Vector";
import {IBaseEdge, IBaseNode, IIcebreaker, IPath, IVessel, IWaybill, tTypeWay, typeTransport} from "../types.ts";
import {GeoJSONFeature} from "ol/format/GeoJSON";
import Feature, {FeatureLike} from "ol/Feature";
import {Overlay} from "ol";
import {Geometry} from "ol/geom";
import {generateVectorLayer} from "../utils/createVectorLayer.ts";
import {WebGLTile} from "ol/layer";

const map: Ref<Map | null> = ref(null);
const popover = ref(undefined)

const vectorLayers: Ref<Record<string, VectorLayer<Feature<Geometry>>>> = ref({})
const graph: Ref<Record<string, VectorLayer<Feature<Geometry>>>> = ref({})
const dateLayer: Ref<Record<string, VectorLayer<Feature<Geometry>>>> = ref({})

const {paths, baseNodes, vessels, baseEdges, icebreakers} = storeToRefs(useVesselsStore())
const {showGraph, date} = storeToRefs(useCommonStore())

onMounted(() => {
  map.value = new Map({
    target: document.getElementById('map') as HTMLDivElement,
    layers: [
      new TileLayer({
        visible: true,
        zIndex: 0,
        tileSize: 512,
        maxZoom: 20,
        source: new OSM('https://{s}.tile.openstreetmap.de/{z}/{x}/{y}.png')
      }),
    ],
    view: new View({
      center: transform([-175, 80], 'EPSG:4326', 'EPSG:3857'),
      zoom: 0,
    }),
  });

  const container = document.getElementById('popup');
  const content = document.getElementById('popup-content');
  const closer = document.getElementById('popup-closer');

  if (!container || !content || !closer) return

  const popup = new Overlay({
    element: container,
    positioning: 'bottom-center',
    stopEvent: false,
  });

  closer.onclick = () => {
    popup.setPosition(undefined);
    closer.blur();
    return false;
  };

  map.value.addOverlay(popup);

  map.value.on('click', (evt) => {
    const feature = map.value?.forEachFeatureAtPixel(evt.pixel, (feature) => feature);

    disposePopover();

    if (!feature) return

    popup.setPosition(evt.coordinate);

    content.innerHTML = getFeature(feature);
  });

  map.value.on('pointermove', (e) => {
    const pixel = map.value?.getEventPixel(e.originalEvent);
    const hit = map.value?.hasFeatureAtPixel(pixel!);
    map.value.getTarget().style.cursor = hit ? 'pointer' : '';
  });

  map.value.on('movestart', disposePopover);
})

const getFeature = (feature: FeatureLike) => {
  const properties = feature.getProperties()
  const type = feature.getGeometry()?.getType()

  return `
  <p><span style="color: gray">Название: </span>${properties.name}</p>
  <p><span style="color: gray">Ледовый класс: </span>${properties.ice_class}</p>
  <p><span style="color: gray">Скорость в узлах по чистой воде: </span>${properties.speed}</p>
  <p><span style="color: gray">Исходный порт: </span>${properties.source_name}</p>
  ${properties.target_name && `<p><span style="color: gray">Конечный порт: </span>${properties.target_name}</p>`}
  <p><span style="color: gray">Дата начала плавания: </span>${properties.start_date}</p>
  <p><span style="color: gray">Текущая точка: </span>${getTypePoint(properties.event, type)}</p>
  <p><span style="color: gray">Текущая дата: </span>${properties.time}</p>
  `
}

const getTypePoint = (event: tTypeWay, type: 'Point' | 'LineString') => {
  if (tTypeWay.MOVE === event && type === 'Point') {
    return 'Исходная точка'
  }

  if (tTypeWay.MOVE === event || (tTypeWay.FIN === event && type !== 'Point')) {
    return 'Судно в пути'
  }

  if (tTypeWay.WAIT === event) {
    return 'Остановка движения'
  }

  if (tTypeWay.FORMATION === event) {
    return 'Проводка караваном'
  }

  return 'Конечная точка'
}

const disposePopover = () => {
  if (popover.value) {
    popover.value.dispose();
    popover.value = undefined;
  }
}

const getCoords = (point: number) => {
  const currentBaseEdge = baseEdges.value.find((edge: IBaseEdge) => edge.id === point)

  if (!currentBaseEdge) return []
  const {start_point_id, end_point_id} = currentBaseEdge;

  const startPoint: IBaseNode | undefined = baseNodes.value.find(({id}: IBaseNode) => id === start_point_id);
  const endPoint: IBaseNode | undefined = baseNodes.value.find(({id}: IBaseNode) => id === end_point_id);
  if (!endPoint || !startPoint) return [];

  return [
    [fromLonLat([startPoint.lon, startPoint.lat])],
    [fromLonLat([endPoint.lon, endPoint.lat])],
  ]
}

const getFeatures = ({waybill, seaTransport, success}: {
  waybill: IWaybill[],
  seaTransport: IVessel,
  success: boolean
}) => {
  const geoJsonData: GeoJSONFeature[] = []

  waybill.forEach((line: IWaybill, idx: number) => {
    const {point, event} = line

    const coordinates = getCoords(point)

    if (event === tTypeWay.WAIT) {
      geoJsonData.push({
        type: 'Feature',
        geometry: {
          'type': 'Point',
          'coordinates': coordinates[0][0],
        },
        properties: {
          ...line,
          ...seaTransport,
        },
      })

      return
    }

    if (idx === 0) {
      geoJsonData.push({
        type: 'Feature',
        geometry: {
          'type': 'Point',
          'coordinates': coordinates[0][0],
        },
        properties: {
          ...line,
          ...seaTransport
        },
      })
    }

    if (idx === waybill.length - 1) {
      geoJsonData.push({
        type: 'Feature',
        geometry: {
          type: 'Point',
          coordinates: coordinates[1][0],
        },
        properties: {
          ...line,
          ...seaTransport
        },
      })
    }

    geoJsonData.push({
      type: 'Feature',
      geometry: {
        type: 'LineString',
        coordinates: coordinates,
      },
      properties: {
        ...line,
        ...seaTransport,
        success
      },
    })
  })

  return geoJsonData
}

const createGeoJson = () => {
  paths.value.forEach((item: IPath) => {
    const {waybill, id, type, success} = item

    if (vectorLayers.value[id]) return

    const listTransport = type === typeTransport.VESSELS ? vessels.value : icebreakers.value
    const seaTransport = listTransport.find((transport: IVessel | IIcebreaker) => transport.id === id)

    if (!seaTransport) {
      throw new Error(`Unknown transport: ${id}`)
    }

    const vectorLayer = generateVectorLayer(getFeatures, {waybill, seaTransport, success})
    vectorLayers.value[id]
    map.value?.addLayer(vectorLayer);
  })
}

const removeLayers = () => {
  const ids = structuredClone(Object.keys(vectorLayers.value))
  ids.forEach(key => {
    if (paths.value.find(path => path.id === key)) {
      map.value?.removeLayer(vectorLayers[key])
      delete vectorLayers[key]
    }
  })
}

const createGraph = () => {
  return baseEdges.value.map((edge) => {
    const coordinates = getCoords(edge.id)

    return ({
      type: 'Feature',
      geometry: {
        type: 'LineString',
        coordinates: coordinates,
      },
    })
  })
}

watch(() => paths.value, (newPathList) => {
  if (vectorLayers.value.length) removeLayers()

  if (newPathList.length) {
    createGeoJson()
  } else if (vectorLayers.value.length) {
    vectorLayers.value.forEach((item) => map.value.removeLayer(item))
  }
}, {deep: true})

watch(() => [baseEdges.value, baseNodes.value], () => {
  if (baseEdges.value.length && baseNodes.value.length) {
    const vectorLayer = generateVectorLayer(createGraph)
    map.value?.addLayer(vectorLayer);
    graph.value = vectorLayer
  }
}, {deep: true})

watch(() => showGraph.value, () => {
  if (showGraph.value) {
    map.value?.addLayer(graph.value);
    return
  }

  map.value?.removeLayer(graph.value);
})


watch(() => date.value, () => {
  if (dateLayer.value) map.value?.removeLayer(dateLayer.value);

  if (date.value) {
    const source = new GeoTIFF({
          sources: [
            {
              url: 'https://openlayers.org/en/latest/examples/data/example.tif',
            },
          ],
        }
    )

    const layer = new WebGLTile({
      source: source,
    })

    map.value.addLayer(layer)

    dateLayer.value = layer

    map.value.setView(source
        .getView().then((options) => {
          const center = options.center;
          const resolution = options.resolutions[0];
          const projection = options.projection;
          return {center, resolution, projection};
        })
    )
  }
})
</script>

<style scoped>
#map {
  height: 100%;
  width: 100%;
}
</style>
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
import {OSM} from "ol/source";
import 'ol/ol.css';
import {fromLonLat, transform} from 'ol/proj';
import {useVesselsStore} from "../store";
import {storeToRefs} from "pinia";
import VectorLayer from "ol/layer/Vector";
import VectorSource from "ol/source/Vector";
import {GeoJSON} from "ol/format";
import {IBaseEdge, IBaseNode, IIcebreaker, IPath, IVessel, IWaybill, tTypeWay, typeTransport} from "../types.ts";
import {GeoJSONFeature} from "ol/format/GeoJSON";
import {Circle, Fill, Icon, Stroke, Style} from "ol/style";
import Feature, {FeatureLike} from "ol/Feature";
import endPoint from '../assets/icons/anchor-icon-svgrepo-com.png'
import {Overlay} from "ol";
import {Geometry} from "ol/geom";
const map: Ref<Map | null> = ref(null);
const popover = ref(undefined)

const vectorLayers: Ref<Record<string, VectorLayer<Feature<Geometry>>>> = ref({})

const {paths, baseNodes, vessels, baseEdges, icebreakers} = storeToRefs(useVesselsStore())

onMounted(() => {
  map.value = new Map({
    target: document.getElementById('map') as HTMLDivElement,
    layers: [
      new TileLayer({
        visible: true,
        zIndex: 0,
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

const getFeatures = (waybill: IWaybill[], currentVessel: IVessel, success: boolean) => {
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
          ...currentVessel,
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
          ...currentVessel
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
          ...currentVessel
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
        ...currentVessel,
        success
      },
    })
  })

  return geoJsonData
}

const getStyles = (feature: FeatureLike) => {
  const {event, success} = feature.getProperties()
  const type = feature.getGeometry()?.getType()

  if (type === 'Point' && event === tTypeWay.MOVE) {
    return new Style({
      fill: new Fill({
        color: 'blue'
      }),
      stroke: new Stroke({
        width: 3,
        color: 'blue'
      }),
      image: new Circle({
        fill: new Fill({
          color: 'blue'
        }),
        stroke: new Stroke({
          width: 5,
          color: 'blue'
        }),
        radius: 5
      }),
    })
  }

  if (type === 'Point' && event === tTypeWay.FIN) {
    return new Style({
      image: new Icon({
        height: 20,
        width: 20,
        src: endPoint,
      }),
    })
  }

  if (type === 'Point' && event === tTypeWay.WAIT) {
    return new Style({
      fill: new Fill({
        color: 'gray'
      }),
      stroke: new Stroke({
        width: 3,
        color: 'gray'
      }),
      image: new Circle({
        fill: new Fill({
          color: 'gray'
        }),
        stroke: new Stroke({
          width: 5,
          color: 'gray'
        }),
        radius: 5
      }),
    })
  }

  if (event === tTypeWay.MOVE || event === tTypeWay.FIN) {
    return new Style({
      stroke: new Stroke({
        color: success ? 'green' : 'red',
        width: 2,
      })
    })
  }

  return new Style({
    stroke: new Stroke({
      color: 'blue',
      width: 2,
    })
  })
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

    const features = {
      type: 'FeatureCollection',
      crs: {
        type: 'lines',
        properties: {
          name: 'EPSG:3857',
        },
      },
      features: getFeatures(waybill, seaTransport, success),
    }
    const vectorSource = new VectorSource({
      features: new GeoJSON().readFeatures(features),
    });

    const vectorLayer = new VectorLayer({
      source: vectorSource,
      style: (feature) => getStyles(feature)
    });

    vectorLayers.value[id] = vectorLayer
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

watch(() => paths.value, (newPathList) => {
  if (vectorLayers.value.length) removeLayers()

  if (newPathList.length) {
    createGeoJson()
  } else if (vectorLayers.value.length) {
    vectorLayers.value.forEach((item) => map.value.removeLayer(item))
  }
}, {deep: true})
</script>

<style scoped>
#map {
  height: 100%;
  width: 100%;
}
</style>
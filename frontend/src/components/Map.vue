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
import {useCommonStore, useIceTransportStore} from "../store";
import {storeToRefs} from "pinia";
import VectorLayer from "ol/layer/Vector";
import {IBaseEdge, IBaseNode, IIcebreaker, IPath, IVessel, IWaybill, tTypeWay, typeTransport} from "../types.ts";
import {GeoJSONFeature} from "ol/format/GeoJSON";
import Feature from "ol/Feature";
import {Overlay} from "ol";
import {Geometry} from "ol/geom";
import {generateVectorLayer} from "../utils/createVectorLayer.ts";
import {getDate} from "../utils/getDate.ts";
import {getWord} from "../utils/getWord.ts";
import {WebGLTile} from "ol/layer";

const map: Ref<Map | null> = ref(null);
const popover = ref(undefined)

const vectorLayersVessels: Ref<Record<string, VectorLayer<Feature<Geometry>>>> = ref({})
const vectorLayersIcebreakers: Ref<Record<string, VectorLayer<Feature<Geometry>>>> = ref({})

const graph: Ref<Record<string, VectorLayer<Feature<Geometry>>>> = ref({})

const dateLayer: Ref<Record<string, VectorLayer<Feature<Geometry>>>> = ref({})

const vesselMarkers: Ref<Record<string, VectorLayer<Feature<Geometry>>>> = ref({})
const icebreakerMarkers: Ref<Record<string, VectorLayer<Feature<Geometry>>>> = ref({})

const {
  pathsVessels,
  pathsIcebreakers,

  baseNodes,
  baseEdges,

  vessels,
  icebreakers,

  vesselPoints,
  icebreakerPoints,

  caravans,

  tiffDate
} = storeToRefs(useIceTransportStore())

const {showGraph} = storeToRefs(useCommonStore())

onMounted(async () => {
  map.value = new Map({
    target: document.getElementById('map') as HTMLDivElement,
    layers: [
      new TileLayer({
        visible: true,
        zIndex: 0,
        // @ts-ignore
        tileSize: 512,
        maxZoom: 20,
        // @ts-ignore
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
    disposePopover();

    const features: Record<string, any>[] = []

    map.value?.forEachFeatureAtPixel(evt.pixel, (feature) => {
          const properties = feature.getProperties()
          const {graph} = properties

          const findFeature = features.find((currentFeature) => {
            if (properties.vessel_id) return properties.vessel_id === currentFeature.vessel_id
            return properties.icebreaker_id === currentFeature.icebreaker_id
          })

          if (feature && !graph && !findFeature) features.push(feature.getProperties())
        }
    )

    if (features.length) {
      popup.setPosition(evt.coordinate);
      const strings = features.map((feature, idx) => getFeature(feature, features.length, idx))
      content.innerHTML = strings.join('\n')
    }
  })

  map.value.on('pointermove', (e) => {
    const pixel = map.value?.getEventPixel(e.originalEvent);
    const hit = map.value?.hasFeatureAtPixel(pixel!);
    // @ts-ignore
    map.value.getTarget().style.cursor = hit ? 'pointer' : '';
  });

  map.value.on('movestart', disposePopover);
})

const getFeature = (feature: Record<string, any>, length: number, idx: number) => {
  if (!feature.name) return ''
  return `
  <p><span style="color: gray">Название: </span>${feature.name}</p>
  <p><span style="color: gray">Ледовый класс: </span>${feature.ice_class}</p>
  <p><span style="color: gray">Скорость в узлах по чистой воде: </span>${feature.speed}</p>
  <p><span style="color: gray">Исходный порт: </span>${feature.source_name}</p>
  ${feature.target_name ? `<p><span style="color: gray">Конечный порт: </span>${feature.target_name}</p>` : ''}
  ${feature.start_date ? `<p><span style="color: gray">Дата начала плавания: </span>${getDate(feature.start_date, 'yyyy-MM-dd')}</p>` : ''}
  ${feature.dt ? `<p><span style="color: gray">Текущая дата: </span>${getDate(feature.dt, 'yyyy-MM-dd')}</p>` : ''}
  ${feature.total_time_hours ? `<p><span style="color: gray">Время в пути: </span>${Math.round(feature.total_time_hours, -1)} ${getWord(Math.round(feature.total_time_hour, -1))}</p>` : ''}
  ${feature.icebreakerName ? `<p><span style="color: gray">Ледокол в проводке: </span>${feature.icebreakerName}</p>` : ''}
  ${feature.vessels ? `<p><span style="color: gray">В проводке участвовали: </span>${feature.vessels}</p>` : ''}
  ${feature.point_name ? `<p><span style="color: gray">Текущая точка: </span>${feature.point_name}</p>` : ''}
  ${length > 1 && idx !== length - 1 ? '<div style="height: 10px"></div>' : ''}
 `
}

const disposePopover = () => {
  if (popover.value) {
    // @ts-ignore
    popover.value.dispose();
    popover.value = undefined;
  }
}

const getCoordsByEdge = (point: number) => {
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

const getCoordsByNode = (point: number, nextWay: IWaybill) => {
  const currentBaseNode = baseNodes.value.find((node: IBaseNode) => node.id === point)

  const endBaseNode = nextWay ? baseNodes.value.find((node: IBaseNode) => node.id === nextWay.point) : null

  if (endBaseNode && currentBaseNode) {
    return [
      [fromLonLat([currentBaseNode.lon, currentBaseNode.lat])],
      [fromLonLat([endBaseNode.lon, endBaseNode.lat])],
    ]
  }

  // @ts-ignore
  return fromLonLat([currentBaseNode.lon, currentBaseNode.lat])
}

const getIcebreaker = (id: string | undefined) => {
  if (!id || !caravans.value.length) return
  const {icebreaker_id} = caravans.value.find(caravan => caravan.uuid === id)!
  return icebreakers.value.find(({id}) => id === icebreaker_id)?.name
}

const getVessels = (id: number) => {
  if (!id || !caravans.value.length) return
  const currentCaravan = caravans.value.find(caravan => caravan.icebreaker_id === id)!

  if (!currentCaravan) return

  return currentCaravan.vessel_ids.map((id: number) => vessels.value.find(vessel => vessel.id === id)?.name!).join(', ')
}

const getFeatures = ({waybill, seaTransport, type}: {
  waybill: IWaybill[],
  seaTransport: IVessel | IIcebreaker,
  type: typeTransport
}) => {
  const geoJsonData: GeoJSONFeature[] = []

  const icebreaker = getIcebreaker(seaTransport?.caravan_id)
  const vessels = getVessels(seaTransport.icebreaker_id)

  waybill.forEach((line: IWaybill, idx: number) => {
    const {point, event} = line

    const coordinates = getCoordsByNode(point, waybill[idx + 1])

    const {point_name} = baseNodes.value.find((node: IBaseNode) => node.id === point)!

    if (event === tTypeWay.WAIT) {
      geoJsonData.push({
        type: 'Feature',
        geometry: {
          'type': 'Point',
          // @ts-ignore
          'coordinates': Array.isArray(coordinates[0]) ? coordinates[0][0] : coordinates,
        },
        properties: {
          ...line,
          ...seaTransport,
          transport: type,
          point_name
        },
      })

      return
    }

    if (event === tTypeWay.STUCK) {
      geoJsonData.push({
        type: 'Feature',
        geometry: {
          'type': 'Point',
          'coordinates': coordinates,
        },
        properties: {
          ...line,
          ...seaTransport,
          transport: type,
          point_name
        },
      })

      return
    }

    if (idx === 0) {
      geoJsonData.push({
        type: 'Feature',
        geometry: {
          'type': 'Point',
          // @ts-ignore
          'coordinates': coordinates[0][0],
        },
        properties: {
          ...line,
          ...seaTransport,
          point: type === typeTransport.VESSELS ? 'start' : '',
          transport: type,
          point_name
        },
      })
    }

    if (event === tTypeWay.FIN || idx === waybill.length - 1) {
      geoJsonData.push({
        type: 'Feature',
        geometry: {
          type: 'Point',
          coordinates: coordinates,
        },
        properties: {
          ...line,
          ...seaTransport,
          transport: type,
          point_name
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
        transport: type,
        icebreakerName: event === tTypeWay.FORMATION ? icebreaker : '',
        vessels: event === tTypeWay.FORMATION ? vessels : '',
        point_name
      },
    })
  })

  return geoJsonData
}

const createGeoJson = (
    layers: IPath[],
    vectorLayers: Ref<Record<string, VectorLayer<Feature<Geometry>>>>[],
    keyIdx: 'vessel_id' | 'icebreaker_id',
    type: typeTransport
) => {
  layers.forEach((item: IPath) => {
    const {waybill} = item

    const listTransport = type === typeTransport.VESSELS ? vessels.value : icebreakers.value
    // @ts-ignore
    const seaTransport = listTransport.find((transport: IVessel | IIcebreaker) => transport.id === item[keyIdx])

    if (!seaTransport) {
      // @ts-ignore
      throw new Error(`Unknown transport: ${item[keyIdx]}`)
    }
    // @ts-ignore
    const vectorLayer = generateVectorLayer(getFeatures,
        {waybill, seaTransport: {...item, ...seaTransport}, type}
    )
    // @ts-ignore
    vectorLayers[item[keyIdx]] = vectorLayer
    map.value?.addLayer(vectorLayer);
  })
}

const createGraph = () => {
  return baseEdges.value.map((edge) => {
    const coordinates = getCoordsByEdge(edge.id)

    return ({
      type: 'Feature',
      geometry: {
        type: 'LineString',
        coordinates: coordinates,
      },
      properties: {
        graph: true
      }
    })
  })
}

const createPointLayer = ({baseEdgeStart, baseEdgeEnd, currentTransport, type}: {
  baseEdgeStart: IBaseEdge, baseEdgeEnd: IBaseEdge, currentTransport: IVessel | IIcebreaker, type: typeTransport
}) => {
  const jsonList = []

  jsonList.push({
    type: 'Feature',
    geometry: {
      'type': 'Point',
      'coordinates': getCoordsByEdge(baseEdgeStart.id)[0][0],
    },
    properties: {
      ...currentTransport,
      point: 'start',
      transport: type,
    }
  })

  if (baseEdgeEnd) jsonList.push({
    type: 'Feature',
    geometry: {
      'type': 'Point',
      'coordinates': getCoordsByEdge(baseEdgeEnd.id)[1][0],

    },
    properties: {
      ...currentTransport,
      point: 'end',
    }
  })

  return jsonList
}

const drawPoints = (points: number[], type: typeTransport) => {
  points.forEach(point => {
    const transportList = type === typeTransport.VESSELS ? vessels.value : icebreakers.value
    const markerList = type === typeTransport.VESSELS ? vesselMarkers.value : icebreakerMarkers.value
    const currentTransport = transportList.find((transport) => transport.id === point)

    const baseEdgeStart = baseEdges.value.find(edge => edge.id === currentTransport?.source)
    const baseEdgeEnd = baseEdges.value.find(edge => edge.id === currentTransport?.target)

    // @ts-ignore
    const vectorLayer = generateVectorLayer(createPointLayer,
        {baseEdgeStart, baseEdgeEnd, currentTransport, type}
    )

    markerList[point] = vectorLayer

    map.value?.addLayer(vectorLayer)
  })
}

const removeLayers = (listLayers: Record<string, VectorLayer<Feature<Geometry>>>) => {
  Object.keys(listLayers)?.forEach((layerKey: string) => {
    const layer = listLayers[layerKey]
    delete listLayers[layerKey]
    map.value?.removeLayer(layer)
  })
}

const generateVectorLayers = (
    vectorLayers: Ref<Record<string, VectorLayer<Feature<Geometry>>>>[],
    paths: IPath[],
    keyIdx: 'vessel_id' | 'icebreaker_id',
    type: typeTransport
) => {
  if (Object.keys(vectorLayers).length && !paths.length) {
    // @ts-ignore
    removeLayers(vectorLayers)
    return
  }

  if (Object.keys(vectorLayers).length) {
    const removingLayers = Object.keys(vectorLayers).filter(layer => {
      const path = paths.find(path => {
        // @ts-ignore
        return path[keyIdx] === Number(layer)
      })
      return !path
    })

    removingLayers.forEach(layer => {
      // @ts-ignore
      const currentLayer = vectorLayers[layer]
      // @ts-ignore
      delete vectorLayers[layer]

      map.value?.removeLayer(currentLayer)
    })
  }
  // @ts-ignore
  const newLayers = paths.filter(path => !vectorLayers[path[keyIdx]])
  createGeoJson(newLayers, vectorLayers, keyIdx, type)
}

const changeMarkersVisibility = (
    points: number[],
    markers: Record<string, VectorLayer<Feature<Geometry>>>[],
    type: typeTransport
) => {
  if (!points.length) {
    removeLayers(markers)
    return
  }

  if (Object.keys(markers).length) {
    const removingPoints = Object.keys(markers).filter(point => {
      return !points.includes(Number(point))
    })
    removingPoints.forEach(point => {
      // @ts-ignore
      const currentPoint = markers[point]
      // @ts-ignore
      map.value?.removeLayer(currentPoint)
      delete markers[point]
    })
  }

  const newPoints = points.filter(point => !markers[point])
  drawPoints(newPoints, type)
}

watch(() => pathsVessels.value, () => {
  generateVectorLayers(
      // @ts-ignore
      vectorLayersVessels.value,
      pathsVessels.value,
      'vessel_id',
      typeTransport.VESSELS
  )
}, {deep: true})

watch(() => pathsIcebreakers.value, () => {
  generateVectorLayers(
      // @ts-ignore
      vectorLayersIcebreakers.value,
      pathsIcebreakers.value,
      'icebreaker_id',
      typeTransport.ICEBREAKERS
  )
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
    // @ts-ignore
    map.value?.addLayer(graph.value);
    return
  }
  // @ts-ignore
  map.value?.removeLayer(graph.value);
})

watch(() => vesselPoints.value, () => {
  // @ts-ignore
  changeMarkersVisibility(vesselPoints.value, vesselMarkers.value, typeTransport.VESSELS)
}, {deep: true})

watch(() => icebreakerPoints.value, () => {
  // @ts-ignore
  changeMarkersVisibility(icebreakerPoints.value, icebreakerMarkers.value, typeTransport.ICEBREAKERS)
}, {deep: true})

watch(() => tiffDate.value, async () => {
  if (dateLayer.value) map.value?.removeLayer(dateLayer.value)

  if (!tiffDate.value) return

  const response = await fetch(`${import.meta.env.VITE_APP_BASE_URL}get_tiff?dt=${tiffDate.value}`)
  const blob = await response.blob()
  const source = new GeoTIFF({
    sources: [
      {
        blob: blob,
      },
    ],
    zIndex: 0
  });

  const layer = new WebGLTile({
    source: source,
  })

  dateLayer.value = layer

  map.value.addLayer(layer)

  map.value.setView(source
      .getView().then((options) => {
        const center = transform(options.center, 'EPSG:4326', 'EPSG:3857')
        const resolution = options.resolutions[0];
        return {
          resolution,
          center,
          constrainResolution: true,
          maxZoom: 8
        }
      })
  )
})
</script>

<style scoped>
#map {
  height: 100%;
  width: 100%;
}
</style>
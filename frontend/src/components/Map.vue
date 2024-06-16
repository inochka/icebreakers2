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
import Feature, {FeatureLike} from "ol/Feature";
import {Overlay} from "ol";
import {Geometry} from "ol/geom";
import {generateVectorLayer} from "../utils/createVectorLayer.ts";
import {WebGLTile} from "ol/layer";
import {getDate} from "../utils/getDate.ts";
import axios from "axios";

const map: Ref<Map | null> = ref(null);
const popover = ref(undefined)

const vectorLayers: Ref<Record<string, VectorLayer<Feature<Geometry>>>> = ref({})
const graph: Ref<Record<string, VectorLayer<Feature<Geometry>>>> = ref({})
const dateLayer: Ref<Record<string, VectorLayer<Feature<Geometry>>>> = ref({})
const vesselMarkers: Ref<Record<string, VectorLayer<Feature<Geometry>>>> = ref({})
const icebreakerMarkers: Ref<Record<string, VectorLayer<Feature<Geometry>>>> = ref({})

const {
  paths,
  baseNodes,
  vessels,
  baseEdges,
  icebreakers,
  vesselPoints,
  icebreakerPoints,
  tiffDate
} = storeToRefs(useIceTransportStore())

const {showGraph} = storeToRefs(useCommonStore())

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
    disposePopover();

    const features: FeatureLike[] = []

    map.value?.forEachFeatureAtPixel(evt.pixel, (feature) => {
          const properties = feature.getProperties()
          const {graph} = properties

          if (feature && !graph) features.push(feature)
        }
    )

    if (features.length) {
      popup.setPosition(evt.coordinate);
      const strings = features.map((feature, idx) => getFeature(feature, features.length, idx))
      content.innerHTML = strings.join('\n')
    }
  });

  map.value.on('pointermove', (e) => {
    const pixel = map.value?.getEventPixel(e.originalEvent);
    const hit = map.value?.hasFeatureAtPixel(pixel!);
    map.value.getTarget().style.cursor = hit ? 'pointer' : '';
  });

  map.value.on('movestart', disposePopover);
})

const getFeature = (feature: FeatureLike, length: number, idx: number) => {
  const properties = feature.getProperties()
  if (!properties.name) return ''

  return `
  <p><span style="color: gray">Название: </span>${properties.name}</p>
  <p><span style="color: gray">Ледовый класс: </span>${properties.ice_class}</p>
  <p><span style="color: gray">Скорость в узлах по чистой воде: </span>${properties.speed}</p>
  <p><span style="color: gray">Исходный порт: </span>${properties.source_name}</p>
  ${properties.target_name ? `<p><span style="color: gray">Конечный порт: </span>${properties.target_name}</p>` : ''}
  ${properties.start_date ? `<p><span style="color: gray">Дата начала плавания: </span>${getDate(properties.start_date, 'yyyy-MM-dd')}</p>` : ''}
  ${properties.dt ? `<p><span style="color: gray">Текущая дата: </span>${getDate(properties.dt, 'yyyy-MM-dd')}</p>` : ''}
  ${length > 1 && idx !== length - 1 ? '<div style="height: 10px"></div>' : ''}
 `
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

    if (event === tTypeWay.STUCK) {
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

const createGeoJson = (layers: IPath[]) => {
  layers.forEach((item: IPath) => {
    const {waybill, vessel_id, success} = item
    // const listTransport = type === typeTransport.VESSELS ? iceTransport.value : icebreakers.value
    const listTransport = vessels.value
    const seaTransport = listTransport.find((transport: IVessel | IIcebreaker) => transport.id === vessel_id)

    if (!seaTransport) {
      throw new Error(`Unknown transport: ${vessel_id}`)
    }

    const vectorLayer = generateVectorLayer(getFeatures,
        {waybill, seaTransport, success}
    )
    vectorLayers.value[vessel_id] = vectorLayer
    map.value?.addLayer(vectorLayer);
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
      properties: {
        graph: true
      }
    })
  })
}

const createPointLayer = ({baseEdgeStart, baseEdgeEnd, currentTransport, type}) => {
  const jsonList = []

  jsonList.push({
    type: 'Feature',
    geometry: {
      'type': 'Point',
      'coordinates': getCoords(baseEdgeStart.id)[0][0],
    },
    properties: {
      ...currentTransport,
      point: 'start',
      transport: type
    }
  })

  if (baseEdgeEnd) jsonList.push({
    type: 'Feature',
    geometry: {
      'type': 'Point',
      'coordinates': getCoords(baseEdgeEnd.id)[1][0],
    },
    properties: {
      ...currentTransport,
      point: 'end'
    }
  })

  return jsonList
}

const drawPoints = (points: number[], type: typeTransport) => {
  points.forEach(point => {
    const transportList = type === typeTransport.VESSELS ? vessels.value : icebreakers.value
    const markerList = type === typeTransport.VESSELS ? vesselMarkers.value : icebreakerMarkers.value
    const currentTransport = transportList.find((transport) => transport.id === point)

    const baseEdgeStart = baseEdges.value.find(edge => edge.id === currentTransport.source)
    const baseEdgeEnd = baseEdges.value.find(edge => edge.id === currentTransport.target)

    const vectorLayer = generateVectorLayer(createPointLayer,
        {baseEdgeStart, baseEdgeEnd, currentTransport, type}
    )

    markerList[point] = vectorLayer

    map.value?.addLayer(vectorLayer)
  })
}

const removeLayers = (listLayers: Record<string, VectorLayer<Feature<Geometry>>>) => {
  Object.keys(listLayers).forEach((layerKey: string) => {
    const layer = listLayers[layerKey]
    delete listLayers[layerKey]
    map.value?.removeLayer(layer)
  })
  return
}

const changeMarkersVisibility = (
    points: number[],
    markers: Record<string, VectorLayer<Feature<Geometry>>>[],
    type: typeTransport
) => {
  if (!points.length && Object.keys(markers).length) {
    removeLayers(markers)
    return
  }

  if (Object.keys(markers).length) {
    const removingPoints = Object.keys(markers).filter(point => {
      return !points.includes(Number(point))
    })
    removingPoints.forEach(point => {
      const currentPoint = markers[point]
      delete markers[point]

      map.value?.removeLayer(currentPoint)
    })
  }

  const newPoints = points.filter(point => !markers[point])
  drawPoints(newPoints, type)
}

watch(() => paths.value, () => {
  if (Object.keys(vectorLayers.value).length && !paths.value.length) {
    removeLayers(vectorLayers.value)
    return
  }

  if (Object.keys(vectorLayers).length) {
    const removingLayers = Object.keys(vectorLayers.value).filter(layer => {
      const path = paths.value.find(path => {
        return path.vessel_id === Number(layer)
      })
      return !path
    })
    removingLayers.forEach(layer => {
      const currentLayer = vectorLayers.value[layer]
      delete vectorLayers.value[layer]

      map.value?.removeLayer(currentLayer)
    })
  }

  const newLayers = paths.value.filter(path => !vectorLayers.value[path.vessel_id])
  createGeoJson(newLayers)
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

watch(() => vesselPoints.value, () => {
  changeMarkersVisibility(vesselPoints.value, vesselMarkers.value, typeTransport.VESSELS)
}, {deep: true})

watch(() => icebreakerPoints.value, () => {
  changeMarkersVisibility(icebreakerPoints.value, icebreakerMarkers.value, typeTransport.ICEBREAKERS)
}, {deep: true})

watch(() => tiffDate.value, () => {
  if (dateLayer.value) map.value?.removeLayer(dateLayer.value);
  //
  // if (tiffDate.value) {
  //   fetch('../mock/vessels.json')
  //       .then((response) => console.log(response))
  //       .then((blob) => {
  //         console.log(blob)
  //         const source = new GeoTIFF({
  //           sources: [
  //             {
  //               blob: blob,
  //             },
  //           ],
  //         });
  //
  //         // const map = new Map({
  //         //   target: 'map',
  //         //   layers: [
  //         //     new TileLayer({
  //         //       source: source,
  //         //     }),
  //         //   ],
  //         //   view: source.getView().then((viewConfig) => {
  //         //     viewConfig.showFullExtent = true;
  //         //     return viewConfig;
  //         //   }),
  //         // });
  //       });
  // }
    // fetch(`../../../tiffs/${tiffDate.value}.tif`)

  //   fetch('./example.tiff')
  //       .then((response) => {
  //         console.log(response)
  //         response.blob()
  //       })
  //       .then((blob) => {
  //         console.log(blob)
  //         const source = new GeoTIFF({
  //           sources: [
  //             {
  //               blob,
  //             },
  //           ],
  //         });
  //
  //         const layer = new WebGLTile({
  //           source: source,
  //         })
  //
  //         map.value.addLayer(layer)
  //
  //         dateLayer.value = layer
  //
  //         map.value.setView(source
  //             .getView().then((options) => {
  //               const center = options.center;
  //               const resolution = options.resolutions[0];
  //               const projection = options.projection;
  //               return {center, resolution, projection};
  //             })
  //         )
  //       })
  // }
})
</script>

<style scoped>
#map {
  height: 100%;
  width: 100%;
}
</style>
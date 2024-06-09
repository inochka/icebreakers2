<template>
  <div id="map"/>
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
import {IBaseEdge, IBaseNode, IPath, IVessel, IWaybill, tTypeWay} from "../types.ts";
import {GeoJSONFeature} from "ol/format/GeoJSON";
import {Circle, Fill, Icon, Stroke, Style} from "ol/style";
import {FeatureLike} from "ol/Feature";
import startPoint from '../assets/icons/port-sign-svgrepo-com.png'
import endPoint from '../assets/icons/anchor-icon-svgrepo-com.png'

const map: Ref<Map | null> = ref(null);

const {paths, baseNodes, vessels, baseEdges} = storeToRefs(useVesselsStore())

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
})

const getCoords = (point: number) => {
  const currentBaseEdge = baseEdges.value.find((edge: IBaseEdge) => edge.id === point)

  if (!currentBaseEdge) return []

  const {start_point_id, end_point_id} = currentBaseEdge;

  const startPoint: IBaseNode | undefined = baseNodes.value.find(({id}: IBaseNode) => id === start_point_id);
  const endPoint: IBaseNode | undefined = baseNodes.value.find(({id}: IBaseNode) => id === end_point_id);
  if (!endPoint || !startPoint) return [];

  return [
    [fromLonLat([startPoint.lat, startPoint.lon])],
    [fromLonLat([endPoint.lat, endPoint.lon])],
  ]
}

const getFeatures = (waybill: IWaybill[], currentVessel: IVessel) => {
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
          ...currentVessel
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
      console.log(coordinates, coordinates[1])
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
        coordinates,
      },
      properties: {
        ...line,
        ...currentVessel
      },
    })
  })

  return geoJsonData
}

const getStyles = (feature: FeatureLike) => {
  const {event} = feature.getProperties()
  const type = feature.getGeometry()?.getType()

  if (type === 'Point' && event === tTypeWay.MOVE) {
    return new Style({
      image: new Icon({
        src: startPoint,
        height: 20,
        width: 20,
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
        color: 'green',
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
    const {waybill, id_vessel} = item

    const currentVessel = vessels.value.find((vessel: IVessel) => vessel.id === id_vessel)

    if (!currentVessel) {
      throw new Error(`Unknown vessel: ${id_vessel}`)
    }

    const features = {
      type: 'FeatureCollection',
      crs: {
        type: 'lines',
        properties: {
          name: 'EPSG:3857',
        },
      },
      features: getFeatures(waybill, currentVessel),
    }

    const vectorSource = new VectorSource({
      features: new GeoJSON().readFeatures(features),
    });

    const vectorLayer = new VectorLayer({
      source: vectorSource,
      style: (feature) => getStyles(feature)
    });

    map.value?.addLayer(vectorLayer);
  })
}

watch(() => paths.value, (newPathList) => {
  if (newPathList.length) createGeoJson()
}, {deep: true})
</script>

<style scoped>
#map {
  height: 100%;
  width: 100%;
}
</style>
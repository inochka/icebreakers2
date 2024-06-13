<template>
  <ol-map ref="map" style="height: 100%">
    <ol-view
        ref="view"
        :center="center"
        :rotation="rotation"
        :zoom="zoom"
        :projection="projection"
    />

    <ol-tile-layer>
      <ol-source-osm />
    </ol-tile-layer>
  </ol-map>
</template>

<script setup lang="ts">
import {onMounted, Ref, ref, watch} from "vue";
import {fromLonLat, transform} from "ol/proj";
import Map from 'ol/Map';
import {storeToRefs} from "pinia";
import {useVesselsStore} from "../store";
import {IBaseEdge, IBaseNode, IIcebreaker, IPath, IVessel, IWaybill, tTypeWay, typeTransport} from "../types.ts";
import VectorSource from "ol/source/Vector";
import {GeoJSON} from "ol/format";
import VectorLayer from "ol/layer/Vector";

const map = ref<{ map: Map }>(null);

const center = ref(transform([-175, 80], 'EPSG:4326', 'EPSG:3857'));
const projection = ref("EPSG:3857");
const zoom = ref(3);
const rotation = ref(0);
const layers: Record<string, any> = ref({})

const {paths, baseNodes, vessels, icebreakers, baseEdges} = storeToRefs(useVesselsStore())

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

const createGeoJson = () => {
  paths.value.forEach((item: IPath) => {
    const {id, type} = item

    if (layers[item.id]) return

    const currentSeaTransport = type === typeTransport.VESSELS
        ? vessels.value.find((vessel: IVessel) => vessel.id === id) :
        icebreakers.value.find((vessel: IIcebreaker) => vessel.id === id)

    if (!currentSeaTransport) {
      throw new Error(`Unknown sea transport: ${id}`)
    }

    const path = { id: [] }

    if (item.success) {
      item.waybill?.forEach((line: IWaybill, idx: number) => {
        const {point, event} = line

        const coordinates = getCoords(point)

        if (event === tTypeWay.WAIT) {
          path.id.push({
            coordinates: coordinates[0][0],
            ...line,
            ...currentSeaTransport,
            radius: 5,
            fill: 'gray',
            strokeColor: 'gray',
            strokeWidth: 5,
          })

          return
        }

        if (idx === 0) {
          path.id.push({
            coordinates: coordinates[0],
            ...line,
            ...currentSeaTransport,
            radius: 5,
            fill: 'gray',
            strokeColor: 'gray',
            strokeWidth: 5,
          })

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
            ...currentVessel
          },
        })
      })
    }
  })
}

watch(() => paths.value, (newPathList) => {
  if (newPathList.length) createGeoJson()
}, {deep: true})
</script>

<style scoped lang="scss">
.ol-map {
  position: relative;
}

.ol-map-loading:after {
  content: "";
  box-sizing: border-box;
  position: absolute;
  top: 50%;
  left: 50%;
  width: 80px;
  height: 80px;
  margin-top: -40px;
  margin-left: -40px;
  border-radius: 50%;
  border: 5px solid rgba(180, 180, 180, 0.6);
  border-top-color: var(--vp-c-brand-1);
  animation: spinner 0.6s linear infinite;
}

@keyframes spinner {
  to {
    transform: rotate(360deg);
  }
}
</style>
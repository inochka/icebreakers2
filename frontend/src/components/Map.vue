<template>
  <div id="map" />
</template>

<script setup lang="ts">
import Map from 'ol/Map';
import View from 'ol/View';
import TileLayer from 'ol/layer/Tile';
import {onMounted, Ref, ref} from "vue";
import {OSM} from "ol/source";
import 'ol/ol.css';
import { transform } from 'ol/proj';

const map: Ref<Map | null> = ref(null);

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
</script>

<style scoped>
#map {
  height: 100%;
  width: 100%;
}
</style>
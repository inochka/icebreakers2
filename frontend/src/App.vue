<template>
  <div class="wrapper">
    <div class="cell cell-sidebar">
      <Layers />
    </div>
    <div class="cell cell-map">
      <Map/>
    </div>
  </div>
</template>

<script setup lang="ts">
import Map from "./components/Map.vue";
import Layers from "./components/Layers.vue";
</script>

<style scoped>
.wrapper {
  display: grid;
  grid-template-columns: 0.5fr 2fr;
  height: 100%;
}
</style>

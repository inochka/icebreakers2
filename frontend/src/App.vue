<template>
  <div class="wrapper">
    <div class="cell cell-sidebar">
      <Layers />
    </div>
    <div class="cell cell-map">
      <Map/>
    </div>
  </div>

  <Teleport to="#modal">
    <Modal v-if="openModal" />
  </Teleport>
</template>

<script setup lang="ts">
import Map from "./components/Map.vue";
import Layers from "./components/Layers.vue";
import {storeToRefs} from "pinia";
import {useStore} from "./store";
import Modal from "./components/UI/Modal.vue";

const {openModal} = storeToRefs(useStore())

</script>

<style scoped>
.wrapper {
  display: grid;
  grid-template-columns: 1fr 3fr;
  height: 100%;
}
</style>

<template>
  <Loader v-if="isLoading"/>

  <div class="wrapper">
    <div class="cell cell-sidebar">
      <Templates v-if="typeSidebar === TypeSidebar.TEMPLATES"/>
      <Layers v-else/>
    </div>
    <div class="cell cell-map">
      <Map/>
    </div>
  </div>

  <Legend/>

  <Teleport to="#modal">
    <Modal v-if="openModal"/>
  </Teleport>
</template>

<script setup lang="ts">
import Map from "./components/Map.vue";
import Layers from "./components/Layers.vue";
import {storeToRefs} from "pinia";
import Modal from "./components/UI/Modal.vue";
import Loader from "./components/UI/Loader.vue";
import {useCommonStore, useIceTransportStore} from "./store";
import Legend from "./components/UI/Legend.vue";
import {onMounted} from "vue";
import {TypeSidebar} from "./types.ts";
import Templates from "./components/Templates.vue";

const {openModal, isLoading, typeSidebar} = storeToRefs(useCommonStore())
const {getBaseNodes, getBaseEdges, getVessels, getIcebreakers} = useIceTransportStore()

onMounted(async () => {
  await Promise.all([
    await getBaseNodes(),
    await getBaseEdges(),
    await getVessels(),
    await getIcebreakers()
  ])
})
</script>

<style scoped>
.wrapper {
  display: grid;
  grid-template-columns: 370px auto;
  height: 100%;
}
</style>

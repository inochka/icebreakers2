<template>
  <Loader v-if="isLoading"/>

  <div class="wrapper">
    <div class="cell cell-sidebar">
      <Layers/>
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
import {useCommonStore, useVesselsStore} from "./store";
import Legend from "./components/UI/Legend.vue";
import {onMounted} from "vue";

const {openModal, isLoading} = storeToRefs(useCommonStore())
const {getBaseNodes, getBaseEdges, getVessels, getIcebreakers} = useVesselsStore()

onMounted(async () => {
  await Promise.all([
    await getBaseNodes(),
    await getIcebreakers(),
    await getVessels(),
    await getBaseEdges()
  ])
})
</script>

<style scoped>
.wrapper {
  display: grid;
  grid-template-columns: 1fr 3fr;
  height: 100%;
}
</style>

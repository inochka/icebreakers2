<template>
  <div>
    <div class="title-wrapper">
      <div class="title-wrapper_block">
        <Checkbox @onChecked="onCheckAll" :checked="checkAllVessels"/>
        <h3 class="title">Заявка на проводку</h3>
      </div>
      <ArrowIcon
          @click="isVisibleVessels = !isVisibleVessels"
          class="icon"
          :class="{'arrow-up': !isVisibleVessels}"
      />
    </div>
    <div class="list" v-if="isVisibleVessels">
      <div v-for="vessel in vessels" :key="vessel.id" class="list_item">
        <Layer
            :is-change-parent="isChangeParentVessel"
            @changeParentCheckbox="changeParentCheckbox"
            :layer="vessel"
            :is-check-parent="checkAllVessels"
            :type="typeTransport.VESSELS"
            :typeLayer="typeLayer"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {TypeLayersForMap, typeTransport} from "../types.ts";
import Checkbox from "./UI/Checkbox.vue";
import ArrowIcon from '../assets/icons/arrow.svg'
import {ref} from "vue";
import {storeToRefs} from "pinia";
import {useIceTransportStore} from "../store";
import Layer from "./Layer.vue";

type Props = {
  typeLayer: TypeLayersForMap
}

const props = defineProps<Props>()

const {vessels, pathsVessels, vesselPoints} = storeToRefs(useIceTransportStore())

const isVisibleVessels = ref(true)

const checkAllVessels = ref(false)

const isChangeParentVessel = ref(false)

const emits = defineEmits(['getAllData'])

const onCheckAll = async () => {
  checkAllVessels.value = !checkAllVessels.value

  if (!checkAllVessels.value) {
    props.typeLayer === TypeLayersForMap.PATH ? pathsVessels.value = [] : vesselPoints.value = []
    isChangeParentVessel.value = true
    return;
  }

  emits('getAllData', vessels.value)
}

const changeParentCheckbox = () => {
  checkAllVessels.value = false
  isChangeParentVessel.value = false
}
</script>

<style lang="scss" scoped>
@import "./src/assets/styles/icons.scss";
</style>
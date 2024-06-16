<template>
  <div>
    <div class="title-wrapper">
      <div class="title-wrapper_block">
        <Checkbox @onChecked="onCheckAll" :checked="checkAllIcebreakers"/>
        <h3 class="title">Ледоколы</h3>
      </div>
      <ArrowIcon
          @click="isVisibleIcebreakers = !isVisibleIcebreakers"
          class="icon"
          :class="{'arrow-up': !isVisibleIcebreakers}"
      />
    </div>
    <div class="list" v-if="isVisibleIcebreakers">
      <div v-for="icebreaker in icebreakers" :key="icebreaker.id" class="list_item">
        <Layer
            :typeLayer="typeLayer"
            @changeParentCheckbox="changeParentCheckbox"
            :layer="icebreaker"
            :is-change-parent="isChangeParentIcebreaker"
            :type="typeTransport.ICEBREAKERS"
            :is-check-parent="checkAllIcebreakers"
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

const {icebreakers, icebreakerPoints, pathsIcebreakers} = storeToRefs(useIceTransportStore())

const isVisibleIcebreakers = ref(true)

const checkAllIcebreakers = ref(false)

const isChangeParentIcebreaker = ref(false)

const emits = defineEmits(['getAllData'])

const onCheckAll = async () => {
  checkAllIcebreakers.value = !checkAllIcebreakers.value

  if (!checkAllIcebreakers.value) {
    if (props.typeLayer === TypeLayersForMap.PATH) {
      pathsIcebreakers.value = []
    } else {
      icebreakerPoints.value = []
    }

    isChangeParentIcebreaker.value = true
    return;
  }

   emits('getAllData', icebreakers.value)
}

const changeParentCheckbox = () => {
  checkAllIcebreakers.value = false
  isChangeParentIcebreaker.value = false
}
</script>

<style lang="scss" scoped>
@import "./src/assets/styles/icons.scss";
</style>
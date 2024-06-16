<template>
  <div class="layer">
    <Checkbox :checked="isChecked" @onChecked="onChecked"/>
    <div>{{ layer.name }}</div>
  </div>
  <p class="layer_date">{{ date }}</p>
  <div class="icons">
    <InfoIcon @click="onOpenInfoModal" class="icon"/>
  </div>
</template>

<script setup lang="ts">
import {IIcebreaker, IVessel, tModal, TypeLayersForMap, typeTransport} from "../types.ts";
import {storeToRefs} from "pinia";
import {useCommonStore, useTemplateStore, useIceTransportStore} from "../store";
import Checkbox from "./UI/Checkbox.vue";
import InfoIcon from '../assets/icons/info.svg'
import {computed, ref, watch} from "vue";
import {getDate} from "../utils/getDate.ts";

const {openModal, typeModal, modalInfo} = storeToRefs(useCommonStore())

const {getPathVessels, getPathIcebreakers} = useIceTransportStore()
const {
  pathsVessels,
  pathsIcebreakers,

  icebreakerPoints,
  vesselPoints
} = storeToRefs(useIceTransportStore())

const {selectTemplate} = storeToRefs(useTemplateStore())

const emits = defineEmits(['changeParentCheckbox'])

type Props = {
  layer: IVessel | IIcebreaker
  isCheckParent: boolean
  type: typeTransport
  isChangeParent: boolean
  typeLayer: TypeLayersForMap
}

const props = defineProps<Props>()

const isChecked = ref(false)

watch(() => props.isCheckParent, (newCheckParent) => {
  if (newCheckParent) isChecked.value = true
})

watch(() => props.isChangeParent, (newChangeParent) => {
  if (newChangeParent) isChecked.value = false
})

const date = computed(() => {
  return getDate(props.layer.start_date, 'yyyy-MM-dd')
})

const loadGraph = async () => {
  if (!isChecked.value) return
  if (props.type === typeTransport.VESSELS) {
    await getPathVessels({vessel_id: props.layer.id, template_name: selectTemplate.value?.name!})

    return
  }

  await getPathIcebreakers({icebreaker_id: props.layer.id, template_name: selectTemplate.value?.name!})
}

const onOpenInfoModal = () => {
  typeModal.value = props.type === typeTransport.VESSELS ? tModal.VESSEL : tModal.ICEBREAKER
  // @ts-ignore
  modalInfo.value = props.layer
  openModal.value = true
}

const createDataForPoints = () => {
  const listTransport = props.type === typeTransport.ICEBREAKERS ? icebreakerPoints.value : vesselPoints.value

  if (props.isCheckParent && !isChecked.value) {
    emits('changeParentCheckbox')
    return;
  }

  if (!isChecked.value) {
    const idx = listTransport.findIndex(id => id === props.layer.id)
    listTransport.splice(idx, 1)

    return
  }

  listTransport.push(props.layer.id)
}

const createDataForPaths = () => {
  if (props.isCheckParent && !isChecked.value) {
    emits('changeParentCheckbox')
  } else if (!isChecked.value) {
    const list = props.type === typeTransport.VESSELS ? pathsVessels.value : pathsIcebreakers.value
    const keyId = props.type === typeTransport.VESSELS ? 'vessel_id' : 'icebreaker_id'

    // @ts-ignore
    const idx = list.findIndex(path => path[keyId] === props.layer.id)
    if (idx !== -1) list.splice(idx, 1)
  }

  loadGraph()
}

const onChecked = () => {
  isChecked.value = !isChecked.value

  if (props.typeLayer === TypeLayersForMap.POINT) {
    createDataForPoints()
    return
  }

  createDataForPaths()
}
</script>

<style lang="scss" scoped>
@import "./src/assets/styles/icons.scss";

.layer {
  display: flex;
  gap: 8px;
  align-items: baseline;

  &_date {
    font-size: 12px;
    color: #bbbbbb;
  }
}

.icons {
  display: flex;
  gap: 10px;
}
</style>
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

const {openModal, typeModal, modalInfo, isLoading} = storeToRefs(useCommonStore())

const {getPath} = useIceTransportStore()
const {paths, icebreakerPoints, vesselPoints} = storeToRefs(useIceTransportStore())

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

const loadGraph =  async() => {
  isLoading.value = true

  if (isChecked.value) await getPath({vessel_id: props.layer.id, template_name: selectTemplate.value.name})

  isLoading.value = false
}

const onOpenInfoModal = () => {
  typeModal.value = props.type === typeTransport.VESSELS ? tModal.VESSEL : tModal.ICEBREAKER
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
    const idx = paths.value.findIndex(path => path.vessel_id === props.layer.id)
    paths.value.splice(idx, 1)
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
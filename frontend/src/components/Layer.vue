<template>
  <div class="layer">
    <Checkbox :checked="isChecked" @onChecked="onChecked"/>
    <div>{{ layer.name }}</div>
  </div>
  <p class="layer_date">{{ layer.start_date }}</p>
  <div class="icons">
    <InfoIcon @click="onOpenInfoModal" class="icon"/>
  </div>
</template>

<script setup lang="ts">
import {IIcebreaker, IVessel, tModal, typeTransport} from "../types.ts";
import {storeToRefs} from "pinia";
import {useCommonStore, useVesselsStore} from "../store";
import Checkbox from "./UI/Checkbox.vue";
import InfoIcon from '../assets/icons/info.svg'
import {ref, watch} from "vue";

const {openModal, typeModal, modalInfo, isLoading} = storeToRefs(useCommonStore())

const {getPath, paths} = useVesselsStore()

const emits = defineEmits(['changeParentCheckbox'])

type Props = {
  layer: IVessel | IIcebreaker
  isCheckParent: boolean
  type: typeTransport
  isChangeParent: boolean
}

const props = defineProps<Props>()

const isChecked = ref(false)

watch(() => props.isCheckParent, (newCheckParent) => {
  if (newCheckParent) isChecked.value = true
})

watch(() => props.isChangeParent, (newChangeParent) => {
  if (newChangeParent) isChecked.value = false
})

const loadGraph = () => {
  isLoading.value = true

  setTimeout(() => {
    isLoading.value = false
    if (isChecked.value) getPath(props.layer.id, props.type)
  }, 1000)
}

const onOpenInfoModal = () => {
  typeModal.value = props.type === typeTransport.VESSELS ? tModal.VESSEL : tModal.ICEBREAKER
  modalInfo.value = props.layer
  openModal.value = true
}

const onChecked = () => {
  isChecked.value = !isChecked.value
  if (props.isCheckParent && !isChecked.value) {
    emits('changeParentCheckbox')
  } else if (!isChecked.value) {
    const idx = paths.value.findIndex(path => path.id === props.layer.id)
    paths.value.splice(idx, 1)
  }

  loadGraph()
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
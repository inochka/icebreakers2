<template>
  <div class="wrapper-layers">
    <div>
      <div class="title-wrapper">
        <div class="title-wrapper_block">
          <Checkbox @onChecked="onCheckAll(typeTransport.ICEBREAKERS)" :checked="checkAllIcebreakers" />
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
              @changeParentCheckbox="changeParentCheckbox(typeTransport.ICEBREAKERS)"
              :layer="icebreaker"
              :is-change-parent="isChangeParentIcebreaker"
              :type="tModal?.ICEBREAKER"
              :is-check-parent="checkAllIcebreakers"
          />
        </div>
      </div>
    </div>

    <div>
      <div class="title-wrapper">
        <div class="title-wrapper_block">
          <Checkbox @onChecked="onCheckAll(typeTransport.VESSELS)" :checked="checkAllVessels" />
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
              @changeParentCheckbox="changeParentCheckbox(typeTransport.VESSELS)"
              :layer="vessel"
              :is-check-parent="checkAllVessels"
              :type="tModal?.VESSEL"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {storeToRefs} from "pinia";
import Checkbox from "./UI/Checkbox.vue";
import {useVesselsStore} from "../store";
import {onMounted, ref} from "vue";
import Layer from "./Layer.vue";
import ArrowIcon from '../assets/icons/arrow.svg'
import {tModal} from "../types.ts";
import {useCommonStore} from "../store";

enum typeTransport {
  "VESSELS" = 'vessels',
  'ICEBREAKERS' = 'icebreakers',
}

const {getVessels, getIcebreakers} = useVesselsStore()
const {vessels, icebreakers} = storeToRefs(useVesselsStore())

const {isLoading} = storeToRefs(useCommonStore())

const isVisibleVessels = ref(true)
const isVisibleIcebreakers = ref(true)
const checkAllVessels = ref(false)
const checkAllIcebreakers = ref(false)
const isChangeParentVessel = ref(false)
const isChangeParentIcebreaker = ref(false)

onMounted(async () => {
  await Promise.all([getVessels(), getIcebreakers()])
})

const loadGraph = () => {
  isLoading.value = true

  setTimeout(() => {
    isLoading.value = false
  }, 1000)
}

const onCheckAll = (type: typeTransport) => {
  if (type === 'vessels') {
    checkAllVessels.value = !checkAllVessels.value

    if (!checkAllVessels.value) {
      isChangeParentVessel.value = true
      return;
    }

    loadGraph()
    return
  }

  checkAllIcebreakers.value = !checkAllIcebreakers.value

  if (!checkAllIcebreakers.value) {
    isChangeParentIcebreaker.value = true
    return
  }

  loadGraph()
}

const changeParentCheckbox = (type: typeTransport) => {
  if (type === 'icebreakers') {
    checkAllIcebreakers.value = false
    isChangeParentIcebreaker.value = false

    return
  }

  checkAllVessels.value = false
  isChangeParentVessel.value = false
}
</script>

<style lang="scss" scoped>
@import "./src/assets/styles/icons.scss";

.wrapper-layers {
  padding: 0 30px 0 30px;
  display: flex;
  flex-direction: column;
  gap: 5px;

  .title-wrapper {
    display: flex;
    gap: 5px;
    align-items: baseline;
    justify-content: space-between;

    .arrow-up {
      transform: rotate(180deg) translateY(-8px);
    }

    &_block {
      display: flex;
      gap: 5px;
      align-items: baseline;

      .title {
        margin-top: 35px;
        margin-bottom: 15px;
      }
    }
  }

  .list {
    margin-left: 20px;
    height: 300px;
    overflow-y: auto;
    padding-right: 10px;
    scrollbar-color: #acace5 #eef3ff;
    scrollbar-width: thin;

    &_item {
      justify-content: space-between;
      align-items: baseline;
      display: flex;
      gap: 5px;
      margin-bottom: 3px;
    }
  }
}
</style>
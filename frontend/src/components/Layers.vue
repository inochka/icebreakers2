<template>
  <div class="wrapper-layers">
    <div class="period">
      <div class="checkbox">
        <Checkbox @onChecked="showGraph = !showGraph" :checked="showGraph"/>
        <p>Показать маршрутный граф</p>
      </div>

      <div>
        <div class="checkbox">
          <Checkbox @onChecked="onCheckedTiff" :checked="isShowTiff"/>
          <p>Показать ледовую обстановку</p>
        </div>
        <div class="datepicker" v-if="isShowTiff">
          <VueDatePicker
              v-model="date"
              text-input
              :enable-time-picker="false"
              :start-date="new Date(vessels[0].start_date)"
              :min-date="new Date(vessels[0].start_date)"
              @update:model-value="changeDate"
          />
        </div>
      </div>
    </div>

    <Icebreakers
        :typeLayer="TypeLayersForMap.PATH"
        @getAllData="list => getAllData(list, typeTransport.ICEBREAKERS)"
    />

    <Vessels
        :typeLayer="TypeLayersForMap.PATH"
        @getAllData="list => getAllData(list, typeTransport.VESSELS)"
    />

    <div class="footer">
      <button class="footer_button" :disabled="!paths.length" @click="onOpenGantt">
        Посмотреть диаграмму Гантта
      </button>
      <button class="footer_button" @click="changeTemplate">
        Сменить шаблон
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import {storeToRefs} from "pinia";
import Checkbox from "./UI/Checkbox.vue";
import {useCommonStore, useTemplateStore, useIceTransportStore} from "../store";
import {ref, toRaw} from "vue";
import {IIcebreaker, IVessel, tModal, TypeLayersForMap, TypeSidebar, typeTransport} from "../types.ts";
import Icebreakers from "./Icebreakers.vue";
import Vessels from "./Vessels.vue";

const {getPath, getTiffDate} = useIceTransportStore()
const {vessels, paths, tiffDate} = storeToRefs(useIceTransportStore())

const {isLoading, openModal, typeModal, showGraph, typeSidebar} = storeToRefs(useCommonStore())

const {selectTemplate} = storeToRefs(useTemplateStore())

const isShowTiff = ref(false)

const date = ref('')

const onOpenGantt = () => {
  openModal.value = true
  openModal.value = true
  typeModal.value = tModal.GANTT
}

const changeTemplate = () => {
  typeSidebar.value = TypeSidebar.TEMPLATES
  paths.value = []
}

const getAllData = async (list: IVessel[] | IIcebreaker[], type: typeTransport) => {
  isLoading.value = true

  await Promise.all(getUniqData(list).map(async (seaTransport: IVessel | IIcebreaker) => {
    await getPath({vessel_id: seaTransport.id, template_name: selectTemplate.value?.name})
  }))

  isLoading.value = false
}

const getUniqData = (list: IVessel[] | IIcebreaker[]) => {
  return list.reduce((accumulator, item2) => {
    if (!accumulator.some(item1 =>
        item1.vessel_id === item2.id)) {
      accumulator.push(item2);
    }
    return accumulator;
  }, structuredClone(toRaw(paths.value)));
}

const onCheckedTiff = () => {
  isShowTiff.value = !isShowTiff.value

  if (!isShowTiff.value) tiffDate.value = ''
}

const changeDate = (modelData: string) => {
  date.value = modelData
  getTiffDate(date.value.toISOString().replaceAll('.000Z', ''))
}
</script>

<style lang="scss" scoped>
@import "./src/assets/styles/icons.scss";
</style>
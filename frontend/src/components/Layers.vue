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
        @getAllData="list => getAllData(list, typeTransport.ICEBREAKERS, 'icebreaker_id', pathsIcebreakers)"
    />

    <Vessels
        :typeLayer="TypeLayersForMap.PATH"
        @getAllData="list => getAllData(list, typeTransport.VESSELS, 'vessel_id', pathsVessels)"
    />

    <div class="footer">
      <button class="footer_button" :disabled="!pathsVessels.length && !pathsIcebreakers.length" @click="onOpenGantt">
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
import {IIcebreaker, IPath, IVessel, tModal, TypeLayersForMap, TypeSidebar, typeTransport} from "../types.ts";
import Icebreakers from "./Icebreakers.vue";
import Vessels from "./Vessels.vue";

const {getPathVessels, getPathIcebreakers} = useIceTransportStore()
const {vessels, pathsVessels, tiffDate, pathsIcebreakers} = storeToRefs(useIceTransportStore())

const {openModal, typeModal, showGraph, typeSidebar, grade} = storeToRefs(useCommonStore())

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
  pathsVessels.value = []
  tiffDate.value = null
  grade.value = null
  pathsIcebreakers.value = []
}

const getAllData = async (
    list: IVessel[] | IIcebreaker[],
    type: typeTransport,
    keyIdx: 'vessel_id' | 'icebreaker_id',
    paths: Record<string, any>
) => {
  //   @ts-ignore
  await Promise.all(getUniqData(list, keyIdx, paths).map(async (seaTransport: IVessel | IIcebreaker) => {
    if (type === typeTransport.VESSELS) {
      //   @ts-ignore
      return await getPathVessels({vessel_id: seaTransport.id, template_name: selectTemplate.value?.name!})
    }

    return await getPathIcebreakers({icebreaker_id: seaTransport.id, template_name: selectTemplate.value?.name!})
  }))
}

const getUniqData = (list: IVessel[] | IIcebreaker[], keyIdx: 'vessel_id' | 'icebreaker_id', paths: IPath[]) => {
  return list.reduce((accumulator, item2) => {
    if (!accumulator.some(item1 =>
        //   @ts-ignore
        item1[keyIdx] === item2.id)) {
      //   @ts-ignore
      accumulator.push(item2);
    }
    return accumulator;
  }, structuredClone(toRaw(paths)));
}

const onCheckedTiff = () => {
  isShowTiff.value = !isShowTiff.value

  if (!isShowTiff.value) tiffDate.value = ''
}

const changeDate = (modelData: string) => {
  date.value = modelData
  tiffDate.value = date.value.toISOString().split('T')[0]
}
</script>

<style lang="scss" scoped>
@import "./src/assets/styles/icons.scss";
</style>
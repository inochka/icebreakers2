<template>
  <div class="wrapper-layers">
    <div class="period">
      <div class="period_checkbox">
        <Checkbox @onChecked="showPeriod" :checked="isShowPeriod"/>
        <p>Выбрать период</p>
      </div>

      <div class="period_select" v-if="isShowPeriod">
        <ArrowIcon
            @click="prevDate"
            :class="{disabled: weeks.findIndex(week => week.value === selectPeriod) === 0}"
            class="icon arrow-left"
        />
        <VueSelect
            v-model="selectPeriod"
            :options="weeks"
            placeholder="Выберите неделю"
        />
        <ArrowIcon
            :class="{disabled: weeks.findIndex(week => week.value === selectPeriod) === weeks.length - 1}"
            @click="nextDate"
            class="icon arrow-right"
        />
      </div>
    </div>

    <div>
      <div class="title-wrapper">
        <div class="title-wrapper_block">
          <Checkbox @onChecked="onCheckAll(typeTransport.ICEBREAKERS)" :checked="checkAllIcebreakers"/>
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
              :type="typeTransport.ICEBREAKERS"
              :is-check-parent="checkAllIcebreakers"
          />
        </div>
      </div>
    </div>

    <div>
      <div class="title-wrapper">
        <div class="title-wrapper_block">
          <Checkbox @onChecked="onCheckAll(typeTransport.VESSELS)" :checked="checkAllVessels"/>
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
              :type="typeTransport.VESSELS"
          />
        </div>
      </div>
    </div>

    <div class="footer">
      <button class="footer_button" :disabled="!paths.length" @click="onOpenGantt">
        Посмотреть диаграмму Гантта
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import {storeToRefs} from "pinia";
import Checkbox from "./UI/Checkbox.vue";
import {useCommonStore, useVesselsStore} from "../store";
import {ref} from "vue";
import Layer from "./Layer.vue";
import ArrowIcon from '../assets/icons/arrow.svg'
import {IIcebreaker, IVessel, Select, tModal, typeTransport} from "../types.ts";
import VueSelect from "vue3-select-component";
import {weeks} from "../custom/weeks.ts";

const {getPath} = useVesselsStore()
const {vessels, icebreakers, paths} = storeToRefs(useVesselsStore())

const {isLoading, openModal, typeModal} = storeToRefs(useCommonStore())

const isVisibleVessels = ref(true)
const isVisibleIcebreakers = ref(true)
const checkAllVessels = ref(false)
const checkAllIcebreakers = ref(false)
const isChangeParentVessel = ref(false)
const isChangeParentIcebreaker = ref(false)
const isShowPeriod = ref(false)
const selectPeriod = ref('')

const showPeriod = () => {
  isShowPeriod.value = !isShowPeriod.value
}

const onOpenGantt = () => {
  openModal.value = true
  typeModal.value = tModal.GANTT
}

const loadGraph = () => {
  isLoading.value = true

  setTimeout(() => {
    isLoading.value = false
  }, 1000)
}

const prevDate = () => {
  const newIdx = weeks.findIndex((week: Select) => week.value === selectPeriod.value) - 1
  if (newIdx > 0) selectPeriod.value = weeks[weeks.findIndex((week: Select) => week.value === selectPeriod.value) - 1].value
}

const nextDate = () => {
  const newIdx = weeks.findIndex((week: Select) => week.value === selectPeriod.value) + 1
  if (newIdx < weeks.length) selectPeriod.value = weeks[weeks.findIndex((week: Select) => week.value === selectPeriod.value) - 1].value
}

const getUniqData = (list: IVessel[] | IIcebreaker[]) => {
  return list.reduce((accumulator, item2) => {
    if (!accumulator.some(item1 =>
        item1.id === item2.id)) {
      accumulator.push(item2);
    }
    return accumulator;
  }, paths.value);
}

const getAllPaths = async (list: IVessel[] | IIcebreaker[], type: typeTransport) => {
  loadGraph()

  await Promise.all(getUniqData(list).map(async (seaTransport: IVessel | IIcebreaker) => {
    await getPath(seaTransport.id, type)
  }))
}

const onCheckAll = async (type: typeTransport) => {
  if (type === 'vessels') {
    checkAllVessels.value = !checkAllVessels.value

    if (!checkAllVessels.value) {
      paths.value = []
      isChangeParentVessel.value = true
      return;
    }

    await getAllPaths(vessels.value, type)
    return
  }

  checkAllIcebreakers.value = !checkAllIcebreakers.value

  if (!checkAllIcebreakers.value) {
    paths.value = []
    isChangeParentIcebreaker.value = true
    return
  }

  await getAllPaths(icebreakers.value, type)
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
  display: flex;
  flex-direction: column;
  gap: 5px;
  padding: 30px 30px 0;

  .period {
    display: flex;
    flex-direction: column;
    gap: 10px;

    &_checkbox {
      display: flex;
      gap: 5px;
      align-items: baseline;
    }

    &_select {
      display: flex;
      gap: 5px;
      align-items: center;

      .arrow-right {
        transform: rotate(-90deg);
      }

      .arrow-left {
        transform: rotate(90deg);
      }
    }
  }

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
    max-height: 300px;
    min-height: 150px;
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

  .footer {
    position: absolute;
    bottom: 20px;
    border: none;
    display: flex;
    flex-direction: column;
    gap: 5px;

    &_button {
      padding: 0.75rem 1.5rem;
      background-color: #488aec;
      color: #ffffff;
      font-size: 0.75rem;
      line-height: 1rem;
      font-weight: 700;
      cursor: pointer;
      text-align: center;
      text-transform: uppercase;
      vertical-align: middle;
      align-items: center;
      border-radius: 0.5rem;
      user-select: none;
      gap: 0.75rem;
      box-shadow: 0 4px 6px -1px #488aec31, 0 2px 4px -1px #488aec17;
      transition: all 0.6s ease;

      &:hover {
        box-shadow: 0 10px 15px -3px #488aec4f, 0 4px 6px -2px #488aec17;
      }

      &:focus,
      &:active {
        opacity: 0.85;
        box-shadow: none;
      }

      &:disabled, &[disabled=disabled] {
        background-color: gray;
      }
    }
  }
}
</style>
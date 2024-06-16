<template>
  <div class="wrapper-templates">
    <h3>Выбор шаблона отрисоки</h3>

    <div class="body">
      <div class="checkbox">
        <Checkbox @onChecked="showGraph = !showGraph" :checked="showGraph"/>
        <p>Показать маршрутный граф</p>
      </div>

      <div v-if="isChoosingTemplate">
        <h4>Шаблоны</h4>
        <div class="radio-buttons">
          <label
              v-for="template in templates"
              :key="template.name"
              class="radio-button"
          >
            <RadioButton
                @onSelect="onSelectTemplate(template)"
                :label="template.description"
                :checked="selectTemplate?.name === template.name"
            />

            <DeleteIcon
                @click="onRemove(template)"
                class="icon"/>
          </label>
        </div>
      </div>

      <div class="wrapper-layers" v-if="!isChoosingTemplate">
        <Icebreakers
            v-if="icebreakers.length"
            :typeLayer="TypeLayersForMap.POINT"
            @getAllData="icebreakerPoints = icebreakers.map(icebreaker => icebreaker.id)"
        />

        <Vessels
            @getAllData="vesselPoints = vessels.map(vessel => vessel.id)"
            v-if="vessels.length"
            :typeLayer="TypeLayersForMap.POINT"
        />
      </div>

      <div class="footer">
        <button v-if="!isChoosingTemplate" class="footer_button" @click="isChoosingTemplate = true">
          Изменить шаблон
        </button>
        <button class="footer_button" @click="onOpenModalCreating">
          Добавить шаблон
        </button>
        <button :disabled="!selectTemplate" class="footer_button" @click="applySettings">
          Принять настройки
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {ITemplate, tModal, TypeLayersForMap, TypeSidebar} from "../types.ts";
import {storeToRefs} from "pinia";
import {useCommonStore, useTemplateStore, useIceTransportStore} from "../store";
import Checkbox from "./UI/Checkbox.vue";
import {onMounted, ref} from 'vue'
import RadioButton from "./UI/RadioButton.vue";
import DeleteIcon from '../assets/icons/delete.svg'
import Icebreakers from "./Icebreakers.vue";
import Vessels from "./Vessels.vue";

const {getVessels, getIcebreakers, calculatePath} = useIceTransportStore()
const {icebreakers, vessels, icebreakerPoints, vesselPoints} = storeToRefs(useIceTransportStore())

const {typeSidebar, showGraph, isLoading, openModal, typeModal} = storeToRefs(useCommonStore())

const {getTemplates} = useTemplateStore()
const {templates, selectTemplate, removingTemplate} = storeToRefs(useTemplateStore())

const isChoosingTemplate = ref(true)

onMounted(async () => {
  await getTemplates()
})

const onRemove = (template: ITemplate) => {
  removingTemplate.value = template

  openModal.value = true
  typeModal.value = tModal.DELETE
}

const applySettings = () => {
  typeSidebar.value = TypeSidebar.LAYERS
  icebreakerPoints.value = []
  vesselPoints.value = []
}

const onOpenModalCreating = async () => {
  openModal.value = true
  typeModal.value = tModal.CREATE_TEMPLATE

  isLoading.value = true

  // TODO: раскомитить как будет готово
  // await calculatePath(selectTemplate.value?.name)

  isLoading.value = false
}

const onSelectTemplate = async (currentTemplate: ITemplate) => {
  selectTemplate.value = currentTemplate

  isChoosingTemplate.value = false

  isLoading.value = true

  icebreakerPoints.value = []
  vesselPoints.value = []

  icebreakers.value = []
  vessels.value = []

  await Promise.all([
    currentTemplate?.vessels?.map(async (vessel) => {
      await getVessels(vessel)
    }),
    currentTemplate?.icebreakers?.map(async (icebreaker) => {
      await getIcebreakers(icebreaker)
    })
  ])

  isLoading.value = false
}
</script>

<style scoped lang="scss">
@import "./src/assets/styles/icons.scss";

.wrapper-templates {
  padding: 30px;

  .body {
    margin-top: 20px;
    display: flex;
    flex-direction: column;
    gap: 10px;

    .wrapper-layers {
      padding: 0;
    }

    .icon {
      transform: none;
    }
  }
}
</style>
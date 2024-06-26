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
                @click.prevent="onRemove(template)"
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
          Сменить шаблон
        </button>
        <button class="footer_button" @click="onOpenModalCreating">
          Добавить шаблон
        </button>
        <button
            v-if="selectTemplate"
            class="footer_button"
            @click="applySettings"
        >
          {{ pathsList.length ? 'Сделать перерассчёт' : 'Рассчитать' }}
        </button>
        <button
            v-if="pathsList.length"
            :disabled="!selectTemplate"
            class="footer_button"
            @click="showRoutes"
        >
          Отобразить маршруты
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

const {
  getVessels,
  getIcebreakers,
  calculatePath,
  getCaravans,
  getPathVessels,
} = useIceTransportStore()
const {icebreakers, vessels, icebreakerPoints, vesselPoints, pathsVessels} = storeToRefs(useIceTransportStore())

const {getGrade} = useCommonStore()
const {typeSidebar, showGraph, isLoading, openModal, typeModal} = storeToRefs(useCommonStore())

const {getTemplates} = useTemplateStore()
const {templates, selectTemplate, removingTemplate} = storeToRefs(useTemplateStore())

const isChoosingTemplate = ref(true)

const pathsList = ref([])

onMounted(async () => {
  await getTemplates()
})

const onRemove = (template: ITemplate) => {
  removingTemplate.value = template

  openModal.value = true
  typeModal.value = tModal.DELETE
}

const showRoutes = async () => {
  typeSidebar.value = TypeSidebar.LAYERS
  icebreakerPoints.value = []
  pathsVessels.value = []

  await Promise.all([
        await getCaravans(selectTemplate.value?.name),
        await getGrade(selectTemplate.value?.name)
      ]
  )
}

const applySettings = async () => {
  typeSidebar.value = TypeSidebar.LAYERS
  icebreakerPoints.value = []
  vesselPoints.value = []

  isLoading.value = true

  await calculatePath(selectTemplate.value?.name)

  await Promise.all([
        await getCaravans(selectTemplate.value?.name),
        await getGrade(selectTemplate.value?.name)
      ]
  )

  isLoading.value = false
}

const onOpenModalCreating = async () => {
  openModal.value = true
  typeModal.value = tModal.CREATE_TEMPLATE
}

const onSelectTemplate = async (currentTemplate: ITemplate) => {
  selectTemplate.value = currentTemplate
  pathsList.value = []
  isChoosingTemplate.value = false

  isLoading.value = true

  icebreakerPoints.value = []
  vesselPoints.value = []

  icebreakers.value = []
  vessels.value = []

  const [paths] = await Promise.all([
    await getPathVessels({template_name: selectTemplate.value?.name}),
    currentTemplate?.vessels?.map(async (vessel) => {
      await getVessels(vessel)
    }),
    currentTemplate?.icebreakers?.map(async (icebreaker) => {
      await getIcebreakers(icebreaker)
    }),
  ])

  pathsList.value = paths

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
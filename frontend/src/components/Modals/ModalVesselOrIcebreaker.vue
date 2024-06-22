<template>
  <div class="header">
    <h3>{{ modalInfo?.name }}</h3>
  </div>

  <div class="body" v-if="modalInfo">
    <div class="list">
      <div class="value">
        <p class="title">Название:</p>
        <p>{{ modalInfo.name }}</p>
      </div>
      <div class="value">
        <p class="title">Ледовый класс:</p>
        <p>{{ modalInfo.ice_class }}</p>
      </div>
      <div class="value">
        <p class="title">Скорость в узлах по чистой воде:</p>
        <p>{{ modalInfo.speed }}</p>
      </div>
      <div class="value">
        <p class="title">Исходный порт:</p>
        <p>{{ modalInfo.source_name }}</p>
      </div>
      <div class="value" v-if="modalInfo.target_name">
        <p class="title">Конечный порт:</p>
        <p>{{ modalInfo.target_name }}</p>
      </div>
      <div class="value">
        <p class="title">Дата начала плавания:</p>
        <p>{{ date }}</p>
      </div>
      <div class="value" v-if="time">
        <p class="title">Время в пути:</p>
        <p>{{ Math.round(time / 24, -1) }} {{ getWord(Math.round(time / 24, -1))}}</p>
      </div>
      <div class="value" v-if="vesselsInFormation?.length">
        <p class="title">В проводке участвовали:</p>
        <p v-for="(vessel, idx) in vesselsInFormation" :key="idx">{{ vessel }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {useCommonStore, useIceTransportStore} from "../../store";
import {getDate} from "../../utils/getDate.ts";
import {computed, onMounted, type Ref, ref} from "vue";
import {storeToRefs} from "pinia";
import {getWord} from "../../utils/getWord.ts";
import {typeTransport} from "../../types.ts";

const {modalInfo} = storeToRefs(useCommonStore())
const {pathsVessels, caravans, vessels} = storeToRefs(useIceTransportStore())

const time: Ref<number | null> = ref(null)

const vesselsInFormation: Ref<string[]> = ref([])

const date = computed(() => {
  return getDate(modalInfo.value?.start_date!, 'yyyy-MM-dd')
})

onMounted(() => {
  if (modalInfo.value?.target_name && pathsVessels.value.length) {
    time.value = pathsVessels.value.find(vessel => vessel.vessel_id === modalInfo.value?.id)?.total_time_hours!
  }

  if (modalInfo.value?.type === typeTransport.ICEBREAKERS && caravans.value.length) {
    const currentCaravan = caravans.value.find(caravan => caravan.icebreaker_id === modalInfo.value?.id)!

    if (!currentCaravan) return

    const {vessel_ids} = currentCaravan
    if (vessel_ids.length) {
      vesselsInFormation.value = vessel_ids.map(id => vessels.value.find(vessel => vessel.id === id)?.name!)
    }
  }
})
</script>

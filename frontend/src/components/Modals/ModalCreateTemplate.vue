<template>
  <div class="header">
    <h3>Создать шаблон</h3>
  </div>

  <div class="body">
    <div class="form">
      <p>Название: </p>
      <input class="input" v-model="description"/>
    </div>

    <div class="form">
      <p>Суда: </p>
      <Multiselect
          v-model="selectVessels"
          :options="allVessels"
          :searchable="false"
          :close-on-select="false"
          :show-labels="false"
          track-by="id"
          label="name"
          :multiple="true"
          placeholder="Выберите суда"
      />
    </div>

    <div class="form">
      <p>Ледоколы: </p>
      <Multiselect
          v-model="selectIcebreakers"
          :options="allIcebreakers"
          :searchable="false"
          :close-on-select="false"
          :show-labels="false"
          track-by="id"
          label="name"
          :multiple="true"
          placeholder="Выберите ледоколы"
      />
    </div>

    <div class="form">
      Алгоритм:
      <Multiselect
          v-model="algorithm"
          :options="algorithmList"
          :searchable="false"
          :close-on-select="false"
          :show-labels="false"
          track-by="value"
          label="label"
          placeholder="Выберите алгоритм"
      />
    </div>
  </div>

  <div class="footer-modal">
    <button class="footer_button" @click="$emit('onClose')">Отмена</button>
    <button class="footer_button" @click="onAdd">Добавить</button>
  </div>
</template>

<script setup lang="ts">
import {ref} from "vue";
import {storeToRefs} from "pinia";
import {useIceTransportStore, useTemplateStore} from "../../store";
import Multiselect from 'vue-multiselect'

import { toast, type ToastOptions } from 'vue3-toastify';
import {generateRandom} from "../../utils/generateRandom.ts";

const {createTemplate} = useTemplateStore()

const {allVessels, allIcebreakers} = storeToRefs(useIceTransportStore())

const selectVessels = ref([])
const selectIcebreakers = ref([])
const algorithm = ref('')
const description = ref('')

const emits = defineEmits(['onClose'])

const algorithmList = [
  {
    label: 'Стандартный',
    value: 'default'
  },
  {
    label: 'С лучшим ледоколом',
    value: 'best'
  },
  {
    label: 'Самостоятельно',
    value: 'solo'
  }
]

const onAdd = async() => {
  let error = false

  if (!description.value) {
    toast("Название должно быть заполнено", {
      type: 'error',
    } as ToastOptions);

    error = true
  }

  if (!algorithm.value) {
    toast("Необходимо выбрать алгоритм", {
      type: 'error',
    } as ToastOptions);

    error = true
  }

  if (error) return

  await createTemplate({
    name: generateRandom(20),
    description: description.value,
    vessels: selectVessels.value.map(vessel => vessel.id),
    icebreakers: selectIcebreakers.value.map(icebreaker => icebreaker.id),
    algorythm: algorithm.value.value,
  })

  emits('onClose')
}
</script>

<style scoped lang="scss">
.body {
  display: flex;
  flex-direction: column;
  gap: 10px;
  font-size: 16px;

  .form {
    display: flex;
    gap: 10px;
    align-items: center;

    p {
      min-width: 71px;
      width: 71px;
    }
  }

  .input {
    padding: 10px;
    border: 1px solid #e4e4e7;
    border-radius: 5px;
    font-size: 16px;
    color: #18181b;
    outline: none;
    width: 100%;
  }

  .input:focus {
    border: 2px solid #007bff;
  }
}

.footer-modal {
  gap: 10px;
  padding: 20px;
  display: flex;
  align-items: center;
  justify-content: end;
}
</style>

<style lang="scss">
.multiselect__tag {
  background: #007bff;
}

.multiselect__option {
  &:hover, &:focus, &--hightlight {
    background: #007bff !important;
  }
}
</style>

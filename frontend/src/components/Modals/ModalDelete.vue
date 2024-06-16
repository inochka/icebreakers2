<template>
  <div class="header">
    <p>Вы уверены, что хотите удалить "{{ removingTemplate.description }}"?</p>
  </div>

  <div class="footer-modal">
    <button class="footer_button" @click="$emit('onClose')">Отмена</button>
    <button class="footer_button" @click="onRemove">Удалить</button>
  </div>
</template>

<script setup lang="ts">
import {storeToRefs} from "pinia";
import {useTemplateStore} from "../../store";

import { toast, type ToastOptions } from 'vue3-toastify';

const {removingTemplate} = storeToRefs(useTemplateStore())
const {removeTemplate} = useTemplateStore()

const emits = defineEmits(['onClose'])

const onRemove = async() => {
  await removeTemplate()
  emits('onClose')
  toast("Шаблон успешно удален", {
    type: 'success',
  } as ToastOptions);
}
</script>

<style scoped lang="scss">
.header {
  font-weight: bold;
}

.footer-modal {
  gap: 10px;
  padding: 20px;
  display: flex;
  align-items: center;
  justify-content: end;
}
</style>
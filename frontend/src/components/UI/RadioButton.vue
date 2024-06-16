<template>
  <div @click="$emit('onSelect')" class="radio-button_input">
    <input type="radio" :checked="checked">
    <div class="radio-circle"></div>
    <span v-if="label.length <= 28" class="radio-label">
        {{ label }}
      </span>
    <template v-else>
      <VTooltip>
          <span class="radio-label">
            {{ getLabel }}
          </span>

        <template #popper>
          {{ label }}
        </template>
      </VTooltip>
    </template>
  </div>
</template>

<script setup lang="ts">
import {computed} from "vue";

type Props = {
  label: string
  checked: boolean
}

const props = defineProps<Props>()

const getLabel = computed(() => {
  return `${props.label.slice(0, 25)}...`
})
</script>

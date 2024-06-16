<template>
  <div class="loader">
    <div class="loader_window">
      <section class="dots-container">
        <div class="dot"></div>
        <div class="dot"></div>
        <div class="dot"></div>
        <div class="dot"></div>
        <div class="dot"></div>
      </section>

      <p>{{text}}</p>
    </div>
  </div>
</template>

<script lang="ts" setup>
import {onBeforeUnmount, onMounted, ref} from "vue";

const textList = [
  'Считаем данные...',
  "Ищем наиболее подходящий вариант...",
  'Осталось немного...',
]

const text = ref(textList[0])
const idx = ref(0)
const interval = ref()

onMounted(() => {
  interval.value = setInterval(() => {
    if (idx.value === textList.length - 1) {
      idx.value = 0
    } else {
      idx.value += 1
    }
    text.value = textList[idx.value]
  }, 5000);
})

onBeforeUnmount(() => {
  clearInterval(interval.value)
})
</script>

<style scoped lang="scss">
.loader {
  position: fixed;
  z-index: 1;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;

  &_window {
    width: 30%;
    height: 30%;
    background: white;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;

    p {
      position: absolute;
      font-size: 20px;
      top: 70%;
    }
  }

  .dots-container {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    width: 100%;
  }

  .dot {
    height: 20px;
    width: 20px;
    margin-right: 10px;
    border-radius: 10px;
    background-color: #b3d4fc;
    animation: pulse 1.5s infinite ease-in-out;
  }

  .dot:last-child {
    margin-right: 0;
  }

  .dot:nth-child(1) {
    animation-delay: -0.3s;
  }

  .dot:nth-child(2) {
    animation-delay: -0.1s;
  }

  .dot:nth-child(3) {
    animation-delay: 0.1s;
  }
}

@keyframes pulse {
  0% {
    transform: scale(0.8);
    background-color: #b3d4fc;
    box-shadow: 0 0 0 0 rgba(178, 212, 252, 0.7);
  }

  50% {
    transform: scale(1.2);
    background-color: #6793fb;
    box-shadow: 0 0 0 10px rgba(178, 212, 252, 0);
  }

  100% {
    transform: scale(0.8);
    background-color: #b3d4fc;
    box-shadow: 0 0 0 0 rgba(178, 212, 252, 0.7);
  }
}
</style>
<script setup lang="ts">
</script>
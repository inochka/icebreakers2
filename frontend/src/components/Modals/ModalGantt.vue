<template>
  <div class="header">
    <h3>Диаграмма Гантта</h3>
  </div>

  <div class="body">
    <Gantt />

    <div class="legend">
      <div class="legend_elem">
        <div class="square move"></div>
        <p>Самостоятельное движение судна</p>
      </div>
      <div class="legend_elem">
        <div class="square formation"></div>
        <p>Проводка караваном</p>
      </div>
      <div class="legend_elem">
        <div class="square without-formation"></div>
        <p>Движение невозможно</p>
      </div>
      <div class="legend_elem">
        <div class="square wait"></div>
        <p>Ожидание</p>
      </div>
      <div class="legend_elem">
        <div class="square icebreaker-path"></div>
        <p>Самостоятельное движение ледокола</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import Gantt from "../UI/Gantt.vue";
</script>

<style lang="scss" scoped>
@import "../../assets/styles/legend.scss";

.body {
  .legend {
    position: absolute;
    bottom: 20px;
    left: 20px;
  }
}
</style>
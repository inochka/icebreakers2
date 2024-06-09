<template>
  <div class="legend">
    <div class="legend_elem">
      <div class="square move"></div>
      <p>Самостоятельное движение</p>
    </div>
    <div class="legend_elem">
      <div class="square formation"></div>
      <p>Проводка караваном</p>
    </div>
    <div class="legend_elem">
      <div class="circle wait"></div>
      <p>Ожидание</p>
    </div>
    <div class="legend_elem">
      <div class="circle start"></div>
      <p>Начальная точка</p>
    </div>
    <div class="legend_elem">
      <img class="point-icon" :src="endPoint"/>
      <p>Конечная точка</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import endPoint from '../../assets/icons/anchor-icon-svgrepo-com.png'
</script>

<style scoped lang="scss">
@import "../../assets/styles/legend.scss";

.legend {
  background: white;
  padding: 15px;
  position: fixed;
  bottom: 10px;
  right: 10px;
}
</style>
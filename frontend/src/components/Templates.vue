<template>
  <div class="wrapper-templates">
    <h3>Выбор шаблона отрисоки</h3>

    <div class="body">
      <div class="checkbox">
        <Checkbox @onChecked="showGraph = !showGraph" :checked="showGraph"/>
        <p>Показать маршрутный граф</p>
      </div>
    </div>

    <div class="footer">
    <!--      TODO: задезуйблить-->
      <button class="footer_button" @click="typeSidebar = TypeSidebar.LAYERS">
        Принять настройки
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import {TypeSidebar} from "../types.ts";
import {storeToRefs} from "pinia";
import {useCommonStore} from "../store";
import Checkbox from "./UI/Checkbox.vue";

const {typeSidebar, showGraph} = storeToRefs(useCommonStore())
</script>

<style scoped lang="scss">
.wrapper-templates {
  padding: 30px;

  .body {
    margin-top: 20px;
  }
}
</style>
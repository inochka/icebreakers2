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
        <p>{{ modalInfo.start_date }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {useCommonStore} from "../../store";

const {modalInfo} = useCommonStore();
</script>

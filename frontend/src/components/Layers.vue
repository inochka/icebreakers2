<template>
  <div class="wrapper-layers">
    <div>
      <div class="title-wrapper">
          <Checkbox/>
          <h3 class="title">Заявка на проводку</h3>
      </div>
      <div class="list">
        <div class="list_item">
          <div class="list_item-value">
            <Checkbox/>
            <div>Судно 1</div>
          </div>
            <InfoIcon @click="onOpenInfoModal(tModal?.VESSEL!)" class="icon"/>
        </div>
        <div class="list_item">
          <div class="list_item-value">
            <Checkbox/>
            <div>Судно 2</div>
          </div>
          <InfoIcon class="icon"/>
        </div>
        <div class="list_item">
          <div class="list_item-value">
            <Checkbox/>
            <div>Судно 3</div>
          </div>
          <InfoIcon class="icon"/>
        </div>
      </div>
    </div>

    <div>
      <div class="title-wrapper">
       <Checkbox />
        <h3 class="title">Ледоколы</h3>
      </div>
      <div class="list">
        <div class="list_item">
          <div class="list_item-value">
            <Checkbox/>
            <div>Ледокол 1</div>
          </div>
          <InfoIcon class="icon"/>
        </div>
        <div class="list_item">
          <div class="list_item-value">
            <Checkbox/>
            <div>Ледокол 2</div>
          </div>
          <InfoIcon class="icon"/>
        </div>
        <div class="list_item">
          <div class="list_item-value">
            <Checkbox/>
            <div>Ледокол 3</div>
          </div>
          <InfoIcon class="icon"/>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import InfoIcon from '../assets/icons/info.svg'
import PathIcon from '../assets/icons/path.svg'
import {storeToRefs} from "pinia";
import {tModal} from "../types.ts";
import {useStore} from "../store";
import Checkbox from "./Modals/Checkbox.vue";

const {openModal, typeModal} = storeToRefs(useStore())

const onOpenInfoModal = (type: tModal) => {
  openModal.value = true
  typeModal.value = type
}
</script>

<style lang="scss" scoped>
.wrapper-layers {
  padding: 0 30px 0 30px;
  display: flex;
  flex-direction: column;
  gap: 5px;

  .title-wrapper {
    display: flex;
    gap: 5px;
    align-items: baseline;

    .title {
      margin-top: 35px;
      margin-bottom: 15px;
    }
  }

  .icon {
    color: gray;
    cursor: pointer;

    &:hover {
      color: black;
    }
  }

  .path {
    width: 18px;
    height: 18px;
    fill: gray;

    &:hover {
      color: black;
    }
  }

  .list {
    margin-left: 20px;

    &_item {
      justify-content: space-between;
      align-items: center;
      display: flex;
      gap: 5px;
      margin-bottom: 3px;

      &-value {
        display: flex;
        gap: 5px;
        align-items: baseline;
      }
    }
  }
}
</style>
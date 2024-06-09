<template>
  <div class="modal">
    <div class="modal-wrapper" :class="{'modal-gantt': typeModal === tModal.GANTT}" v-click-outside="onClose">
      <div @click="onClose" class="close-icon">
        <CloseIcon />
      </div>
      <ModalVesselOrIcebreaker v-if="typeModal === tModal.VESSEL || typeModal === tModal.ICEBREAKER" />
      <ModalGantt v-else-if="typeModal === tModal.GANTT" />
    </div>
  </div>
</template>

<script setup lang="ts">
import {storeToRefs} from "pinia";
import {tModal} from "../../types.ts";
import CloseIcon from '../../assets/icons/close.svg'
import {useCommonStore} from "../../store";
import ModalVesselOrIcebreaker from "../Modals/ModalVesselOrIcebreaker.vue";
import ModalGantt from "../Modals/ModalGantt.vue";

const {typeModal, openModal, modalInfo} = storeToRefs(useCommonStore())

const onClose = () => {
  openModal.value = false
  typeModal.value = null
  modalInfo.value = null
}
</script>

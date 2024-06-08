<template>
  <div class="modal">
    <div class="modal-wrapper" v-click-outside="onClose">
      <div @click="onClose" class="close-icon">
        <CloseIcon />
      </div>
      <ModalVessel v-if="typeModal === tModal.VESSEL"/>
    </div>
  </div>
</template>

<script setup lang="ts">
import ModalVessel from "../Modals/ModalVessel.vue";
import {storeToRefs} from "pinia";
import {useStore} from "../../store";
import {tModal} from "../../types.ts";
import CloseIcon from '../../assets/icons/close.svg'

const {typeModal, openModal} = storeToRefs(useStore())

const onClose = () => {
  openModal.value = false
  typeModal.value = null
}
</script>

<template>
  <input type="checkbox"/>
  <span class="custom-checkbox"></span>
</template>

<script setup lang="ts">

</script>

<style scoped>
input[type="checkbox"] {
  display: none;
}

/* Style for the custom checkbox */
.custom-checkbox {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 2px solid #333;
  border-radius: 4px;
  position: relative;
  cursor: pointer;
  transform: translateY(5px);
}

/* Style for the custom checkmark */
.custom-checkbox::after {
  content: "";
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 10px;
  height: 10px;
  background-color: #333;
  border-radius: 2px;
  opacity: 0;
}

/* Show the checkmark when checkbox is checked */
input[type="checkbox"]:checked + .custom-checkbox::after {
  opacity: 1;
}
</style>
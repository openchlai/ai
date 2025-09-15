<template>
  <label class="form-label" style="display:flex; gap:8px; align-items:center; font-weight:500; cursor:pointer;">
    <input type="checkbox" v-model="model" :disabled="disabled" />
    <span><slot /></span>
  </label>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({ modelValue: Boolean, disabled: Boolean })
const emit = defineEmits(['update:modelValue'])
const model = computed({ get:()=>props.modelValue, set:v=>emit('update:modelValue', v) })
</script>



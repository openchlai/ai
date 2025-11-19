<template>
  <label style="display:inline-flex; align-items:center; gap:8px; cursor:pointer;">
    <input type="checkbox" v-model="model" :disabled="disabled" style="display:none;" />
    <span :style="trackStyle"><span :style="thumbStyle"></span></span>
    <span><slot /></span>
  </label>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({ modelValue: Boolean, disabled: Boolean })
const emit = defineEmits(['update:modelValue'])
const model = computed({ get:()=>props.modelValue, set:v=>emit('update:modelValue', v) })
const trackStyle = computed(() => ({
  display:'inline-block', width:'42px', height:'24px', borderRadius:'9999px', border:`1px solid var(--color-border)`, background: model.value ? 'var(--color-primary)' : 'var(--color-surface)', position:'relative', transition:'all .2s'
}))
const thumbStyle = computed(() => ({
  position:'absolute', top:'2px', left: model.value ? '22px' : '2px', width:'20px', height:'20px', borderRadius:'50%', background:'#fff', boxShadow:'var(--shadow-sm)', transition:'left .2s'
}))
</script>



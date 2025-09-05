<template>
  <button
    class="btn"
    :class="[`btn--${variant}`, sizeClass]"
    :disabled="disabled || loading"
    @click="$emit('click', $event)"
  >
    <slot name="icon-left" />
    <span><slot /></span>
    <slot name="icon-right" />
  </button>
  
</template>

<script setup>
const props = defineProps({
  variant: { type: String, default: 'primary' },
  size: { type: String, default: 'md' },
  disabled: { type: Boolean, default: false },
  loading: { type: Boolean, default: false }
})

const sizeClass = computed(() => props.size === 'sm' ? 'btn--sm' : props.size === 'lg' ? 'btn--lg' : '')
</script>



<template>
  <span :class="['badge', `badge--${variant}`]">
    <slot />
  </span>
</template>

<script setup>
const props = defineProps({ variant: { type: String, default: 'info' } })
</script>

<style scoped>
.badge { display:inline-flex; align-items:center; padding:2px 6px; border-radius:6px; font-size: var(--text-sm); background: var(--color-surface-muted); border: 1px solid var(--color-border); }
.badge--info { color: var(--color-fg); }
.badge--warning { color: #b45309; background: #fff7ed; border-color: #fed7aa; }
.badge--success { color: var(--color-success); background: color-mix(in oklab, var(--color-success) 8%, transparent); border-color: color-mix(in oklab, var(--color-success) 35%, transparent); }
</style>



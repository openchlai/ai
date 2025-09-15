<template>
  <span :class="['tag', `tag--${variant}`]">
    <slot />
  </span>
</template>

<script setup>
const props = defineProps({ variant: { type: String, default: 'neutral' } })
</script>

<style scoped>
.tag { display:inline-flex; align-items:center; padding:2px 8px; border-radius:999px; font-size: var(--text-sm); border:1px solid var(--color-border); background: var(--color-surface-muted); }
.tag--success { background: color-mix(in oklab, var(--color-success) 10%, transparent); color: var(--color-success); border-color: color-mix(in oklab, var(--color-success) 40%, transparent); }
.tag--danger { background: color-mix(in oklab, var(--color-danger) 10%, transparent); color: var(--color-danger); border-color: color-mix(in oklab, var(--color-danger) 40%, transparent); }
</style>



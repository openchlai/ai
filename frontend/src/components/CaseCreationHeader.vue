<template>
  <div class="case-header">
    <div>
      <h1>Create New Case</h1>
      <p>{{ description }}</p>
    </div>
    <div class="toggle-container">
      <span class="toggle-label">
        <span class="ai-icon">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
            <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
            <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
          </svg>
        </span>
        AI Enabled
      </span>
      <label class="toggle-switch">
        <input :checked="isAIEnabled" @change="$emit('update:isAIEnabled', $event.target.checked)" type="checkbox" />
        <span class="toggle-slider"></span>
      </label>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  description: { type: String, default: '' },
  isAIEnabled: { type: Boolean, default: false }
})
</script>

<style scoped>
.case-header { display:flex; align-items:center; justify-content:space-between; gap:12px; }
.toggle-container { display:flex; align-items:center; gap:8px; }
.toggle-label { display:flex; align-items:center; gap:6px; color: var(--color-muted); font-weight:600; }
.toggle-switch { position:relative; width:46px; height:26px; }
.toggle-switch input{ opacity:0; width:0; height:0; }
.toggle-slider{ position:absolute; cursor:pointer; top:0; left:0; right:0; bottom:0; background:#cbd5e1; transition:.2s; border-radius:999px; }
.toggle-slider:before{ position:absolute; content:""; height:22px; width:22px; left:2px; top:2px; background:white; transition:.2s; border-radius:999px; }
.toggle-switch input:checked + .toggle-slider{ background: var(--color-primary); }
.toggle-switch input:checked + .toggle-slider:before{ transform: translateX(20px); }
</style>



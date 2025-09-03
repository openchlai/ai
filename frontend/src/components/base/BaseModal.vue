<template>
  <teleport to="body">
    <div v-if="modelValue" class="modal-overlay" @click="onBackdrop">
      <div class="modal" role="dialog" aria-modal="true" @click.stop>
        <div class="modal__header">
          <slot name="header">Modal</slot>
        </div>
        <div class="modal__body">
          <slot />
        </div>
        <div class="modal__footer">
          <slot name="footer">
            <button class="btn" @click="close">Close</button>
          </slot>
        </div>
      </div>
    </div>
  </teleport>
</template>

<script setup>
const props = defineProps({
  modelValue: { type: Boolean, default: false },
  closeOnEsc: { type: Boolean, default: true },
  closeOnBackdrop: { type: Boolean, default: true }
})
const emit = defineEmits(['update:modelValue'])
const close = () => emit('update:modelValue', false)
const onBackdrop = () => { if (props.closeOnBackdrop) close() }

onMounted(() => {
  const onKey = (e) => { if (props.modelValue && props.closeOnEsc && e.key === 'Escape') close() }
  window.addEventListener('keydown', onKey)
  onUnmounted(() => window.removeEventListener('keydown', onKey))
})
</script>



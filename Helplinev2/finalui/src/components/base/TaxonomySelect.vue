<template>
  <div :class="['taxonomy-select-wrapper', customClass]">
    <BaseSelect
      :id="id"
      :label="label"
      :hint="hint"
      :error="error"
      :placeholder="placeholder"
      :disabled="disabled"
      :searchable="searchable"
      :categoryId="computedRootId"
      v-model="internalValue"
      @change="handleSelectionChange"
    />
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import BaseSelect from './BaseSelect.vue'
import { useTaxonomyStore } from '@/stores/taxonomy'

const props = defineProps({
  modelValue: [String, Number],
  rootKey: String, // Key from TAXONOMY_ROOTS (e.g., 'CASE_CATEGORY')
  rootId: [String, Number], // Direct ID if rootKey isn't used
  label: String,
  hint: String,
  error: String,
  id: String,
  placeholder: String,
  disabled: Boolean,
  searchable: {
    type: Boolean,
    default: true
  },
  customClass: String
})

const emit = defineEmits(['update:modelValue', 'change', 'trigger'])

const taxonomyStore = useTaxonomyStore()
const internalValue = ref(props.modelValue)

// Resolve the correct Root ID based on Key or Direct ID
const computedRootId = computed(() => {
  if (props.rootKey && taxonomyStore.roots[props.rootKey]) {
    return taxonomyStore.roots[props.rootKey]
  }
  return props.rootId
})

// Bubble up changes
const handleSelectionChange = (id, text) => {
  emit('update:modelValue', id)
  emit('change', { id, text })

  // Check for workflow triggers
  Object.keys(taxonomyStore.triggers).forEach(triggerKey => {
    if (taxonomyStore.isTrigger(id, triggerKey)) {
      emit('trigger', { triggerKey, id, text })
    }
  })
}

// Watch for external model changes
watch(() => props.modelValue, (newVal) => {
  internalValue.value = newVal
})
</script>

<style scoped>
.taxonomy-select-wrapper {
  width: 100%;
}
</style>

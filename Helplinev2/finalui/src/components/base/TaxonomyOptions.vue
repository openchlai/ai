<template>
  <div :class="['taxonomy-options-wrapper', customClass]">
    <BaseOptions
      :id="id"
      :label="label"
      :placeholder="placeholder"
      :disabled="disabled"
      :categoryId="computedRootId"
      :maxSelections="maxSelections"
      :returnText="returnText"
      v-model="internalValue"
      @change="handleSelectionChange"
      @selection-change="handleSelectionChangeComplex"
    />
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import BaseOptions from './BaseOptions.vue'
import { useTaxonomyStore } from '@/stores/taxonomy'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  rootKey: String,
  rootId: [String, Number],
  label: String,
  id: String,
  placeholder: String,
  disabled: Boolean,
  maxSelections: Number,
  returnText: Boolean,
  customClass: String
})

const emit = defineEmits(['update:modelValue', 'change', 'selection-change'])

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
const handleSelectionChange = (newValues) => {
  emit('update:modelValue', newValues)
  emit('change', newValues)
}

const handleSelectionChangeComplex = (data) => {
    emit('selection-change', data)
}

// Watch for external model changes
watch(() => props.modelValue, (newVal) => {
  internalValue.value = newVal
}, { deep: true })
</script>

<style scoped>
.taxonomy-options-wrapper {
  width: 100%;
}
</style>

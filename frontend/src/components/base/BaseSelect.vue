<template>
  <div class="form-group">
    <label v-if="label" class="form-label" :for="id">{{ label }}</label>

    <!-- Input Display -->
    <div class="select-container" @click="toggleDropdown" :class="{ disabled: disabled }">
      <div class="selected-value">
        {{ displayValue || placeholder || 'Select an option' }}
      </div>
      <span class="arrow" :class="{ open: isOpen }">▼</span>
    </div>

    <!-- Dropdown -->
    <div v-if="isOpen" class="dropdown">
      <!-- Breadcrumb navigation -->
      <div v-if="breadcrumb.length" class="breadcrumb">
        <span v-for="(name, i) in breadcrumb" :key="i">
          {{ name }}<span v-if="i < breadcrumb.length - 1"> > </span>
        </span>
      </div>

      <!-- Loading state -->
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <span>Loading options...</span>
      </div>

      <!-- Options list -->
      <ul v-else-if="currentOptions.length" class="options">
        <li
          v-for="option in currentOptions"
          :key="option.id"
          @click.stop="handleOptionClick(option)"
          :class="{ 
            selected: option.id === selectedOption?.id,
            highlighted: option.id === selectedOption?.id,
            'has-children': option.hasChildren === true
          }"
        >
          <span class="option-text">{{ option.name }}</span>
          <span v-if="option.hasChildren === true" class="expand-arrow">→</span>
        </li>
      </ul>

      <!-- No options -->
      <div v-else class="no-options">
        No options available
      </div>

      <!-- Controls -->
      <div class="controls" v-if="navigationPath.length > 0 || selectedOption">
        <button v-if="navigationPath.length > 0" type="button" class="btn back" @click.stop="goBack">
          ← Back
        </button>
        <button v-if="selectedOption" type="button" class="btn reset" @click.stop="clearSelection">
          Clear Selection
        </button>
      </div>
    </div>

    <div v-if="hint && !error" class="form-hint">{{ hint }}</div>
    <div v-if="error" class="form-error">{{ error }}</div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useCategoryStore } from '@/stores/categories'

const props = defineProps({
  modelValue: [String, Number],
  label: String,
  hint: String,
  error: String,
  id: String,
  placeholder: String,
  disabled: Boolean,
  categoryId: [String, Number]
})

const emit = defineEmits(['update:modelValue', 'change'])

const store = useCategoryStore()
const isOpen = ref(false)
const loading = ref(false)
const navigationPath = ref([])
const levelOptions = ref([])
const selectedOption = ref(null)

// Toggle dropdown
function toggleDropdown() {
  if (props.disabled) return
  if (!isOpen.value && !levelOptions.value.length && props.categoryId) {
    loadLevel(props.categoryId)
  }
  isOpen.value = !isOpen.value
}

function closeDropdown() {
  isOpen.value = false
}

// Load options for a specific category level
async function loadLevel(categoryId, isRoot = true) {
  if (!categoryId) return []
  try {
    loading.value = true
    await store.viewCategory(categoryId)

    const k = store.subcategories_k
    const idIdx = Number(k?.id?.[0] ?? 0)
    const nameIdx = Number(k?.name?.[0] ?? 5)

    const parsedOptions = (store.subcategories || [])
      .map(row => ({
        id: row[idIdx],
        name: row[nameIdx] || `Option ${row[idIdx]}`,
        hasChildren: null
      }))
      .filter(Boolean)

    if (isRoot) {
      levelOptions.value = parsedOptions
    }
    return parsedOptions
  } catch (error) {
    console.error('Error loading level:', error)
    return []
  } finally {
    loading.value = false
  }
}

// Handle option click
async function handleOptionClick(option) {
  if (option.hasChildren === null) {
    try {
      await store.viewCategory(option.id)
      option.hasChildren = store.subcategories && store.subcategories.length > 0
    } catch {
      option.hasChildren = false
    }
  }

  if (option.hasChildren) {
    const subOptions = await loadLevel(option.id, false)
    if (subOptions.length > 0) {
      navigationPath.value.push({
        id: option.id,
        name: option.name,
        options: levelOptions.value
      })
      levelOptions.value = subOptions
    } else {
      selectOption(option)
    }
  } else {
    selectOption(option)
  }
}

// ✅ Emit the ID but display the name
function selectOption(option) {
  selectedOption.value = option
  emit('update:modelValue', option.id)
  emit('change', option.id)
  isOpen.value = false
}

// Go back a level
function goBack() {
  if (navigationPath.value.length === 0) return
  const previousLevel = navigationPath.value.pop()
  levelOptions.value = previousLevel.options
}

// Clear selection
function clearSelection() {
  selectedOption.value = null
  navigationPath.value = []
  if (props.categoryId) loadLevel(props.categoryId)
  emit('update:modelValue', '')
  emit('change', '')
  isOpen.value = false
}

// ✅ Watch modelValue (now an ID) and update display name accordingly
watch(() => props.modelValue, async (newValue) => {
  if (newValue && newValue !== selectedOption.value?.id) {
    const matchingOption = levelOptions.value.find(opt => opt.id == newValue)
    if (matchingOption) {
      selectedOption.value = matchingOption
    } else {
      selectedOption.value = { id: newValue, name: `Option ${newValue}`, hasChildren: false }
    }
  } else if (!newValue) {
    selectedOption.value = null
  }
})

// Reload on categoryId change
watch(() => props.categoryId, (newCategoryId) => {
  if (newCategoryId) {
    levelOptions.value = []
    navigationPath.value = []
    selectedOption.value = null
    loadLevel(newCategoryId)
  }
}, { immediate: true })

// Computed
const currentOptions = computed(() => levelOptions.value)
const breadcrumb = computed(() => navigationPath.value.map(level => level.name))
const displayValue = computed(() => selectedOption.value?.name || '')

// Close dropdown when clicking outside
onMounted(() => {
  document.addEventListener('click', (event) => {
    if (!event.target.closest('.form-group')) closeDropdown()
  })
})
</script>

<style scoped>
.form-group {
  position: relative;
  max-width: 420px;
}
.form-label {
  display: block;
  font-weight: 600;
  margin-bottom: 6px;
  color: var(--color-text, #333);
}
.select-container {
  border: 1px solid var(--color-border, #ddd);
  border-radius: 6px;
  padding: 10px 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  background: var(--color-surface, #fff);
  transition: all 0.2s ease;
  min-height: 20px;
}
.select-container:hover:not(.disabled) {
  border-color: var(--color-primary, #007bff);
}
.select-container:focus-within:not(.disabled) {
  border-color: var(--color-primary, #007bff);
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}
.select-container.disabled {
  background: var(--color-surface-muted, #f5f5f5);
  color: var(--color-muted, #999);
  cursor: not-allowed;
}
.selected-value {
  color: var(--color-text, #333);
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.select-container.disabled .selected-value {
  color: var(--color-muted, #999);
}
.arrow {
  font-size: 12px;
  color: var(--color-muted, #666);
  margin-left: 8px;
  transition: transform 0.2s ease;
}
.arrow.open {
  transform: rotate(180deg);
}
.dropdown {
  border: 1px solid var(--color-border, #ddd);
  border-radius: 6px;
  margin-top: 4px;
  background: var(--color-surface, #fff);
  padding: 6px;
  max-height: 300px;
  overflow-y: auto;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  position: absolute;
  width: 100%;
  z-index: 1000;
}
.loading-state {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 16px;
  justify-content: center;
  color: var(--color-muted, #666);
}
.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid var(--color-border, #ddd);
  border-top: 2px solid var(--color-primary, #007bff);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
.options {
  list-style: none;
  margin: 0;
  padding: 0;
}
.options li {
  padding: 10px 12px;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.2s ease;
  color: var(--color-text, #333);
}
.options li:hover {
  background: var(--color-surface-hover, #f8f9fa);
}
.options li.selected,
.options li.highlighted {
  background: var(--color-primary-light, rgba(0, 123, 255, 0.1));
  color: var(--color-primary, #007bff);
  font-weight: 500;
}
.no-options {
  padding: 16px;
  text-align: center;
  color: var(--color-muted, #666);
  font-style: italic;
}
.controls {
  margin-top: 8px;
  display: flex;
  justify-content: center;
  border-top: 1px solid var(--color-border, #eee);
  padding-top: 8px;
}
.btn {
  padding: 6px 12px;
  border-radius: 4px;
  border: 1px solid var(--color-border, #ddd);
  background: var(--color-surface, #fff);
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s ease;
}
.btn:hover {
  background: var(--color-surface-hover, #f8f9fa);
  transform: translateY(-1px);
}
.reset {
  color: var(--color-danger, #dc3545);
  border-color: var(--color-danger, #dc3545);
}
.reset:hover {
  background: var(--color-danger, #dc3545);
  color: white;
}
.form-hint {
  font-size: 12px;
  color: var(--color-muted, #666);
  margin-top: 4px;
}
.form-error {
  font-size: 12px;
  color: var(--color-danger, #dc3545);
  margin-top: 4px;
}
</style>

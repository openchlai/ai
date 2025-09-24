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
            selected: option.name === modelValue,
            highlighted: option.name === modelValue,
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
  categoryId: [String, Number] // Category ID to fetch options from
})

const emit = defineEmits(['update:modelValue', 'change'])

const store = useCategoryStore()
const isOpen = ref(false)
const loading = ref(false)
const navigationPath = ref([]) // Path of categories navigated through
const levelOptions = ref([]) // Options at different levels
const selectedOption = ref(null)

// Toggle dropdown
function toggleDropdown() {
  if (props.disabled) return
  
  if (!isOpen.value) {
    // Opening dropdown - load root options if needed
    if (!levelOptions.value.length && props.categoryId) {
      loadLevel(props.categoryId)
    }
  }
  
  isOpen.value = !isOpen.value
}

// Close dropdown when clicking outside
function closeDropdown() {
  isOpen.value = false
}

// Load options for a specific level/category
async function loadLevel(categoryId, isRoot = true) {
  if (!categoryId) {
    console.warn('BaseSelect: No categoryId provided')
    return []
  }

  console.log('BaseSelect: Loading level for categoryId:', categoryId)
  
  try {
    loading.value = true
    await store.viewCategory(categoryId)
    
    // Parse the options using the store's mapping structure
    const k = store.subcategories_k
    if (!k) {
      console.warn('BaseSelect: No subcategories_k mapping found')
      return []
    }

    const idIdx = Number(k?.id?.[0] ?? 0)
    const nameIdx = Number(k?.name?.[0] ?? 5)
    
    console.log('BaseSelect: Field indices - id:', idIdx, 'name:', nameIdx)

    const parsedOptions = (store.subcategories || []).map(row => {
      if (!Array.isArray(row)) {
        console.warn('BaseSelect: Invalid row format:', row)
        return null
      }

      return {
        id: row[idIdx],
        name: row[nameIdx] || `Option ${row[idIdx]}`,
        hasChildren: null // We'll check this only when clicked
      }
    }).filter(Boolean)

    if (isRoot) {
      levelOptions.value = parsedOptions
    }

    console.log('BaseSelect: Parsed options:', parsedOptions)
    return parsedOptions

  } catch (error) {
    console.error('BaseSelect: Error loading level:', error)
    return []
  } finally {
    loading.value = false
  }
}

// Handle option click - either select or navigate deeper
async function handleOptionClick(option) {
  console.log('BaseSelect: Option clicked:', option)
  
  // Check if this option has children (only when clicked)
  if (option.hasChildren === null) {
    console.log('BaseSelect: Checking for subcategories of:', option.name)
    
    try {
      await store.viewCategory(option.id)
      const hasSubcategories = store.subcategories && store.subcategories.length > 0
      option.hasChildren = hasSubcategories
      console.log(`BaseSelect: Option ${option.name} hasChildren:`, hasSubcategories)
    } catch (error) {
      option.hasChildren = false
      console.log(`BaseSelect: Option ${option.name} has no subcategories (error):`, error.message)
    }
  }
  
  if (option.hasChildren) {
    // Navigate to subcategory
    const subOptions = await loadLevel(option.id, false)
    
    if (subOptions.length > 0) {
      navigationPath.value.push({
        id: option.id,
        name: option.name,
        options: levelOptions.value // Store current level options
      })
      levelOptions.value = subOptions
      console.log('BaseSelect: Navigated deeper to:', option.name)
    } else {
      // No subcategories found, treat as final selection
      selectOption(option)
    }
  } else {
    // Leaf node - make final selection
    selectOption(option)
  }
}

// Select an option (final selection)
function selectOption(option) {
  console.log('BaseSelect: Final option selected:', option)
  
  selectedOption.value = option
  // 🔧 CHANGED: Emit option.name instead of option.id
  emit('update:modelValue', option.name)
  emit('change', option.name)
  
  // Close dropdown after selection
  isOpen.value = false
}

// Go back to previous level
function goBack() {
  if (navigationPath.value.length === 0) return
  
  const previousLevel = navigationPath.value.pop()
  levelOptions.value = previousLevel.options
  
  console.log('BaseSelect: Navigated back from:', previousLevel.name)
}

// Clear selection and reset navigation
function clearSelection() {
  console.log('BaseSelect: Clearing selection')
  
  selectedOption.value = null
  navigationPath.value = []
  
  // Reset to root level
  if (props.categoryId) {
    loadLevel(props.categoryId)
  }
  
  emit('update:modelValue', '')
  emit('change', '')
  
  // Close dropdown after clearing
  isOpen.value = false
}

// Watch for external modelValue changes
watch(() => props.modelValue, async (newValue) => {
  console.log('BaseSelect: modelValue changed to:', newValue)
  
  if (newValue && newValue !== selectedOption.value?.name) {
    // 🔧 CHANGED: Look for option by name instead of id
    const matchingOption = levelOptions.value.find(opt => opt.name == newValue)
    if (matchingOption) {
      selectedOption.value = matchingOption
    } else {
      // Value doesn't match current options - might be from a deeper level
      // For now, create a placeholder option with the text value
      selectedOption.value = { id: null, name: newValue, hasChildren: false }
      console.warn('BaseSelect: modelValue does not match current level options:', newValue)
    }
  } else if (!newValue) {
    selectedOption.value = null
  }
})

// Watch for categoryId changes
watch(() => props.categoryId, (newCategoryId) => {
  if (newCategoryId) {
    console.log('BaseSelect: categoryId changed to:', newCategoryId)
    // Reset all state and load new options
    levelOptions.value = []
    navigationPath.value = []
    selectedOption.value = null
    loadLevel(newCategoryId)
  }
}, { immediate: true })

// Computed properties
const currentOptions = computed(() => levelOptions.value)

const breadcrumb = computed(() => {
  return navigationPath.value.map(level => level.name)
})

const displayValue = computed(() => {
  if (selectedOption.value) {
    return selectedOption.value.name
  }
  return ''
})

// Close dropdown when clicking outside
onMounted(() => {
  document.addEventListener('click', (event) => {
    if (!event.target.closest('.form-group')) {
      closeDropdown()
    }
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
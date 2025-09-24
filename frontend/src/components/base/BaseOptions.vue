<template>
  <div class="base-options">
    <label v-if="label" :for="id" class="form-label">{{ label }}</label>
    
    <div class="options-container" :class="{ 'is-open': isOpen, 'has-selections': selectedOptions.length > 0 }">
      <!-- Selected items display -->
      <div v-if="selectedOptions.length > 0" class="selected-items">
        <div 
          v-for="option in selectedOptions" 
          :key="option.value"
          class="selected-item"
        >
          <span class="selected-text">{{ option.text }}</span>
          <button 
            type="button" 
            class="remove-item"
            @click="removeSelection(option)"
            :title="`Remove ${option.text}`"
          >
            ×
          </button>
        </div>
      </div>

      <!-- Dropdown trigger -->
      <div 
        class="dropdown-trigger"
        :class="{ 'has-placeholder': selectedOptions.length === 0 }"
        @click="toggleDropdown"
      >
        <span v-if="selectedOptions.length === 0" class="placeholder-text">
          {{ placeholder || 'Select options...' }}
        </span>
        <span v-else class="selection-count">
          {{ selectedOptions.length }} selected
        </span>
        
        <div class="dropdown-arrow" :class="{ 'is-open': isOpen }">
          <svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor">
            <path d="M2 4l4 4 4-4" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
      </div>

      <!-- Dropdown menu -->
      <div v-if="isOpen" class="dropdown-menu">
        <div v-if="loading" class="loading-state">
          <div class="loading-spinner"></div>
          <span>Loading options...</span>
        </div>

        <div v-else-if="error" class="error-state">
          <span class="error-icon">⚠️</span>
          <span class="error-text">{{ error }}</span>
          <button type="button" class="retry-btn" @click="fetchOptions">
            Retry
          </button>
        </div>

        <div v-else-if="options.length === 0" class="empty-state">
          <span class="empty-icon">📋</span>
          <span>No options available</span>
        </div>

        <div v-else class="options-list">
          <!-- Options list -->
          <div class="scrollable-options">
            <label
              v-for="option in options"
              :key="option.value"
              class="option-item"
              :class="{ 'is-selected': isSelected(option) }"
            >
              <input
                type="checkbox"
                :value="option.value"
                :checked="isSelected(option)"
                @change="toggleSelection(option)"
                class="option-checkbox"
              >
              <span class="option-text">{{ option.text }}</span>
              <span v-if="option.description" class="option-description">
                {{ option.description }}
              </span>
            </label>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import { useCategoryStore } from '@/stores/categories';

// Props
const props = defineProps({
  id: { type: String, required: true },
  label: { type: String, default: '' },
  placeholder: { type: String, default: 'Select options...' },
  modelValue: { type: Array, default: () => [] }, // Array of selected values
  categoryId: { type: [String, Number], required: true },
  disabled: { type: Boolean, default: false },
  required: { type: Boolean, default: false },
  maxSelections: { type: Number, default: null }, // Limit number of selections
});

// Emits
const emit = defineEmits(['update:modelValue', 'change', 'selection-change']);

// Store and state
const store = useCategoryStore();
const isOpen = ref(false);
const loading = ref(false);
const error = ref(null);
const options = ref([]);

// Computed
const selectedOptions = computed(() => {
  return options.value.filter(option => 
    props.modelValue.includes(option.value)
  );
});

// Methods
const fetchOptions = async () => {
  if (!props.categoryId) {
    console.warn('BaseOptions: No categoryId provided');
    return;
  }

  loading.value = true;
  error.value = null;

  try {
    console.log('BaseOptions: Loading options for categoryId:', props.categoryId);
    
    // Use the same category store as BaseSelect
    await store.viewCategory(props.categoryId);
    
    // Parse the options using the store's mapping structure (same as BaseSelect)
    const k = store.subcategories_k;
    if (!k) {
      throw new Error('No subcategories mapping found for this category');
    }

    const idIdx = Number(k?.id?.[0] ?? 0);
    const nameIdx = Number(k?.name?.[0] ?? 5);
    
    console.log('BaseOptions: Field indices - id:', idIdx, 'name:', nameIdx);

    const parsedOptions = (store.subcategories || []).map(row => {
      if (!Array.isArray(row)) {
        console.warn('BaseOptions: Invalid row format:', row);
        return null;
      }

      const textValue = row[nameIdx] || `Option ${row[idIdx]}`;
      
      return {
        value: textValue,  // 🔧 CHANGED: Use text as value instead of ID
        text: textValue,   // 🔧 Same text for display
        description: null  // Could add description mapping if needed
      };
    }).filter(Boolean);

    options.value = parsedOptions;
    console.log('BaseOptions: Parsed options:', parsedOptions);

  } catch (error) {
    console.error('BaseOptions: Error loading options:', error);
    error.value = error.message || 'Failed to load options';
    options.value = []; // Clear options on error
  } finally {
    loading.value = false;
  }
};

const toggleDropdown = () => {
  if (props.disabled) return;
  
  isOpen.value = !isOpen.value;
  
  if (isOpen.value && options.value.length === 0) {
    fetchOptions();
  }
};

const closeDropdown = () => {
  isOpen.value = false;
};

const isSelected = (option) => {
  return props.modelValue.includes(option.value);
};

const toggleSelection = (option) => {
  const currentValues = [...props.modelValue];
  const index = currentValues.indexOf(option.value);
  
  if (index > -1) {
    // Remove selection
    currentValues.splice(index, 1);
  } else {
    // Add selection (check max limit)
    if (props.maxSelections && currentValues.length >= props.maxSelections) {
      alert(`Maximum ${props.maxSelections} selections allowed`);
      return;
    }
    currentValues.push(option.value);
  }
  
  updateValue(currentValues);
};

const removeSelection = (option) => {
  const currentValues = props.modelValue.filter(value => value !== option.value);
  updateValue(currentValues);
};

const updateValue = (newValue) => {
  emit('update:modelValue', newValue);
  emit('change', newValue);
  emit('selection-change', {
    values: newValue,
    options: options.value.filter(opt => newValue.includes(opt.value))
  });
};

// Click outside handler
const handleClickOutside = (event) => {
  if (!event.target.closest('.base-options')) {
    closeDropdown();
  }
};

// Lifecycle
onMounted(() => {
  document.addEventListener('click', handleClickOutside);
  
  // Load options if we have selections but no options loaded
  if (props.modelValue.length > 0 && options.value.length === 0) {
    fetchOptions();
  }
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});

// Watch for category changes
watch(() => props.categoryId, () => {
  options.value = [];
  if (isOpen.value) {
    fetchOptions();
  }
});
</script>

<style scoped>
.base-options {
  position: relative;
  width: 100%;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: var(--color-fg, #1f2937);
  margin-bottom: 6px;
}

.options-container {
  position: relative;
  border: 1px solid var(--color-border, #d1d5db);
  border-radius: var(--radius-md, 6px);
  background: var(--color-surface, #ffffff);
  transition: all 0.2s ease;
}

.options-container:hover {
  border-color: var(--color-primary, #8b4513);
}

.options-container.is-open {
  border-color: var(--color-primary, #8b4513);
  box-shadow: 0 0 0 2px rgba(var(--color-primary-rgb, 139, 69, 19), 0.1);
}

.selected-items {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  padding: 8px 12px 4px 12px;
  border-bottom: 1px solid var(--color-border-light, #e5e7eb);
}

.selected-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 8px;
  background: var(--color-primary, #8b4513);
  color: white;
  border-radius: var(--radius-sm, 4px);
  font-size: 12px;
  font-weight: 500;
}

.selected-text {
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.remove-item {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 16px;
  line-height: 1;
  padding: 0;
  margin-left: 2px;
  border-radius: 2px;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
}

.remove-item:hover {
  background: rgba(255, 255, 255, 0.2);
}

.dropdown-trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  cursor: pointer;
  user-select: none;
  min-height: 44px;
}

.dropdown-trigger.has-placeholder .placeholder-text {
  color: var(--color-muted, #6b7280);
}

.selection-count {
  color: var(--color-fg, #1f2937);
  font-weight: 500;
}

.dropdown-arrow {
  color: var(--color-muted, #6b7280);
  transition: transform 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.dropdown-arrow.is-open {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  z-index: 50;
  background: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #d1d5db);
  border-radius: var(--radius-md, 6px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  margin-top: 2px;
  max-height: 300px;
  overflow: hidden;
}

.loading-state,
.error-state,
.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 20px;
  color: var(--color-muted, #6b7280);
  font-size: 14px;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid var(--color-border, #d1d5db);
  border-top-color: var(--color-primary, #8b4513);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-state {
  flex-direction: column;
  gap: 12px;
}

.retry-btn {
  padding: 6px 12px;
  background: var(--color-primary, #8b4513);
  color: white;
  border: none;
  border-radius: var(--radius-sm, 4px);
  font-size: 12px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.retry-btn:hover {
  background: var(--color-primary-dark, #7a3a0f);
}

.options-list {
  display: flex;
  flex-direction: column;
}

.scrollable-options {
  max-height: 200px;
  overflow-y: auto;
}

.option-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  cursor: pointer;
  transition: background-color 0.2s;
  border-bottom: 1px solid var(--color-border-light, #e5e7eb);
}

.option-item:last-child {
  border-bottom: none;
}

.option-item:hover {
  background: var(--color-background, #f9fafb);
}

.option-item.is-selected {
  background: rgba(var(--color-primary-rgb, 139, 69, 19), 0.05);
}

.option-checkbox {
  margin: 2px 0 0 0;
  cursor: pointer;
  accent-color: var(--color-primary, #8b4513);
}

.option-text {
  font-size: 14px;
  color: var(--color-fg, #1f2937);
  font-weight: 500;
}

.option-description {
  display: block;
  font-size: 12px;
  color: var(--color-muted, #6b7280);
  margin-top: 2px;
}

/* Accessibility */
.option-item:focus-within {
  background: var(--color-background, #f9fafb);
  outline: 2px solid var(--color-primary, #8b4513);
  outline-offset: -2px;
}

/* Mobile responsiveness */
@media (max-width: 640px) {
  .selected-items {
    gap: 4px;
  }
  
  .selected-item {
    font-size: 11px;
    padding: 3px 6px;
  }
  
  .selected-text {
    max-width: 100px;
  }
  
  .dropdown-menu {
    max-height: 250px;
  }
  
  .scrollable-options {
    max-height: 150px;
  }
}
</style>
<template>
  <div class="relative w-full">
    <label v-if="label" :for="id" class="block text-sm font-medium text-gray-900 dark:text-gray-100 mb-1.5">{{ label }}</label>
    
    <div :class="['relative border rounded-md bg-white dark:bg-gray-800 transition-all', isOpen ? 'border-primary ring-2 ring-primary/10' : 'border-gray-300 dark:border-gray-600 hover:border-primary', selectedOptions.length > 0 ? '' : '']">
      <!-- Selected items display -->
      <div v-if="selectedOptions.length > 0" class="flex flex-wrap gap-1.5 p-2 pb-1 border-b border-gray-200 dark:border-gray-600">
        <div 
          v-for="option in selectedOptions" 
          :key="option.value"
          class="inline-flex items-center gap-1.5 px-2 py-1 bg-primary text-white rounded text-xs font-medium"
        >
          <span class="max-w-[150px] overflow-hidden text-ellipsis whitespace-nowrap">{{ option.text }}</span>
          <button 
            type="button" 
            class="bg-transparent border-none text-white cursor-pointer text-base leading-none p-0 ml-0.5 rounded-sm w-4 h-4 flex items-center justify-center transition-colors hover:bg-white/20"
            @click="removeSelection(option)"
            :title="`Remove ${option.text}`"
          >
            ×
          </button>
        </div>
      </div>

      <!-- Dropdown trigger -->
      <div 
        :class="['flex items-center justify-between px-3 cursor-pointer select-none min-h-[44px]', selectedOptions.length === 0 ? 'py-3' : 'py-3']"
        @click="toggleDropdown"
      >
        <span v-if="selectedOptions.length === 0" class="text-gray-600 dark:text-gray-400">
          {{ placeholder || 'Select options...' }}
        </span>
        <span v-else class="text-gray-900 dark:text-gray-100 font-medium">
          {{ selectedOptions.length }} selected
        </span>
        
        <div :class="['text-gray-600 dark:text-gray-400 transition-transform flex items-center justify-center', isOpen ? 'rotate-180' : '']">
          <svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor">
            <path d="M2 4l4 4 4-4" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
      </div>

      <!-- Dropdown menu -->
      <div v-if="isOpen" class="absolute top-full left-0 right-0 z-50 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md shadow-xl mt-0.5 max-h-[300px] overflow-hidden">
        <div v-if="loading" class="flex items-center justify-center gap-2 p-5 text-gray-600 dark:text-gray-400 text-sm">
          <div class="w-4 h-4 border-2 border-gray-300 dark:border-gray-600 border-t-primary rounded-full animate-spin"></div>
          <span>Loading options...</span>
        </div>

        <div v-else-if="error" class="flex flex-col items-center justify-center gap-3 p-5 text-red-600 text-sm">
          <span class="text-xl">⚠️</span>
          <span>{{ error }}</span>
          <button type="button" class="px-3 py-1.5 bg-primary text-white border-none rounded text-xs cursor-pointer transition-colors hover:bg-primary/90" @click="fetchOptions">
            Retry
          </button>
        </div>

        <div v-else-if="options.length === 0" class="flex flex-col items-center justify-center gap-2 p-5 text-gray-600 dark:text-gray-400 text-sm">
          <span class="text-xl">📋</span>
          <span>No options available</span>
        </div>

        <div v-else class="flex flex-col">
          <!-- Options list -->
          <div class="max-h-[200px] overflow-y-auto">
            <label
              v-for="option in options"
              :key="option.value"
              :class="['flex items-start gap-3 px-3 py-3 cursor-pointer transition-colors border-b border-gray-100 dark:border-gray-700 last:border-b-0', isSelected(option) ? 'bg-primary/5' : 'hover:bg-gray-50 dark:hover:bg-gray-700']"
            >
              <input
                type="checkbox"
                :value="option.value"
                :checked="isSelected(option)"
                @change="toggleSelection(option)"
                class="mt-0.5 cursor-pointer accent-primary"
              >
              <div class="flex-1 min-w-0">
                <span class="text-sm text-gray-900 dark:text-gray-100 font-medium block">{{ option.text }}</span>
                <span v-if="option.description" class="block text-xs text-gray-600 dark:text-gray-400 mt-0.5">
                  {{ option.description }}
                </span>
              </div>
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
  modelValue: { type: Array, default: () => [] },
  categoryId: { type: [String, Number], required: true },
  disabled: { type: Boolean, default: false },
  required: { type: Boolean, default: false },
  maxSelections: { type: Number, default: null },
  returnText: { type: Boolean, default: false }
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
    
    await store.viewCategory(props.categoryId);
    
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

      const id = row[idIdx];
      const textValue = row[nameIdx] || `Option ${row[idIdx]}`;
      
      return {
        value: props.returnText ? textValue : id,
        id: id,
        text: textValue,
        description: null
      };
    }).filter(Boolean);

    options.value = parsedOptions;
    console.log('BaseOptions: Parsed options:', parsedOptions);

  } catch (error) {
    console.error('BaseOptions: Error loading options:', error);
    error.value = error.message || 'Failed to load options';
    options.value = [];
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
    currentValues.splice(index, 1);
  } else {
    if (props.maxSelections && currentValues.length >= props.maxSelections) {
      alert(`Maximum ${props.maxSelections} selections allowed`);
      return;
    }
    currentValues.push(option.value);
  }
  
  updateValue(currentValues, option, index > -1 ? 'remove' : 'add');
};

const removeSelection = (option) => {
  const currentValues = props.modelValue.filter(value => value !== option.value);
  updateValue(currentValues, option, 'remove');
};

const updateValue = (newValue, changedOption = null, action = null) => {
  emit('update:modelValue', newValue);
  emit('change', newValue);
  
  const selectedOpts = options.value.filter(opt => newValue.includes(opt.value));
  emit('selection-change', {
    values: newValue,
    ids: selectedOpts.map(opt => opt.id),
    texts: selectedOpts.map(opt => opt.text),
    options: selectedOpts,
    changedOption: changedOption,
    action: action
  });
};

// Click outside handler
const handleClickOutside = (event) => {
  if (!event.target.closest('.relative')) {
    closeDropdown();
  }
};

// Lifecycle
onMounted(() => {
  document.addEventListener('click', handleClickOutside);
  
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
<template>
  <div class="relative max-w-[420px]">
    <label 
      v-if="label" 
      class="block font-semibold mb-1.5" 
      :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
      :for="id"
    >
      {{ label }}
    </label>

    <!-- Input Display -->
    <div 
      @click="toggleDropdown" 
      :class="[
        'border rounded-lg px-3 py-2.5 flex justify-between items-center cursor-pointer transition-all min-h-[20px]',
        disabled 
          ? isDarkMode
            ? 'bg-black text-gray-500 cursor-not-allowed'
            : 'bg-gray-200 text-gray-400 cursor-not-allowed'
          : isDarkMode
            ? 'bg-gray-700 border-transparent hover:border-amber-600 focus-within:border-amber-600 focus-within:ring-2 focus-within:ring-amber-500/50'
            : 'bg-gray-50 border-transparent hover:border-amber-600 focus-within:border-amber-600 focus-within:ring-2 focus-within:ring-amber-600/50'
      ]"
    >
      <div 
        :class="[
          'flex-1 overflow-hidden text-ellipsis whitespace-nowrap',
          disabled 
            ? 'text-gray-500'
            : isDarkMode 
              ? 'text-gray-100' 
              : 'text-gray-900'
        ]"
      >
        {{ displayValue || placeholder || 'Select an option' }}
      </div>
      <span 
        :class="[
          'text-xs ml-2 transition-transform',
          isDarkMode ? 'text-gray-400' : 'text-gray-500',
          isOpen ? 'rotate-180' : ''
        ]"
      >
        ▼
      </span>
    </div>

    <!-- Dropdown -->
    <div 
      v-if="isOpen" 
      class="border rounded-lg mt-1 p-1.5 max-h-[300px] overflow-y-auto shadow-xl absolute w-full z-[1000]"
      :class="isDarkMode 
        ? 'border-transparent bg-black' 
        : 'border-transparent bg-white'"
    >
      <!-- Search Input -->
      <div v-if="searchable" class="p-2 border-b sticky top-0 bg-inherit z-10" :class="isDarkMode ? 'border-neutral-800' : 'border-gray-100'">
        <input 
          v-model="searchQuery"
          type="text" 
          placeholder="Search..." 
          class="w-full px-3 py-1.5 text-sm rounded border outline-none focus:ring-2 focus:ring-amber-500/50"
          :class="isDarkMode ? 'bg-neutral-800 border-neutral-700 text-white placeholder-gray-500' : 'bg-gray-50 border-gray-200 text-gray-900'"
          @click.stop
        />
      </div>

      <!-- Breadcrumb navigation -->
      <div 
        v-if="breadcrumb.length" 
        class="px-3 py-2 text-sm border-b mb-1.5"
        :class="isDarkMode 
          ? 'text-gray-400 border-transparent' 
          : 'text-gray-600 border-transparent'"
      >
        <span v-for="(name, i) in breadcrumb" :key="i">
          {{ name }}<span v-if="i < breadcrumb.length - 1"> > </span>
        </span>
      </div>

      <!-- Loading state -->
      <div 
        v-if="loading" 
        class="flex items-center gap-2 p-4 justify-center"
        :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
      >
        <div 
          class="w-4 h-4 border-2 rounded-full animate-spin"
          :class="isDarkMode 
            ? 'border-transparent border-t-amber-500' 
            : 'border-transparent border-t-amber-700'"
        ></div>
        <span>Loading options...</span>
      </div>

      <!-- Options list -->
      <ul v-else-if="currentOptions.length" class="list-none m-0 p-0">
        <li
          v-for="option in currentOptions"
          :key="option.id"
          @click.stop="handleOptionClick(option)"
          :class="[
            'px-3 py-2.5 cursor-pointer rounded transition-colors',
            option.id === selectedOption?.id 
              ? isDarkMode 
                ? 'bg-amber-600/20 text-amber-500 font-medium' 
                : 'bg-amber-100 text-amber-800 font-medium'
              : isDarkMode
                ? 'text-gray-100 hover:bg-gray-700'
                : 'text-gray-900 hover:bg-gray-100'
          ]"
        >
          <span class="option-text">{{ option.name }}</span>
          <span 
            v-if="option.hasChildren === true" 
            class="float-right"
            :class="isDarkMode ? 'text-gray-400' : 'text-gray-500'"
          >
            →
          </span>
        </li>
      </ul>

      <!-- No options -->
      <div 
        v-else 
        class="p-4 text-center italic"
        :class="isDarkMode ? 'text-gray-400' : 'text-gray-500'"
      >
        No options available
      </div>

      <!-- Controls -->
      <div 
        v-if="navigationPath.length > 0 || selectedOption" 
        class="mt-2 flex justify-center border-t pt-2"
        :class="isDarkMode ? 'border-transparent' : 'border-transparent'"
      >
        <button 
          v-if="navigationPath.length > 0" 
          type="button" 
          class="px-3 py-1.5 rounded border cursor-pointer text-xs transition-all duration-200 flex items-center gap-1"
          :class="isDarkMode 
            ? 'border-transparent bg-black text-gray-300 hover:bg-gray-700' 
            : 'border-transparent bg-white text-gray-700 hover:bg-gray-50'"
          @click.stop="goBack"
        >
          <i-mdi-chevron-left class="w-4 h-4" />
          Back
        </button>
        <button 
          v-if="selectedOption" 
          type="button" 
          class="px-3 py-1.5 rounded border border-red-600 cursor-pointer text-xs transition-all duration-200 text-red-400 hover:bg-red-600 hover:text-white ml-2 flex items-center gap-1"
          :class="isDarkMode ? 'bg-black' : 'bg-white'"
          @click.stop="clearSelection"
        >
          <i-mdi-close class="w-4 h-4" />
          Clear
        </button>
      </div>
    </div>

    <div 
      v-if="hint && !error" 
      class="text-xs mt-1"
      :class="isDarkMode ? 'text-gray-400' : 'text-gray-500'"
    >
      {{ hint }}
    </div>
    <div 
      v-if="error" 
      class="text-xs mt-1"
      :class="isDarkMode ? 'text-red-400' : 'text-red-600'"
    >
      {{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, inject } from 'vue'
import { useCategoryStore } from '@/stores/categories'

// Inject theme
const isDarkMode = inject('isDarkMode')

const props = defineProps({
  modelValue: [String, Number],
  label: String,
  hint: String,
  error: String,
  id: String,
  placeholder: String,
  disabled: Boolean,
  categoryId: [String, Number],
  searchable: Boolean
})

const emit = defineEmits(['update:modelValue', 'change'])

const store = useCategoryStore()
const isOpen = ref(false)
const loading = ref(false)
const navigationPath = ref([])
const levelOptions = ref([])
const selectedOption = ref(null)
const searchQuery = ref('')

// Toggle dropdown
function toggleDropdown() {
  if (props.disabled) return
  if (!isOpen.value && !levelOptions.value.length && props.categoryId) {
    loadLevel(props.categoryId)
  }
  isOpen.value = !isOpen.value
  if (!isOpen.value) {
     searchQuery.value = ''
  }
}

function closeDropdown() {
  isOpen.value = false
  searchQuery.value = ''
}

// Load options for a specific category level
async function loadLevel(categoryId, isRoot = true) {
  if (!categoryId) return []
  try {
    loading.value = true
    await store.viewCategory(categoryId)
    const parsedOptions = parseRows(store.subcategories, store.subcategories_k)

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

// Parse rows for normal navigation mode
function parseRows(rows = [], k = {}) {
    const idIdx = Number(k.id?.[0] ?? 0)
    const nameIdx = Number(k.name?.[0] ?? 5)

    if (!rows || !rows.length) return []

    return rows
      .map(row => ({
        id: row[idIdx],
        name: row[nameIdx] || `Option ${row[idIdx]}`,
        hasChildren: null
      }))
      .filter(Boolean)
}

// Parse search results - display hierarchical path from fullname field
function parseSearchResults(rows = [], k = {}) {
    const idIdx = Number(k.id?.[0] ?? 0)
    const nameIdx = Number(k.name?.[0] ?? 5)
    const fullnameIdx = Number(k.fullname?.[0] ?? 6)

    if (!rows || !rows.length) return []

    return rows.map(row => {
        const fullname = row[fullnameIdx] || ''
        // Convert "^CENTRAL^BUIKWE^KAMULI" to "CENTRAL > BUIKWE > KAMULI"
        const displayPath = fullname
            .split('^')
            .filter(Boolean)
            .join(' > ')

        return {
            id: row[idIdx],
            name: displayPath || row[nameIdx] || `Option ${row[idIdx]}`,
            hasChildren: false // Search results are treated as leaf nodes for direct selection
        }
    })
}

let searchTimeout
watch(searchQuery, (newVal) => {
    if (!props.searchable) return

    if (!newVal) {
        // Restore previous level when search cleared
        if (navigationPath.value.length > 0) {
            const last = navigationPath.value[navigationPath.value.length - 1]
            loadLevel(last.id, false).then(opts => levelOptions.value = opts)
        } else if (props.categoryId) {
            loadLevel(props.categoryId, true)
        }
    } else {
        // Server-side search with debounce
        clearTimeout(searchTimeout)
        searchTimeout = setTimeout(async () => {
            loading.value = true
            try {
                await store.searchSubcategories(props.categoryId, newVal, 10)
                levelOptions.value = parseSearchResults(
                    store.subcategories,
                    store.subcategories_k
                )
            } catch (e) {
                console.error('Search failed:', e)
                levelOptions.value = []
            } finally {
                loading.value = false
            }
        }, 300)
    }
})

// Handle option click
async function handleOptionClick(option) {
  // If in search mode, directly select the option (search results show full paths)
  if (searchQuery.value) {
    selectOption(option)
    return
  }

  // Normal navigation mode - check for children
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

// Emit the ID but display the name
function selectOption(option) {
  selectedOption.value = option
  emit('update:modelValue', option.id)
  // IMPORTANT: Emit change with both ID and text
  emit('change', option.id, option.name)
  closeDropdown()
}

// Go back a level
function goBack() {
  if (navigationPath.value.length === 0) return
  const previousLevel = navigationPath.value.pop()
  levelOptions.value = previousLevel.options
  // Should we restore search query?
  // If we backed up to search results, maybe?
  // But levelOptions is restored. SearchQuery text might be empty if we cleared it on dive.
  // Ideally clear search query on Back to ensure consistent state/UI match.
  searchQuery.value = ''
}

// Clear selection
function clearSelection() {
  selectedOption.value = null
  navigationPath.value = []
  if (props.categoryId) loadLevel(props.categoryId)
  emit('update:modelValue', '')
  emit('change', '', '')
  closeDropdown()
}

// Watch modelValue and update display name
watch(() => props.modelValue, async (newValue) => {
  if (newValue && newValue !== selectedOption.value?.id) {
    // If not in current options, we might need to fetch info about this ID?
    // Current logic tries to find in levelOptions.
    const matchingOption = levelOptions.value.find(opt => opt.id == newValue)
    if (matchingOption) {
      selectedOption.value = matchingOption
    } else {
      // Fallback display if not found in current list
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
    searchQuery.value = ''
    loadLevel(newCategoryId)
  }
}, { immediate: true })

// Computed
const currentOptions = computed(() => {
   // Since search replaces levelOptions via backend call, 
   // we don't filter client side anymore if we rely on backend.
   // BUT, to be safe (if backend ignores q), we can still filter.
   // However, if backend returns partial matches, client filter is fine.
   // If backend returns hierarchy, client filter might break it.
   // Let's assume levelOptions contains what we want to show.
   // Only filter if we want local filtering capability as well?
   // The requirements say "search through hierarchy", so local filter of visible level is wrong.
   // We trust levelOptions is updated by performSearch.
   return levelOptions.value
})
const breadcrumb = computed(() => navigationPath.value.map(level => level.name))
const displayValue = computed(() => selectedOption.value?.name || '')

// Close dropdown when clicking outside
onMounted(() => {
  document.addEventListener('click', (event) => {
    if (!event.target.closest('.relative')) closeDropdown()
  })
})
</script>
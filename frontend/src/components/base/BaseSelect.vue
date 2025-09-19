<template>
  <div class="form-group">
    <label v-if="label" class="form-label" :for="id">{{ label }}</label>

    <!-- Input Display -->
    <div class="select-container" @click="toggleDropdown">
      <div class="selected-value">
        {{ selectedPath || placeholder || 'Select an option' }}
      </div>
      <span class="arrow">▼</span>
    </div>

    <!-- Dropdown -->
    <div v-if="open" class="dropdown">
      <div class="breadcrumb" v-if="breadcrumb.length">
        <span v-for="(name, i) in breadcrumb" :key="i">
          {{ name }}<span v-if="i < breadcrumb.length - 1"> > </span>
        </span>
      </div>

      <ul class="options">
        <li
          v-for="opt in currentOptions"
          :key="opt.id"
          @click.stop="handleOptionClick(opt)"
        >
          {{ opt.name }}
        </li>
      </ul>

      <!-- Navigation controls -->
      <div class="controls" v-if="path.length">
        <button class="btn back" @click="goBack">← Back</button>
        <button class="btn reset" @click="resetCascade">Reset</button>
      </div>
    </div>

    <div v-if="hint && !error" class="form-hint">{{ hint }}</div>
    <div v-if="error" class="form-error">{{ error }}</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useCategoryStore } from '@/stores/categories'

const props = defineProps({
  modelValue: [String, Number],
  label: String,
  hint: String,
  error: String,
  id: String,
  placeholder: String,
  disabled: Boolean,
  categoryId: [String, Number] // Root category for fetching
})

const emit = defineEmits(['update:modelValue'])

const store = useCategoryStore()
const open = ref(false)
const path = ref([])      // chosen path: [{id, name}]
const levels = ref([])    // options for each depth

// --- Toggle dropdown ---
function toggleDropdown() {
  if (!props.disabled) open.value = !open.value
}

// --- Load level options based on parentId ---
async function loadLevel(parentId) {
  await store.viewCategory(parentId)
  const k = store.subcategories_k
  const idIdx = Number(k?.id?.[0] ?? 0)
  const nameIdx = Number(k?.name?.[0] ?? 5)

  return (store.subcategories || []).map(r => ({
    id: r?.[idIdx],
    name: r?.[nameIdx]
  }))
}

async function handleOptionClick(opt) {
  const nextLevel = await loadLevel(opt.id)

  if (nextLevel.length) {
    // Has subcategories → go deeper
    path.value.push(opt)
    levels.value.push(nextLevel)
  } else {
    // Leaf node → select and close
    path.value.push(opt) // Add to path so it shows in selectedPath
    emit('update:modelValue', opt.id) // or `opt` if you want full object
    open.value = false
  }
}


// --- Navigation ---
function goBack() {
  path.value.pop()
  levels.value.pop()
}

function resetCascade() {
  path.value = []
  levels.value = []
  init()
}

// --- Computed helpers ---
const currentOptions = computed(() => {
  if (!levels.value.length) return []
  return levels.value[levels.value.length - 1]
})

const breadcrumb = computed(() => path.value.map(p => p.name))
const selectedPath = computed(() => breadcrumb.value.join(' > '))

// --- Initial load ---
async function init() {
  if (!props.categoryId) return
  const first = await loadLevel(props.categoryId)
  levels.value = [first]
}

watch(() => props.categoryId, init, { immediate: true })
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
}
.select-container {
  border: 1px solid #bbb;
  border-radius: 6px;
  padding: 8px;
  display: flex;
  justify-content: space-between;
  cursor: pointer;
  background: #fff;
}
.selected-value {
  color: #333;
}
.arrow {
  font-size: 12px;
}
.dropdown {
  border: 1px solid #ccc;
  border-radius: 6px;
  margin-top: 4px;
  background: #fff;
  padding: 6px;
  max-height: 250px;
  overflow-y: auto;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  position: absolute;
  width: 100%;
  z-index: 10;
}
.breadcrumb {
  font-size: 14px;
  margin-bottom: 6px;
  font-weight: 500;
}
.options {
  list-style: none;
  margin: 0;
  padding: 0;
}
.options li {
  padding: 6px;
  cursor: pointer;
  border-radius: 4px;
}
.options li:hover {
  background: #f2f2f2;
}
.controls {
  margin-top: 8px;
  display: flex;
  gap: 6px;
}
.btn {
  padding: 6px 10px;
  border-radius: 4px;
  border: 1px solid #888;
  background: #f7f7f7;
  cursor: pointer;
  font-size: 13px;
}
.btn:hover {
  background: #efefef;
}
.back { color: #333; }
.reset { color: #b00; }
</style>




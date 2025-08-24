<template>
  <div class="cascade">
    <label class="lbl">Location</label>

    <!-- Input (trigger/display) -->
    <div class="input-box" @click="toggleDropdown">
      <span>{{ fullLocation || 'Select Location' }}</span>
      <span class="arrow">▼</span>
    </div>

    <!-- Dropdown (expanding options) -->
    <div v-if="open" class="dropdown">
      <div class="breadcrumb">
        <span v-for="(name, i) in breadcrumb" :key="i">
          {{ name }}
          <span v-if="i < breadcrumb.length - 1"> > </span>
        </span>
      </div>

      <ul class="options">
        <li v-for="opt in currentOptions" :key="opt.id" @click.stop="selectOption(opt)">
          {{ opt.name }}
        </li>
      </ul>

      <!-- Controls -->
      <div class="controls">
        <button class="btn back" v-if="path.length" @click="goBack">← Back</button>
        <button class="btn reset" v-if="path.length" @click="resetCascade">Reset</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useCategoryStore } from "@/stores/categories";

const store = useCategoryStore();

const open = ref(false);
const path = ref([]);       // chosen path [{id, name}]
const levels = ref([]);     // options at each depth

function toggleDropdown() {
  open.value = !open.value;
}

function getIndexes(k = store.subcategories_k) {
  const idIdx = Number(k?.id?.[0] ?? 0);
  const nameIdx = Number(k?.name?.[0] ?? 5);
  return { idIdx, nameIdx };
}

function mapRows(rows, k = store.subcategories_k) {
  const { idIdx, nameIdx } = getIndexes(k);
  return (rows || []).map(r => ({ id: r?.[idIdx], name: r?.[nameIdx] }));
}

async function loadLevelByParentId(parentId) {
  await store.viewCategory(parentId);
  return mapRows(store.subcategories, store.subcategories_k);
}

async function selectOption(opt) {
  path.value.push(opt);
  const next = await loadLevelByParentId(opt.id);

  if (next.length) {
    levels.value.push(next);
  } else {
    // End of tree
    open.value = false;
  }
}

function goBack() {
  path.value.pop();
  levels.value.pop();
}

function resetCascade() {
  path.value = [];
  levels.value = [];
  init();
}

const currentOptions = computed(() => {
  if (!levels.value.length) return [];
  return levels.value[levels.value.length - 1];
});

const breadcrumb = computed(() => path.value.map(p => p.name));

const fullLocation = computed(() => breadcrumb.value.join(" > "));

async function init() {
  const first = await loadLevelByParentId(88); // Root category
  levels.value = [first];
}

onMounted(init);
</script>

<style scoped>
.cascade { max-width: 420px; position: relative; }
.lbl { display: block; font-weight: 600; margin-bottom: 6px; }
.input-box {
  border: 1px solid #bbb;
  border-radius: 6px;
  padding: 8px;
  display: flex;
  justify-content: space-between;
  cursor: pointer;
}
.dropdown {
  border: 1px solid #ccc;
  border-radius: 6px;
  margin-top: 4px;
  background: #fff;
  padding: 6px;
  max-height: 300px;
  overflow-y: auto;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
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
.arrow { font-size: 12px; }
</style>

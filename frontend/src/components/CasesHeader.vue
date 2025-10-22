<template>
  <header class="page-header">
    <div class="header-top">
      <div class="header-left">
        <h1 class="page-title">Cases</h1>
        <router-link to="/case-creation" class="btn btn--primary btn--sm">Add New Case</router-link>
      </div>
    </div>

    <div class="search-and-controls-section">
      <div class="search-container">
        <input
          :value="searchQuery"
          @input="$emit('update:search-query', $event.target.value)"
          type="text"
          placeholder="Search case by title, assignee, or filter..."
          class="input"
        />
      </div>
      <div class="view-toggle">
        <button
          class="btn btn--secondary btn--sm"
          :class="{ active: currentView === 'table' }"
          @click="$emit('set-view', 'table')"
        >
          Table View
        </button>
        <button
          class="btn btn--secondary btn--sm"
          :class="{ active: currentView === 'timeline' }"
          @click="$emit('set-view', 'timeline')"
        >
          Timeline
        </button>
      </div>
    </div>

    <div class="filter-section">
      <button
        v-for="filter in filters"
        :key="filter.id"
        class="btn btn--secondary btn--sm"
        :class="{ active: activeFilter === filter.id }"
        @click="$emit('set-filter', filter.id)"
      >
        {{ filter.name }}
      </button>
      <router-link to="/reports-category" class="btn btn--secondary btn--sm">Advanced Filters</router-link>
    </div>
  </header>
</template>

<script setup>
const props = defineProps({
  searchQuery: { type: String, default: '' },
  currentView: { type: String, default: 'table' },
  filters: { type: Array, default: () => [] },
  activeFilter: { type: String, default: 'all' }
})
</script>

<style scoped>
.page-header { margin-bottom: 16px; }
.search-and-controls-section { display: flex; gap: 12px; align-items: center; justify-content: space-between; }
.view-toggle { display: flex; gap: 8px; }
.filter-section { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 10px; }
.btn.btn--secondary.active { border-color: var(--color-primary); background: var(--color-surface); }
</style>

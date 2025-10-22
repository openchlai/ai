<template>
  <div class="cases-table-wrapper card" style="padding:0;">
    <table class="cases-table">
      <thead>
        <tr>
          <th class="case-id-header">Case ID</th>
          <th class="created-by-header">Created By</th>
          <th class="created-on-header">Created On</th>
          <th class="source-header">Source</th>
          <th class="priority-header">Priority</th>
          <th class="status-header">Status</th>
          <th class="actions-header">Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="caseItem in cases"
          :key="casesK?.id ? caseItem[casesK.id[0]] : caseItem.id"
          :class="['table-row', { selected: selectedId === (casesK?.id ? caseItem[casesK.id[0]] : caseItem.id) }]"
          @click="$emit('select', casesK?.id ? caseItem[casesK.id[0]] : caseItem.id)"
        >
          <td class="case-id-cell">{{ casesK?.id ? caseItem[casesK.id[0]] : caseItem.id || 'N/A' }}</td>
          <td class="created-by-cell">{{ casesK?.created_by ? caseItem[casesK.created_by[0]] || 'N/A' : 'N/A' }}</td>
          <td class="created-on-cell">
            {{ casesK?.dt ? new Date((caseItem[casesK.dt[0]] < 10000000000 ? caseItem[casesK.dt[0]] * 1000 : caseItem[casesK.dt[0]] * 3600 * 1000)).toLocaleDateString() : 'N/A' }}
          </td>
          <td class="source-cell">{{ casesK?.source ? caseItem[casesK.source[0]] || 'N/A' : 'N/A' }}</td>
          <td class="priority-cell">
            <span class="priority-badge" :class="(casesK?.priority ? caseItem[casesK.priority[0]] || 'normal' : 'normal').toLowerCase()">
              <span :class="['priority-dot', (casesK?.priority ? caseItem[casesK.priority[0]] || '' : '').toLowerCase()]" />
              {{ casesK?.priority ? caseItem[casesK.priority[0]] || 'Normal' : 'Normal' }}
            </span>
          </td>
          <td class="status-cell">
            <span class="status-badge" :class="(casesK?.status ? caseItem[casesK.status[0]] || 'open' : 'open').toLowerCase()">
              {{ casesK?.status ? caseItem[casesK.status[0]] || 'Open' : 'Open' }}
            </span>
          </td>
          <td class="actions-cell">
            <button class="btn btn--secondary btn--sm" @click.stop="$emit('select', casesK?.id ? caseItem[casesK.id[0]] : caseItem.id)">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                <circle cx="12" cy="12" r="3"/>
              </svg>
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
const props = defineProps({
  cases: { type: Array, default: () => [] },
  casesK: { type: Object, default: null },
  selectedId: { type: [String, Number], default: null }
})
</script>

<style scoped>
.cases-table { width: 100%; border-collapse: collapse; }
.cases-table th, .cases-table td { padding: 12px; text-align: left; }
.table-row { cursor: pointer; }
.table-row.selected { background: color-mix(in oklab, var(--color-primary) 8%, transparent); }
</style>



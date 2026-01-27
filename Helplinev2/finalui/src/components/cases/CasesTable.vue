<template>
  <div class="rounded-lg shadow-xl overflow-hidden border" :class="isDarkMode
    ? 'bg-black border-transparent'
    : 'bg-white border-transparent'">
    <table class="w-full">
      <thead>
        <tr class="border-b" :class="isDarkMode
          ? 'bg-black/60 border-transparent'
          : 'bg-gray-50 border-transparent'">
          <th class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider"
            :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'">
            Case ID
          </th>
          <th class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider"
            :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'">
            Created By
          </th>
          <th class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider"
            :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'">
            Created On
          </th>
          <th class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider"
            :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'">
            Source
          </th>
          <th class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider"
            :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'">
            Category
          </th>
          <th class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider"
            :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'">
            Priority
          </th>
          <th class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider"
            :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'">
            Status
          </th>
        </tr>
      </thead>

      <tbody class="divide-y" :class="isDarkMode ? 'divide-gray-700' : 'divide-gray-200'">
        <tr v-for="caseItem in cases" :key="cases_k.id ? caseItem[cases_k.id[0]] : caseItem.id"
          @click="selectCase(caseItem)" class="cursor-pointer transition-all duration-200" :class="isDarkMode
            ? 'hover:bg-neutral-800'
            : 'hover:bg-gray-50'">
          <td class="px-6 py-4" :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'">
            {{ getValue(caseItem, 'id') }}
          </td>
          <td class="px-6 py-4" :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'">
            {{ getValue(caseItem, 'created_by') || 'N/A' }}
          </td>
          <td class="px-6 py-4" :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'">
            {{ formatDateTime(getValue(caseItem, 'dt')) }}
          </td>
          <td class="px-6 py-4" :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'">
            {{ getValue(caseItem, 'src') || 'N/A' }}
          </td>
          <td class="px-6 py-4">
            <div class="flex flex-wrap gap-1.5">
              <span
                v-for="(cat, idx) in formatCategories(getValue(caseItem, 'case_category') || getValue(caseItem, 'cat_0'))"
                :key="idx"
                class="px-2 py-0.5 rounded text-[10px] font-bold uppercase transition-all duration-200 border"
                :class="getCategoryBadgeClass(idx)">
                {{ cat }}
              </span>
              <span v-if="!getValue(caseItem, 'case_category') && !getValue(caseItem, 'cat_0')"
                :class="isDarkMode ? 'text-gray-500' : 'text-gray-400'">
                N/A
              </span>
            </div>
          </td>

          <!-- Priority -->
          <td class="px-6 py-4">
            <span :class="[
              'px-3 py-1 rounded-full text-xs font-semibold uppercase border',
              getPriorityClass(getValue(caseItem, 'priority'))
            ]">
              {{ formatPriority(getValue(caseItem, 'priority')) }}
            </span>
          </td>

          <!-- Status -->
          <td class="px-6 py-4">
            <span :class="[
              'px-3 py-1 rounded-full text-xs font-semibold uppercase border',
              getStatusClass(getValue(caseItem, 'status'))
            ]">
              {{ formatStatus(getValue(caseItem, 'status')) }}
            </span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
  import { inject } from 'vue'

  const props = defineProps({
    cases: Array,
    cases_k: Object,
  })

  const emit = defineEmits(['select-case'])

  // Inject theme
  const isDarkMode = inject('isDarkMode')

  // ✅ FIXED: Emit case ID only
  const selectCase = (caseItem) => {
    const caseId = getValue(caseItem, 'id')
    console.log('📤 Table emitting case ID:', caseId)
    emit('select-case', caseId)
  }

  // Access values using the cases_k structure
  const getValue = (caseItem, key) => {
    if (!props.cases_k?.[key]) return null
    return caseItem[props.cases_k[key][0]]
  }

  // Format timestamp to date only (no time for cases)
  const formatDateTime = (timestamp) => {
    if (!timestamp || timestamp === '0') return 'N/A'
    const date = new Date(parseInt(timestamp) * 1000)
    return date.toLocaleString('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    })
  }

  // Priority label formatter
  const formatPriority = (priority) => {
    if (!priority) return 'N/A'
    switch (Number(priority)) {
      case 3:
        return 'High'
      case 2:
        return 'Medium'
      case 1:
        return 'Low'
      default:
        return 'Unknown'
    }
  }

  // Status label formatter
  const formatStatus = (status) => {
    if (!status) return 'N/A'
    switch (Number(status)) {
      case 1:
        return 'Open'
      case 2:
        return 'Closed'
      default:
        return 'Unknown'
    }
  }

  // Tailwind color classes based on priority
  const getPriorityClass = (priority) => {
    switch (Number(priority)) {
      case 3: // High
        return isDarkMode.value
          ? 'bg-red-600/20 text-red-400 border-red-600/30'
          : 'bg-red-100 text-red-700 border-red-300'
      case 2: // Medium
        return isDarkMode.value
          ? 'bg-amber-600/20 text-amber-400 border-amber-600/30'
          : 'bg-amber-100 text-amber-700 border-amber-300'
      case 1: // Low
        return isDarkMode.value
          ? 'bg-green-600/20 text-green-400 border-green-600/30'
          : 'bg-green-100 text-green-700 border-green-300'
      default:
        return isDarkMode.value
          ? 'bg-gray-600/20 text-gray-400 border-transparent/30'
          : 'bg-gray-100 text-gray-600 border-transparent'
    }
  }

  // Tailwind color classes based on status
  const getStatusClass = (status) => {
    switch (Number(status)) {
      case 1: // Open
        return isDarkMode.value
          ? 'bg-amber-600/20 text-amber-400 border-amber-600/30'
          : 'bg-amber-100 text-amber-700 border-amber-300'
      case 2: // Closed
        return isDarkMode.value
          ? 'bg-green-600/20 text-green-400 border-green-600/30'
          : 'bg-green-100 text-green-700 border-green-300'
      default:
        return isDarkMode.value
          ? 'bg-gray-600/20 text-gray-400 border-transparent/30'
          : 'bg-gray-100 text-gray-600 border-transparent'
    }
  }

  // Split category string by ^ and trim
  const formatCategories = (catString) => {
    if (!catString) return []
    return String(catString).split('^').map(s => s.trim()).filter(Boolean)
  }

  // Dynamic colors for categories sticking to theme colors
  const getCategoryBadgeClass = (index) => {
    const darkColors = [
      'bg-amber-900/40 text-amber-500 border-amber-800/50 hover:bg-amber-900/60',
      'bg-orange-900/40 text-orange-400 border-orange-800/50 hover:bg-orange-900/60',
      'bg-yellow-900/40 text-yellow-500 border-yellow-800/50 hover:bg-yellow-900/60'
    ]

    const lightColors = [
      'bg-amber-50 text-amber-700 border-amber-200 hover:bg-amber-100',
      'bg-orange-50 text-orange-700 border-orange-200 hover:bg-orange-100',
      'bg-yellow-50 text-yellow-700 border-yellow-200 hover:bg-yellow-100'
    ]

    const palette = isDarkMode.value ? darkColors : lightColors
    return palette[index % palette.length]
  }
</script>
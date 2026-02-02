<template>
  <div class="relative border-l-[1px] pl-8 space-y-6" :class="isDarkMode ? 'border-transparent' : 'border-transparent'">
    <div v-for="caseItem in cases" :key="cases_k.id ? caseItem[cases_k.id[0]] : caseItem.id"
      @click="selectCase(caseItem)"
      class="relative shadow-xl rounded-lg p-6 border cursor-pointer transition-all duration-200" :class="isDarkMode
        ? 'bg-black border-transparent hover:bg-neutral-800'
        : 'bg-white border-transparent hover:bg-gray-50'">
      <!-- Timeline Dot - Hollow Circle Split by Line -->
      <div class="absolute -left-[42px] top-1/2 -translate-y-1/2 w-5 h-5 rounded-full border-[3px]" :class="isDarkMode
        ? 'border-transparent bg-black'
        : 'border-transparent bg-white'"></div>

      <!-- Case Info -->
      <h3 class="text-lg font-semibold" :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'">
        Case {{ getValue(caseItem, 'id') }}
      </h3>
      <p class="text-sm mt-1" :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'">
        Created on: {{ formatDateTime(getValue(caseItem, 'dt')) }}
      </p>
      <p class="text-sm mt-1" :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'">
        Created by: {{ getValue(caseItem, 'created_by') || 'N/A' }}
      </p>

      <!-- Labels -->
      <div class="flex flex-wrap gap-2 mt-4">
        <!-- Priority -->
        <span :class="[
          'px-3 py-1 rounded-full text-xs font-semibold uppercase border',
          getPriorityClass(getValue(caseItem, 'priority'))
        ]">
          Priority: {{ getPriorityText(getValue(caseItem, 'priority')) }}
        </span>

        <!-- Status -->
        <span :class="[
          'px-3 py-1 rounded-full text-xs font-semibold uppercase border',
          getStatusClass(getValue(caseItem, 'status'))
        ]">
          Status: {{ getStatusText(getValue(caseItem, 'status')) }}
        </span>

        <!-- Category -->
        <div v-if="getValue(caseItem, 'case_category') || getValue(caseItem, 'cat_0')" class="flex flex-wrap gap-2">
          <span
            v-for="(cat, idx) in formatCategories(getValue(caseItem, 'case_category') || getValue(caseItem, 'cat_0'))"
            :key="idx" :class="[
              'px-3 py-1 rounded-full text-[10px] font-bold uppercase border transition-all duration-200',
              getCategoryBadgeClass(idx)
            ]">
            {{ cat }}
          </span>
        </div>
      </div>
    </div>
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
    console.log('📤 Timeline emitting case ID:', caseId)
    emit('select-case', caseId)
  }

  // Map the array-style structure
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

  // --- Priority ---
  const getPriorityClass = (priority) => {
    switch (String(priority)) {
      case '3':
        return isDarkMode.value
          ? 'bg-red-600/20 text-red-400 border-red-600/30'
          : 'bg-red-100 text-red-700 border-red-300'
      case '2':
        return isDarkMode.value
          ? 'bg-amber-600/20 text-amber-400 border-amber-600/30'
          : 'bg-amber-100 text-amber-700 border-amber-300'
      case '1':
      default:
        return isDarkMode.value
          ? 'bg-green-600/20 text-green-400 border-green-600/30'
          : 'bg-green-100 text-green-700 border-green-300'
    }
  }

  const getPriorityText = (priority) => {
    switch (String(priority)) {
      case '3':
        return 'High'
      case '2':
        return 'Medium'
      case '1':
        return 'Low'
      default:
        return 'Unknown'
    }
  }

  // --- Status ---
  const getStatusClass = (status) => {
    switch (String(status)) {
      case '2':
        return isDarkMode.value
          ? 'bg-green-600/20 text-green-400 border-green-600/30'
          : 'bg-green-100 text-green-700 border-green-300'
      case '1':
      default:
        return isDarkMode.value
          ? 'bg-amber-600/20 text-amber-400 border-amber-600/30'
          : 'bg-amber-100 text-amber-700 border-amber-300'
    }
  }

  const getStatusText = (status) => {
    switch (String(status)) {
      case '2':
        return 'Closed'
      case '1':
        return 'Open'
      default:
        return 'Unknown'
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
      'bg-amber-900/40 text-amber-500 border-amber-800/50 hover:bg-amber-900/60 hover:scale-105',
      'bg-orange-900/40 text-orange-400 border-orange-800/50 hover:bg-orange-900/60 hover:scale-105',
      'bg-yellow-900/40 text-yellow-500 border-yellow-800/50 hover:bg-yellow-900/60 hover:scale-105'
    ]

    const lightColors = [
      'bg-amber-50 text-amber-700 border-amber-200 hover:bg-amber-100 hover:scale-105',
      'bg-orange-50 text-orange-700 border-orange-200 hover:bg-orange-100 hover:scale-105',
      'bg-yellow-50 text-yellow-700 border-yellow-200 hover:bg-yellow-100 hover:scale-105'
    ]

    const palette = isDarkMode.value ? darkColors : lightColors
    return palette[index % palette.length]
  }
</script>
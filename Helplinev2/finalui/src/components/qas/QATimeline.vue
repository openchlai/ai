<template>
  <div class="space-y-6">
    <div 
      v-for="(group, date) in groupedQAs" 
      :key="date" 
      class="rounded-lg shadow-xl border overflow-hidden"
      :class="isDarkMode 
        ? 'bg-neutral-900 border-transparent' 
        : 'bg-white border-transparent'"
    >
      <!-- Date Header -->
      <div 
        class="px-6 py-3 border-b"
        :class="isDarkMode 
          ? 'bg-black/60 border-transparent' 
          : 'bg-gray-50 border-transparent'"
      >
        <h3 
          class="text-sm font-semibold flex items-center gap-2"
          :class="isDarkMode ? 'text-amber-500' : 'text-amber-700'"
        >
          <i-mdi-calendar class="w-4 h-4" />
          {{ date }}
        </h3>
      </div>

      <!-- QA Records List -->
      <div 
        class="divide-y"
        :class="isDarkMode ? 'divide-gray-700' : 'divide-gray-200'"
      >
        <div 
          v-for="qa in group" 
          :key="getFieldValue(qa, 'id')"
          class="p-6 transition-all duration-200 cursor-pointer"
          :class="isDarkMode 
            ? 'hover:bg-neutral-800' 
            : 'hover:bg-gray-50'"
          @click="viewQADetails(qa)"
        >
          <div class="flex items-start gap-4">
            <!-- Icon & Score -->
            <div 
              class="flex-shrink-0 w-16 h-16 rounded-lg flex flex-col items-center justify-center border"
              :class="isDarkMode 
                ? 'bg-gradient-to-br from-amber-600/20 to-purple-600/20 border-amber-600/30' 
                : 'bg-gradient-to-br from-amber-100 to-orange-100 border-amber-300'"
            >
              <span 
                class="text-2xl font-bold"
                :class="isDarkMode ? 'text-amber-500' : 'text-amber-700'"
              >
                {{ calculateScore(qa) }}%
              </span>
            </div>

            <!-- Content -->
            <div class="flex-1 min-w-0">
              <div class="flex items-start justify-between gap-4 mb-2">
                <div>
                  <h4 
                    class="text-sm font-semibold"
                    :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
                  >
                    QA {{ getFieldValue(qa, 'id') }}
                  </h4>
                  <p 
                    class="text-xs mt-1"
                    :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
                  >
                    Call: {{ getFieldValue(qa, 'chan_uniqueid') }}
                  </p>
                </div>
                <div class="text-right">
                  <p 
                    class="text-xs"
                    :class="isDarkMode ? 'text-gray-500' : 'text-gray-500'"
                  >
                    Evaluated on
                  </p>
                  <p 
                    class="text-sm"
                    :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
                  >
                    {{ formatTimestamp(getFieldValue(qa, 'created_on')) }}
                  </p>
                </div>
              </div>

              <div class="grid grid-cols-3 gap-4 mt-3">
                <div>
                  <p 
                    class="text-xs mb-1"
                    :class="isDarkMode ? 'text-gray-500' : 'text-gray-500'"
                  >
                    Opening
                  </p>
                  <p 
                    class="text-sm font-medium" 
                    :class="getRatingColor(getFieldValue(qa, 'opening_phrase'))"
                  >
                    {{ getRatingText(getFieldValue(qa, 'opening_phrase')) }}
                  </p>
                </div>
                <div>
                  <p 
                    class="text-xs mb-1"
                    :class="isDarkMode ? 'text-gray-500' : 'text-gray-500'"
                  >
                    Communication
                  </p>
                  <p 
                    class="text-sm font-medium" 
                    :class="getRatingColor(getFieldValue(qa, 'courteous'))"
                  >
                    {{ getRatingText(getFieldValue(qa, 'courteous')) }}
                  </p>
                </div>
                <div>
                  <p 
                    class="text-xs mb-1"
                    :class="isDarkMode ? 'text-gray-500' : 'text-gray-500'"
                  >
                    Resolution
                  </p>
                  <p 
                    class="text-sm font-medium" 
                    :class="getRatingColor(getFieldValue(qa, 'accuracy'))"
                  >
                    {{ getRatingText(getFieldValue(qa, 'accuracy')) }}
                  </p>
                </div>
              </div>

              <div 
                v-if="getFieldValue(qa, 'feedback')" 
                class="mt-3 pt-3 border-t"
                :class="isDarkMode ? 'border-transparent' : 'border-transparent'"
              >
                <p 
                  class="text-xs mb-1"
                  :class="isDarkMode ? 'text-gray-500' : 'text-gray-500'"
                >
                  Feedback
                </p>
                <p 
                  class="text-sm line-clamp-2"
                  :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
                >
                  {{ getFieldValue(qa, 'feedback') }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div 
      v-if="Object.keys(groupedQAs).length === 0" 
      class="rounded-lg shadow-xl border p-12 text-center"
      :class="isDarkMode 
        ? 'bg-neutral-900 border-transparent' 
        : 'bg-white border-transparent'"
    >
      <i-mdi-clipboard-check-outline 
        class="w-16 h-16 mx-auto mb-4"
        :class="isDarkMode ? 'text-gray-600' : 'text-gray-400'"
      />
      <p 
        :class="isDarkMode ? 'text-gray-500' : 'text-gray-500'"
      >
        No QA records found
      </p>
    </div>
  </div>
</template>

<script setup>
import { computed, inject } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const props = defineProps({
  qas: {
    type: Array,
    default: () => []
  },
  qas_k: {
    type: Object,
    default: () => ({})
  }
})

// Inject theme
const isDarkMode = inject('isDarkMode')

// Helper to get field value from array
const getFieldValue = (qa, fieldName) => {
  const index = props.qas_k[fieldName]?.[0]
  return index !== undefined ? qa[index] : ''
}

// Group QAs by date
const groupedQAs = computed(() => {
  const groups = {}
  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(today.getDate() - 1)

  props.qas.forEach(qa => {
    const timestamp = getFieldValue(qa, 'created_on')
    if (!timestamp || timestamp === '0') return

    const date = new Date(parseInt(timestamp) * 1000)
    let label

    if (date.toDateString() === today.toDateString()) {
      label = 'Today'
    } else if (date.toDateString() === yesterday.toDateString()) {
      label = 'Yesterday'
    } else {
      label = date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    }

    if (!groups[label]) groups[label] = []
    groups[label].push(qa)
  })

  return groups
})

// Calculate overall score
const calculateScore = (qa) => {
  const fields = [
    'opening_phrase', 'non_interrupting', 'empathy', 'paraphrasing',
    'courteous', 'grammar', 'nonhesitant', 'educative',
    'procedure_adherance', 'extra_mile_willingness', 'consults',
    'follows_up_on_case_updates', 'accuracy', 'confirms_client_satisfaction',
    'notifies_hold', 'updates_hold', 'call_closing_coutesy'
  ]

  let totalPoints = 0
  let maxPoints = fields.length

  fields.forEach(field => {
    const value = getFieldValue(qa, field)
    if (value === '2') totalPoints += 1
    else if (value === '1') totalPoints += 0.5
  })

  return maxPoints > 0 ? Math.round((totalPoints / maxPoints) * 100) : 0
}

// Get rating color class
const getRatingColor = (value) => {
  if (value === '2') {
    return isDarkMode.value ? 'text-green-400' : 'text-green-700'
  }
  if (value === '1') {
    return isDarkMode.value ? 'text-yellow-400' : 'text-yellow-700'
  }
  return isDarkMode.value ? 'text-red-400' : 'text-red-700'
}

// Get rating text
const getRatingText = (value) => {
  if (value === '2') return 'Excellent'
  if (value === '1') return 'Average'
  if (value === '0') return 'Poor'
  return 'N/A'
}

// Format unix timestamp to readable date
const formatTimestamp = (timestamp) => {
  if (!timestamp || timestamp === '0') return '-'
  const date = new Date(parseInt(timestamp) * 1000)
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// View QA details
const viewQADetails = (qa) => {
  const qaId = getFieldValue(qa, 'id')
  console.log('Viewing QA details for:', qaId)
  // Navigate to QA details page if needed
  // router.push({ name: 'QADetails', params: { id: qaId } })
}
</script>
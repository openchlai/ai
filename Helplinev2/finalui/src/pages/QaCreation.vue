<template>
  <div 
    class="min-h-screen py-6 px-4"
    :class="isDarkMode ? 'bg-gray-900' : 'bg-gray-50'"
  >
    <div class="max-w-[1800px] mx-auto flex flex-col gap-6">
      <!-- Page Header -->
      <div 
        class="rounded-lg shadow-xl p-6 border-l-4"
        :class="isDarkMode 
          ? 'bg-gray-800 border-amber-500' 
          : 'bg-white border-amber-600'"
      >
        <div class="flex items-center gap-4 mb-2">
          <button 
            @click="goBack"
            class="p-2 rounded-lg transition-all"
            :class="isDarkMode 
              ? 'hover:bg-blue-900/30' 
              : 'hover:bg-amber-100'"
          >
            <i-mdi-arrow-left 
              class="w-6 h-6"
              :class="isDarkMode ? 'text-amber-500' : 'text-amber-700'"
            />
          </button>
          <div>
            <h1 
              class="text-3xl font-bold flex items-center gap-3"
              :class="isDarkMode ? 'text-amber-500' : 'text-amber-700'"
            >
              <i-mdi-clipboard-check class="w-8 h-8" />
              Quality Assurance Evaluation
            </h1>
            <p 
              class="text-sm mt-1"
              :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
            >
              Review and evaluate call quality based on established criteria
            </p>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="flex flex-col items-center gap-4">
          <div 
            class="animate-spin rounded-full h-12 w-12 border-4"
            :class="isDarkMode 
              ? 'border-blue-900/30 border-t-blue-500' 
              : 'border-amber-200 border-t-amber-700'"
          ></div>
          <div :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'">
            Loading call data...
          </div>
        </div>
      </div>

      <!-- Error State -->
      <div 
        v-else-if="error" 
        class="rounded-lg p-6 border"
        :class="isDarkMode 
          ? 'bg-red-600/20 border-red-600/50 text-red-400' 
          : 'bg-red-50 border-red-300 text-red-700'"
      >
        <p>{{ error }}</p>
      </div>

      <!-- Main Content -->
      <div v-else class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <!-- Left Column: Call Details -->
        <div class="lg:col-span-4 xl:col-span-3">
          <CallDetailsCard :call-data="callData" />
        </div>

        <!-- Right Column -->
        <div class="lg:col-span-8 xl:col-span-9 flex flex-col gap-6">
          <!-- Section Navigation -->
          <QASectionNav 
            :sections="sectionsWithScores"
            :active-section="activeSection"
            @change-section="changeSection"
          />

          <!-- Active Form Section -->
          <CreateQA 
            ref="createQARef"
            :active-section="activeSection"
            :chan-uniqueid="callData.chanUniqueid"
            @qa-submitted="handleQASubmitted"
            @next-section="nextSection"
            @previous-section="previousSection"
            @section-scores-updated="updateSectionScores"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, inject } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useCallStore } from '@/stores/calls'
import CallDetailsCard from '@/components/qa-create/CallDetailsCard.vue'
import QASectionNav from '@/components/qa-create/QASectionNav.vue'
import CreateQA from '@/components/qa-create/CreateQA.vue'

const isDarkMode = inject('isDarkMode')

const router = useRouter()
const route = useRoute()
const callStore = useCallStore()
const createQARef = ref(null)

const loading = ref(false)
const error = ref(null)
const activeSection = ref(0)
const sectionScores = ref([0, 0, 0, 0, 0, 0, 0])

const chanUniqueid = route.params.chanUniqueid || route.query.chanUniqueid || '1761627874.2'

const callData = reactive({
  chanUniqueid: chanUniqueid,
  callDateTime: '',
  reporter: '',
  direction: '',
  phone: '',
  extension: '',
  waitTime: '',
  hangupStatus: '',
  talkTime: ''
})

onMounted(async () => {
  if (!chanUniqueid) {
    error.value = 'No call ID provided'
    return
  }

  loading.value = true
  error.value = null

  try {
    await callStore.listCalls()
    const call = callStore.getCallById(chanUniqueid)

    if (!call) {
      error.value = 'Call not found'
      return
    }

    const k = callStore.calls_k

    const chanTsIndex = parseInt(k.chan_ts[0])
    const usrNameIndex = parseInt(k.usr_name[0])
    const vectorIndex = parseInt(k.vector[0])
    const phoneIndex = parseInt(k.phone[0])
    const usrIndex = parseInt(k.usr[0])
    const waitTimeTotIndex = parseInt(k.wait_time_tot[0])
    const hangupStatusIndex = parseInt(k.hangup_status[0])
    const talkTimeIndex = parseInt(k.talk_time[0])

    callData.chanUniqueid = chanUniqueid
    callData.callDateTime = call[chanTsIndex] || ''
    callData.reporter = call[usrNameIndex] || ''
    callData.direction = call[vectorIndex] || ''
    callData.phone = call[phoneIndex] || ''
    callData.extension = call[usrIndex] || ''
    callData.waitTime = formatTime(call[waitTimeTotIndex]) || ''
    callData.hangupStatus = call[hangupStatusIndex] || ''
    callData.talkTime = formatTime(call[talkTimeIndex]) || ''

  } catch (err) {
    console.error('Failed to load call data:', err)
    error.value = 'Failed to load call data. Please try again.'
  } finally {
    loading.value = false
  }
})

const formatTime = (seconds) => {
  if (!seconds || seconds === '0') return '00:00'
  
  const sec = parseInt(seconds)
  const hours = Math.floor(sec / 3600)
  const minutes = Math.floor((sec % 3600) / 60)
  const secs = sec % 60

  if (hours > 0) {
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

const sectionsWithScores = computed(() => [
  { name: 'Opening Phrase', score: sectionScores.value[0] },
  { name: 'Listening Skills', score: sectionScores.value[1] },
  { name: 'Communication', score: sectionScores.value[2] },
  { name: 'Proactive', score: sectionScores.value[3] },
  { name: 'Resolution', score: sectionScores.value[4] },
  { name: 'Hold Management', score: sectionScores.value[5] },
  { name: 'Call Closing', score: sectionScores.value[6] },
  { name: 'Submit', score: 0 }
])

const changeSection = (index) => {
  activeSection.value = index
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const nextSection = () => {
  if (activeSection.value < sectionsWithScores.value.length - 1) {
    activeSection.value++
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

const previousSection = () => {
  if (activeSection.value > 0) {
    activeSection.value--
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

const updateSectionScores = (scores) => {
  sectionScores.value = scores
}

const handleQASubmitted = (result) => {
  console.log('QA Submitted:', result)
  
  if (result.success) {
    setTimeout(() => {
      router.push('/qa')
    }, 2000)
  }
}

const goBack = () => {
  router.push('/qa')
}
</script>
<template>
  <div 
    class="rounded-lg shadow-xl p-6 border"
    :class="isDarkMode 
      ? 'bg-gray-800 border-transparent' 
      : 'bg-white border-transparent'"
  >
    <form @submit.prevent="handleSubmit">
      <!-- Active Section Display -->
      <div v-if="activeSection < qaData.sections.length" class="animate-fadeIn">
        <QASection :title="qaData.sections[activeSection].title">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-4">
            <QARatingField
              v-for="field in qaData.sections[activeSection].fields"
              :key="field.key"
              v-model="formData[field.key]"
              :label="field.label"
              :name="field.key"
              required
            />
          </div>

          <!-- Comment field -->
          <QACommentField
            v-if="qaData.sections[activeSection].commentKey"
            v-model="formData[qaData.sections[activeSection].commentKey]"
            :label="qaData.sections[activeSection].commentLabel"
          />
        </QASection>
      </div>

      <!-- Submit Section -->
      <div v-else class="animate-fadeIn">
        <QASection title="Overall Feedback & Submit">
          <QACommentField
            v-model="formData.feedback"
            label="Overall Feedback *"
            :rows="6"
            placeholder="Enter comprehensive feedback about the call quality..."
            required
          />
        </QASection>
      </div>

      <!-- Navigation Buttons -->
      <div 
        class="flex items-center justify-between pt-6 border-t mt-6"
        :class="isDarkMode ? 'border-transparent' : 'border-transparent'"
      >
        <button
          v-if="activeSection > 0"
          type="button"
          @click="previousSection"
          class="px-6 py-3 rounded-lg font-semibold transition-all flex items-center gap-2 border"
          :class="isDarkMode 
            ? 'bg-gray-700 text-gray-300 border-transparent hover:bg-gray-600' 
            : 'bg-white text-gray-700 border-transparent hover:border-amber-600 hover:text-amber-700'"
        >
          <i-mdi-chevron-left class="w-5 h-5" />
          Previous
        </button>
        
        <div v-else></div>

        <button
          v-if="activeSection < qaData.sections.length"
          type="button"
          @click="nextSection"
          class="px-6 py-3 text-white rounded-lg font-semibold transition-all shadow-lg flex items-center gap-2"
          :class="isDarkMode 
            ? 'bg-amber-600 hover:bg-amber-700' 
            : 'bg-amber-700 hover:bg-amber-800'"
        >
          Next
          <i-mdi-chevron-right class="w-5 h-5" />
        </button>
        
        <button
          v-else
          type="submit"
          :disabled="qaStore.loading || !isFormValid"
          class="px-8 py-3 text-white rounded-lg font-bold transition-all shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          :class="isDarkMode 
            ? 'bg-green-600 hover:bg-green-700' 
            : 'bg-green-600 hover:bg-green-700'"
        >
          <span v-if="qaStore.loading" class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
          <i-mdi-check v-else class="w-5 h-5" />
          <span>{{ qaStore.loading ? 'Submitting...' : 'Submit QA' }}</span>
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, inject } from 'vue'
import { toast } from 'vue-sonner'
import { useQAStore } from '@/stores/qas'
import QASection from './QASection.vue'
import QARatingField from './QARatingField.vue'
import QACommentField from './QACommentField.vue'

const isDarkMode = inject('isDarkMode')

const props = defineProps({
  activeSection: {
    type: Number,
    default: 0
  },
  chanUniqueid: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['qa-submitted', 'next-section', 'previous-section', 'section-scores-updated'])

const qaStore = useQAStore()

const qaData = reactive({
  sections: [
    {
      title: 'Opening Phrase',
      fields: [{ key: 'opening_phrase', label: 'Opening Phrase Rating' }],
      commentKey: 'opening_phrase_comments',
      commentLabel: 'Opening Phrase Comments'
    },
    {
      title: 'Listening Skills',
      fields: [
        { key: 'non_interrupting', label: 'Non Interrupting' },
        { key: 'empathy', label: 'Empathy' },
        { key: 'paraphrasing', label: 'Paraphrasing' }
      ],
      commentKey: 'listening_comments',
      commentLabel: 'Listening Comments'
    },
    {
      title: 'Communication Skills',
      fields: [
        { key: 'courteous', label: 'Courteous' },
        { key: 'grammar', label: 'Grammar' },
        { key: 'nonhesitant', label: 'Non Hesitant' },
        { key: 'educative', label: 'Educative' }
      ],
      commentKey: null,
      commentLabel: null
    },
    {
      title: 'Proactive Approach',
      fields: [
        { key: 'procedure_adherance', label: 'Procedure Adherence' },
        { key: 'extra_mile_willingness', label: 'Extra Mile Willingness' },
        { key: 'consults', label: 'Consults' },
        { key: 'follows_up_on_case_updates', label: 'Follows Up On Case Updates' }
      ],
      commentKey: 'pro_active_comments',
      commentLabel: 'Proactive Comments'
    },
    {
      title: 'Resolution',
      fields: [
        { key: 'accuracy', label: 'Accuracy' },
        { key: 'confirms_client_satisfaction', label: 'Confirms Client Satisfaction' }
      ],
      commentKey: 'resolution_comments',
      commentLabel: 'Resolution Comments'
    },
    {
      title: 'Hold Management',
      fields: [
        { key: 'notifies_hold', label: 'Notifies Hold' },
        { key: 'updates_hold', label: 'Updates Hold' }
      ],
      commentKey: 'hold_comments',
      commentLabel: 'Hold Comments'
    },
    {
      title: 'Call Closing',
      fields: [{ key: 'call_closing_coutesy', label: 'Call Closing Courtesy' }],
      commentKey: 'call_closing_comments',
      commentLabel: 'Call Closing Comments'
    }
  ]
})

const formData = reactive({
  chan_uniqueid: '',
  opening_phrase: '',
  opening_phrase_comments: '',
  non_interrupting: '',
  empathy: '',
  paraphrasing: '',
  listening_comments: '',
  courteous: '',
  grammar: '',
  nonhesitant: '',
  educative: '',
  procedure_adherance: '',
  extra_mile_willingness: '',
  consults: '',
  follows_up_on_case_updates: '',
  pro_active_comments: '',
  accuracy: '',
  confirms_client_satisfaction: '',
  resolution_comments: '',
  notifies_hold: '',
  updates_hold: '',
  hold_comments: '',
  call_closing_coutesy: '',
  call_closing_comments: '',
  feedback: ''
})

// Initialize chan_uniqueid on mount
onMounted(() => {
  console.log('CreateQA mounted with chanUniqueid:', props.chanUniqueid)
  formData.chan_uniqueid = props.chanUniqueid
})

// Watch for chanUniqueid changes
watch(() => props.chanUniqueid, (newValue) => {
  console.log('chanUniqueid prop changed to:', newValue)
  formData.chan_uniqueid = newValue
}, { immediate: true })

const calculateSectionScore = (sectionIndex) => {
  const section = qaData.sections[sectionIndex]
  const fields = section.fields
  
  let totalPoints = 0
  let maxPoints = fields.length
  
  fields.forEach(field => {
    const value = formData[field.key]
    if (value === '2') totalPoints += 1
    else if (value === '1') totalPoints += 0.5
  })
  
  return maxPoints > 0 ? Math.round((totalPoints / maxPoints) * 100) : 0
}

const sectionScores = computed(() => {
  return qaData.sections.map((_, index) => calculateSectionScore(index))
})

watch(sectionScores, (newScores) => {
  emit('section-scores-updated', newScores)
}, { deep: true })

const isFormValid = computed(() => {
  const ratingFields = qaData.sections.flatMap(s => s.fields.map(f => f.key))
  const allRatingsFilled = ratingFields.every(key => formData[key] !== '')
  const feedbackFilled = formData.feedback.trim() !== ''
  const hasCallId = formData.chan_uniqueid && formData.chan_uniqueid.trim() !== ''
  
  return allRatingsFilled && feedbackFilled && hasCallId
})

const nextSection = () => {
  emit('next-section')
}

const previousSection = () => {
  emit('previous-section')
}

const handleSubmit = async () => {
  // Validate chan_uniqueid before submission
  if (!formData.chan_uniqueid || formData.chan_uniqueid.trim() === '') {
    toast.error('Call ID is missing. Please go back and try again.')
    console.error('chan_uniqueid is missing:', formData.chan_uniqueid)
    return
  }

  if (!isFormValid.value) {
    toast.error('Please fill in all required fields (all ratings and feedback)')
    return
  }

  try {
    console.log('Submitting QA with payload:', formData)
    console.log('chan_uniqueid value:', formData.chan_uniqueid)
    
    // Create a clean payload
    const payload = {
      chan_uniqueid: formData.chan_uniqueid,
      opening_phrase: formData.opening_phrase,
      opening_phrase_comments: formData.opening_phrase_comments,
      non_interrupting: formData.non_interrupting,
      empathy: formData.empathy,
      paraphrasing: formData.paraphrasing,
      listening_comments: formData.listening_comments,
      courteous: formData.courteous,
      grammar: formData.grammar,
      nonhesitant: formData.nonhesitant,
      educative: formData.educative,
      procedure_adherance: formData.procedure_adherance,
      extra_mile_willingness: formData.extra_mile_willingness,
      consults: formData.consults,
      follows_up_on_case_updates: formData.follows_up_on_case_updates,
      pro_active_comments: formData.pro_active_comments,
      accuracy: formData.accuracy,
      confirms_client_satisfaction: formData.confirms_client_satisfaction,
      resolution_comments: formData.resolution_comments,
      notifies_hold: formData.notifies_hold,
      updates_hold: formData.updates_hold,
      hold_comments: formData.hold_comments,
      call_closing_coutesy: formData.call_closing_coutesy,
      call_closing_comments: formData.call_closing_comments,
      feedback: formData.feedback
    }
    
    const response = await qaStore.createQA(payload)
    
    console.log('QA created successfully:', response)
    toast.success('QA submitted successfully!')
    
    emit('qa-submitted', { success: true, data: response })
    
  } catch (error) {
    console.error('Failed to create QA:', error)
    toast.error('Failed to submit QA. Please try again.')
    emit('qa-submitted', { success: false, error })
  }
}

defineExpose({
  sectionScores
})
</script>

<style scoped>
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fadeIn {
  animation: fadeIn 0.3s ease-out;
}
</style>
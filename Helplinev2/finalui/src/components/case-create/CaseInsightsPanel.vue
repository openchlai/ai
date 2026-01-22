<template>
  <div class="space-y-6">
    <!-- AI Title Badge (Shown when expanded) -->
    <div 
      class="rounded-xl shadow-lg border p-5 transition-all duration-200"
      :class="isDarkMode ? 'bg-neutral-900 border-transparent' : 'bg-white border-transparent'"
    >
      <div class="flex items-center gap-3">
        <div class="w-8 h-8 rounded-lg flex items-center justify-center shrink-0 transition-colors"
          :class="isDarkMode ? 'bg-amber-500/10 text-amber-500' : 'bg-amber-600/10 text-amber-600'"
        >
          <i-mdi-robot class="w-5 h-5" />
        </div>
        <div>
          <h3 
            class="text-sm font-bold leading-none mb-1"
            :class="isDarkMode ? 'text-amber-500' : 'text-amber-600'"
          >
            Insights Active
          </h3>
          <p class="text-[10px] font-medium text-gray-500 leading-none">
            Processing real-time analytics
          </p>
        </div>
      </div>
    </div>

    <!-- Audio Upload Section - Shows when AI is enabled -->
    <div 
      v-if="aiEnabled"
      class="rounded-xl shadow-lg border p-6 transition-all duration-200"
      :class="isDarkMode ? 'bg-neutral-900 border-transparent' : 'bg-white border-transparent'"
    >
      <h3 
        class="text-sm font-bold mb-4"
        :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
      >
        Call Recording
      </h3>

      <!-- Upload State -->
      <div 
        v-if="!audioFile"
        class="border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all duration-300"
        :class="isDarkMode 
          ? 'border-neutral-800 hover:border-amber-500/50 hover:bg-neutral-800/50' 
          : 'border-gray-100 hover:border-amber-600/50 hover:bg-gray-50'"
        @click="triggerFileInput"
        @dragover.prevent
        @drop.prevent="handleDrop"
      >
        <input 
          type="file" 
          ref="fileInput" 
          class="hidden" 
          accept="audio/*"
          @change="handleFileSelect"
        />
        <div class="flex flex-col items-center gap-1">
          <p class="text-sm font-bold" :class="isDarkMode ? 'text-white' : 'text-gray-900'">
            Upload Audio
          </p>
          <p class="text-xs text-gray-500 font-medium">
            Drag files or click to browse
          </p>
        </div>
      </div>

      <!-- Player State -->
      <div v-else class="space-y-4">
        <div 
          class="flex items-center gap-4 p-4 rounded-xl border"
          :class="isDarkMode ? 'bg-black/40 border-neutral-800' : 'bg-gray-50 border-gray-100'"
        >
          <div class="flex-1 min-w-0">
            <p 
              class="text-sm font-bold truncate mb-0.5"
              :class="isDarkMode ? 'text-white' : 'text-gray-900'"
            >
              {{ audioFile.name }}
            </p>
            <p class="text-[11px] font-medium text-gray-500">
              {{ formatFileSize(audioFile.size) }}
            </p>
          </div>
          <button 
            @click="removeAudio"
            class="px-3 py-1.5 text-[11px] font-bold border border-red-500/30 text-red-500 rounded-lg hover:bg-red-500 hover:text-white transition-all shadow-sm"
          >
            Remove
          </button>
        </div>
        
        <audio controls class="w-full h-8 opacity-90 custom-audio-player" :src="audioUrl"></audio>
      </div>
    </div>

    <!-- Results Section (Insights & Feedback) -->
    <div 
      v-if="aiEnabled && audioFile"
      class="rounded-xl shadow-lg border overflow-hidden transition-all duration-500 animate-in fade-in slide-in-from-bottom-8"
      :class="isDarkMode ? 'bg-neutral-900 border-transparent' : 'bg-white border-transparent'"
    >
      <!-- Mode Selector Tabs (Segmented Control Layout) -->
      <div class="p-1 px-5 pt-5">
        <div class="flex p-1 rounded-xl" :class="isDarkMode ? 'bg-black/40' : 'bg-gray-100/50'">
          <button 
            @click="activeMode = 'insights'"
            class="flex-1 py-2 text-sm font-bold transition-all duration-300 rounded-lg"
            :class="activeMode === 'insights' 
              ? (isDarkMode ? 'bg-amber-600 text-white shadow-lg shadow-amber-600/20' : 'bg-amber-700 text-white shadow-lg shadow-amber-900/40')
              : (isDarkMode ? 'text-gray-400 hover:text-gray-200' : 'text-gray-500 hover:text-gray-700')"
          >
            Insights
          </button>
          <button 
            @click="activeMode = 'feedback'"
            class="flex-1 py-2 text-sm font-bold transition-all duration-300 rounded-lg"
            :class="activeMode === 'feedback' 
              ? (isDarkMode ? 'bg-amber-600 text-white shadow-lg shadow-amber-600/20' : 'bg-amber-700 text-white shadow-lg shadow-amber-900/40')
              : (isDarkMode ? 'text-gray-400 hover:text-gray-200' : 'text-gray-500 hover:text-gray-700')"
          >
            Feedback
          </button>
        </div>
      </div>

      <!-- Content Area -->
      <div class="p-6">
        <!-- AI Insights View -->
        <div v-if="activeMode === 'insights'" class="space-y-8 animate-in fade-in transition-all duration-300">
          
          <!-- 1. Case Summary -->
          <div>
            <div class="flex items-center justify-between mb-4">
              <h4 
                class="text-[11px] font-bold uppercase tracking-widest flex items-center gap-2"
                :class="isDarkMode ? 'text-amber-500/80' : 'text-amber-600/80'"
              >
                Case Summary
              </h4>
              <div class="px-2 py-0.5 rounded text-[9px] font-bold"
                :class="isDarkMode ? 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20' : 'bg-emerald-50 text-emerald-700 border border-emerald-200'">
                AI GENERATED
              </div>
            </div>
            <p 
              class="text-xs leading-relaxed font-semibold italic"
              :class="isDarkMode ? 'text-white' : 'text-gray-900'"
            >
              "{{ mockData.case_summary }}"
            </p>
          </div>

          <!-- 2. Named Entities -->
          <div class="space-y-3">
            <h4 class="text-[11px] font-bold uppercase tracking-widest" :class="isDarkMode ? 'text-amber-500/80' : 'text-amber-600/80'">Named Entities</h4>
            <div class="grid grid-cols-2 gap-3">
              <div v-for="(entities, type) in mockData.named_entities" :key="type" 
                v-show="entities.length > 0"
                class="p-3 rounded-xl border" 
                :class="isDarkMode ? 'bg-black/20 border-neutral-800' : 'bg-gray-50 border-gray-100'"
              >
                <span class="text-[9px] font-bold text-gray-500 uppercase block mb-2 tracking-tighter">{{ type }}</span>
                <div class="flex flex-wrap gap-1.5">
                  <span v-for="item in entities" :key="item"
                    class="px-2 py-1 rounded-md text-[10px] font-bold"
                    :class="isDarkMode ? 'bg-neutral-800 text-white border border-neutral-700' : 'bg-white text-gray-800 border border-gray-200 shadow-sm'"
                  >
                    {{ item }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- 3. Classification -->
          <div class="p-4 rounded-xl border border-dashed" :class="isDarkMode ? 'border-neutral-800 bg-neutral-900/40' : 'border-gray-200 bg-amber-50/10'">
            <h4 class="text-[11px] font-bold uppercase tracking-widest mb-4" :class="isDarkMode ? 'text-amber-500/80' : 'text-amber-600/80'">Classification</h4>
            <div class="grid grid-cols-2 gap-6">
              <div class="space-y-4">
                <div>
                  <span class="text-[9px] font-bold text-gray-500 uppercase block mb-1">Category</span>
                  <div class="flex flex-wrap gap-1.5">
                    <span v-for="cat in mockData.classification.category" :key="cat"
                      class="text-xs font-bold"
                      :class="isDarkMode ? 'text-white' : 'text-gray-900'"
                    >
                      {{ cat }}
                    </span>
                  </div>
                </div>
                <div>
                  <span class="text-[9px] font-bold text-gray-500 uppercase block mb-1">Priority Level</span>
                  <span 
                    class="px-2 py-0.5 rounded text-[10px] font-black uppercase tracking-tighter"
                    :class="mockData.classification.priority_level === 'high' 
                      ? 'bg-red-500 text-white shadow-lg shadow-red-500/20' 
                      : 'bg-amber-500 text-black'"
                  >
                    {{ mockData.classification.priority_level }}
                  </span>
                </div>
              </div>
              <div>
                <span class="text-[9px] font-bold text-gray-500 uppercase block mb-2">Interventions Required</span>
                <ul class="space-y-1.5">
                  <li v-for="int in mockData.classification.interventions_needed" :key="int" class="flex items-center gap-2">
                    <div class="w-1 h-1 rounded-full" :class="isDarkMode ? 'bg-amber-500' : 'bg-amber-600'"></div>
                    <span class="text-[10px] font-semibold" :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'">{{ int }}</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <!-- 4. Case Management -->
          <div class="space-y-4">
            <h4 class="text-[11px] font-bold uppercase tracking-widest" :class="isDarkMode ? 'text-amber-500/80' : 'text-amber-600/80'">Case Management</h4>
            <div class="space-y-4">
              <div v-for="(proto, key) in mockData.case_management" :key="key" 
                class="p-4 rounded-xl border relative overflow-hidden group transition-all duration-300 hover:shadow-lg"
                :class="isDarkMode ? 'bg-black/20 border-neutral-800 hover:border-amber-500/30' : 'bg-white border-gray-100 shadow-sm hover:border-amber-600/30'"
              >
                <!-- Section Icon Background -->
                <div class="absolute -right-2 -top-2 opacity-[0.03] grayscale pointer-events-none group-hover:opacity-10 transition-all duration-500">
                  <i-mdi-shield-check v-if="key.includes('safety')" class="w-20 h-20" />
                  <i-mdi-account-heart v-if="key.includes('psychosocial')" class="w-20 h-20" />
                  <i-mdi-gavel v-if="key.includes('legal')" class="w-20 h-20" />
                  <i-mdi-medical-bag v-if="key.includes('medical')" class="w-20 h-20" />
                </div>

                <div class="flex items-center gap-2 mb-3">
                  <div class="w-6 h-6 rounded-lg flex items-center justify-center shrink-0 transition-colors"
                    :class="isDarkMode ? 'bg-amber-500/10 text-amber-500' : 'bg-amber-600/10 text-amber-600'"
                  >
                    <i-mdi-shield-check v-if="key.includes('safety')" class="w-3.5 h-3.5" />
                    <i-mdi-account-heart v-if="key.includes('psychosocial')" class="w-3.5 h-3.5" />
                    <i-mdi-gavel v-if="key.includes('legal')" class="w-3.5 h-3.5" />
                    <i-mdi-medical-bag v-if="key.includes('medical')" class="w-3.5 h-3.5" />
                  </div>
                  <span class="text-[11px] font-bold uppercase tracking-tight" :class="isDarkMode ? 'text-gray-200' : 'text-gray-900'">
                    {{ key.replace('_', ' ') }}
                  </span>
                </div>

                <div class="grid grid-cols-1 gap-3">
                  <div v-for="(actions, actionType) in proto" :key="actionType" class="space-y-1">
                    <span class="text-[8px] font-bold text-gray-500 uppercase tracking-tighter">{{ actionType.replace('_', ' ') }}</span>
                    <div class="flex flex-col gap-1.5">
                      <div v-for="action in actions" :key="action" class="text-[10px] font-medium leading-relaxed" :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'">
                        • {{ action }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 5. Risk Assessment -->
          <div class="space-y-3">
            <h4 class="text-[11px] font-bold uppercase tracking-widest" :class="isDarkMode ? 'text-amber-500/80' : 'text-amber-600/80'">Risk Assessment</h4>
            <div class="grid grid-cols-1 gap-3">
              <div v-for="(factors, type) in mockData.risk_assessment" :key="type" 
                class="p-4 rounded-xl border flex flex-col gap-2"
                :class="[
                  isDarkMode ? 'bg-black/20 border-neutral-800' : 'bg-white border-gray-100 shadow-sm',
                  type === 'red_flags' ? (isDarkMode ? 'border-red-500/20 bg-red-500/5' : 'border-red-100 bg-red-50/30') : ''
                ]"
              >
                <div class="flex items-center gap-2">
                  <i-mdi-alert-circle v-if="type === 'red_flags'" class="w-3.5 h-3.5 text-red-500" />
                  <i-mdi-barrier v-if="type === 'potential_barriers'" class="w-3.5 h-3.5 text-orange-500" />
                  <i-mdi-shield-star v-if="type === 'protective_factors'" class="w-3.5 h-3.5 text-emerald-500" />
                  <span class="text-[9px] font-bold text-gray-500 uppercase tracking-tighter">{{ type.replace('_', ' ') }}</span>
                </div>
                <div class="space-y-1.5">
                  <div v-for="factor in factors" :key="factor" class="text-[10px] font-semibold leading-relaxed" :class="isDarkMode ? 'text-gray-300' : 'text-gray-800'">
                    {{ factor }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 6. Cultural Considerations -->
          <div v-if="mockData.cultural_considerations.length > 0" class="space-y-3">
            <h4 class="text-[11px] font-bold uppercase tracking-widest" :class="isDarkMode ? 'text-amber-500/80' : 'text-amber-600/80'">Cultural Considerations</h4>
            <div class="p-4 rounded-xl border border-dashed text-center" :class="isDarkMode ? 'bg-black/20 border-neutral-800 text-gray-400' : 'bg-gray-50 border-gray-200 text-gray-500'">
              <div v-for="cult in mockData.cultural_considerations" :key="cult" class="text-xs font-medium">
                {{ cult }}
              </div>
            </div>
          </div>
          <div v-else>
             <h4 class="text-[11px] font-bold uppercase tracking-widest mb-2" :class="isDarkMode ? 'text-amber-500/80' : 'text-amber-600/80'">Cultural Considerations</h4>
             <div class="p-4 rounded-xl border border-dashed text-center italic text-[10px]" :class="isDarkMode ? 'bg-black/10 border-neutral-800 text-gray-600' : 'bg-gray-50 border-gray-200 text-gray-400'">
                No specific cultural considerations identified for this case.
             </div>
          </div>

        </div>

        <!-- AI Feedback View (Simplified/Updated to maintain audit fields) -->
        <div v-if="activeMode === 'feedback'" class="space-y-6 animate-in fade-in transition-all duration-300">
          <!-- Rating Section -->
          <div class="p-6 rounded-2xl border border-dashed text-center">
            <h4 class="text-sm font-bold mb-4" :class="isDarkMode ? 'text-white' : 'text-gray-900'">Review AI Accuracy</h4>
            
            <!-- Rating Dots -->
            <div class="flex items-center justify-center gap-3 mb-6">
              <button 
                v-for="star in 5" 
                :key="star"
                @click="rating = star"
                @mouseenter="hoverRating = star"
                @mouseleave="hoverRating = 0"
                class="transition-all duration-200 transform hover:scale-110 focus:outline-none"
              >
                <div 
                  class="w-8 h-8 rounded-full border-2 flex items-center justify-center text-xs font-bold transition-all duration-300"
                  :class="(hoverRating || rating) >= star 
                    ? (isDarkMode ? 'bg-amber-600 border-amber-600 text-white shadow-lg shadow-amber-600/20' : 'bg-amber-700 border-amber-700 text-white shadow-lg shadow-amber-900/30') 
                    : (isDarkMode ? 'border-neutral-700 text-neutral-500' : 'border-gray-200 text-gray-300')"
                >
                  {{ star }}
                </div>
              </button>
            </div>

            <!-- Conditional Feedback Input & Actions -->
            <div v-if="rating > 0" class="space-y-4 animate-in fade-in zoom-in-95 duration-300">
              <textarea 
                v-if="rating < 4"
                v-model="feedbackComment"
                rows="2"
                placeholder="What was incorrect?"
                class="w-full rounded-xl p-3 text-xs font-medium focus:outline-none focus:ring-1 focus:ring-amber-500/50 transition-all border"
                :class="isDarkMode ? 'bg-black border-neutral-800 text-white' : 'bg-white border-gray-100 text-gray-900 shadow-sm'"
              ></textarea>
              
              <div v-if="!feedbackSubmitted" class="flex justify-center">
                <button 
                  @click="submitFeedback"
                  :disabled="isSubmittingFeedback || (rating < 4 && !feedbackComment.trim())"
                  class="px-6 py-2 text-white text-xs font-bold rounded-xl transition-all flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
                  :class="isDarkMode ? 'bg-amber-600 hover:bg-amber-500 shadow-amber-600/20' : 'bg-amber-700 hover:bg-amber-800 shadow-amber-900/40'"
                >
                  <span v-if="isSubmittingFeedback" class="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                  {{ rating >= 4 ? 'Confirm Accuracy' : 'Submit Feedback' }}
                </button>
              </div>

              <div v-else class="text-amber-500 text-xs font-bold animate-in zoom-in-95 flex items-center justify-center gap-2">
                <i-mdi-check-circle class="w-4 h-4" />
                Feedback Recorded
              </div>
            </div>
          </div>

          <!-- Audit Trail (Fixed data for system trace) -->
          <div class="pt-6 border-t border-dashed" :class="isDarkMode ? 'border-neutral-800' : 'border-gray-100'">
            <div class="grid grid-cols-2 gap-4 text-[8px] font-bold uppercase tracking-wider">
              <div class="space-y-1">
                <span class="text-gray-400 block mb-1">Engines Involved</span>
                <p :class="isDarkMode ? 'text-gray-300' : 'text-gray-600'" class="leading-relaxed normal-case font-medium text-[9px]">
                  whisper, translator, ner, classifier, summarizer, case-manager-v2
                </p>
                <div class="flex gap-2 pt-1">
                  <span class="px-1.5 py-0.5 rounded border border-amber-500/20 text-amber-500 font-bold tracking-tight">COMPLETED</span>
                  <span class="px-1.5 py-0.5 rounded border border-gray-500/20 text-gray-500 font-bold tracking-tight">DEV-SITE-001</span>
                </div>
              </div>
              <div class="text-right space-y-1">
                <span class="text-gray-400 block mb-1">System Trace</span>
                <p :class="isDarkMode ? 'text-gray-300' : 'text-gray-600'" class="font-medium tracking-tighter text-[9px]">
                  #1768420272.211
                </p>
                <p class="text-gray-500">
                  GATEWAY / INBOUND
                </p>
                <p class="text-[7px] text-gray-400 mt-2 font-medium">
                  Processing: 2.1s • {{ new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, inject } from 'vue'

const props = defineProps({
  aiEnabled: {
    type: Boolean,
    default: false
  }
})

const isDarkMode = inject('isDarkMode')
const activeMode = ref('insights')
const rating = ref(0)
const hoverRating = ref(0)
const feedbackComment = ref('')
const isSubmittingFeedback = ref(false)
const feedbackSubmitted = ref(false)

const submitFeedback = () => {
  if (isSubmittingFeedback.value) return
  
  isSubmittingFeedback.value = true
  
  // Simulate API call
  setTimeout(() => {
    isSubmittingFeedback.value = false
    feedbackSubmitted.value = true
    import('vue-sonner').then(({ toast }) => {
      toast.success('Thank you for your feedback!')
    })
  }, 800)
}

const fileInput = ref(null)
const audioFile = ref(null)
const audioUrl = ref(null)

const triggerFileInput = () => {
  fileInput.value.click()
}

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    processFile(file)
  }
}

const handleDrop = (event) => {
  const file = event.dataTransfer.files[0]
  if (file && file.type.startsWith('audio/')) {
    processFile(file)
  }
}

const processFile = (file) => {
  audioFile.value = file
  audioUrl.value = URL.createObjectURL(file)
}

const removeAudio = () => {
  audioFile.value = null
  audioUrl.value = null
  if (fileInput.value) fileInput.value.value = ''
  rating.value = 0
  feedbackComment.value = ''
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// Data from User Request - Domestic Violence Case study
const mockData = {
  "case_summary": "Repeated domestic violence reported by a caller against her partner over the past six months, with the most recent incident occurring last night at their residence in Kayole. The caller has two minor children and fears further harm if she reports to authorities.",
  "named_entities": {
    "persons": ["Caller", "Partner"],
    "organizations": [],
    "locations": ["Kayole"],
    "dates": ["Past six months", "Last night"],
    "contact_information": []
  },
  "classification": {
    "category": ["Domestic violence"],
    "interventions_needed": [
      "Safety planning",
      "Psychosocial support",
      "Legal protocols",
      "Medical protocols"
    ],
    "priority_level": "high"
  },
  "case_management": {
    "safety_planning": {
      "immediate_actions": [
        "Establish a safe location for the caller and children"
      ],
      "long_term_measures": [
        "Develop a safety plan, including contacting local authorities for protection"
      ]
    },
    "psychosocial_support": {
      "short_term": [
        "Provide emotional support and crisis intervention"
      ],
      "long_term": [
        "Refer the caller to counseling services for herself and children"
      ]
    },
    "legal_protocols": {
      "applicable_laws": [
        "Domestic Violence Act (Kenya)"
      ],
      "required_documents": [
        "Police report"
      ],
      "authorities_to_contact": [
        "Local police station",
        "Legal Aid Kenya"
      ]
    },
    "medical_protocols": {
      "immediate_needs": [
        "Refer the caller and children for medical attention, including mental health services"
      ],
      "follow_up_care": [
        "Regular follow-ups with healthcare providers"
      ]
    }
  },
  "risk_assessment": {
    "red_flags": [
      "Fear of further harm if reporting to authorities"
    ],
    "potential_barriers": [
      "Caller's fear and potential retaliation from the perpetrator"
    ],
    "protective_factors": [
      "Support network",
      "Presence of children"
    ]
  },
  "cultural_considerations": []
}
</script>

<style scoped>
.custom-audio-player::-webkit-media-controls-enclosure {
  background-color: transparent;
}
</style>


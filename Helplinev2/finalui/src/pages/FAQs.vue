<template>
  <div 
    class="min-h-screen py-8 px-4 sm:px-6 lg:px-8 transition-colors duration-300"
    :class="isDarkMode ? 'bg-black text-gray-100' : 'bg-gray-50 text-gray-900'"
  >
    <div class="max-w-4xl mx-auto space-y-8">
      
      <!-- Header Section -->
      <div 
        class="relative overflow-hidden rounded-3xl p-8 sm:p-12 shadow-2xl border border-transparent transition-all duration-500"
        :class="isDarkMode ? 'bg-neutral-900/80 backdrop-blur-xl' : 'bg-white shadow-amber-900/5'"
      >
        <div class="absolute top-0 right-0 p-8 opacity-10 pointer-events-none">
          <i-mdi-book-open-page-variant class="w-32 h-32" />
        </div>
        
        <div class="relative z-10 flex flex-col sm:flex-row items-center gap-6 sm:gap-10">
        <div class="flex-shrink-0 w-20 h-20 rounded-2xl flex items-center justify-center shrink-0 transition-colors"
          :class="isDarkMode ? 'bg-amber-500/10 text-amber-500' : 'bg-amber-600/10 text-amber-600'"
        >
          <i-mdi-library class="w-10 h-10" />
        </div>
          <div class="text-center sm:text-left">
            <h1 class="text-3xl sm:text-4xl font-black tracking-tight mb-2">OpenCHS AI Service</h1>
            <p class="text-lg font-semibold" :class="isDarkMode ? 'text-amber-500/80' : 'text-amber-600'">Frequently Asked Questions & Documentation</p>
            
            <div class="flex flex-wrap items-center justify-center sm:justify-start gap-4 mt-6 text-[10px] uppercase font-bold tracking-widest opacity-60">
              <div class="flex items-center gap-2">
                <i-mdi-calendar class="w-3 h-3" />
                Last Updated: Dec 2025
              </div>
              <div class="flex items-center gap-2">
                <i-mdi-office-building class="w-3 h-3" />
                C-Sema Tanzania
              </div>
              <div class="flex items-center gap-2">
                <i-mdi-wrench class="w-3 h-3" />
                v1.0
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Navigation -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <a 
          v-for="nav in quickNav" 
          :key="nav.id"
          :href="'#' + nav.id"
          class="p-4 rounded-2xl border border-transparent text-center transition-all duration-300 hover:scale-105 active:scale-95 group"
          :class="isDarkMode ? 'bg-neutral-900 hover:bg-neutral-800' : 'bg-white hover:bg-amber-600/5 shadow-sm'"
        >
          <component :is="nav.icon" class="w-6 h-6 mx-auto mb-2 group-hover:scale-110 transition-transform" 
            :class="isDarkMode ? 'text-amber-500' : 'text-amber-600'"
          />
          <span class="text-[10px] font-black uppercase tracking-tighter">{{ nav.label }}</span>
        </a>
      </div>

      <!-- FAQ Content -->
      <div v-for="section in faqSections" :key="section.id" :id="section.id" class="space-y-6 pt-10">
        <div class="flex items-center gap-4 mb-4">
          <div class="w-10 h-10 rounded-xl flex items-center justify-center"
            :class="isDarkMode ? 'bg-amber-500/10 text-amber-500' : 'bg-amber-600/10 text-amber-600'"
          >
            <component :is="section.icon" class="w-5 h-5" />
          </div>
          <h2 class="text-xl font-black uppercase tracking-tight">{{ section.title }}</h2>
        </div>

        <div class="grid gap-4">
          <div 
            v-for="(faq, index) in section.items" 
            :key="index"
            class="rounded-2xl border transition-all duration-300 overflow-hidden"
            :class="[
              isDarkMode 
                ? 'bg-neutral-900/40 border-neutral-800 hover:border-amber-500/30' 
                : 'bg-white border-gray-100 shadow-sm hover:border-amber-600/30',
              openItems.includes(`${section.id}-${index}`) ? (isDarkMode ? 'border-amber-500/50' : 'border-amber-600/50') : ''
            ]"
          >
            <button 
              @click="toggleItem(`${section.id}-${index}`)"
              class="w-full flex items-center justify-between p-5 text-left transition-colors"
            >
              <span class="text-sm font-bold leading-snug">{{ faq.question }}</span>
              <div 
                class="w-6 h-6 rounded-lg flex items-center justify-center shrink-0 transition-all duration-300"
                :class="openItems.includes(`${section.id}-${index}`) 
                  ? (isDarkMode ? 'bg-amber-600 text-white rotate-45' : 'bg-amber-700 text-white rotate-45') 
                  : (isDarkMode ? 'bg-amber-500/10 text-amber-500' : 'bg-amber-600/10 text-amber-600')"
              >
                <i-mdi-plus class="w-4 h-4" />
              </div>
            </button>

            <div 
              v-show="openItems.includes(`${section.id}-${index}`)"
              class="p-5 pt-0 text-xs font-medium leading-relaxed opacity-80 animate-in fade-in slide-in-from-top-2"
              :class="isDarkMode ? 'text-gray-300' : 'text-gray-600'"
              v-html="faq.answer"
            >
            </div>
          </div>
        </div>
      </div>

      <!-- Footer Help -->
      <div 
        class="mt-20 p-8 rounded-3xl border-2 border-dashed text-center"
        :class="isDarkMode ? 'border-neutral-800 bg-neutral-900/20' : 'border-amber-100 bg-amber-50/20'"
      >
        <h3 class="text-lg font-black uppercase tracking-tight mb-2">Need More Help?</h3>
        <p class="text-xs font-medium opacity-60 mb-6 italic">If your question isn't answered here, please contact the appropriate support team.</p>
        
        <div class="grid sm:grid-cols-3 gap-4 text-left">
          <div v-for="contact in supportContacts" :key="contact.role" class="p-4 rounded-2xl" :class="isDarkMode ? 'bg-black/40' : 'bg-white shadow-sm border border-transparent hover:border-amber-600/20 transition-colors'">
            <p class="text-[9px] font-black uppercase tracking-widest mb-1" :class="isDarkMode ? 'text-amber-500' : 'text-amber-600'">{{ contact.role }}</p>
            <p class="text-xs font-bold">{{ contact.target }}</p>
          </div>
        </div>
        
        <div class="mt-8 pt-8 border-t border-dashed" :class="isDarkMode ? 'border-neutral-800' : 'border-amber-600/20'">
          <p class="text-[9px] font-bold uppercase tracking-[0.2em] opacity-40">
            Document Version 1.0 | Prepared by BITZ IT Consulting Ltd for C-Sema Tanzania
          </p>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, inject } from 'vue'

const isDarkMode = inject('isDarkMode')
const openItems = ref([])

const toggleItem = (id) => {
  if (openItems.value.includes(id)) {
    openItems.value = openItems.value.filter(i => i !== id)
  } else {
    openItems.value.push(id)
  }
}

const quickNav = [
  { id: 'getting-started', label: 'Getting Started', icon: 'i-mdi-rocket' },
  { id: 'ai-features', label: 'AI Features', icon: 'i-mdi-robot' },
  { id: 'call-management', label: 'Call Management', icon: 'i-mdi-phone-cog' },
  { id: 'data-reports', label: 'Data & Reports', icon: 'i-mdi-chart-areaspline' }
]

const supportContacts = [
  { role: 'Technical Support', target: 'IT Support Team' },
  { role: 'Training Questions', target: 'Your Team Leader' },
  { role: 'System Issues', target: 'System Administrator' }
]

const faqSections = [
  {
    id: 'getting-started',
    title: 'Getting Started',
    icon: 'i-mdi-rocket',
    items: [
      {
        question: 'What is the OpenCHS AI Service?',
        answer: `<ul class="list-disc pl-5 space-y-1">
          <li>Automatic Speech Recognition (ASR) for Swahili language</li>
          <li>Post-Call transcription of counseling calls</li>
          <li>Automated case classification into categories, subcategories, and interventions</li>
          <li>Quality assurance scoring with sentiment analysis</li>
          <li>Call summarization and narrative generation</li>
          <li>Machine translation for English support</li>
          <li>Named Entity Recognition (NER) for extracting key information</li>
        </ul>
        <p class="mt-3">The system helps counselors work more efficiently by automating documentation and providing assistance during calls.</p>`
      },
      {
        question: 'How do I access the OpenCHS AI Service?',
        answer: `<ol class="list-decimal pl-5 space-y-1">
          <li>Open your web browser (Chrome, Edge, or Firefox recommended)</li>
          <li>Navigate to the OpenCHS AI Service URL provided by your administrator</li>
          <li>Log in with your counselor credentials (username and password)</li>
          <li>The AI service interface will appear integrated with your existing OpenCHS dashboard</li>
        </ol>
        <p class="mt-3 bg-amber-500/10 p-3 rounded-xl border border-amber-500/20">💡 <strong>Tip:</strong> Each counselor and team leader should have their own individual account. Contact your system administrator if you need an account activated.</p>`
      },
      {
        question: 'What browsers are supported?',
        answer: `<p>The OpenCHS AI Service is optimized for:</p>
        <ul class="list-disc pl-5 mt-2 space-y-1">
          <li>Google Chrome (recommended, version 90+)</li>
          <li>Microsoft Edge (version 90+)</li>
          <li>Mozilla Firefox (version 88+)</li>
        </ul>
        <p class="mt-3 text-red-500 font-bold">⚠️ Important: If you experience loading errors or compatibility issues, ensure your browser is updated to the latest version. Internet Explorer is not supported.</p>`
      }
    ]
  },
  {
    id: 'ai-features',
    title: 'AI Features & Capabilities',
    icon: 'i-mdi-robot',
    items: [
      {
        question: 'How does the AI transcribe calls in real-time?',
        answer: `<p>The AI uses Automatic Speech Recognition (ASR) technology specifically trained for Swahili language:</p>
        <ol class="list-decimal pl-5 mt-2 space-y-1">
          <li>As you speak with a caller, the AI listens to the conversation</li>
          <li>It converts speech to text post-call, displaying the transcription on your screen</li>
          <li>The transcription can be reviewed and edited after the call</li>
          <li>You can insert or pre-fill case narration directly from the transcription</li>
        </ol>
        <p class="mt-3">💡 <strong>Best Practice:</strong> Speak clearly and minimize background noise for better transcription accuracy. The system works best in quiet environments.</p>`
      },
      {
        question: 'What is case classification and how does it work?',
        answer: `<p>The AI automatically categorizes calls into:</p>
        <ul class="list-disc pl-5 mt-2 space-y-1">
          <li><strong>Main Categories:</strong> Primary issue type (e.g., child protection, health, legal)</li>
          <li><strong>Subcategories:</strong> More specific classification within main categories</li>
          <li><strong>Interventions:</strong> Actions taken or recommended during the call</li>
        </ul>
        <div class="mt-3 p-4 rounded-xl bg-amber-500/5 border border-amber-500/10 italic">
          📌 <strong>Multi-Label Classification:</strong> Some cases involve multiple issues (e.g., custody and GBV). The system can assign multiple categories to a single case.
        </div>`
      }
    ]
  },
  {
    id: 'call-management',
    title: 'Call Management',
    icon: 'i-mdi-phone-cog',
    items: [
      {
        question: 'How do I handle repeat calls from the same number?',
        answer: `<p>The system includes features to manage repeat callers:</p>
        <ul class="list-disc pl-5 mt-2 space-y-1">
          <li><strong>Automatic Hold:</strong> Repeat calls from test numbers (often children) can be held for 15-30 minutes</li>
          <li><strong>Call Rotation:</strong> Repeat calls are distributed to different counselors to prevent fatigue</li>
          <li><strong>Caller History:</strong> View previous interactions with the same number</li>
        </ul>`
      },
      {
        question: 'How do I handle abusive or inappropriate calls?',
        answer: `<ol class="list-decimal pl-5 mt-2 space-y-1">
          <li>Use the "Mark as Abusive" option in the call interface</li>
          <li>End the call professionally but firmly</li>
          <li>The call will be flagged in the system</li>
          <li>Transcription is retained for quality and safety purposes</li>
          <li>Report to your supervisor if the abuse is severe or threatening</li>
        </ol>
        <p class="mt-3 text-red-500 font-bold italic">⚠️ Safety First: Never tolerate verbal abuse or threats. You have the right to end inappropriate calls while maintaining professional conduct.</p>`
      }
    ]
  },
  {
    id: 'data-reports',
    title: 'Data & Reports',
    icon: 'i-mdi-chart-areaspline',
    items: [
      {
        question: 'What mandatory fields must I complete for each case?',
        answer: `<p>The following fields are mandatory and must be completed before saving a case:</p>
        <ul class="list-disc pl-5 mt-2 space-y-1">
          <li>Reporter Name/Contact: Who reported the case (or phone number)</li>
          <li>Client Gender: Gender of the person receiving counseling</li>
          <li>Client Age Group: Age bracket of the client</li>
          <li>Region/Location: Geographic area of the caller</li>
          <li>Case Narrative: Summary of the counseling session</li>
        </ul>
        <p class="mt-3 text-red-500 font-bold">⚠️ Critical: Cases cannot be saved without these fields. This ensures data completeness for accurate reporting and analysis.</p>`
      },
      {
        question: 'What are the standard age group categories?',
        answer: `<div class="overflow-hidden rounded-xl border border-neutral-200 dark:border-neutral-800 mt-2">
          <table class="w-full text-[10px] sm:text-xs">
            <thead class="bg-gray-100 dark:bg-neutral-800 font-bold uppercase tracking-tight">
              <tr>
                <th class="p-2 text-left">Group</th>
                <th class="p-2 text-left">Range</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-neutral-200 dark:divide-neutral-800">
              <tr><td class="p-2">Infant</td><td class="p-2">0-1 years</td></tr>
              <tr><td class="p-2">Early Childhood</td><td class="p-2">2-5 years</td></tr>
              <tr><td class="p-2">Middle Childhood</td><td class="p-2">6-11 years</td></tr>
              <tr><td class="p-2">Adolescent</td><td class="p-2">12-17 years</td></tr>
            </tbody>
          </table>
        </div>`
      }
    ]
  },
  {
    id: 'technical',
    title: 'Technical Information',
    icon: 'i-mdi-cog-outline',
    items: [
      {
        question: 'What hardware is required to run the AI models locally?',
        answer: `<p><strong>Server Requirements:</strong></p>
        <ul class="list-disc pl-5 mt-2 space-y-1">
          <li>GPU: High-performance GPU (NVIDIA recommended)</li>
          <li>RAM: Minimum 16GB, 32GB+ recommended</li>
          <li>Storage: Minimum 500GB SSD</li>
          <li>Processor: Multi-core CPU (Intel Xeon or AMD EPYC)</li>
        </ul>`
      }
    ]
  },
  {
    id: 'training',
    title: 'Training & Support',
    icon: 'i-mdi-school-outline',
    items: [
      {
        question: 'When and how will training be conducted?',
        answer: `<p><strong>Schedule:</strong> 2-week comprehensive program. Primary Sessions on Fridays (11:00-13:00).</p>
        <p class="mt-2"><strong>Focus:</strong> New AI features and counselor guidance.</p>`
      }
    ]
  },
  {
    id: 'compliance',
    title: 'Compliance & Privacy',
    icon: 'i-mdi-shield-check-outline',
    items: [
      {
        question: 'How does the system comply with Tanzania\'s Data Protection Act?',
        answer: `<ul class="list-disc pl-5 mt-2 space-y-1">
          <li>Encryption: All data encrypted in transit and at rest</li>
          <li>Access Controls: Role-based permissions</li>
          <li>Audit Trails: All system actions are logged</li>
          <li>User Consent: Callers are informed about data collection</li>
        </ul>`
      }
    ]
  },
  {
    id: 'troubleshooting',
    title: 'Troubleshooting',
    icon: 'i-mdi-alert-circle-outline',
    items: [
      {
        question: 'The system won\'t load or shows a blank screen. What should I do?',
        answer: `<ol class="list-decimal pl-5 mt-2 space-y-1">
          <li>Clear browser cache (Ctrl+Shift+Delete)</li>
          <li>Try a different browser (Chrome, Edge, Firefox)</li>
          <li>Check internet connection</li>
          <li>Disable browser extensions</li>
        </ol>`
      }
    ]
  },
  {
    id: 'resources',
    title: 'Additional Resources',
    icon: 'i-mdi-book-multiple-outline',
    items: [
      {
        question: 'Will the AI replace counselors?',
        answer: `<p class="font-bold text-amber-500 mb-2">Absolutely not! The AI is a support tool designed to enhance your work, not replace it.</p>
        <p><strong>What the AI Does:</strong> Automates documentation, suggests classifications, provides quality scoring, and generates summaries.</p>
        <p class="mt-2"><strong>What Only YOU Can Do:</strong> Provide empathy, make nuanced judgments, build trust, and application cultural understanding.</p>
        <p class="mt-3 p-3 bg-amber-500/10 rounded-xl border border-amber-500/20 italic">
          The Goal: The AI handles the administrative work so you can focus on what matters most—helping people. You remain the expert, and the AI is your assistant.
        </p>`
      }
    ]
  }
]
</script>

<style scoped>
.animate-in {
  animation-duration: 0.3s;
}
</style>

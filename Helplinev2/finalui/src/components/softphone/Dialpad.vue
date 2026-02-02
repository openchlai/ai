<template>
  <div class="flex flex-col w-[350px] max-w-[95vw] mx-auto rounded-[32px] p-6 shadow-2xl relative overflow-hidden transition-all duration-300 backdrop-blur-xl"
    :class="isDarkMode 
      ? 'bg-black/90 shadow-[0_20px_60px_-15px_rgba(0,0,0,0.8)] border border-white/10' 
      : 'bg-white/95 shadow-[0_20px_60px_-15px_rgba(0,0,0,0.3)] border border-white/40 ring-1 ring-black/5'"
    role="dialog"
    aria-label="Voice Terminal Dialpad"
  >
    <!-- Background Gradient Glow (Optional) -->
    <div v-if="isDarkMode" class="absolute top-0 right-0 w-64 h-64 bg-emerald-500/10 rounded-full blur-[80px] -translate-y-1/2 translate-x-1/2 pointer-events-none"></div>

    <!-- Header & Tools Combined (Top Placement) -->
    <div class="flex flex-col gap-4 mb-6 relative z-10">
        <!-- Top Status Bar -->
        <div class="flex justify-between items-center">
            <div>
                <h2 class="text-[10px] font-black tracking-[0.25em] uppercase mb-1.5 opacity-80" 
                  :class="isDarkMode ? 'text-white' : 'text-gray-900'"
                >
                  Terminal
                </h2>
                <div class="flex items-center gap-2" role="status">
                   <div class="w-1.5 h-1.5 rounded-full transition-colors duration-300 shadow-[0_0_8px_currentColor]" :class="statusDotClass" aria-hidden="true"></div>
                   <span class="text-xs font-bold transition-colors duration-300"
                      :class="sipStore.isRegistered ? (isDarkMode ? 'text-white' : 'text-gray-900') : 'text-gray-500'"
                   >
                     {{ displayStatus }}
                   </span>
                   <!-- Force Refresh/Reconnect -->
                   <button @click="forceRefresh" 
                     class="p-1 rounded-md hover:bg-gray-200 dark:hover:bg-white/10 text-gray-400 hover:text-amber-500 transition-colors"
                     title="Refresh Status"
                   >
                      <i-mdi-refresh class="w-3.5 h-3.5" :class="{'animate-spin': connectionLoading}" />
                   </button>
                </div>
            </div>
            
            <div class="bg-gray-100 dark:bg-white/10 rounded-lg px-3 py-1.5 flex items-center gap-2">
                 <span class="text-[9px] font-bold tracking-wider uppercase text-gray-500 dark:text-gray-400">EXT</span>
                 <span class="text-xs font-black" :class="isDarkMode ? 'text-white' : 'text-gray-900'">{{ sipStore.extension || '---' }}</span>
            </div>
        </div>
        
        <!-- Tools Row (Moved to Top) -->
        <div class="grid grid-cols-2 gap-3 w-full">
            <!-- Connect Agent -->
            <button @click="toggleAgent"
                class="flex items-center justify-center gap-2 py-3 rounded-xl transition-all focus:outline-none focus:ring-2 focus:ring-emerald-500/50"
                :class="[
                    isDarkMode ? 'bg-white/5 hover:bg-white/10' : 'bg-gray-50 hover:bg-gray-100',
                    sipStore.isEnabled 
                        ? (isDarkMode ? 'text-red-400' : 'text-red-600') 
                        : (isDarkMode ? 'text-gray-300' : 'text-gray-600')
                ]"
                :disabled="connectionLoading"
                :aria-label="sipStore.isEnabled ? 'Disconnect Agent' : 'Connect Agent'"
                aria-live="polite"
            >
                <i-mdi-loading class="w-4 h-4 animate-spin" v-if="connectionLoading || sipStore.status === 'connecting'" aria-hidden="true" />
                <i-mdi-power class="w-4 h-4" v-else aria-hidden="true" />
                <span class="text-[11px] font-bold uppercase tracking-wider">
                    {{ connectionLoading ? 'Working...' : (sipStore.isEnabled ? 'Disconnect' : 'Connect') }}
                </span>
            </button>

            <!-- Queue Toggle -->
            <button @click="handleToggleQueue" 
                class="flex items-center justify-center gap-2 py-3 rounded-xl transition-all focus:outline-none focus:ring-2 focus:ring-amber-500/50 disabled:opacity-50 disabled:cursor-not-allowed"
                :class="[
                    isDarkMode ? 'bg-white/5 hover:bg-white/10' : 'bg-gray-50 hover:bg-gray-100',
                    activeCallStore.queueStatus === 'online' 
                        ? 'text-amber-500 bg-amber-500/10 shadow-inner' 
                        : (isDarkMode ? 'text-gray-300' : 'text-gray-600')
                ]"
                :aria-label="activeCallStore.queueStatus === 'online' ? 'Leave Queue' : 'Join Queue'"
            >
                 <i-mdi-account-group class="w-4 h-4" v-if="!queueActionLoading" aria-hidden="true" />
                 <i-mdi-loading class="w-4 h-4 animate-spin" v-else aria-hidden="true" />
                 <span class="text-[11px] font-bold uppercase tracking-wider">
                    {{ activeCallStore.queueStatus === 'online' ? 'Leave Queue' : 'Join Queue' }}
                 </span>
            </button>
        </div>
    </div>
    
    <!-- Error Feedback -->
    <div v-if="errorMessage" class="mb-3 px-3 py-1.5 bg-red-100 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded text-xs text-red-600 dark:text-red-400 text-center">
        {{ errorMessage }}
    </div>

    <!-- Input Display -->
    <div class="flex justify-center items-center mb-6 relative h-16 z-10 bg-gray-50/50 dark:bg-white/5 rounded-2xl border border-gray-100 dark:border-white/5">
      <label for="dial-input" class="sr-only">Phone Number to Dial</label>
      <input
        id="dial-input"
        v-model="dialString"
        type="text"
        readonly
        placeholder="Enter number..."
        class="w-full text-center text-3xl font-bold bg-transparent border-none focus:ring-0 p-0 tracking-widest placeholder-gray-400 opacity-90"
        :class="isDarkMode ? 'text-white' : 'text-gray-900'"
      />
      
      <!-- Backspace (Only visible if input exists) -->
      <button v-if="dialString"
        @click="dialString = dialString.slice(0, -1)"
        class="absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-full hover:bg-gray-200 dark:hover:bg-white/20 transition-colors focus:outline-none focus:ring-2 focus:ring-gray-400"
        :class="isDarkMode ? 'text-gray-300' : 'text-gray-500'"
        aria-label="Backspace"
      >
        <i-mdi-backspace-outline class="w-6 h-6" aria-hidden="true" />
      </button>
    </div>

    <!-- Keypad Grid -->
    <div class="grid grid-cols-3 gap-3 mb-6 px-1 z-10" role="group" aria-label="Keypad">
      <button
        v-for="key in keys"
        :key="key.value"
        @click="appendKey(key.value)"
        class="flex flex-col items-center justify-center w-full h-[60px] rounded-xl transition-all duration-150 active:scale-95 hover:bg-gray-100 dark:hover:bg-white/10 focus:outline-none focus:ring-2 focus:ring-emerald-500/30"
        :aria-label="key.value + ' ' + key.letters"
      >
        <span class="text-2xl font-semibold transition-colors duration-200"
          :class="isDarkMode ? 'text-white' : 'text-gray-900'"
        >{{ key.value }}</span>
        <span class="text-[9px] font-bold tracking-[0.1em] uppercase -mt-0.5 transition-colors duration-200 opacity-50"
          :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
        >{{ key.letters }}</span>
      </button>
    </div>

    <!-- Call Action -->
    <div class="flex flex-col items-center justify-center gap-4 z-10">
      <button
        @click="handleCall"
        :disabled="!canCall"
        class="w-full py-4 rounded-xl flex items-center justify-center shadow-lg shadow-emerald-500/20 transition-all duration-300 active:scale-95 disabled:opacity-50 disabled:grayscale disabled:shadow-none bg-emerald-600 hover:bg-emerald-500 text-white gap-3 focus:outline-none focus:ring-4 focus:ring-emerald-500/30"
        :aria-label="connectionLoading ? 'Connecting call...' : 'Initiate Call'"
      >
        <i-mdi-loading class="w-6 h-6 animate-spin" v-if="connectionLoading" aria-hidden="true" />
        <i-mdi-phone class="w-6 h-6" v-else aria-hidden="true" />
        <span class="text-sm font-black uppercase tracking-[0.15em]">{{ connectionLoading ? 'Connecting...' : 'Initiate Call' }}</span>
      </button>
    </div>
    
  </div>
</template>

<script setup>
import { ref, computed, inject, onMounted } from 'vue'
import { useSipStore } from '@/stores/sip'
import { useActiveCallStore } from '@/stores/activeCall'
import { useAuthStore } from '@/stores/auth'
import { toast } from 'vue-sonner'

const isDarkMode = inject('isDarkMode')
const sipStore = useSipStore()
const activeCallStore = useActiveCallStore()
const authStore = useAuthStore()
const dialString = ref('')
const queueActionLoading = ref(false)

onMounted(() => {
  if (!sipStore.extension && authStore.userId) {
    sipStore.fetchExtension().catch(err => {
      console.warn('[Dialpad] Failed to pre-fetch extension:', err)
    })
  }
})

const keys = [
  { value: '1', letters: '' },
  { value: '2', letters: 'ABC' },
  { value: '3', letters: 'DEF' },
  { value: '4', letters: 'GHI' },
  { value: '5', letters: 'JKL' },
  { value: '6', letters: 'MNO' },
  { value: '7', letters: 'PQRS' },
  { value: '8', letters: 'TUV' },
  { value: '9', letters: 'WXYZ' },
  { value: '*', letters: '' },
  { value: '0', letters: '+' },
  { value: '#', letters: '' },
]

const canCall = computed(() => {
  return dialString.value.length > 0
})

const displayStatus = computed(() => {
    if (sipStore.isRegistered) return 'Registered'
    if (sipStore.status === 'connecting' || sipStore.isRegistering) return 'Connecting...'
    // If connected (socket open) but not registered yet
    if (sipStore.status === 'connected' && !sipStore.isRegistered) return 'Registering...'
    if (sipStore.status === 'connected') return 'Online'
    if (sipStore.status === 'error') return 'Error'
    return 'Offline'
})

const statusDotClass = computed(() => {
  if (sipStore.isRegistered) return 'bg-emerald-500 shadow-[0_0_12px_rgba(16,185,129,0.5)]'
  if (sipStore.status === 'connecting' || sipStore.isEnabled) return 'bg-amber-500 animate-pulse shadow-[0_0_12px_rgba(245,158,11,0.5)]'
  if (sipStore.status === 'error') return 'bg-red-500 shadow-[0_0_12px_rgba(239,68,68,0.5)]'
  return 'bg-gray-400'
})

const errorMessage = computed(() => sipStore.error)

function appendKey(char) {
  if (dialString.value.length < 15) {
      dialString.value += char
  }
}

const connectionLoading = ref(false)

async function handleCall() {
  if (!dialString.value) return
  
  if (!sipStore.isRegistered) {
    try {
      toast.info('Connecting to voice server...')
      connectionLoading.value = true
      
      // If we are 'connected' but not registered, it might be a stale auth state
      // We will try to start() again which now handles re-auth
      await sipStore.start()
      
      // Poll for registration for up to 10 seconds
      let attempts = 0
      while (!sipStore.isRegistered && attempts < 20) {
        await new Promise(r => setTimeout(r, 500))
        attempts++
      }

      if (!sipStore.isRegistered) {
        // Don't throw, just warn users so they can retry manually
        toast.warning('Still registering... please wait or click Reconnect.')
        return
      }
    } catch (e) {
      console.error('[Dialpad] Auto-connect failed:', e)
      toast.error('Connection error: ' + e.message)
      connectionLoading.value = false
      return
    } finally {
      connectionLoading.value = false
    }
  }

  try {
    const number = dialString.value
    console.log('[Dialpad] Initiating call to:', number)
    await sipStore.makeCall(number)
    dialString.value = '' // Clear after successful dial
  } catch (err) {
    console.error('[Dialpad] Call initiation failed:', err)
    toast.error('Call failed: ' + err.message)
  }
}

async function forceRefresh() {
    connectionLoading.value = true
    try {
        toast.info('Refreshing connection...')
        // Reset specific queue and sip flags in storage if truly stuck
        await sipStore.stop()
        await new Promise(r => setTimeout(r, 500))
        await sipStore.start()
        await activeCallStore.initializeQueue()
        toast.success('Status refreshed')
    } catch (e) {
        toast.error('Refresh failed: ' + e.message)
    } finally {
        connectionLoading.value = false
    }
}

async function toggleAgent() {
    connectionLoading.value = true
    try {
        if (sipStore.isEnabled) {
            await sipStore.stop()
        } else {
            await sipStore.start()
        }
    } catch(e) {
        toast.error(e.message)
    } finally {
        connectionLoading.value = false
    }
}

async function handleToggleQueue() {
    if (queueActionLoading.value) return
    queueActionLoading.value = true
    try {
        if (activeCallStore.queueStatus === 'offline') {
            await activeCallStore.joinQueue()
            toast.success('Queue join initiated')
        } else {
            await activeCallStore.leaveQueue()
            toast.success('Queue leave initiated')
        }
    } catch (e) {
        toast.error('Queue error: ' + e.message)
    } finally {
        queueActionLoading.value = false
    }
}
</script>

<style scoped>
/* Optional: Hide scrollbar if needed for overflow */
input::-webkit-outer-spin-button,
input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
</style>

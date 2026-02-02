<template>
    <div v-if="['active', 'calling', 'ringing'].includes(activeCallStore.callState)"
        class="fixed top-24 left-1/2 -translate-x-1/2 z-[100] pointer-events-auto">
        
        <!-- Hidden Audio for WebRTC -->
        <audio ref="remoteAudio" autoplay playsinline class="hidden"></audio>

        <div
            class="flex items-center gap-1 p-2 bg-white/90 dark:bg-neutral-900/90 backdrop-blur-md rounded-2xl shadow-xl border border-gray-200 dark:border-neutral-800 animate-in fade-in slide-in-from-top-4 duration-500">

            <!-- Ringing: Answer Action -->
            <template v-if="activeCallStore.callState === 'ringing'">
                <div class="flex items-center gap-4 px-4">
                    <span class="text-xs font-bold animate-pulse text-emerald-500">Incoming Call...</span>
                    <span class="text-sm font-black">{{ activeCallStore.callerNumber }}</span>
                </div>
                <div class="flex items-center gap-2 pl-4 border-l border-gray-200 dark:border-neutral-800">
                    <button @click="activeCallStore.answerCall"
                        class="flex items-center gap-2 px-6 py-2 rounded-xl text-xs font-bold uppercase tracking-wider bg-emerald-600 text-white hover:bg-emerald-700 transition-colors shadow-lg shadow-emerald-600/20 shadow-emerald-600/50 ring-4 ring-emerald-500/20">
                        <i-mdi-phone class="w-4 h-4 animate-pulse" />
                        Answer
                    </button>
                    <button @click="activeCallStore.hangupCall"
                        class="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold uppercase tracking-wider bg-red-600/10 text-red-600 hover:bg-red-600/20 transition-colors">
                        <i-mdi-phone-hangup class="w-4 h-4" />
                        Reject
                    </button>
                </div>
            </template>

            <!-- Active/Calling: Normal Actions -->
            <template v-else>
                <!-- Timer Section -->
                <div class="flex flex-col px-6 border-r border-gray-200 dark:border-neutral-800">
                    <span class="text-[9px] font-black uppercase tracking-[0.2em] text-gray-400">Duration</span>
                    <span class="text-xl font-black font-mono tracking-widest text-emerald-600 dark:text-emerald-500">
                        {{ activeCallStore.formatDuration(activeCallStore.durationSeconds) }}
                    </span>
                </div>

                <!-- Info -->
                <div class="flex items-center gap-3 px-4">
                    <div class="w-3 h-3 rounded-full bg-emerald-500 animate-pulse"></div>
                    <div class="flex flex-col">
                        <span class="text-[9px] font-bold uppercase tracking-wider opacity-50">Caller</span>
                        <span class="text-sm font-bold">{{ activeCallStore.callerNumber }}</span>
                    </div>
                </div>

                <!-- Actions -->
                <div class="flex items-center gap-2 pl-4 border-l border-gray-200 dark:border-neutral-800">
                    <button @click="openCaseForm"
                        class="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold uppercase tracking-wider bg-gray-100 dark:bg-neutral-800 hover:bg-gray-200 dark:hover:bg-neutral-700 transition-colors">
                        <i-mdi-plus-circle class="w-4 h-4" />
                        Case
                    </button>

                    <button @click="isDispositionOpen = true"
                        class="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold uppercase tracking-wider bg-amber-100 dark:bg-amber-900/20 text-amber-700 dark:text-amber-500 hover:bg-amber-200 dark:hover:bg-amber-900/40 transition-colors">
                        <i-mdi-file-document-edit class="w-4 h-4" />
                        Disposition
                    </button>

                    <button @click="activeCallStore.hangupCall"
                        class="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold uppercase tracking-wider bg-red-600 text-white hover:bg-red-700 transition-colors shadow-lg shadow-red-600/20">
                        <i-mdi-phone-hangup class="w-4 h-4" />
                        End
                    </button>
                </div>
            </template>
        </div>

        <!-- Disposition Drawer -->
        <DispositionDrawer :is-open="isDispositionOpen" :call-id="activeCallStore.src_callid"
            :phone="activeCallStore.callerNumber"
            @close="isDispositionOpen = false" @submit="handleDispositionSubmit" />
    </div>
</template>

<script setup>
import { ref, inject, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useActiveCallStore } from '@/stores/activeCall'
import DispositionDrawer from './DispositionDrawer.vue'

const activeCallStore = useActiveCallStore()
const router = useRouter()
const isDarkMode = inject('isDarkMode')

const isDispositionOpen = ref(false)
const remoteAudio = ref(null)

// formatDuration removed; using store version in template

const openCaseForm = () => {
    router.push({
        path: '/case-creation',
        query: {
            phone: activeCallStore.callerNumber,
            call_id: activeCallStore.src_callid,
            uniqueid: activeCallStore.src_uid
        }
    })
}

// Watch for call state to attach media
watch(() => activeCallStore.callState, (newState) => {
    if (newState === 'active' && activeCallStore.currentSession) {
        // Give a small delay to ensure session established and PC ready
        setTimeout(() => setupMedia(activeCallStore.currentSession), 100)
    } else if (newState === 'idle') {
        if (remoteAudio.value) remoteAudio.value.srcObject = null
    }
})


function setupMedia(session, retryCount = 0) {
    if (!remoteAudio.value) return 
    
    // Check for peer connection and receiver
    const pc = session.sessionDescriptionHandler?.peerConnection
    if (!pc) {
         if (retryCount < 10) {
             console.log(`No PC found, retrying media setup (${retryCount + 1}/10)...`)
             setTimeout(() => setupMedia(session, retryCount + 1), 300)
         } else {
             console.warn('Media setup failed: No peer connection after retries')
         }
         return
    }

    const inboundStream = new MediaStream()
    let tracksFound = 0
    
    // Modern WebRTC: getReceivers
    pc.getReceivers().forEach((receiver) => {
        if (receiver.track && receiver.track.kind === "audio") {
            console.log('Found audio track:', receiver.track.id, receiver.track.enabled, receiver.track.readyState)
            inboundStream.addTrack(receiver.track)
            tracksFound++
        }
    })

    // Legacy/Fallback: getRemoteStreams
    if (tracksFound === 0 && pc.getRemoteStreams) {
        const streams = pc.getRemoteStreams()
        if (streams.length > 0) {
             streams[0].getAudioTracks().forEach(track => {
                 inboundStream.addTrack(track)
                 tracksFound++
             })
        }
    }

    if (tracksFound > 0) {
        console.log('Attaching valid audio stream to element')
        remoteAudio.value.srcObject = inboundStream
        remoteAudio.value.volume = 1.0
        remoteAudio.value.muted = false
        remoteAudio.value.play().then(() => {
             console.log('Audio playing successfully')
             activeCallStore.hasAudioTrack = true
        }).catch(e => {
             console.error('Audio play error (likely interaction needed):', e)
             // Retry play on click if needed?
        })
    } else {
         if (retryCount < 10) {
             console.log(`No audio tracks found yet, retrying (${retryCount + 1}/10)...`)
             setTimeout(() => setupMedia(session, retryCount + 1), 300)
         } else {
             console.warn('Media setup failed: No audio tracks found after retries')
         }
    }
}

const handleDispositionSubmit = () => {
    // Legacy support: manual hangup is available
}
</script>

<template>
    <div class="rounded-xl border p-5 shadow-sm transition-all hover:shadow-md"
        :class="isDarkMode ? 'bg-neutral-800/50 border-neutral-700' : 'bg-white border-gray-100'">

        <!-- Header -->
        <div class="flex items-center justify-between mb-3">
            <div class="flex items-center gap-2">
                <span class="px-2.5 py-1 rounded-md text-[10px] font-bold uppercase tracking-widest border"
                    :class="isDarkMode ? 'bg-blue-900/30 text-blue-300 border-blue-800' : 'bg-blue-50 text-blue-600 border-blue-100'">
                    Transcript
                </span>
                <span class="text-xs font-mono opacity-50">{{ formatTime(prediction.created_on) }}</span>
            </div>
            <div class="text-xs font-semibold" :class="isDarkMode ? 'text-gray-400' : 'text-gray-500'">
                {{ payload.language || 'Unknown' }}
            </div>
        </div>

        <!-- Content -->
        <div class="space-y-4">
            <!-- Audio Player -->
            <div v-if="prediction.src_callid" class="p-3 rounded-xl border flex items-center gap-4 transition-all"
                :class="isDarkMode ? 'bg-black border-neutral-700' : 'bg-gray-50 border-gray-100'">
                <button @click="togglePlay"
                    class="w-10 h-10 rounded-full flex items-center justify-center transition-all shadow-lg active:scale-95"
                    :class="isPlaying
                        ? 'bg-rose-500 text-white shadow-rose-500/20'
                        : 'bg-blue-600 text-white shadow-blue-500/20 hover:bg-blue-700'">
                    <i-mdi-pause v-if="isPlaying" class="w-5 h-5" />
                    <i-mdi-play v-else class="w-5 h-5" />
                </button>
                <div class="flex-1">
                    <div class="text-[10px] uppercase font-bold tracking-widest opacity-50 mb-0.5">Recording</div>
                    <div class="text-[11px] font-mono opacity-70 truncate">{{ prediction.src_callid }}.wav</div>
                </div>
                <!-- Visualizer Mockup -->
                <div class="hidden md:flex items-center gap-0.5 h-6">
                    <div v-for="i in 12" :key="i" class="w-0.5 bg-blue-500/40 rounded-full transition-all duration-300"
                        :class="isPlaying ? 'animate-pulse' : ''"
                        :style="{ height: isPlaying ? (Math.random() * 100 + 20) + '%' : '30%' }">
                    </div>
                </div>
            </div>

            <div class="relative">
                <div class="text-sm leading-relaxed overflow-hidden transition-all duration-500" :class="[
                    isDarkMode ? 'text-gray-300' : 'text-gray-700',
                    expanded ? 'max-h-full' : 'max-h-[200px]'
                ]">
                    <p class="whitespace-pre-wrap">{{ payload.transcript || 'No transcript available.' }}</p>
                </div>

                <!-- Fade Overlay -->
                <div v-if="!expanded && hasLongContent" class="absolute bottom-0 left-0 w-full h-16 bg-gradient-to-t"
                    :class="isDarkMode ? 'from-neutral-900' : 'from-white'"></div>
            </div>
        </div>

        <!-- Toggle Button -->
        <button v-if="hasLongContent" @click="expanded = !expanded"
            class="mt-2 text-xs font-semibold flex items-center gap-1 hover:underline focus:outline-none"
            :class="isDarkMode ? 'text-blue-400' : 'text-blue-600'">
            {{ expanded ? 'Read Less' : 'Read More' }}
            <i-mdi-chevron-down class="w-4 h-4 transition-transform duration-300" :class="{ 'rotate-180': expanded }" />
        </button>

        <!-- Feedback -->
        <AiFeedbackWidget :call-id="prediction.src_callid" :task-type="prediction.notification_type" />
    </div>
</template>

<script setup>
    import { ref, inject, computed } from 'vue'
    import AiFeedbackWidget from './AiFeedbackWidget.vue'

    const props = defineProps({
        prediction: Object,
        payload: Object
    })

    const isDarkMode = inject('isDarkMode')
    const expanded = ref(false)
    const isPlaying = ref(false)
    const audioObj = ref(null)

    const hasLongContent = computed(() => {
        return (props.payload.transcript || '').length > 300
    })

    const togglePlay = () => {
        if (isPlaying.value) {
            audioObj.value?.pause()
            isPlaying.value = false
            return
        }

        if (!audioObj.value) {
            const url = `/api-proxy/api/calls/${props.prediction.src_callid}?file=wav&`
            audioObj.value = new Audio(url)
            audioObj.value.onended = () => {
                isPlaying.value = false
            }
        }

        audioObj.value.play().catch(e => {
            console.error('Audio playback failed', e)
            isPlaying.value = false
        })
        isPlaying.value = true
    }

    const formatTime = (ts) => {
        if (!ts) return ''
        return new Date(ts * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
</script>

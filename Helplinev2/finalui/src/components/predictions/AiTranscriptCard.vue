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

    const hasLongContent = computed(() => {
        return (props.payload.transcript || '').length > 300
    })

    const formatTime = (ts) => {
        if (!ts) return ''
        return new Date(ts * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
</script>

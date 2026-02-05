<template>
    <div class="rounded-xl border p-5 shadow-sm transition-all hover:shadow-md border-green-500/20"
        :class="isDarkMode ? 'bg-neutral-800/50' : 'bg-green-50/20'">

        <div class="flex items-center gap-3">
            <div class="p-2 rounded-full"
                :class="isDarkMode ? 'bg-green-900/30 text-green-400' : 'bg-green-100 text-green-600'">
                <i-mdi-check-all class="w-5 h-5" />
            </div>
            <div>
                <div class="text-xs font-bold uppercase tracking-widest opacity-60">Processing Complete</div>
                <div class="text-sm font-semibold">
                    All AI tasks for this call have finished.
                </div>
                <!-- Metadata -->
                <div v-if="payload.models_used || payload.processing_time" class="mt-2 flex flex-wrap gap-2">
                    <span v-for="model in payload.models_used" :key="model"
                        class="px-1.5 py-0.5 rounded bg-black/5 dark:bg-white/5 text-[10px] font-mono opacity-70 border border-black/10 dark:border-white/10">
                        {{ model }}
                    </span>
                    <span v-if="payload.processing_time" class="text-[10px] opacity-60 flex items-center gap-1">
                        <i-mdi-timer-outline class="w-3 h-3" />
                        {{ payload.processing_time.toFixed(2) }}s
                    </span>
                </div>
            </div>
            <div class="ml-auto text-xs font-mono opacity-50">{{ formatTime(prediction.created_on) }}</div>
        </div>

        <!-- Feedback -->
        <AiFeedbackWidget :call-id="prediction.src_callid" :task-type="prediction.notification_type" />

    </div>
</template>

<script setup>
    import { inject } from 'vue'
    import AiFeedbackWidget from './AiFeedbackWidget.vue'

    const props = defineProps({
        prediction: Object,
        payload: Object
    })

    const isDarkMode = inject('isDarkMode')

    const formatTime = (ts) => {
        if (!ts) return ''
        return new Date(ts * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
</script>

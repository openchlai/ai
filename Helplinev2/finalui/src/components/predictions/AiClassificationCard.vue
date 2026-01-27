<template>
    <div class="rounded-xl border p-5 shadow-sm transition-all hover:shadow-md"
        :class="isDarkMode ? 'bg-neutral-800/50 border-neutral-700' : 'bg-white border-gray-100'">

        <div class="flex items-center gap-2 mb-4">
            <span class="px-2.5 py-1 rounded-md text-[10px] font-bold uppercase tracking-widest border"
                :class="isDarkMode ? 'bg-amber-900/30 text-amber-300 border-amber-800' : 'bg-amber-50 text-amber-600 border-amber-100'">
                Classification
            </span>
            <span class="text-xs font-mono opacity-50">{{ formatTime(prediction.created_on) }}</span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Main Category -->
            <div class="p-4 rounded-lg border"
                :class="isDarkMode ? 'bg-neutral-900 border-neutral-700' : 'bg-gray-50 border-gray-100'">
                <div class="text-xs font-semibold uppercase tracking-wider mb-1 opacity-60">Main Category</div>
                <div class="text-lg font-bold" :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'">
                    {{ classification.main_category || 'N/A' }}
                </div>
            </div>

            <!-- Sub Category -->
            <div class="p-4 rounded-lg border"
                :class="isDarkMode ? 'bg-neutral-900 border-neutral-700' : 'bg-gray-50 border-gray-100'">
                <div class="text-xs font-semibold uppercase tracking-wider mb-1 opacity-60">Sub Category</div>
                <div class="text-lg font-bold" :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'">
                    {{ classification.sub_category || 'N/A' }}
                </div>
            </div>
        </div>

        <div v-if="classification.risk_level" class="mt-4 flex items-center gap-2 text-sm font-medium">
            <span class="opacity-60">Risk Level:</span>
            <span :class="getRiskColor(classification.risk_level)">{{ classification.risk_level }}</span>
        </div>

        <AiFeedbackWidget :call-id="prediction.src_callid" :task-type="prediction.notification_type" />
    </div>
</template>

<script setup>
    import { inject, computed } from 'vue'
    import AiFeedbackWidget from './AiFeedbackWidget.vue'

    const props = defineProps({
        prediction: Object,
        payload: Object
    })

    const isDarkMode = inject('isDarkMode')

    const classification = computed(() => {
        return props.payload.classification || props.payload || {}
    })

    const formatTime = (ts) => {
        if (!ts) return ''
        return new Date(ts * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }

    const getRiskColor = (level) => {
        const l = (level || '').toLowerCase()
        if (l === 'high' || l === 'critical') return 'text-red-500 font-bold'
        if (l === 'medium') return 'text-amber-500 font-bold'
        return 'text-green-500 font-bold'
    }
</script>

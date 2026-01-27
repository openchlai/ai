<template>
    <div class="rounded-xl border p-5 shadow-sm transition-all hover:shadow-md"
        :class="isDarkMode ? 'bg-neutral-800/50 border-neutral-700' : 'bg-white border-gray-100'">

        <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-2">
                <span class="px-2.5 py-1 rounded-md text-[10px] font-bold uppercase tracking-widest border"
                    :class="isDarkMode ? 'bg-indigo-900/30 text-indigo-300 border-indigo-800' : 'bg-indigo-50 text-indigo-600 border-indigo-100'">
                    Case Insights
                </span>
                <span class="text-xs font-mono opacity-50">{{ formatTime(prediction.created_on) }}</span>
            </div>
            <div v-if="insights.risk_level" class="px-2 py-1 rounded text-xs font-bold uppercase"
                :class="getRiskColor(insights.risk_level)">
                {{ insights.risk_level }} Risk
            </div>
        </div>

        <div class="space-y-4">
            <!-- Rationale -->
            <div v-if="insights.rationale_summary" class="text-sm leading-relaxed"
                :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'">
                <p>{{ insights.rationale_summary }}</p>
            </div>

            <!-- Disposition -->
            <div v-if="insights.suggested_disposition" class="p-3 rounded-lg border text-sm"
                :class="isDarkMode ? 'bg-neutral-900 border-neutral-700' : 'bg-gray-50 border-gray-100'">
                <div class="text-[10px] uppercase font-bold tracking-wider mb-1 opacity-60">Suggested Disposition</div>
                <div class="font-medium">{{ insights.suggested_disposition }}</div>
            </div>

            <!-- Metrics Grid -->
            <div class="grid grid-cols-2 gap-4">
                <div class="p-3 rounded-lg border"
                    :class="isDarkMode ? 'bg-neutral-900 border-neutral-700' : 'bg-gray-50 border-gray-100'">
                    <div class="text-[10px] uppercase font-bold tracking-wider mb-1 opacity-60">Confidence</div>
                    <div class="font-mono text-lg font-bold" :class="isDarkMode ? 'text-gray-200' : 'text-gray-900'">
                        {{ formatPercent(insights.confidence_score) }}
                    </div>
                </div>
                <div class="p-3 rounded-lg border"
                    :class="isDarkMode ? 'bg-neutral-900 border-neutral-700' : 'bg-gray-50 border-gray-100'">
                    <div class="text-[10px] uppercase font-bold tracking-wider mb-1 opacity-60">Priority</div>
                    <div class="font-mono text-lg font-bold" :class="isDarkMode ? 'text-gray-200' : 'text-gray-900'">
                        {{ insights.priority || 'N/A' }}
                    </div>
                </div>
            </div>
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

    const insights = computed(() => {
        return props.payload.insights || props.payload || {}
    })

    const formatTime = (ts) => {
        if (!ts) return ''
        return new Date(ts * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }

    const formatPercent = (val) => {
        if (typeof val === 'number') return (val * 100).toFixed(0) + '%'
        return val || 'N/A'
    }

    const getRiskColor = (level) => {
        const l = (level || '').toLowerCase()
        if (l === 'high' || l === 'critical') return isDarkMode ? 'bg-red-900/50 text-red-400' : 'bg-red-100 text-red-700'
        if (l === 'medium') return isDarkMode ? 'bg-amber-900/50 text-amber-400' : 'bg-amber-100 text-amber-700'
        return isDarkMode ? 'bg-green-900/50 text-green-400' : 'bg-green-100 text-green-700'
    }
</script>

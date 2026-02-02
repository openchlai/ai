<template>
    <div class="rounded-xl border p-5 shadow-sm transition-all hover:shadow-md"
        :class="isDarkMode ? 'bg-neutral-800/50 border-neutral-700' : 'bg-white border-gray-100'">

        <div class="flex items-center gap-2 mb-4">
            <span class="px-2.5 py-1 rounded-md text-[10px] font-bold uppercase tracking-widest border"
                :class="isDarkMode ? 'bg-cyan-900/30 text-cyan-300 border-cyan-800' : 'bg-cyan-50 text-cyan-600 border-cyan-100'">
                QA Scoring
            </span>
            <span class="text-xs font-mono opacity-50">{{ formatTime(prediction.created_on) }}</span>
        </div>

        <div class="space-y-6">
            <template v-for="(metrics, category) in qaData" :key="category">
                <div v-if="metrics && metrics.length > 0" class="border rounded-xl"
                    :class="isDarkMode ? 'border-neutral-700 bg-neutral-900/30' : 'border-gray-100 bg-gray-50/50'">
                    <!-- Category Header -->
                    <div class="px-4 py-3 border-b flex justify-between items-center"
                        :class="isDarkMode ? 'border-neutral-700' : 'border-gray-100'">
                        <div class="font-bold uppercase tracking-wider text-xs"
                            :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'">
                            {{ formatKey(category) }}
                        </div>
                    </div>

                    <!-- Metrics Table -->
                    <div class="p-2">
                        <table class="w-full text-sm">
                            <tbody class="divide-y" :class="isDarkMode ? 'divide-neutral-800' : 'divide-gray-100'">
                                <tr v-for="(item, idx) in metrics" :key="idx"
                                    :class="isDarkMode ? 'hover:bg-neutral-800/50' : 'hover:bg-white'">
                                    <td class="px-3 py-2 text-xs"
                                        :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'">
                                        {{ item.submetric }}
                                    </td>
                                    <td class="px-3 py-2 text-right text-xs font-mono font-bold w-20">
                                        <span :class="getScoreColor(item.probability)">
                                            {{ formatPercent(item.probability) }}
                                        </span>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </template>
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

    const qaData = computed(() => {
        return props.payload.qa_scores || props.payload || {}
    })

    const formatTime = (ts) => {
        if (!ts) return ''
        return new Date(ts * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }

    const formatKey = (key) => {
        return key.replace(/_/g, ' ').toUpperCase()
    }

    const formatPercent = (val) => {
        if (typeof val === 'number') {
            return (val * 100).toFixed(2) + '%'
        }
        return 'N/A'
    }

    const getScoreColor = (val) => {
        if (typeof val === 'number') {
            if (val >= 0.8) return 'text-green-500'
            if (val < 0.5) return 'text-red-500'
            return 'text-amber-500'
        }
        return 'text-gray-400'
    }
</script>

<template>
    <!-- Backdrop -->
    <div class="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 transition-opacity duration-300"
        @click="$emit('close')"></div>

    <!-- Panel Slide-out -->
    <div class="fixed right-0 top-0 h-full w-full md:w-[600px] shadow-2xl z-50 flex flex-col border-l animate-slide-in overflow-hidden"
        :class="isDarkMode
            ? 'bg-black border-transparent'
            : 'bg-white border-transparent'">
        <!-- Header -->
        <div class="flex items-center justify-between p-6 border-b" :class="isDarkMode
            ? 'bg-black/50 border-transparent'
            : 'bg-gray-50 border-transparent'">
            <div class="flex items-center gap-3">
                <div class="w-12 h-12 rounded-2xl flex items-center justify-center text-white shadow-lg"
                    :class="isDarkMode ? 'bg-indigo-600' : 'bg-indigo-700'">
                    <i-mdi-robot-outline class="w-7 h-7" />
                </div>
                <div>
                    <h3 class="text-xl font-bold" :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'">
                        AI Assistant
                    </h3>
                    <p class="text-xs font-medium uppercase tracking-wider"
                        :class="isDarkMode ? 'text-indigo-400' : 'text-indigo-600'">
                        Post-Call Classification
                    </p>
                </div>
            </div>
            <button @click="$emit('close')" class="p-2.5 rounded-xl transition-all hover:rotate-90" :class="isDarkMode
                ? 'hover:bg-neutral-800 text-gray-400 hover:text-white'
                : 'hover:bg-gray-200 text-gray-600 hover:text-black'">
                <i-mdi-close class="w-6 h-6" />
            </button>
        </div>

        <!-- Content -->
        <div v-if="predictionData" class="flex-1 overflow-y-auto p-6 space-y-8 custom-scrollbar"
            :class="isDarkMode ? 'bg-black' : 'bg-gray-50'">
            <!-- Summary Card -->
            <section class="space-y-4">
                <div class="p-5 rounded-2xl border shadow-sm transition-all" :class="isDarkMode
                    ? 'bg-neutral-900/50 border-neutral-800'
                    : 'bg-white border-gray-100'">
                    <div class="flex justify-between items-start mb-6">
                        <div>
                            <p :class="isDarkMode ? 'text-gray-400' : 'text-gray-500'"
                                class="text-xs uppercase font-bold tracking-widest mb-1">Confidence Score</p>
                            <div class="flex items-baseline gap-2">
                                <span class="text-4xl font-black"
                                    :class="getConfidenceColor(predictionData.payload?.classification?.confidence)">
                                    {{ (predictionData.payload?.classification?.confidence * 100).toFixed(1) }}%
                                </span>
                                <span :class="isDarkMode ? 'text-gray-500' : 'text-gray-400'"
                                    class="text-sm font-medium">Reliability</span>
                            </div>
                        </div>
                        <div class="px-4 py-2 rounded-xl text-xs font-bold uppercase tracking-wide border"
                            :class="getPriorityBadgeClass(predictionData.payload?.classification?.priority)">
                            Priority {{ predictionData.payload?.classification?.priority }}
                        </div>
                    </div>

                    <!-- Progress Bar -->
                    <div class="w-full h-3 bg-gray-200 dark:bg-neutral-800 rounded-full overflow-hidden mb-2">
                        <div class="h-full transition-all duration-1000 ease-out rounded-full"
                            :class="getConfidenceBg(predictionData.payload?.classification?.confidence)"
                            :style="{ width: (predictionData.payload?.classification?.confidence * 100) + '%' }"></div>
                    </div>
                </div>
            </section>

            <!-- Classification Breakdown -->
            <section class="space-y-4">
                <h4 :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
                    class="text-xs uppercase font-bold tracking-widest">Classification Details</h4>

                <div class="grid grid-cols-1 gap-3">
                    <div v-for="(item, key) in classificationFields" :key="key"
                        class="p-4 rounded-xl border flex justify-between items-center group transition-all" :class="isDarkMode
                            ? 'bg-neutral-900/30 border-neutral-800/50 hover:border-indigo-500/50 hover:bg-neutral-900'
                            : 'bg-white border-gray-100 hover:border-indigo-500/50 hover:shadow-md'">
                        <div>
                            <p class="text-[10px] uppercase font-bold text-gray-500 mb-0.5">{{ item.label }}</p>
                            <p class="text-sm font-semibold" :class="isDarkMode ? 'text-gray-200' : 'text-gray-900'">
                                {{ predictionData.payload?.classification?.[item.key] || 'Not specified' }}
                            </p>
                        </div>
                        <div v-if="predictionData.payload?.classification?.confidence_breakdown?.[item.key]"
                            class="text-right">
                            <p class="text-[10px] uppercase font-bold text-gray-500 mb-0.5">Confidence</p>
                            <p class="text-xs font-mono font-bold"
                                :class="getConfidenceColor(predictionData.payload?.classification?.confidence_breakdown[item.key])">
                                {{ (predictionData.payload?.classification?.confidence_breakdown[item.key] *
                                100).toFixed(1) }}%
                            </p>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Call Metadata -->
            <section class="space-y-4">
                <h4 :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
                    class="text-xs uppercase font-bold tracking-widest">Session Context</h4>
                <div class="p-5 rounded-2xl border space-y-4" :class="isDarkMode
                    ? 'bg-neutral-900/30 border-neutral-800/50'
                    : 'bg-white border-gray-100'">
                    <div class="grid grid-cols-2 gap-6">
                        <div>
                            <p class="text-[10px] uppercase font-bold text-gray-500 mb-1">Call Reference</p>
                            <p class="text-sm font-mono break-all"
                                :class="isDarkMode ? 'text-indigo-400' : 'text-indigo-700'">
                                {{ predictionData.call_metadata?.call_id }}
                            </p>
                        </div>
                        <div>
                            <p class="text-[10px] uppercase font-bold text-gray-500 mb-1">Processed At</p>
                            <p class="text-sm font-semibold" :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'">
                                {{ formatTimestamp(predictionData.timestamp) }}
                            </p>
                        </div>
                    </div>
                    <div class="pt-4 border-t" :class="isDarkMode ? 'border-neutral-800' : 'border-gray-50'">
                        <div class="flex items-center gap-2">
                            <i-mdi-check-circle-outline class="w-4 h-4 text-green-500" />
                            <span class="text-xs font-semibold uppercase tracking-wider text-green-500">Processing
                                Success</span>
                        </div>
                    </div>
                </div>
            </section>
        </div>

        <!-- Empty/Error State -->
        <div v-else class="flex-1 flex flex-col items-center justify-center p-12 text-center opacity-50">
            <i-mdi-alert-circle-outline class="w-16 h-16 mb-4" />
            <p class="text-lg font-bold">Could not parse prediction data</p>
            <p class="text-sm">The message content may be malformed or invalid.</p>
        </div>

        <!-- Footer -->
        <div class="p-6 border-t" :class="isDarkMode ? 'bg-black border-neutral-800' : 'bg-white border-gray-100'">
            <button @click="$emit('close')"
                class="w-full py-4 rounded-xl font-bold transition-all transform active:scale-[0.98] shadow-lg" :class="isDarkMode
                    ? 'bg-white text-black hover:bg-gray-200'
                    : 'bg-black text-white hover:bg-neutral-800'">
                Acknowledge Insight
            </button>
        </div>
    </div>
</template>

<script setup>
    import { computed, inject } from 'vue'

    const props = defineProps({
        msg: {
            type: [Object, Array],
            default: null
        },
        pmessages_k: {
            type: Object,
            default: () => ({})
        }
    })

    defineEmits(['close'])

    const isDarkMode = inject('isDarkMode')

    const getValue = (key) => {
        // Support normalized object
        if (props.msg && typeof props.msg === 'object' && !Array.isArray(props.msg)) {
             // specific mapping for AIPrediction
             if (key === 'src_msg') return props.msg.text
        }
    
        if (!props.msg || !props.pmessages_k?.[key]) return null
        const index = props.pmessages_k[key][0]
        return props.msg[index]
    }

    const predictionData = computed(() => {
        const rawMsg = getValue('src_msg')
        if (!rawMsg) return null

        try {
            // If it's already an object (rare but possible if normalized parsed it)
            if (typeof rawMsg === 'object') return rawMsg
            
            // If it's a string, it might be JSON (already decoded) or Base64
            if (rawMsg.trim().startsWith('{')) {
                 return JSON.parse(rawMsg)
            }
            
            // Fallback to legacy decoding
            const decoded = atob(rawMsg)
            return JSON.parse(decoded)
        } catch (e) {
            console.error('Failed to parse AI prediction:', e)
            return null
        }
    })

    const classificationFields = [
        { label: 'Primary Domain', key: 'main_category' },
        { label: 'Support Category', key: 'sub_category' },
        { label: 'Specific Violation', key: 'sub_category_2' },
        { label: 'Proposed Action', key: 'intervention' }
    ]

    const getConfidenceColor = (score) => {
        if (!score) return 'text-gray-500'
        if (score >= 0.8) return 'text-green-500'
        if (score >= 0.5) return 'text-amber-500'
        return 'text-rose-500'
    }

    const getConfidenceBg = (score) => {
        if (!score) return 'bg-gray-500'
        if (score >= 0.8) return 'bg-green-500 shadow-[0_0_15px_rgba(34,197,94,0.3)]'
        if (score >= 0.5) return 'bg-amber-500 shadow-[0_0_15px_rgba(245,158,11,0.3)]'
        return 'bg-rose-500 shadow-[0_0_15px_rgba(244,63,94,0.3)]'
    }

    const getPriorityBadgeClass = (priority) => {
        switch (String(priority)) {
            case '3': return 'bg-rose-500/10 border-rose-500/30 text-rose-500 shadow-[0_0_10px_rgba(244,63,94,0.1)]'
            case '2': return 'bg-amber-500/10 border-amber-500/30 text-amber-500'
            case '1': return 'bg-emerald-500/10 border-emerald-500/30 text-emerald-500'
            default: return 'bg-gray-500/10 border-gray-500/30 text-gray-500'
        }
    }

    const formatTimestamp = (ts) => {
        if (!ts) return 'Unknown'
        return new Date(ts).toLocaleString('en-US', {
            dateStyle: 'medium',
            timeStyle: 'short'
        })
    }
</script>

<style scoped>
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }

        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    .animate-slide-in {
        animation: slideIn 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .custom-scrollbar::-webkit-scrollbar {
        width: 6px;
    }

    .custom-scrollbar::-webkit-scrollbar-track {
        background: transparent;
    }

    .custom-scrollbar::-webkit-scrollbar-thumb {
        background: rgba(155, 155, 155, 0.2);
        border-radius: 20px;
    }

    .custom-scrollbar::-webkit-scrollbar-thumb:hover {
        background: rgba(155, 155, 155, 0.4);
    }
</style>

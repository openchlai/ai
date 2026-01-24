<template>
    <!-- Overlay -->
    <div v-if="show" class="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 transition-opacity duration-300"
        @click="$emit('close')"></div>

    <!-- Sliding Panel -->
    <div v-if="show"
        class="fixed top-0 right-0 h-full w-full md:w-[600px] shadow-2xl z-50 transform transition-all duration-300 ease-out flex flex-col overflow-hidden"
        :class="isDarkMode ? 'bg-black border-l border-transparent' : 'bg-white border-l border-transparent'">

        <!-- Header -->
        <div class="flex items-center justify-between px-6 py-4 border-b" :class="isDarkMode
            ? 'bg-black/50 border-transparent'
            : 'bg-gray-50 border-transparent'">
            <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-xl flex items-center justify-center text-white"
                    :class="isDarkMode ? 'bg-indigo-600' : 'bg-indigo-700'">
                    <i-mdi-robot-outline class="w-6 h-6" />
                </div>
                <div>
                    <h3 class="font-bold text-lg" :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'">
                        Prediction Details
                    </h3>
                    <p class="text-xs uppercase tracking-wider font-semibold"
                        :class="isDarkMode ? 'text-indigo-400' : 'text-indigo-600'">
                        AI Insight #{{ getPredictionValue('id') }}
                    </p>
                </div>
            </div>

            <div class="flex items-center gap-2">
                <button @click="copyPayload" class="p-2 rounded-lg transition-colors group" :class="isDarkMode
                    ? 'hover:bg-gray-800 text-gray-400'
                    : 'hover:bg-gray-100 text-gray-600'" title="Copy JSON Payload">
                    <i-mdi-content-copy class="w-5 h-5 group-active:scale-95" />
                </button>
                <button @click="$emit('close')" class="p-2 rounded-lg transition-colors" :class="isDarkMode
                    ? 'hover:bg-gray-700 text-gray-400'
                    : 'hover:bg-gray-100 text-gray-600'">
                    <i-mdi-close class="w-6 h-6" />
                </button>
            </div>
        </div>

        <!-- Content -->
        <div class="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar"
            :class="isDarkMode ? 'bg-black' : 'bg-gray-50'">

            <!-- Basic Info Grid -->
            <section class="grid grid-cols-2 gap-4">
                <div class="p-4 rounded-xl border transition-all"
                    :class="isDarkMode ? 'bg-neutral-900/50 border-neutral-800' : 'bg-white border-gray-100'">
                    <p class="text-[10px] uppercase font-bold text-gray-500 mb-1">Call ID</p>
                    <p class="text-sm font-mono font-semibold truncate"
                        :class="isDarkMode ? 'text-indigo-400' : 'text-indigo-700'">
                        {{ getPredictionValue('src_callid') || 'N/A' }}
                    </p>
                </div>
                <div class="p-4 rounded-xl border transition-all"
                    :class="isDarkMode ? 'bg-neutral-900/50 border-neutral-800' : 'bg-white border-gray-100'">
                    <p class="text-[10px] uppercase font-bold text-gray-500 mb-1">Created At</p>
                    <p class="text-sm font-semibold" :class="isDarkMode ? 'text-gray-200' : 'text-gray-900'">
                        {{ formatDateTime(getPredictionValue('created_on')) }}
                    </p>
                </div>
            </section>

            <!-- Processing Info -->
            <section class="grid grid-cols-2 gap-4">
                <div class="p-4 rounded-xl border transition-all"
                    :class="isDarkMode ? 'bg-neutral-900/50 border-neutral-800' : 'bg-white border-gray-100'">
                    <p class="text-[10px] uppercase font-bold text-gray-500 mb-1">Processing Mode</p>
                    <p class="text-sm font-bold uppercase tracking-wider"
                        :class="isDarkMode ? 'text-gray-200' : 'text-gray-900'">
                        {{ decodedPayload?.processing_mode?.replace('_', ' ') || 'N/A' }}
                    </p>
                </div>
                <div class="p-4 rounded-xl border transition-all"
                    :class="isDarkMode ? 'bg-neutral-900/50 border-neutral-800' : 'bg-white border-gray-100'">
                    <p class="text-[10px] uppercase font-bold text-gray-500 mb-1">Status</p>
                    <span
                        class="px-2 py-0.5 rounded-full text-[10px] font-black uppercase border tracking-widest shadow-sm inline-block"
                        :class="decodedPayload?.status === 'success' ? 'bg-green-500/10 text-green-500 border-green-500/20' : 'bg-amber-500/10 text-amber-500 border-amber-500/20'">
                        {{ decodedPayload?.status || 'N/A' }}
                    </span>
                </div>
            </section>

            <!-- Payload Analysis -->
            <section v-if="decodedPayload" class="space-y-4">
                <h4 class="text-xs uppercase font-bold tracking-widest text-gray-500">Decoded Payload</h4>

                <!-- Classification Summary -->
                <div v-if="decodedPayload.payload?.classification" class="p-5 rounded-2xl border bg-gradient-to-br"
                    :class="isDarkMode ? 'from-neutral-900 to-black border-neutral-800' : 'from-white to-gray-50 border-gray-100'">

                    <div class="flex justify-between items-center mb-6">
                        <div>
                            <p class="text-[10px] uppercase font-bold text-gray-500 mb-1">Main Category</p>
                            <h5 class="text-xl font-black text-indigo-500">{{
                                decodedPayload.payload.classification.main_category }}</h5>
                        </div>
                        <div class="text-right">
                            <p class="text-[10px] uppercase font-bold text-gray-500 mb-1">Confidence</p>
                            <p class="text-2xl font-black"
                                :class="getConfidenceColor(decodedPayload.payload.classification.confidence)">
                                {{ (decodedPayload.payload.classification.confidence * 100).toFixed(1) }}%
                            </p>
                        </div>
                    </div>

                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <p class="text-[10px] uppercase font-bold text-gray-500 mb-1">Sub Category</p>
                            <p class="text-sm font-semibold">{{ decodedPayload.payload.classification.sub_category ||
                                'N/A' }}</p>
                        </div>
                        <div>
                            <p class="text-[10px] uppercase font-bold text-gray-500 mb-1">Intervention</p>
                            <p class="text-sm font-semibold">{{ decodedPayload.payload.classification.intervention ||
                                'N/A' }}</p>
                        </div>
                    </div>
                </div>

                <!-- Full JSON View -->
                <div class="space-y-2">
                    <div class="flex justify-between items-center px-1">
                        <h4 class="text-xs uppercase font-bold tracking-widest text-gray-500">Raw JSON</h4>
                    </div>
                    <div class="rounded-xl overflow-hidden border"
                        :class="isDarkMode ? 'border-neutral-800' : 'border-gray-200'">
                        <pre class="p-4 text-xs font-mono overflow-x-auto"
                            :class="isDarkMode ? 'bg-neutral-950 text-indigo-400' : 'bg-gray-900 text-indigo-300'">{{ JSON.stringify(decodedPayload, null, 2) }}</pre>
                    </div>
                </div>
            </section>

            <!-- Failure State -->
            <div v-else class="p-12 text-center opacity-50">
                <i-mdi-alert-circle-outline class="w-12 h-12 mx-auto mb-4" />
                <p class="font-bold">Failed to decode prediction payload</p>
            </div>
        </div>
    </div>
</template>

<script setup>
    import { computed, inject } from 'vue'
    import { toast } from 'vue-sonner'

    const props = defineProps({
        show: Boolean,
        prediction: Array,
        predictions_k: Object
    })

    defineEmits(['close'])

    const isDarkMode = inject('isDarkMode')

    const getPredictionValue = (key) => {
        if (!props.prediction || !props.predictions_k?.[key]) return null
        const index = props.predictions_k[key][0]
        return props.prediction[index]
    }

    const decodedPayload = computed(() => {
        const rawMsg = getPredictionValue('src_msg')
        if (!rawMsg) return null
        try {
            return JSON.parse(atob(rawMsg))
        } catch (e) {
            console.error('Failed to parse AI prediction:', e)
            return null
        }
    })

    const formatDateTime = (timestamp) => {
        if (!timestamp) return 'N/A'
        const date = new Date(timestamp * 1000)
        return date.toLocaleString()
    }

    const getConfidenceColor = (score) => {
        if (!score) return 'text-gray-500'
        if (score >= 0.8) return 'text-green-500'
        if (score >= 0.5) return 'text-amber-500'
        return 'text-rose-500'
    }

    const copyPayload = () => {
        if (!decodedPayload.value) return
        navigator.clipboard.writeText(JSON.stringify(decodedPayload.value, null, 2))
        toast.success('JSON payload copied to clipboard')
    }
</script>

<style scoped>
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
</style>

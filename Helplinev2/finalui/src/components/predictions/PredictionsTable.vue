<template>
    <div class="space-y-4">
        <!-- Table View -->
        <div class="rounded-2xl border overflow-hidden shadow-sm transition-all"
            :class="isDarkMode ? 'bg-black border-neutral-800' : 'bg-white border-gray-200'">
            <div class="overflow-x-auto">
                <table class="w-full">
                    <thead>
                        <tr class="border-b text-xs font-bold uppercase tracking-wider text-left"
                            :class="isDarkMode ? 'bg-neutral-900/50 border-neutral-800 text-gray-400' : 'bg-gray-50/80 border-gray-100 text-gray-500'">
                            <th class="px-6 py-4">Type</th>
                            <th class="px-6 py-4">Call ID</th>
                            <th class="px-6 py-4">Created On</th>
                            <th class="px-6 py-4">Messages</th>
                            <th class="px-6 py-4 text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y" :class="isDarkMode ? 'divide-neutral-800' : 'divide-gray-100'">
                        <tr v-if="mappedPredictions.length === 0">
                            <td colspan="4" class="px-6 py-12 text-center opacity-50 text-sm">
                                No gateway predictions found.
                            </td>
                        </tr>
                        <tr v-for="item in mappedPredictions" :key="item.id"
                            class="group transition-colors cursor-pointer"
                            :class="isDarkMode ? 'hover:bg-neutral-900' : 'hover:bg-gray-50'"
                            @click="selectPrediction(item)">
                            <!-- Type -->
                            <td class="px-6 py-4">
                                <div class="flex items-center gap-2">
                                    <div class="w-2 h-2 rounded-full" :class="getTypeColor(item.notification_type)">
                                    </div>
                                    <span class="text-sm font-bold"
                                        :class="isDarkMode ? 'text-gray-200' : 'text-gray-900'">
                                        {{ formatType(item.notification_type) }}
                                    </span>
                                </div>
                            </td>

                            <!-- Call ID -->
                            <td class="px-6 py-4">
                                <div class="font-mono text-xs opacity-70"
                                    :class="isDarkMode ? 'text-gray-300' : 'text-gray-600'">
                                    {{ item.src_callid || '---' }}
                                </div>
                            </td>

                            <!-- Created On -->
                            <td class="px-6 py-4">
                                <div class="text-xs" :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'">
                                    {{ formatDateTime(item.created_on) }}
                                </div>
                            </td>

                            <!-- Messages Count -->
                            <td class="px-6 py-4">
                                <div class="text-xs font-mono" :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'">
                                    {{ item.message_count }}
                                </div>
                            </td>

                            <!-- Actions -->
                            <td class="px-6 py-4 text-right">
                                <button class="px-3 py-1.5 rounded-lg text-xs font-bold transition-colors border"
                                    :class="isDarkMode
                                        ? 'bg-neutral-800 border-neutral-700 text-gray-300 group-hover:bg-indigo-900/30 group-hover:text-indigo-400 group-hover:border-indigo-800'
                                        : 'bg-white border-gray-200 text-gray-600 group-hover:bg-indigo-50 group-hover:text-indigo-600 group-hover:border-indigo-200'">
                                    View Details
                                </button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Detail Modal/Drawer -->
        <Teleport to="body">
            <Transition name="slide-fade">
                <div v-if="selectedCallPredictions"
                    class="fixed inset-y-0 right-0 w-full md:w-[600px] lg:w-[800px] shadow-2xl z-50 flex flex-col border-l backdrop-blur-xl"
                    :class="isDarkMode ? 'bg-black/95 border-neutral-800' : 'bg-white/95 border-gray-200'">

                    <!-- Modal Header -->
                    <div class="px-6 py-4 border-b flex items-center justify-between shrink-0"
                        :class="isDarkMode ? 'border-neutral-800' : 'border-gray-100'">
                        <div>
                            <div class="text-[10px] font-black uppercase tracking-widest opacity-50 mb-1">
                                AI Predictions
                            </div>
                            <h3 class="text-lg font-bold flex items-center gap-2"
                                :class="isDarkMode ? 'text-white' : 'text-gray-900'">
                                {{ selectedCallPredictions[0]?.src_callid || 'Unknown Call' }}
                            </h3>
                        </div>

                        <div class="flex items-center gap-2">
                            <!-- Edit Button (Mock) -->
                            <button
                                class="px-4 py-2 rounded-lg text-xs font-bold transition-colors border flex items-center gap-2"
                                :class="isDarkMode ? 'bg-neutral-800 border-neutral-700 text-gray-300 hover:bg-neutral-700' : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50'">
                                <i-mdi-pencil class="w-4 h-4" />
                                Edit
                            </button>

                            <button @click="closeModal"
                                class="p-2 rounded-full transition-colors hover:scale-110 active:scale-95"
                                :class="isDarkMode ? 'bg-neutral-800 hover:bg-neutral-700 text-gray-400' : 'bg-gray-100 hover:bg-gray-200 text-gray-600'">
                                <i-mdi-close class="w-5 h-5" />
                            </button>
                        </div>
                    </div>

                    <!-- Modal Content (Scrollable) -->
                    <div class="flex-1 overflow-y-auto p-6 scrollbar-hide space-y-8">
                        <div v-for="pred in selectedCallPredictions" :key="pred.id">
                            <component :is="getComponent(pred.notification_type)" :prediction="pred"
                                :payload="pred.payload" />
                        </div>

                        <div v-if="selectedCallPredictions.length === 0" class="text-center opacity-50">
                            No details found.
                        </div>
                    </div>
                </div>
            </Transition>

            <!-- Backdrop -->
            <Transition name="fade">
                <div v-if="selectedCallPredictions" @click="closeModal"
                    class="fixed inset-0 bg-black/40 backdrop-blur-sm z-40">
                </div>
            </Transition>
        </Teleport>
    </div>
</template>

<script setup>
    import { ref, inject, computed, watch } from 'vue'

    // Import specialized components
    import AiTranscriptCard from './AiTranscriptCard.vue'
    import AiTranslationCard from './AiTranslationCard.vue'
    import AiClassificationCard from './AiClassificationCard.vue'
    import AiEntitiesCard from './AiEntitiesCard.vue'
    import AiSummaryCard from './AiSummaryCard.vue'
    import AiQaScoringCard from './AiQaScoringCard.vue'
    import AiCompleteCard from './AiCompleteCard.vue'
    import AiInsightsCard from './AiInsightsCard.vue'

    // Generic fallback
    const AiGenericCard = {
        template: '<div class="p-4 border rounded text-xs font-mono opacity-50">Unknown Type: {{ prediction.notification_type }}<br>Check console for payload.</div>',
        props: ['prediction', 'payload']
    }

    const props = defineProps({
        predictions: Array,
        predictions_k: Object
    })

    const isDarkMode = inject('isDarkMode')
    const selectedCallPredictions = ref(null)

    watch(selectedCallPredictions, (val) => {
        console.log('selectedCallPredictions changed:', val)
    })

    const AI_TEMPLATE_MAP = {
        post_call_transcription: AiTranscriptCard,
        postcall_transcription: AiTranscriptCard,
        post_call_translation: AiTranslationCard,
        postcall_translation: AiTranslationCard,
        post_call_classification: AiClassificationCard,
        postcall_classification: AiClassificationCard,
        post_call_entities: AiEntitiesCard,
        postcall_entities: AiEntitiesCard,
        post_call_summary: AiSummaryCard,
        postcall_summary: AiSummaryCard,
        post_call_mistral_insights: AiInsightsCard,
        postcall_mistral_insights: AiInsightsCard,
        post_call_qa_scoring: AiQaScoringCard,
        postcall_qa_scoring: AiQaScoringCard,
        post_call_complete: AiCompleteCard,
        postcall_complete: AiCompleteCard
    }

    const PRIORITY_ORDER = [
        'post_call_transcription',
        'post_call_translation',
        'post_call_classification',
        'post_call_entities',
        'post_call_summary',
        'post_call_mistral_insights',
        'post_call_qa_scoring',
        'post_call_complete'
    ]

    const normalizeType = (type) => {
        if (!type) return ''
        return type.replace(/^postcall_/, 'post_call_')
    }

    const getComponent = (type) => {
        if (!type) return AiGenericCard
        const t = type.trim()
        const normalized = t.replace(/^postcall_/, 'post_call_')
        // console.log(`getComponent: '${type}' -> '${normalized}' found=${!!AI_TEMPLATE_MAP[normalized]}`)
        return AI_TEMPLATE_MAP[normalized] || AI_TEMPLATE_MAP[t] || AiGenericCard
    }

    const getValue = (row, key) => {
        // Try dynamic lookup first
        if (props.predictions_k && props.predictions_k[key]) {
            return row[props.predictions_k[key][0]]
        }

        // Fallback to hardcoded indices based on legacy structure
        const FALLBACK_INDICES = {
            'id': 0,
            'created_on': 1,
            'src_address': 9,
            'src_callid': 12,
            'in_count': 17,
            'out_count': 18,
            'src_msg': 21
        }

        if (FALLBACK_INDICES[key] !== undefined) {
            return row[FALLBACK_INDICES[key]]
        }

        return null
    }

    const formatDateTime = (ts) => {
        if (!ts) return 'N/A'
        return new Date(ts * 1000).toLocaleString()
    }

    const formatType = (type) => {
        if (!type) return 'Unknown'
        // Handle both formats for display
        return type.replace(/^post_?call_/, '').replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
    }

    const getTypeColor = (type) => {
        const norm = normalizeType(type)
        const colors = {
            post_call_transcription: 'bg-blue-500',
            post_call_translation: 'bg-indigo-500',
            post_call_classification: 'bg-purple-500',
            post_call_entities: 'bg-pink-500',
            post_call_summary: 'bg-amber-500',
            post_call_qa_scoring: 'bg-emerald-500',
            post_call_complete: 'bg-gray-500'
        }
        return colors[norm] || 'bg-gray-400'
    }

    // Main Processing Logic
    const mappedPredictions = computed(() => {
        if (!props.predictions || !props.predictions_k) return []

        const rows = []

        props.predictions.forEach(row => {
            // 1. Filter Gateway
            const srcAddress = getValue(row, 'src_address')
            // Debug log every few rows or if it's gateway
            // console.log('Checking row:', srcAddress, row) 

            if (srcAddress !== 'gateway') return

            // 2. Decode Payload
            const srcMsg = getValue(row, 'src_msg')
            if (!srcMsg) {
                console.warn('Gateway row missing src_msg', row)
                return
            }

            let decoded = {}
            try {
                decoded = JSON.parse(atob(srcMsg))
            } catch (e) {
                console.warn('Failed to decode prediction msg', e, srcMsg)
                return
            }

            const inCount = parseInt(getValue(row, 'in_count') || 0)
            const outCount = parseInt(getValue(row, 'out_count') || 0)

            // 3. Map Fields
            rows.push({
                id: getValue(row, 'id'),
                created_on: getValue(row, 'created_on'),
                src_callid: getValue(row, 'src_callid'),
                notification_type: decoded.notification_type,
                payload: decoded.payload,
                call_metadata: decoded.call_metadata,
                message_count: inCount + outCount,
                raw_row: row
            })
        })

        // 4. Sort Semantically: CallID -> Priority
        // User requested: "Sort predictions by a semantic priority order, not by timestamp"
        return rows.sort((a, b) => {
            // Primary: Call ID (Group context)
            if (a.src_callid !== b.src_callid) {
                return (a.src_callid || '').localeCompare(b.src_callid || '')
            }

            // Secondary: Priority Order
            const idxA = PRIORITY_ORDER.indexOf(a.notification_type)
            const idxB = PRIORITY_ORDER.indexOf(b.notification_type)

            if (idxA !== -1 && idxB !== -1) return idxA - idxB
            if (idxA !== -1) return -1
            if (idxB !== -1) return 1

            return 0
        })
    })

    // Group Selection Logic
    const isLoading = ref(false)

    const selectPrediction = async (item) => {
        const callId = item.src_callid
        console.log('Selecting prediction:', item.id, callId)

        // Open modal immediately with loading state or fallback
        isLoading.value = true
        selectedCallPredictions.value = [item] // Show clicked item initially if possible

        try {
            // Fetch detailed thread/context
            // User indicated URL: /api/pmessages/16340?
            // Using /api-proxy/api/ to route correctly to backend resource
            const url = `/api-proxy/api/pmessages/${item.id}?`
            // console.log('Fetching details from:', url)
            const res = await fetch(url)
            if (!res.ok) throw new Error('Failed to fetch details')

            const data = await res.json()
            console.log('Fetched details:', data)

            // The 'messages' array in the response contains independent AI predictions
            if (data.messages && data.messages_k) {
                const detailedRows = []
                data.messages.forEach(row => {
                    // Use local mapping helper for this response's schema [messages_k]
                    // Fallback indices might be different for 'messages' vs 'pmessages'
                    // but usually consistent if created by same backend.
                    // User JSON shows messages_k. src_msg key is needed.

                    const getKeyIndex = (k) => {
                        if (data.messages_k[k]) return data.messages_k[k][0]
                        return -1
                    }

                    // For 'messages', src_msg might be labeled 'src_msg' or 'msg'?
                    // User JSON for messages_k shows: "src_msg": ["17", "src_msg", "", "Message", ""]
                    // The index is 17.
                    // My FALLBACK has index 21 for pmessages.
                    // So I must rely on messages_k dynamically.

                    const idxSrcMsg = getKeyIndex('src_msg')
                    const idxCallId = getKeyIndex('src_callid')
                    const idxCreated = getKeyIndex('created_on')
                    const idxIn = getKeyIndex('in_count')
                    const idxOut = getKeyIndex('out_count')
                    const idxAddress = getKeyIndex('src_address')

                    let decoded = {}
                    let srcMsg = null

                    if (idxSrcMsg !== -1) {
                        srcMsg = row[idxSrcMsg]
                        try {
                            decoded = JSON.parse(atob(srcMsg))
                        } catch (e) {
                            // console.warn('Decode fail', e)
                        }
                    }

                    if (decoded.notification_type) {
                        detailedRows.push({
                            id: data.messages_k.id ? row[data.messages_k.id[0]] : null,
                            created_on: idxCreated !== -1 ? row[idxCreated] : null,
                            src_callid: idxCallId !== -1 ? row[idxCallId] : null,
                            notification_type: decoded.notification_type,
                            payload: decoded.payload,
                            call_metadata: decoded.call_metadata,
                            message_count: 0, // Detail rows usually individual
                            raw_row: row
                        })
                    }
                })

                // If found related items, use them.
                if (detailedRows.length > 0) {
                    console.log(`Found ${detailedRows.length} detailed items via API`)
                    selectedCallPredictions.value = detailedRows.sort((a, b) => {
                        const idxA = PRIORITY_ORDER.indexOf(normalizeType(a.notification_type))
                        const idxB = PRIORITY_ORDER.indexOf(normalizeType(b.notification_type))
                        if (idxA !== -1 && idxB !== -1) return idxA - idxB
                        if (idxA !== -1) return -1
                        if (idxB !== -1) return 1
                        return 0
                    })
                }
            }

        } catch (e) {
            console.error('Error fetching prediction details:', e)
            // Fallback to local filter if API fails (current behavior)
            if (callId) {
                const related = mappedPredictions.value.filter(p => p.src_callid === callId)
                if (related.length > 0) selectedCallPredictions.value = related // sort...
            }
        } finally {
            isLoading.value = false
        }
    }

    const closeModal = () => {
        selectedCallPredictions.value = null
    }

</script>

<style scoped>

    .slide-fade-enter-active,
    .slide-fade-leave-active {
        transition: all 0.3s ease-out;
    }

    .slide-fade-enter-from,
    .slide-fade-leave-to {
        transform: translateX(100%);
        opacity: 0;
    }

    .fade-enter-active,
    .fade-leave-active {
        transition: opacity 0.3s ease;
    }

    .fade-enter-from,
    .fade-leave-to {
        opacity: 0;
    }
</style>

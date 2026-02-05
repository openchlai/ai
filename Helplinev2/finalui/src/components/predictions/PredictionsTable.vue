<template>
    <div class="space-y-4">
        <!-- Table View -->
        <div class="rounded-2xl border overflow-hidden shadow-sm transition-all"
            :class="isDarkMode ? 'bg-black border-neutral-800' : 'bg-white border-gray-200'">
            <div class="overflow-x-auto">
                <table class="w-full">
                    <thead>
                        <tr class="border-b text-[10px] font-black uppercase tracking-[0.2em] text-left"
                            :class="isDarkMode ? 'bg-neutral-900/50 border-neutral-800 text-gray-500' : 'bg-gray-50/80 border-gray-100 text-gray-400'">
                            <th class="px-6 py-5">Date</th>
                            <th class="px-6 py-5">Direction</th>
                            <th class="px-6 py-5">Phone</th>
                            <th class="px-6 py-5">Extension</th>
                            <th class="px-6 py-5">Source</th>
                            <th class="px-6 py-5 text-center">Messages</th>
                            <th class="px-6 py-5 text-center">Replies</th>
                            <th class="px-6 py-5 text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y" :class="isDarkMode ? 'divide-neutral-800' : 'divide-gray-100'">
                        <tr v-if="mappedPredictions.length === 0">
                            <td colspan="8" class="px-6 py-24 text-center">
                                <div class="flex flex-col items-center opacity-30">
                                    <i-mdi-database-off class="w-12 h-12 mb-4" />
                                    <p class="text-sm font-bold uppercase tracking-widest">No Records Found</p>
                                </div>
                            </td>
                        </tr>
                        <tr v-for="item in mappedPredictions" :key="item.id"
                            class="group transition-all cursor-pointer duration-300"
                            :class="isDarkMode ? 'hover:bg-indigo-500/5' : 'hover:bg-gray-50/50'"
                            @click="selectPrediction(item)">

                            <!-- Date -->
                            <td class="px-6 py-5">
                                <div class="text-xs font-bold whitespace-nowrap"
                                    :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'">
                                    {{ formatDateTime(item.created_on) }}
                                </div>
                            </td>

                            <!-- Direction -->
                            <td class="px-6 py-5">
                                <span
                                    class="text-[10px] font-black uppercase tracking-widest px-2 py-0.5 rounded border"
                                    :class="isDarkMode ? 'bg-blue-900/10 text-blue-400 border-blue-800/30' : 'bg-blue-50 text-blue-600 border-blue-100'">
                                    Inbound
                                </span>
                            </td>

                            <!-- Phone -->
                            <td class="px-6 py-5">
                                <div class="font-mono text-sm font-bold tracking-tight"
                                    :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'">
                                    {{ item.src_address || 'gateway' }}
                                </div>
                                <div class="text-[10px] mt-0.5 opacity-50 font-semibold"
                                    :class="isDarkMode ? 'text-gray-400' : 'text-gray-500'">
                                    ID: {{ item.src_callid }}
                                </div>
                            </td>

                            <!-- Extension -->
                            <td class="px-6 py-5 text-xs opacity-50">---</td>

                            <!-- Source -->
                            <td class="px-6 py-5">
                                <div class="flex items-center gap-2">
                                    <div class="w-1.5 h-1.5 rounded-full" :class="getTypeColor(item.notification_type)">
                                    </div>
                                    <span class="text-[11px] font-black uppercase tracking-wider">AI</span>
                                </div>
                            </td>

                            <!-- Messages Count -->
                            <td class="px-6 py-5 text-center">
                                <span class="font-mono text-sm font-bold"
                                    :class="isDarkMode ? 'text-indigo-400' : 'text-indigo-600'">
                                    {{ item.message_count }}
                                </span>
                            </td>

                            <!-- Replies -->
                            <td class="px-6 py-5 text-center text-xs opacity-50">0</td>

                            <!-- Actions -->
                            <td class="px-6 py-5 text-right">
                                <button
                                    class="p-2.5 rounded-xl transition-all border shadow-sm group-hover:rotate-12 active:scale-90"
                                    :class="isDarkMode
                                        ? 'bg-neutral-900 border-neutral-700 text-gray-400 group-hover:bg-indigo-500 group-hover:text-white group-hover:border-indigo-400'
                                        : 'bg-white border-gray-200 text-gray-500 group-hover:bg-indigo-600 group-hover:text-white group-hover:border-indigo-500'">
                                    <i-mdi-eye-outline class="w-5 h-5" />
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
        post_call_summarization: AiSummaryCard,
        postcall_summarization: AiSummaryCard,
        post_call_mistral_insights: AiInsightsCard,
        postcall_mistral_insights: AiInsightsCard,
        post_call_insights: AiInsightsCard,
        postcall_insights: AiInsightsCard,
        post_call_qa_scoring: AiQaScoringCard,
        postcall_qa_scoring: AiQaScoringCard,
        post_call_complete: AiCompleteCard,
        postcall_complete: AiCompleteCard
    }

    const PRIORITY_ORDER = [
        'post_call_mistral_insights',
        'post_call_insights',
        'post_call_summary',
        'post_call_summarization',
        'post_call_classification',
        'post_call_qa_scoring',
        'post_call_entities',
        'post_call_translation',
        'post_call_transcription',
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

    const FALLBACK_INDICES = {
        id: [0],
        created_on: [1],
        created_by: [2],
        src: [5],
        src_ts: [6],
        src_uid: [7],
        src_address: [9],
        src_vector: [11],
        src_callid: [12],
        src_mime: [16],
        in_count: [17],
        out_count: [18],
        src_msg: [21]
    }

    const getValue = (row, key) => {
        // 1. Try dynamic lookup (Primary)
        if (props.predictions_k && props.predictions_k[key]) {
            return row[props.predictions_k[key][0]]
        }

        // 2. Try variations
        const variations = {
            src_callid: ['callid', 'call_id', 'src_callid'],
            src_msg: ['msg', 'message', 'text', 'content', 'src_msg'],
            created_on: ['dth', 'timestamp', 'created_on'],
            in_count: ['in_count', 'count_in'],
            out_count: ['out_count', 'count_out']
        }

        if (variations[key]) {
            for (const v of variations[key]) {
                if (props.predictions_k?.[v]) return row[props.predictions_k[v][0]]
            }
        }

        // 3. Ultimate Fallback (Positional based on User Schema)
        if (FALLBACK_INDICES[key]) {
            return row[FALLBACK_INDICES[key][0]]
        }

        return null
    }

    const getBadgeStyles = (type) => {
        const norm = normalizeType(type)
        const isDark = isDarkMode.value

        const base = isDark ? 'bg-neutral-900 border-neutral-700 text-gray-400' : 'bg-gray-50 border-gray-100 text-gray-500'

        const variants = {
            post_call_mistral_insights: isDark ? 'bg-rose-500/10 border-rose-500/20 text-rose-400' : 'bg-rose-50 border-rose-100 text-rose-600',
            post_call_insights: isDark ? 'bg-rose-500/10 border-rose-500/20 text-rose-400' : 'bg-rose-50 border-rose-100 text-rose-600',
            post_call_summary: isDark ? 'bg-amber-500/10 border-amber-500/20 text-amber-400' : 'bg-amber-50 border-amber-100 text-amber-600',
            post_call_summarization: isDark ? 'bg-amber-500/10 border-amber-500/20 text-amber-400' : 'bg-amber-50 border-amber-100 text-amber-600',
            post_call_classification: isDark ? 'bg-indigo-500/10 border-indigo-500/20 text-indigo-400' : 'bg-indigo-50 border-indigo-100 text-indigo-600',
            post_call_qa_scoring: isDark ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' : 'bg-emerald-50 border-emerald-100 text-emerald-600',
            post_call_complete: isDark ? 'bg-slate-500/10 border-slate-500/20 text-slate-400' : 'bg-slate-50 border-slate-100 text-slate-600'
        }

        return variants[norm] || base
    }

    const formatDateTime = (ts) => {
        if (!ts) return 'N/A'
        return new Date(ts * 1000).toLocaleString()
    }

    const formatType = (type) => {
        if (!type) return 'Unknown'
        const norm = normalizeType(type)
        if (norm === 'post_call_complete') return 'Analysis Ready'

        return type.replace(/^post_?call_/, '').replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
    }

    const getTypeColor = (type) => {
        const norm = normalizeType(type)
        const colors = {
            post_call_mistral_insights: 'bg-rose-500',
            post_call_insights: 'bg-rose-500',
            post_call_summary: 'bg-amber-500',
            post_call_summarization: 'bg-amber-500',
            post_call_classification: 'bg-indigo-500',
            post_call_qa_scoring: 'bg-emerald-500',
            post_call_entities: 'bg-pink-500',
            post_call_translation: 'bg-blue-500',
            post_call_transcription: 'bg-blue-300',
            post_call_complete: 'bg-gray-400'
        }
        return colors[norm] || 'bg-gray-400'
    }

    // Main Processing Logic
    const mappedPredictions = computed(() => {
        if (!props.predictions || !props.predictions_k) return []

        const rows = []

        props.predictions.forEach(row => {
            // 2. Decode Payload
            const srcMsg = getValue(row, 'src_msg')
            if (!srcMsg) return

            let decoded = {}
            try {
                // Try JSON first
                if (srcMsg.trim().startsWith('{')) {
                    decoded = JSON.parse(srcMsg)
                } else {
                    const cleanBase64 = srcMsg.trim().replace(/[^A-Za-z0-9+/=]/g, "");
                    decoded = JSON.parse(atob(cleanBase64))
                }
            } catch (e) {
                return
            }

            const inCount = parseInt(getValue(row, 'in_count') || 0)
            const outCount = parseInt(getValue(row, 'out_count') || 0)

            // 3. Map Fields
            // Use top level callid or fall back to payload metadata
            const callId = getValue(row, 'src_callid') || decoded.call_metadata?.call_id || decoded.call_metadata?.src_callid

            // Source Address (Phone number)
            const address = decoded.call_metadata?.callerid || decoded.call_metadata?.phone || getValue(row, 'src_address')

            rows.push({
                id: getValue(row, 'id'),
                created_on: getValue(row, 'created_on'),
                src_callid: callId,
                src_address: address,
                notification_type: decoded.notification_type,
                payload: decoded.payload,
                call_metadata: decoded.call_metadata,
                message_count: inCount + outCount,
                raw_row: row
            })
        })

        // 4. Group by Address (Caller ID) - combining all events from the same person into one row
        const groups = {}
        rows.forEach(r => {
            const cid = r.src_address || `unknown-${r.id}`
            if (!groups[cid]) {
                groups[cid] = {
                    src_callid: r.src_callid,
                    src_address: cid,
                    created_on: r.created_on,
                    predictions: []
                }
            }
            groups[cid].predictions.push(r)

            // Keep the latest created_on for the table row (newest activity)
            if (r.created_on > groups[cid].created_on) {
                groups[cid].created_on = r.created_on
            }
            // Update callid if missing
            if (!groups[cid].src_callid && r.src_callid) {
                groups[cid].src_callid = r.src_callid
            }
        })

        // 5. Select Primary prediction to display for each group
        return Object.values(groups).map(g => {
            // Sort internal predictions by priority (Insights > Summary > Transcription)
            g.predictions.sort((a, b) => {
                const idxA = PRIORITY_ORDER.indexOf(normalizeType(a.notification_type))
                const idxB = PRIORITY_ORDER.indexOf(normalizeType(b.notification_type))
                if (idxA !== -1 && idxB !== -1) return idxA - idxB
                if (idxA !== -1) return -1
                if (idxB !== -1) return 1
                return 0
            })

            const primary = g.predictions[0]

            // The 'message_count' should be the highest of:
            // 1. The sum of in_count + out_count from the primary record (often provided by gateway)
            // 2. The actual number of grouped rows found for this call
            const totalMessages = Math.max(primary.message_count, g.predictions.length)

            return {
                ...primary,
                message_count: totalMessages,
                child_predictions: g.predictions
            }
        }).sort((a, b) => b.created_on - a.created_on) // Newest first
    })

    // Group Selection Logic
    const isLoading = ref(false)

    const selectPrediction = async (item) => {
        const callId = item.src_callid
        console.log('Selecting prediction:', item.id, callId)

        // Open modal immediately with local group data for instant feedback
        isLoading.value = true
        selectedCallPredictions.value = item.child_predictions || [item]

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
                        if (k === 'src_callid' && data.messages_k['callid']) return data.messages_k['callid'][0]
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
                        const rowCallId = idxCallId !== -1 ? row[idxCallId] : null
                        const finalCallId = rowCallId || decoded.call_metadata?.call_id || decoded.call_metadata?.src_callid

                        detailedRows.push({
                            id: data.messages_k.id ? row[data.messages_k.id[0]] : null,
                            created_on: idxCreated !== -1 ? row[idxCreated] : null,
                            src_callid: finalCallId,
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
                    // console.log(`Found ${detailedRows.length} detailed items via API`)
                    selectedCallPredictions.value = detailedRows.map(row => ({
                        ...row,
                        // Ensure src_callid is never null if we have it from the parent
                        src_callid: row.src_callid || callId
                    })).sort((a, b) => {
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

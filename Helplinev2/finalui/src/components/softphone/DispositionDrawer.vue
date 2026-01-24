<template>
    <Transition enter-active-class="transform transition ease-in-out duration-300" enter-from-class="translate-x-full"
        enter-to-class="translate-x-0" leave-active-class="transform transition ease-in-out duration-300"
        leave-from-class="translate-x-0" leave-to-class="translate-x-full">
        <div v-if="isOpen"
            class="fixed inset-y-0 right-0 w-[400px] z-[110] flex shadow-2xl bg-white dark:bg-neutral-900 border-l border-gray-200 dark:border-neutral-800">
            <div class="flex flex-col w-full h-full">
                <div class="p-6 border-b dark:border-neutral-800 flex justify-between items-center">
                    <h2 class="text-lg font-black dark:text-white">Call Disposition</h2>
                    <button @click="$emit('close')"
                        class="p-2 hover:bg-gray-100 dark:hover:bg-neutral-800 rounded-full">
                        <i-mdi-close class="w-5 h-5 dark:text-gray-400" />
                    </button>
                </div>

                <div class="p-6 flex-1 overflow-y-auto space-y-4">
                    <p class="text-sm dark:text-gray-400">Select the outcome of the call:</p>

                    <div class="space-y-2">
                        <button v-for="opt in options" :key="opt" @click="selectOption(opt)"
                            class="w-full text-left px-4 py-3 rounded-xl border dark:border-neutral-700 hover:border-amber-500 dark:hover:border-amber-500 transition-all font-medium text-sm"
                            :class="selected === opt ? 'bg-amber-50 dark:bg-amber-900/20 border-amber-500 text-amber-700 dark:text-amber-500' : 'dark:text-gray-300'">
                            {{ opt }}
                        </button>
                    </div>

                    <div v-if="selected === 'Other'" class="mt-4">
                        <label
                            class="text-xs font-bold uppercase tracking-widest block mb-2 dark:text-gray-400">Notes</label>
                        <textarea v-model="notes"
                            class="w-full rounded-lg border p-3 text-sm dark:bg-neutral-800 dark:border-neutral-700"></textarea>
                    </div>

                    <!-- History Section -->
                    <div class="mt-8 pt-8 border-t dark:border-neutral-800">
                        <h3 class="text-xs font-bold uppercase tracking-widest mb-4 dark:text-gray-400">Previous Dispositions</h3>
                        <div v-if="loadingHistory" class="flex justify-center p-4">
                            <i-mdi-loading class="w-6 h-6 animate-spin text-amber-500" />
                        </div>
                        <div v-else-if="history.length === 0" class="text-xs text-gray-500 text-center py-4">
                            No previous records for this number
                        </div>
                        <div v-else class="space-y-3">
                            <div v-for="(item, idx) in history" :key="idx" 
                                class="p-3 rounded-lg bg-gray-50 dark:bg-neutral-800/50 border border-gray-100 dark:border-neutral-800">
                                <div class="flex justify-between items-start mb-1">
                                    <span class="text-xs font-bold text-amber-600">{{ item.outcome }}</span>
                                    <span class="text-[10px] text-gray-400">{{ item.date }}</span>
                                </div>
                                <p v-if="item.notes" class="text-[11px] text-gray-600 dark:text-gray-400 italic">"{{ item.notes }}"</p>
                                <div class="mt-1 text-[9px] text-gray-400 flex items-center gap-1">
                                    <i-mdi-account class="w-2.5 h-2.5" />
                                    {{ item.agent }}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="p-6 border-t dark:border-neutral-800">
                    <button @click="submit" :disabled="!selected"
                        class="w-full py-3 bg-amber-600 hover:bg-amber-500 text-white rounded-xl font-bold uppercase tracking-widest shadow-lg disabled:opacity-50 disabled:cursor-not-allowed">
                        Save Disposition
                    </button>
                </div>
            </div>
        </div>
    </Transition>

    <div v-if="isOpen" @click="$emit('close')" class="fixed inset-0 bg-black/20 z-[105] backdrop-blur-sm"></div>
</template>

<script setup>
    import { ref, watch } from 'vue'
    import { toast } from 'vue-sonner'
    import axiosInstance from '@/utils/axios'

    const props = defineProps({
        isOpen: Boolean,
        callId: String,
        phone: String
    })

    const emit = defineEmits(['close', 'submit'])

    const options = ['Prank Call', 'No Answer', 'Dropped Call', 'General Inquiry', 'Wrong Number', 'Escalated', 'Other']
    const selected = ref(null)
    const notes = ref('')
    const history = ref([])
    const loadingHistory = ref(false)

    // Watch for drawer open to fetch history
    watch(() => props.isOpen, (newVal) => {
        if (newVal && props.phone) {
            fetchHistory()
        }
    })

    async function fetchHistory() {
        loadingHistory.value = true
        history.value = []
        try {
            const { data } = await axiosInstance.get('api/dispositions/', {
                params: {
                    reporter_phone: props.phone,
                    _c: 10
                }
            })
            
            // Map backend structure to UI structure
            if (data.dispositions && data.dispositions_k) {
                const k = data.dispositions_k
                history.value = data.dispositions.map(row => ({
                    outcome: row[k.outcome_txt?.[0]] || 'Other',
                    notes: row[k.notes?.[0]] || '',
                    date: row[k.created_on?.[0]] || 'Unknown date',
                    agent: row[k.created_by?.[0]] || 'Agent'
                }))
            }
        } catch (e) {
            console.error('Failed to fetch disposition history:', e)
        } finally {
            loadingHistory.value = false
        }
    }

    const selectOption = (opt) => {
        selected.value = opt
    }

    const submit = async () => {
        console.log('Disposing call', props.callId, selected.value, notes.value)
        try {
            // Placeholder for real API submission logic if needed
            toast.success('Disposition Saved')
            emit('close')
            emit('submit', { reason: selected.value, notes: notes.value })
        } catch (e) {
            toast.error('Failed to save disposition')
        }
    }
</script>

<template>
    <div class="mt-4 pt-4 border-t border-dashed" :class="isDarkMode ? 'border-gray-700' : 'border-gray-200'">
        <div class="flex items-center justify-between">
            <h4 class="text-xs font-semibold uppercase tracking-wider"
                :class="isDarkMode ? 'text-gray-400' : 'text-gray-500'">
                Feedback
            </h4>
            <div v-if="callId && taskType" class="flex gap-1">
                <button v-for="star in 5" :key="star" @click="setRating(star)"
                    class="focus:outline-none transition-colors duration-200"
                    :class="star <= rating ? 'text-amber-400' : (isDarkMode ? 'text-neutral-700 hover:text-neutral-500' : 'text-gray-300 hover:text-gray-400')">
                    <i-mdi-star class="w-5 h-5" />
                </button>
            </div>
            <div v-else class="text-[10px] opacity-30 italic">Feedback unavailable</div>
        </div>

        <div v-if="rating > 0" class="mt-3 space-y-3 animate-fadeIn">
            <textarea v-model="comment" rows="2" placeholder="Optional comments..."
                class="w-full rounded-lg text-sm p-3 focus:outline-none focus:ring-2 transition-all resize-none" :class="isDarkMode
                    ? 'bg-neutral-900 border border-neutral-700 text-gray-200 focus:ring-indigo-500/50'
                    : 'bg-white border border-gray-200 text-gray-700 focus:ring-indigo-500/30'"></textarea>

            <div class="flex justify-end">
                <button @click="submitFeedback" :disabled="submitting"
                    class="px-4 py-1.5 rounded-lg text-xs font-bold uppercase tracking-wide text-white transition-all shadow-sm"
                    :class="submitting
                        ? 'opacity-50 cursor-not-allowed bg-gray-500'
                        : 'bg-indigo-600 hover:bg-indigo-700 active:scale-95'">
                    {{ submitting ? 'Sending...' : 'Submit Feedback' }}
                </button>
            </div>
        </div>
    </div>
</template>

<script setup>
    import { ref, inject } from 'vue'
    import { toast } from 'vue-sonner'
    import axiosInstance from '@/utils/axios'

    const props = defineProps({
        callId: {
            type: [String, Number],
            required: true
        },
        taskType: {
            type: String,
            required: true
        }
    })

    const isDarkMode = inject('isDarkMode')
    const rating = ref(0)
    const comment = ref('')
    const submitting = ref(false)

    const setRating = (val) => {
        rating.value = val
    }

    const submitFeedback = async () => {
        if (rating.value === 0) return

        submitting.value = true
        try {
            await axiosInstance.post('api/feedback/', {
                call_id: props.callId,
                task_type: props.taskType,
                rating: rating.value,
                comment: comment.value
            })
            toast.success('Feedback submitted successfully')
            // Reset after success if desired, or keep it to show state
            // comment.value = '' 
            // rating.value = 0
        } catch (err) {
            console.error('Feedback error:', err)
            toast.error('Failed to submit feedback')
        } finally {
            submitting.value = false
        }
    }
</script>

<style scoped>
    .animate-fadeIn {
        animation: fadeIn 0.3s ease-out;
    }

    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(-5px);
        }

        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
</style>

import { ref, computed, reactive } from 'vue'
import axiosInstance from '@/utils/axios'
import { QA_RUBRIC } from './qaRubric'
import { toast } from 'vue-sonner'

export function useQaForm() {
    const isOpen = ref(false)
    const isLoading = ref(false)
    const currentCall = ref(null)

    // Form State
    const scores = reactive({})
    const comments = reactive({})
    const generalFeedback = ref('')

    // Initialize scores
    const initForm = () => {
        QA_RUBRIC.forEach(cat => {
            cat.criteria.forEach(crit => {
                scores[crit.id] = 0 // Default to 0? Or null? Legacy implies 0-2. Let's start at 0.
            })
            comments[cat.category] = ''
        })
        generalFeedback.value = ''
    }

    const openForm = (call) => {
        currentCall.value = call
        initForm()
        isOpen.value = true
    }

    const closeForm = () => {
        isOpen.value = false
        currentCall.value = null
    }

    // Calculations
    const categoryScores = computed(() => {
        const result = {}
        QA_RUBRIC.forEach(cat => {
            let sum = 0
            cat.criteria.forEach(crit => {
                sum += (scores[crit.id] || 0)
            })
            result[cat.category] = {
                score: sum,
                max: cat.maxScore,
                percentage: (sum / cat.maxScore) * 100
            }
        })
        return result
    })

    const totalScore = computed(() => {
        let sum = 0
        QA_RUBRIC.forEach(cat => {
            cat.criteria.forEach(crit => {
                sum += (scores[crit.id] || 0)
            })
        })
        return sum
    })

    const totalMaxScore = 34

    const totalPercentage = computed(() => {
        return Math.round((totalScore.value / totalMaxScore) * 100)
    })

    // Submit
    const submitQa = async () => {
        if (!currentCall.value) return

        isLoading.value = true
        try {
            const payload = {
                chan_uniqueid: currentCall.value.uniqueid || currentCall.value[1], // Handle array/obj mismatch if any
                ...scores, // Spread criterion scores (e.g. accuracy: 2)
                ...comments, // Spread category comments if backend accepts specific keys? 
                // Legacy system often accepted generic 'comments' or specific fields. 
                // The prompt says "comments" and "all 16 criterion values".
                // We should map category comments to something expected or just send them.
                // Assuming backend expects a 'comments' field for the general feedback, 
                // and maybe specific fields for category comments if the DB has them.
                // For safety, let's append category comments to the main comments if no specific fields exist.
                // Or keys like 'comment_listening' etc.
                // Without backend schema, I'll send 'comments' as the general feedback
                // and maybe include category comments in the payload.
                comments: generalFeedback.value,

                // Let's add category comments as specific keys if needed, but the prompt says 
                // "Each category must allow supervisor comments."
                // I'll send them as keys matching the category name (sanitized) or just one big blob if I had to guess.
                // Actually, let's look at `qaRubric`. 
                // I'll send distinct keys: 'comment_Opening', 'comment_Listening_Skills', etc.
            }

            // Append category comments
            for (const [key, val] of Object.entries(comments)) {
                const safeKey = `comment_${key.replace(/[^a-zA-Z0-9]/g, '_')}`
                payload[safeKey] = val
            }

            // Debug payload
            console.log('QA Payload:', payload)

            // POST
            await axiosInstance.post('api/qas/', payload)

            toast.success('QA Assessment Saved')
            closeForm()
            return true
        } catch (e) {
            console.error('QA Save Error:', e)
            toast.error('Failed to save assessment', {
                description: e.response?.data?.message || e.message
            })
            return false
        } finally {
            isLoading.value = false
        }
    }

    return {
        isOpen,
        isLoading,
        currentCall,
        scores,
        comments,
        generalFeedback,
        openForm,
        closeForm,
        categoryScores,
        totalScore,
        totalPercentage,
        submitQa
    }
}

<template>
    <Transition enter-active-class="transform transition ease-in-out duration-300" enter-from-class="translate-x-full"
        enter-to-class="translate-x-0" leave-active-class="transform transition ease-in-out duration-300"
        leave-from-class="translate-x-0" leave-to-class="translate-x-full">
        <div v-if="isOpen" class="fixed inset-y-0 right-0 w-[950px] z-[100] flex shadow-2xl">

            <!-- Main Form Section -->
            <div class="flex-1 flex flex-col h-full bg-white dark:bg-neutral-900 border-l"
                :class="isDarkMode ? 'border-neutral-800' : 'border-gray-200'">

                <!-- Helper Header from Composable State -->
                <div class="px-6 py-4 border-b flex items-center justify-between"
                    :class="isDarkMode ? 'border-neutral-800 bg-neutral-900' : 'border-gray-100 bg-white'">
                    <div>
                        <h2 class="text-lg font-black tracking-tight flex items-center gap-3">
                            <span :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'">QA Assessment</span>
                            <span
                                class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-widest bg-amber-100 text-amber-700">
                                Evaluation
                            </span>
                        </h2>
                        <p class="text-xs mt-1" :class="isDarkMode ? 'text-gray-400' : 'text-gray-500'">
                            evaluating call #{{ currentCall?.uniqueid }}
                        </p>
                    </div>
                    <button @click="closeForm"
                        class="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-neutral-800 transition-colors">
                        <i-mdi-close class="w-6 h-6" :class="isDarkMode ? 'text-gray-400' : 'text-gray-500'" />
                    </button>
                </div>

                <!-- Scrollable Form Content -->
                <div class="flex-1 overflow-y-auto p-6 space-y-8 relative">

                    <!-- Call Metadata Card -->
                    <div class="rounded-xl p-4 border grid grid-cols-2 lg:grid-cols-4 gap-4"
                        :class="isDarkMode ? 'bg-neutral-800/50 border-neutral-700' : 'bg-gray-50 border-gray-200'">
                        <div>
                            <span
                                class="text-[10px] font-bold uppercase tracking-widest opacity-50 block mb-1">Agent</span>
                            <span class="text-sm font-bold">{{ currentCall?.extension || 'Unknown' }}</span>
                        </div>
                        <div>
                            <span
                                class="text-[10px] font-bold uppercase tracking-widest opacity-50 block mb-1">Caller</span>
                            <span class="text-sm font-mono">{{ currentCall?.phone || 'Unknown' }}</span>
                        </div>
                        <div>
                            <span
                                class="text-[10px] font-bold uppercase tracking-widest opacity-50 block mb-1">Duration</span>
                            <span class="text-sm font-mono">{{ currentCall?.duration || '0:00' }}</span>
                        </div>
                        <div>
                            <span
                                class="text-[10px] font-bold uppercase tracking-widest opacity-50 block mb-1">Date</span>
                            <span class="text-sm">{{ currentCall ? new Date(currentCall.created *
                                1000).toLocaleDateString() : '-' }}</span>
                        </div>
                    </div>

                    <!-- Audio Player -->
                    <div v-if="currentCall"
                        class="p-4 rounded-xl border bg-indigo-50 dark:bg-indigo-900/20 border-indigo-100 dark:border-indigo-800 flex items-center gap-4">
                        <div class="w-10 h-10 rounded-full flex items-center justify-center transition-colors" :class="isPlaying
                            ? 'bg-indigo-600 text-white animate-pulse'
                            : 'bg-indigo-100 dark:bg-indigo-800 text-indigo-600 dark:text-indigo-300'">
                            <i-mdi-stop v-if="isPlaying" class="w-6 h-6" />
                            <i-mdi-play v-else class="w-6 h-6 ml-0.5" />
                        </div>
                        <div class="flex-1">
                            <div class="h-1 bg-indigo-200 dark:bg-indigo-700 rounded-full w-full mb-1 overflow-hidden">
                                <div class="h-full bg-indigo-500 transition-all duration-500"
                                    :style="{ width: isPlaying ? '100%' : '0%' }"></div>
                            </div>
                            <div class="flex justify-between text-[10px] font-bold text-indigo-500 uppercase">
                                <span>{{ isPlaying || currentTime > 0 ? formatTime(currentTime) : 'Ready' }}</span>
                                <span>{{ currentCall.duration }}</span>
                            </div>
                        </div>
                        <button @click="togglePlay"
                            class="px-4 py-1.5 text-white text-xs font-bold rounded-lg shadow-sm hover:opacity-90 min-w-[70px]"
                            :class="isPlaying ? 'bg-red-500' : 'bg-indigo-600'">
                            {{ isPlaying ? 'Stop' : 'Play' }}
                        </button>
                    </div>

                    <!-- Categories Loop -->
                    <div v-for="category in rubric" :key="category.category" class="pb-6 border-b last:border-0"
                        :class="isDarkMode ? 'border-neutral-800' : 'border-gray-100'">

                        <div class="flex items-center gap-3 mb-4">
                            <div class="w-8 h-8 rounded-lg flex items-center justify-center text-sm font-black"
                                :class="isDarkMode ? 'bg-neutral-800 text-gray-300' : 'bg-gray-100 text-gray-700'">
                                {{ category.category.charAt(0) }}
                            </div>
                            <h4 class="font-bold text-lg" :class="isDarkMode ? 'text-gray-200' : 'text-gray-800'">
                                {{ category.category }}
                            </h4>
                            <span
                                class="ml-auto text-xs font-bold px-2 py-1 rounded bg-gray-100 dark:bg-neutral-800 opacity-60">
                                Max {{ category.maxScore }} pts
                            </span>
                        </div>

                        <!-- Criteria List -->
                        <div class="space-y-4 pl-11">
                            <div v-for="crit in category.criteria" :key="crit.id"
                                class="flex items-start justify-between group p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-neutral-800/50 transition-colors">
                                <label class="text-sm font-medium pt-1"
                                    :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'">
                                    {{ crit.label }}
                                </label>

                                <div class="flex items-center gap-2">
                                    <div v-for="opt in scoringOptions" :key="opt.value"
                                        @click="scores[crit.id] = opt.value"
                                        class="cursor-pointer px-3 py-1.5 rounded-md text-xs font-bold uppercase transition-all border select-none"
                                        :class="getOptionClass(scores[crit.id], opt.value)">
                                        {{ opt.label }} ({{ opt.value }})
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Category Comments -->
                        <div class="ml-11 mt-4">
                            <input type="text" v-model="comments[category.category]"
                                :placeholder="`Add comments for ${category.category}...`"
                                class="w-full text-sm rounded-lg border-0 bg-gray-50 dark:bg-neutral-800 p-3 focus:ring-2 focus:ring-amber-500 transition-all placeholder:text-gray-400"
                                :class="isDarkMode ? 'text-white' : 'text-gray-900'" />
                        </div>
                    </div>

                    <!-- General Feedback -->
                    <div>
                        <h4 class="font-bold text-base mb-3" :class="isDarkMode ? 'text-gray-200' : 'text-gray-800'">
                            Overall Feedback
                        </h4>
                        <textarea :value="generalFeedback" @input="$emit('update:generalFeedback', $event.target.value)"
                            rows="4"
                            class="w-full rounded-xl border border-gray-200 dark:border-neutral-700 bg-white dark:bg-neutral-900 p-4 text-sm focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                            placeholder="Enter summary, strengths, and areas for improvement..."></textarea>
                    </div>
                </div>

                <!-- Footer Actions -->
                <div class="p-6 border-t flex justify-between items-center bg-gray-50/50 dark:bg-neutral-900/50 backdrop-blur-sm"
                    :class="isDarkMode ? 'border-neutral-800' : 'border-gray-100'">
                    <button @click="closeForm"
                        class="px-6 py-2.5 rounded-xl text-sm font-bold text-gray-500 hover:bg-gray-100 dark:hover:bg-neutral-800 transition-colors">
                        Cancel
                    </button>
                    <button @click="handleSubmit" :disabled="isLoading"
                        class="px-8 py-2.5 rounded-xl bg-amber-600 hover:bg-amber-500 text-white text-sm font-black uppercase tracking-widest shadow-lg shadow-amber-600/20 active:scale-95 transition-all flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed">
                        <i-mdi-loading v-if="isLoading" class="w-4 h-4 animate-spin" />
                        {{ isLoading ? 'Saving...' : 'Submit Assessment' }}
                    </button>
                </div>
            </div>

            <!-- Score Sidebar -->
            <div class="w-64 border-l h-full" :class="isDarkMode ? 'border-neutral-800' : 'border-gray-200'">
                <QaScoreSidebar :categoryScores="categoryScores" :totalScore="totalScore"
                    :totalPercentage="totalPercentage" />
            </div>
        </div>
    </Transition>

    <!-- Backdrop -->
    <Transition enter-active-class="transition-opacity duration-300" enter-from-class="opacity-0"
        enter-to-class="opacity-100" leave-active-class="transition-opacity duration-300" leave-from-class="opacity-100"
        leave-to-class="opacity-0">
        <div v-if="isOpen" @click="closeForm" class="fixed inset-0 bg-black/40 backdrop-blur-sm z-[90]"></div>
    </Transition>
</template>

<script setup>
    import { inject, ref, onUnmounted, watch } from 'vue'
    import QaScoreSidebar from './QaScoreSidebar.vue'
    import { QA_RUBRIC, SCORING_OPTIONS } from './qaRubric'

    const props = defineProps({
        isOpen: Boolean,
        currentCall: Object,
        isDarkMode: Boolean,
        scores: Object,
        comments: Object,
        generalFeedback: String,
        categoryScores: Object,
        totalScore: Number,
        totalPercentage: Number,
        isLoading: Boolean
    })

    const emit = defineEmits(['close', 'submit', 'update:scores', 'update:comments', 'update:generalFeedback'])

    const currentTime = ref(0) // Playback time in seconds

    const formatTime = (seconds) => {
        if (!seconds) return '0:00'
        const m = Math.floor(seconds / 60)
        const s = Math.floor(seconds % 60)
        return `${m}:${s.toString().padStart(2, '0')}`
    }

    // Audio Playback
    const isPlaying = ref(false)
    const currentAudio = ref(null)

    const togglePlay = () => {
        if (isPlaying.value && currentAudio.value) {
            currentAudio.value.pause()
            isPlaying.value = false
            return
        }

        if (currentAudio.value) {
            currentAudio.value.play()
            isPlaying.value = true
            return
        }

        const uid = props.currentCall?.uniqueid
        if (!uid) return

        // Construct URL
        const url = `/api-proxy/api/calls/${uid}?file=wav&`
        console.log('QA Player loading:', url)

        currentAudio.value = new Audio(url)

        currentAudio.value.ontimeupdate = () => {
            currentTime.value = currentAudio.value.currentTime
        }

        currentAudio.value.onended = () => {
            isPlaying.value = false
            currentTime.value = 0
        }

        currentAudio.value.onerror = (e) => {
            console.error('Audio load error', e)
            isPlaying.value = false
        }

        currentAudio.value.play()
        isPlaying.value = true
    }

    // Cleanup audio on close or unmount
    const stopAudio = () => {
        if (currentAudio.value) {
            currentAudio.value.pause()
            currentAudio.value = null
            isPlaying.value = false
        }
    }

    watch(() => props.isOpen, (newVal) => {
        if (!newVal) stopAudio()
    })

    onUnmounted(() => {
        stopAudio()
    })

    const closeForm = () => emit('close')
    const handleSubmit = () => emit('submit')

    const rubric = QA_RUBRIC
    const scoringOptions = SCORING_OPTIONS

    const getOptionClass = (currentVal, optVal) => {
        const isSelected = currentVal === optVal
        if (isSelected) {
            if (optVal === 2) return 'bg-emerald-600 border-emerald-600 text-white ring-2 ring-emerald-200 dark:ring-emerald-900'
            if (optVal === 1) return 'bg-amber-500 border-amber-500 text-white ring-2 ring-amber-200 dark:ring-amber-900'
            return 'bg-red-500 border-red-500 text-white ring-2 ring-red-200 dark:ring-red-900'
        }
        return 'bg-white dark:bg-neutral-800 border-gray-200 dark:border-neutral-700 text-gray-500 hover:border-gray-300'
    }
</script>

<template>
    <div class="h-full flex flex-col p-4 bg-gray-50 dark:bg-neutral-900 overflow-y-auto">
        <h3 class="text-sm font-black uppercase tracking-widest mb-4 border-b pb-2"
            :class="isDarkMode ? 'text-gray-400 border-gray-800' : 'text-gray-500 border-gray-200'">
            Live Scoring
        </h3>

        <!-- Overall Score Card -->
        <div class="mb-6 p-6 rounded-2xl text-center relative overflow-hidden shadow-lg"
            :class="getScoreColorClass(totalPercentage)">

            <div class="relative z-10">
                <div class="text-5xl font-black tracking-tighter mb-1">
                    {{ totalPercentage }}<span class="text-2xl">%</span>
                </div>
                <div class="text-xs font-bold uppercase tracking-widest opacity-80">
                    Total Score
                </div>
                <div class="mt-2 text-sm font-medium opacity-90">
                    {{ totalScore }} / 34 Points
                </div>
            </div>

            <!-- Background Decoration -->
            <div class="absolute -bottom-6 -right-6 w-24 h-24 rounded-full bg-white opacity-10 blur-2xl"></div>
            <div class="absolute -top-6 -left-6 w-24 h-24 rounded-full bg-black opacity-5 blur-2xl"></div>
        </div>

        <!-- Category Breakdown -->
        <div class="space-y-4">
            <div v-for="(catName, idx) in Object.keys(categoryScores)" :key="idx" class="flex flex-col gap-1">
                <div class="flex justify-between items-end text-xs font-bold uppercase tracking-wider mb-1"
                    :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'">
                    <span>{{ catName }}</span>
                    <span>{{ categoryScores[catName].score }} / {{ categoryScores[catName].max }}</span>
                </div>

                <!-- Progress Bar -->
                <div class="h-2 w-full bg-gray-200 dark:bg-gray-800 rounded-full overflow-hidden">
                    <div class="h-full rounded-full transition-all duration-500 ease-out"
                        :class="getProgressBarColor(categoryScores[catName].percentage)"
                        :style="{ width: `${categoryScores[catName].percentage}%` }">
                    </div>
                </div>
            </div>
        </div>

        <!-- Mini Info -->
        <div class="mt-auto pt-6 text-[10px] text-center opacity-40 font-mono">
            Legacy OPENCHS Rubric v2.0
        </div>
    </div>
</template>

<script setup>
    import { inject } from 'vue'

    const props = defineProps({
        categoryScores: Object,
        totalScore: Number,
        totalPercentage: Number
    })

    const isDarkMode = inject('isDarkMode', false)

    const getScoreColorClass = (pct) => {
        if (pct >= 80) return 'bg-emerald-600 text-white'
        if (pct >= 60) return 'bg-amber-500 text-white'
        return 'bg-red-600 text-white'
    }

    const getProgressBarColor = (pct) => {
        if (pct >= 80) return 'bg-emerald-500'
        if (pct >= 60) return 'bg-amber-500'
        return 'bg-red-500'
    }
</script>

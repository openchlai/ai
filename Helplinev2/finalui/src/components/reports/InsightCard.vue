<template>
    <div
        class="bg-white dark:bg-zinc-900 border border-gray-100 dark:border-zinc-800 rounded-xl p-6 shadow-sm hover:shadow-md transition-all duration-500 group relative overflow-hidden">

        <!-- Loading State -->
        <div v-if="loading" class="animate-pulse space-y-4">
            <div class="h-6 bg-gray-200 dark:bg-zinc-800 rounded w-1/3"></div>
            <div class="h-20 bg-gray-200 dark:bg-zinc-800 rounded w-full"></div>
            <div class="space-y-2">
                <div class="h-4 bg-gray-200 dark:bg-zinc-800 rounded w-1/2"></div>
                <div class="h-4 bg-gray-200 dark:bg-zinc-800 rounded w-1/2"></div>
            </div>
        </div>

        <!-- Content -->
        <div v-else class="relative z-10">
            <!-- Header -->
            <div class="flex items-start justify-between mb-4">
                <div>
                    <h3
                        class="text-lg font-bold text-gray-900 dark:text-white group-hover:text-amber-600 transition-colors">
                        Case Distribution by Protection Category
                    </h3>
                    <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
                        Safeguarding Summary
                    </p>
                </div>
                <div class="p-2 bg-amber-50 dark:bg-amber-900/20 rounded-lg text-amber-600 dark:text-amber-400">
                    <i-mdi-lightbulb-on-outline class="w-5 h-5" />
                </div>
            </div>

            <!-- Primary Insight -->
            <div class="mb-6 p-4 bg-gray-50 dark:bg-zinc-800/50 rounded-lg border border-gray-100 dark:border-zinc-800">
                <p class="text-gray-700 dark:text-gray-300 leading-relaxed font-medium">
                    {{ primaryInsight }}
                </p>
            </div>

            <!-- Metrics & Breakdown Grid -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <!-- Key Metrics -->
                <div>
                    <h4 class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Key Metrics</h4>
                    <ul class="space-y-3">
                        <li class="flex items-center justify-between group/item">
                            <span class="text-gray-600 dark:text-gray-400 text-sm">Total Survivors</span>
                            <span
                                class="font-bold text-gray-900 dark:text-white bg-gray-100 dark:bg-zinc-800 px-2 py-0.5 rounded group-hover/item:text-amber-600">
                                {{ metrics.total.toLocaleString() }}
                            </span>
                        </li>
                        <li class="flex items-center justify-between group/item">
                            <span class="text-gray-600 dark:text-gray-400 text-sm">Primary Category</span>
                            <span
                                class="font-bold text-gray-900 dark:text-white bg-gray-100 dark:bg-zinc-800 px-2 py-0.5 rounded text-right truncate max-w-[60%] group-hover/item:text-amber-600">
                                {{ metrics.topCaseType }}
                            </span>
                        </li>
                        <li class="flex items-center justify-between group/item">
                            <span class="text-gray-600 dark:text-gray-400 text-sm">Predominant Gender</span>
                            <span
                                class="font-bold text-gray-900 dark:text-white bg-gray-100 dark:bg-zinc-800 px-2 py-0.5 rounded group-hover/item:text-amber-600">
                                {{ metrics.topGender }}
                            </span>
                        </li>
                    </ul>
                </div>

                <!-- Breakdown Summary -->
                <div>
                    <h4 class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Distribution Trend
                    </h4>
                    <p class="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                        {{ breakdownSummary }}
                    </p>
                </div>
            </div>

            <!-- Data Notes -->
            <div class="border-t border-gray-100 dark:border-zinc-800 pt-4 mt-auto">
                <p class="text-xs text-gray-400 italic">
                    * Data is aggregated by protection category and survivor gender. Counts represent number of
                    survivors, not number of cases.
                </p>
            </div>
        </div>

        <!-- Decorative Background Gradient -->
        <div
            class="absolute top-0 right-0 -mt-4 -mr-4 w-24 h-24 bg-gradient-to-br from-amber-500/10 to-transparent rounded-full blur-xl pointer-events-none">
        </div>
    </div>
</template>

<script setup>
    import { computed } from 'vue'

    const props = defineProps({
        data: {
            type: Array, // Expected: [{ label: 'Type A', Male: 10, Female: 20 }, ...]
            default: () => []
        },
        loading: Boolean
    })

    // Extract valid gender keys dynamically, assuming standard ones or inferring from data keys
    const genderKeys = computed(() => {
        if (!props.data || props.data.length === 0) return []
        // Get all keys from first object that are not 'label' and not 'Unknown' or empty
        return Object.keys(props.data[0]).filter(k => k !== 'label' && k !== 'Unknown' && k !== '')
    })

    const analysis = computed(() => {
        if (!props.data || props.data.length === 0) {
            return {
                total: 0,
                topCaseType: 'N/A',
                topGender: 'N/A',
                topCaseCount: 0,
                genderCounts: {},
                caseTypeCounts: {}
            }
        }

        let total = 0
        let maxCaseCount = -1
        let topCaseType = ''

        const genderCounts = {}
        const caseTypeCounts = {}

        // Initialize gender counts
        genderKeys.value.forEach(k => genderCounts[k] = 0)

        props.data.forEach(row => {
            const label = row.label || 'Unknown'
            let rowTotal = 0

            genderKeys.value.forEach(gender => {
                const val = parseInt(row[gender] || 0)
                rowTotal += val
                genderCounts[gender] = (genderCounts[gender] || 0) + val
            })

            caseTypeCounts[label] = rowTotal
            total += rowTotal

            if (rowTotal > maxCaseCount) {
                maxCaseCount = rowTotal
                topCaseType = label
            }
        })

        // Find top gender
        let maxGenderCount = -1
        let topGender = ''
        Object.entries(genderCounts).forEach(([gender, count]) => {
            if (count > maxGenderCount) {
                maxGenderCount = count
                topGender = gender
            }
        })

        return {
            total,
            topCaseType,
            topGender,
            topCaseCount: maxCaseCount,
            genderCounts,
            caseTypeCounts,
            topGenderCount: maxGenderCount
        }
    })

    const metrics = computed(() => ({
        total: analysis.value.total,
        topCaseType: analysis.value.topCaseType,
        topGender: analysis.value.topGender
    }))

    const primaryInsight = computed(() => {
        const { total, topCaseType, topGender, topCaseCount, topGenderCount } = analysis.value
        if (total === 0) return "No data available for the selected period."

        const casePercent = Math.round((topCaseCount / total) * 100)
        const genderPercent = Math.round((topGenderCount / total) * 100)

        return `The data indicates that ${topCaseType} is the predominant protection category, accounting for ${casePercent}% of all survivors. Additionally, ${topGender} survivors make up the majority (${genderPercent}%) across the reported incidents.`
    })

    const breakdownSummary = computed(() => {
        const { topGender, total, genderCounts } = analysis.value
        if (total === 0) return "No active cases to report."

        // Check distinct gender patterns
        const genders = Object.entries(genderCounts).sort((a, b) => b[1] - a[1])
        if (genders.length < 2) return `Survivor distribution is exclusively ${genders[0]?.[0] || 'uniform'}.`

        const [first, second] = genders
        const ratio = Math.round(first[1] / (second[1] || 1))

        if (ratio >= 2) {
            return `There is a significant disparity in gender representation, with ${first[0]} survivors outnumbering ${second[0]} survivors by a factor of roughly ${ratio} to 1 across major categories.`
        } else {
            return `Gender distribution remains relatively balanced, though ${first[0]} survivors show a slightly higher prevalence in the primary protection categories compared to ${second[0]} survivors.`
        }
    })

</script>

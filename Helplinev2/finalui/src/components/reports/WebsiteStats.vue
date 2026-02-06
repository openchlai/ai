<template>
    <div class="space-y-8 animate-in fade-in duration-500">

        <!-- 1. Header & Global Filters -->
        <div class="bg-white dark:bg-black border dark:border-gray-800 rounded-lg p-6 shadow-sm">
            <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h2 class="text-xl font-bold dark:text-white flex items-center gap-2">
                        <i-mdi-web class="text-amber-500" />
                        Digital Reporting Dashboard
                    </h2>
                    <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
                        System-wide metrics and safeguarding overview.
                    </p>
                </div>

                <!-- Date Range Filter -->
                <div class="flex flex-wrap items-center gap-2">
                    <div
                        class="flex items-center gap-2 bg-gray-50 dark:bg-gray-900 p-1 rounded-lg border dark:border-gray-800">
                        <input type="date" v-model="startDate"
                            class="bg-transparent border-none text-sm focus:ring-0 dark:text-white" />
                        <span class="text-gray-400">-</span>
                        <input type="date" v-model="endDate"
                            class="bg-transparent border-none text-sm focus:ring-0 dark:text-white" />
                    </div>

                    <button @click="fetchWebsiteStatistics"
                        class="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white text-sm font-bold rounded-lg transition-colors flex items-center gap-2"
                        :disabled="loading">
                        <i-mdi-refresh class="w-4 h-4" :class="{ 'animate-spin': loading }" />
                        Apply Filter
                    </button>
                </div>
            </div>
        </div>

        <!-- 2. KPI Summary Cards -->
        <div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
            <div v-for="(val, key) in stats" :key="key"
                class="bg-white dark:bg-black border dark:border-gray-800 p-5 rounded-lg shadow-sm hover:shadow-md transition-all border-l-4"
                :class="getKpiColor(key)">
                <p class="text-xs uppercase font-bold text-gray-500 dark:text-gray-400 mb-1">
                    {{ formatKpiTitle(key) }}
                </p>
                <div class="text-2xl font-black dark:text-white">
                    <span v-if="loading" class="animate-pulse">...</span>
                    <span v-else>{{ val.toLocaleString() }}</span>
                </div>
            </div>
        </div>

        <!-- 3. Gender Analysis -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div class="lg:col-span-2 bg-white dark:bg-black border dark:border-gray-800 rounded-lg p-5 shadow-sm">
                <h3 class="font-bold mb-4 dark:text-white">Protection Category by Survivor Gender</h3>
                <WebsiteBarChart v-if="!loading" :data="charts.abuseVsSex" :keys="['Male', 'Female', 'Unknown']"
                    :isDarkMode="isDarkMode" />
                <div v-else class="h-64 flex items-center justify-center text-gray-400">Loading...</div>
            </div>

            <div class="lg:col-span-1">
                <InsightCard :data="charts.abuseVsSex" :loading="loading" />
            </div>
        </div>

        <!-- 4. Demographic Breakdowns -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <!-- Abuse Type vs Region -->
            <div class="bg-white dark:bg-black border dark:border-gray-800 rounded-lg p-5 shadow-sm">
                <h3 class="font-bold mb-4 dark:text-white">Protection Category by Region</h3>
                <WebsiteBarChart v-if="!loading" :data="charts.abuseVsRegion" :isDarkMode="isDarkMode" />
                <div v-else class="h-64 flex items-center justify-center text-gray-400">Loading...</div>
            </div>

            <!-- Abuse Type vs Age Group -->
            <div class="bg-white dark:bg-black border dark:border-gray-800 rounded-lg p-5 shadow-sm">
                <h3 class="font-bold mb-4 dark:text-white">Protection Category by Age Group</h3>
                <WebsiteBarChart v-if="!loading" :data="charts.abuseVsAgeGroup"
                    :keys="['0-5', '6-9', '10-12', '13-15', '16-18', 'Adult']" :isDarkMode="isDarkMode" />
                <div v-else class="h-64 flex items-center justify-center text-gray-400">Loading...</div>
            </div>

            <!-- Abuse Type vs District -->
            <div class="bg-white dark:bg-black border dark:border-gray-800 rounded-lg p-5 shadow-sm">
                <h3 class="font-bold mb-4 dark:text-white">Protection Category by District</h3>
                <WebsiteBarChart v-if="!loading" :data="charts.abuseVsDistrict" :isDarkMode="isDarkMode" />
                <div v-else class="h-64 flex items-center justify-center text-gray-400">Loading...</div>
            </div>
        </div>

    </div>
</template>

<script setup>
    import { ref, onMounted, onUnmounted, inject } from 'vue'
    import { useCaseStore } from '@/stores/cases'
    import { useCallStore } from '@/stores/calls'
    import axiosInstance from '@/utils/axios'
    import WebsiteBarChart from './WebsiteBarChart.vue'
    import InsightCard from './InsightCard.vue'

    // Props & Injections
    const isDarkMode = inject('isDarkMode')
    const caseStore = useCaseStore()
    const callStore = useCallStore()

    // State
    const loading = ref(false)
    const startDate = ref(new Date().toISOString().split('T')[0])
    const endDate = ref(new Date().toISOString().split('T')[0])
    let poolingInterval = null

    // KPI State
    const stats = ref({
        totalCalls: 0,
        totalCases: 0,
        totalGBVCases: 0,
        totalSEACases: 0,
        totalMigrationCases: 0
    })

    // Chart Data State
    const charts = ref({
        abuseVsSex: [],
        abuseVsRegion: [],
        abuseVsDistrict: [],
        abuseVsAgeGroup: []
    })

    // Helpers
    const formatKpiTitle = (key) => {
        return key.replace(/([A-Z])/g, ' $1').trim()
    }

    const getKpiColor = (key) => {
        if (key === 'totalCalls') return 'border-blue-500'
        if (key === 'totalCases') return 'border-emerald-500'
        if (key === 'totalGBVCases') return 'border-purple-500'
        if (key === 'totalSEACases') return 'border-red-500'
        return 'border-amber-500'
    }

    // Polling Logic for Global Stats
    const pollGlobalStats = async () => {
        try {
            console.log("Polling global stats...");
            const { data } = await axiosInstance.get('api/wallonly/rpt', {
                params: {
                    dash_period: 'today',
                    type: 'bar',
                    stacked: 'stacked',
                    xaxis: 'hangup_status_txt',
                    yaxis: 'h',
                    vector: '1',
                    rpt: 'call_count',
                    metrics: 'call_count'
                }
            })

            if (data?.stats) {
                // Update specific global totals
                if (data.stats.calls_total) stats.value.totalCalls = parseInt(data.stats.calls_total);
                if (data.stats.cases_total) stats.value.totalCases = parseInt(data.stats.cases_total);
            }
        } catch (e) {
            console.error("Failed to poll global stats", e)
        }
    }

    // Data Fetching Logic
    const fetchWebsiteStatistics = async () => {
        loading.value = true
        try {
            const commonParams = {
                start_date: startDate.value,
                end_date: endDate.value,
                _c: Date.now()
            }

            // ----------------------------------------
            // 1. Fetch KPI Totals (Server-Side)
            // ----------------------------------------
            const callsReq = callStore.getPivotReport({
                ...commonParams,
                xaxis: '-',
                metrics: 'call_count',
                rpt: 'call_count'
            })

            const casesReq = caseStore.getPivotReport({
                ...commonParams,
                xaxis: '-',
                metrics: 'case_count',
                rpt: 'case_count'
            })

            const [callsRes, casesRes] = await Promise.all([callsReq, casesReq])

            // Parse Calls Total
            if (callsRes?.calls_z?.call_count) {
                stats.value.totalCalls = parseInt(callsRes.calls_z.call_count)
            } else if (callsRes?.calls && callsRes.calls.length > 0) {
                stats.value.totalCalls = callsRes.calls.reduce((acc, r) => acc + parseInt(r[r.length - 1] || 0), 0)
            } else if (callsRes?.stats?.calls_total) {
                stats.value.totalCalls = parseInt(callsRes.stats.calls_total)
            } else {
                stats.value.totalCalls = 0
            }

            // Parse Cases Total
            if (casesRes?.cases_z?.case_count) {
                stats.value.totalCases = parseInt(casesRes.cases_z.case_count)
            } else if (casesRes?.cases && casesRes.cases.length > 0) {
                stats.value.totalCases = casesRes.cases.reduce((acc, r) => acc + parseInt(r[r.length - 1] || 0), 0)
            } else if (casesRes?.stats?.cases_total) {
                stats.value.totalCases = parseInt(casesRes.stats.cases_total)
            } else {
                stats.value.totalCases = 0
            }

            // ----------------------------------------
            // 2. Fetch Raw Cases for Breakdowns (Client-Side Aggregation)
            // ----------------------------------------
            const rawRes = await caseStore.getAnalytics({
                ...commonParams,
                _c: 5000 // Fetch up to 5000 raw rows for breakdown
            })

            const rows = rawRes.cases || []
            const k = rawRes.cases_k || {}

            // Helper to get index safely checking multiple potential keys
            const findColIdx = (candidates) => {
                for (const key of candidates) {
                    if (k[key] && k[key][0]) return parseInt(k[key][0])
                }
                return -1
            }

            // Resolve Indices with more robust fallbacks
            const idxAbuse = findColIdx(['cat_1', 'sub_category_1', 'cat_2', 'category'])
            const idxSex = findColIdx(['client_sex', 'reporter_sex', 'sex', 'gender'])
            const idxRegion = findColIdx(['client_region', 'reporter_location_0', 'region', 'location_0'])
            const idxDistrict = findColIdx(['client_district', 'reporter_location_1', 'district', 'location_1'])
            const idxAge = findColIdx(['age_group', 'reporter_age_group', 'age'])
            const idxMainCat = findColIdx(['main_category', 'cat_0'])

            // Category KPIs (Count from raw data)
            if (idxMainCat > -1) {
                const countByKeyword = (keyword) => rows.filter(r => String(r[idxMainCat]).toUpperCase().includes(keyword)).length
                stats.value.totalGBVCases = countByKeyword('GBV')
                stats.value.totalSEACases = countByKeyword('SEA')
                stats.value.totalMigrationCases = countByKeyword('MIGRATION')
            }

            // Helper: Group by Two Dimensions with Top N Stacks
            const aggregate = (idxX, idxY, topN = 0) => {
                if (idxX === -1 || idxY === -1) return []

                // 1. First pass: count frequencies for stack keys (Y) to determine Top N
                const stackCounts = {}
                rows.forEach(r => {
                    const stack = r[idxY] || 'Unknown'
                    stackCounts[stack] = (stackCounts[stack] || 0) + 1
                })

                let allowedStacks = null
                if (topN > 0) {
                    allowedStacks = new Set(
                        Object.entries(stackCounts)
                            .sort((a, b) => b[1] - a[1]) // Sort desc
                            .slice(0, topN)
                            .map(e => e[0])
                    )
                }

                // 2. Build the map
                const map = {}
                // Collect all unique keys for chart props
                const allKeys = new Set()

                rows.forEach(r => {
                    const label = r[idxX] || 'Unknown'
                    let stack = r[idxY] || 'Unknown'

                    // Group into 'Other' if not in top N (and top N is active)
                    if (allowedStacks && !allowedStacks.has(stack)) {
                        stack = 'Other'
                    }

                    if (!map[label]) map[label] = { label }
                    map[label][stack] = (map[label][stack] || 0) + 1
                    allKeys.add(stack)
                })

                return { data: Object.values(map), keys: Array.from(allKeys).sort() }
            }

            // Generate Charts

            // A. Abuse vs Sex (Specific Request: cat_0, cat_1, sex)
            // URL Structure: api/cases/?...&xaxis=cat_0,cat_1,clients^contact_sex&...
            // This returns rows like: ["Abuse", "Child Exploitation", "^Female", "1"]
            const sexReq = await caseStore.getAnalytics({
                ...commonParams,
                xaxis: 'cat_0,cat_1,clients^contact_sex',
                yaxis: '-',
                metrics: 'case_count',
                case_category_id: 87, // Filter for Abuse cases explicitly
            })

            if (sexReq && sexReq.cases) {
                const mapSex = {}
                // Indexes based on user example: 0=cat_0(Abuse), 1=cat_1(SubCat), 2=Sex, 3=Count
                // But let's try to be dynamic if possible, falling back to 1,2,3
                const kSex = sexReq.cases_k || {}
                const idxSubCat = (kSex.cat_1 && kSex.cat_1[0]) ? parseInt(kSex.cat_1[0]) : 1

                sexReq.cases.forEach(r => {
                    const label = r[1] || 'Unknown' // Sub Category
                    let sexRaw = r[2] || 'Unknown'
                    const val = parseInt(r[r.length - 1] || 0)

                    // Clean sex label: Remove leading ^ (e.g. ^Female -> Female)
                    let sex = sexRaw.replace(/^\^/, '')
                    if (!sex) sex = 'Unknown' // Handle empty strings that might have just been ^ or blank

                    if (!mapSex[label]) mapSex[label] = { label }
                    mapSex[label][sex] = (mapSex[label][sex] || 0) + val
                })
                charts.value.abuseVsSex = Object.values(mapSex)
            } else {
                // Fallback if request fails
                charts.value.abuseVsSex = []
            }

            // B. Abuse vs Region (Limit to Top 5 regions to avoid rainbow clutter)
            const regionAgg = aggregate(idxAbuse, idxRegion, 5)
            charts.value.abuseVsRegion = regionAgg.data
            // We pass the keys explicitly to help the chart component assign consistent colors if needed
            // (The component currently auto-generates keys if not passed, but passing them is safer)

            // C. Abuse vs District (Limit to Top 5)
            const districtAgg = aggregate(idxAbuse, idxDistrict, 5)
            charts.value.abuseVsDistrict = districtAgg.data

            // D. Abuse vs Age Group (Usually few, but limit to 6 just in case)
            const ageAgg = aggregate(idxAbuse, idxAge, 6)
            charts.value.abuseVsAgeGroup = ageAgg.data

        } catch (e) {
            console.error("Website Stats Error", e)
        } finally {
            loading.value = false
        }
    }

    // Initial Load
    onMounted(() => {
        // Set default range to current month
        const now = new Date();
        const firstDay = new Date(now.getFullYear(), now.getMonth(), 1);
        startDate.value = firstDay.toISOString().split('T')[0];

        // Initial fetch with filters
        fetchWebsiteStatistics();

        // 3. Start Polling (Every 20 mins)
        pollGlobalStats(); // Fetch immediately on load as well? Or rely on fetchWebsiteStatistics?
        // fetchWebsiteStatistics calls pivot report which RETURNS stats too (in `res.stats`), 
        // but `pollGlobalStats` calls `wallonly/rpt` which might be lighter/different.
        // We'll trust the user's specific request to poll this endpoint.

        poolingInterval = setInterval(pollGlobalStats, 20 * 60 * 1000);
    })

    onUnmounted(() => {
        if (poolingInterval) clearInterval(poolingInterval)
    })

</script>

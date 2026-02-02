<template>
    <div class="space-y-6">
        <!-- Header/Filter Section -->
        <PredictionsFilter @update:filters="handleFilterUpdate" />

        <!-- Loading State -->
        <div v-if="predictionsStore.loading"
            class="flex flex-col items-center justify-center py-24 rounded-2xl border border-dashed"
            :class="isDarkMode ? 'bg-neutral-900/10 border-neutral-800' : 'bg-gray-50/50 border-gray-200'">
            <div class="w-12 h-12 border-4 rounded-full animate-spin mb-4"
                :class="isDarkMode ? 'border-indigo-500/20 border-t-indigo-500' : 'border-indigo-100 border-t-indigo-700'">
            </div>
            <p class="text-sm font-medium animate-pulse" :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'">
                Analyzing AI prediction records...
            </p>
        </div>

        <!-- Content -->
        <div v-else class="animate-fadeIn">
            <!-- Stats / View Control -->
            <div class="flex justify-between items-center mb-6">
                <div class="flex items-center gap-3">
                    <div class="p-2.5 rounded-xl transition-all shadow-sm"
                        :class="isDarkMode ? 'bg-indigo-600/10 text-indigo-400' : 'bg-indigo-50 text-indigo-700'">
                        <i-mdi-robot-outline class="w-6 h-6" />
                    </div>
                    <div>
                        <div class="flex items-baseline gap-2">
                            <span class="text-2xl font-black tracking-tight"
                                :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'">
                                {{ predictionsStore.paginationInfo.total }}
                            </span>
                            <span class="text-sm font-bold uppercase tracking-widest"
                                :class="isDarkMode ? 'text-gray-500' : 'text-gray-400'">
                                Predictions
                            </span>
                        </div>
                        <p class="text-xs font-semibold" :class="isDarkMode ? 'text-gray-500' : 'text-gray-400'">
                            Showing {{ predictionsStore.paginationInfo.rangeStart }} - {{
                                predictionsStore.paginationInfo.rangeEnd }}
                        </p>
                    </div>
                </div>

                <button @click="refreshList" :disabled="predictionsStore.loading"
                    class="px-6 py-3 rounded-xl font-bold transition-all border flex items-center gap-2 text-sm shadow-sm active:scale-95 disabled:opacity-50"
                    :class="isDarkMode
                        ? 'bg-neutral-900 border-neutral-800 text-gray-300 hover:text-green-400 hover:border-green-500/50'
                        : 'bg-white border-gray-100 text-gray-700 hover:text-green-700 hover:border-green-600/50'">
                    <i-mdi-refresh class="w-5 h-5" />
                    Sync Data
                </button>
            </div>

            <!-- List Representation -->
            <PredictionsTable :predictions="predictionsStore.predictions"
                :predictions_k="predictionsStore.predictions_k" />

            <!-- Pagination UI -->
            <div class="mt-8">
                <Pagination :paginationInfo="predictionsStore.paginationInfo"
                    :hasNextPage="predictionsStore.hasNextPage" :hasPrevPage="predictionsStore.hasPrevPage"
                    :loading="predictionsStore.loading" :pageSize="pageSize"
                    @prev="predictionsStore.prevPage(activeFilters)" @next="predictionsStore.nextPage(activeFilters)"
                    @goToPage="page => predictionsStore.goToPage(page, activeFilters)"
                    @changePageSize="handlePageSizeChange" />
            </div>
        </div>
    </div>
</template>

<script setup>
    import { ref, onMounted, inject } from 'vue'
    import { toast } from 'vue-sonner'
    import { usePredictionsStore } from '@/stores/predictions'

    import PredictionsFilter from '@/components/predictions/PredictionsFilter.vue'
    import PredictionsTable from '@/components/predictions/PredictionsTable.vue'
    import Pagination from '@/components/base/Pagination.vue'

    const predictionsStore = usePredictionsStore()
    const isDarkMode = inject('isDarkMode')

    const pageSize = ref(20)
    const activeFilters = ref({})

    onMounted(async () => {
        try {
            await predictionsStore.listPredictions({ _c: pageSize.value })
        } catch (e) {
            toast.error('Initialization failed', { description: 'Could not load AI records.' })
        }
    })

    const handleFilterUpdate = async (filters) => {
        activeFilters.value = filters
        predictionsStore.resetPagination()
        try {
            await predictionsStore.listPredictions({ ...filters, _c: pageSize.value })
        } catch (e) {
            toast.error('Search failed')
        }
    }

    const handlePageSizeChange = async (size) => {
        pageSize.value = size
        await predictionsStore.setPageSize(size, activeFilters.value)
    }

    const refreshList = async () => {
        try {
            await predictionsStore.listPredictions({ ...activeFilters.value, _c: pageSize.value })
            toast.success('Records synchronized')
        } catch (e) {
            toast.error('Refresh failed')
        }
    }
</script>

<style scoped>
    .animate-fadeIn {
        animation: fadeIn 0.4s ease-out;
    }

    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }

        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
</style>

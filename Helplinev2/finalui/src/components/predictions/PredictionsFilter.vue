<template>
    <div class="p-6 rounded-2xl shadow-xl border transition-all duration-300" :class="isDarkMode
        ? 'bg-black border-neutral-800'
        : 'bg-white border-gray-100'">
        <div class="flex flex-col md:flex-row gap-6 items-end">
            <!-- Search Section -->
            <div class="flex-1 flex gap-4">
                <!-- Source Selector -->
                <div class="w-48 space-y-2">
                    <label class="text-xs font-bold uppercase tracking-widest px-1"
                        :class="isDarkMode ? 'text-gray-400' : 'text-gray-500'">
                        Source
                    </label>
                    <select v-model="filters.src"
                        class="w-full px-4 py-3.5 rounded-xl border transition-all outline-none text-sm appearance-none"
                        :class="isDarkMode
                            ? 'bg-neutral-900 border-neutral-700 text-gray-200 focus:border-indigo-500/50'
                            : 'bg-gray-50 border-gray-200 text-gray-900 focus:border-indigo-500/50'">
                        <option value="aii">Legacy (AII)</option>
                        <option value="gateway">Gateway</option>
                    </select>
                </div>

                <!-- Search Call ID -->
                <div class="flex-1 space-y-2">
                    <label class="text-xs font-bold uppercase tracking-widest px-1"
                        :class="isDarkMode ? 'text-gray-400' : 'text-gray-500'">
                        Search Call ID
                    </label>
                    <div class="relative group">
                        <span class="absolute left-4 top-1/2 -translate-y-1/2">
                            <i-mdi-magnify
                                class="w-5 h-5 text-gray-400 group-focus-within:text-indigo-500 transition-colors" />
                        </span>
                        <input v-model="filters.q" type="text" placeholder="Enter Call ID or reference..."
                            class="w-full pl-12 pr-4 py-3.5 rounded-xl border transition-all outline-none text-sm"
                            :class="isDarkMode
                                ? 'bg-neutral-900 border-neutral-700 text-gray-200 focus:border-indigo-500/50 focus:ring-4 focus:ring-indigo-500/10'
                                : 'bg-gray-50 border-gray-200 text-gray-900 focus:border-indigo-500/50 focus:ring-4 focus:ring-indigo-500/10'"
                            @keyup.enter="emitFilters" />
                    </div>
                </div>
            </div>

            <!-- Action Buttons -->
            <div class="flex gap-3">
                <button @click="resetFilters"
                    class="px-6 py-3.5 rounded-xl font-bold text-sm transition-all border flex items-center gap-2"
                    :class="isDarkMode
                        ? 'bg-neutral-900 border-neutral-700 text-gray-400 hover:bg-neutral-800 hover:text-white'
                        : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50 hover:text-black'">
                    <i-mdi-filter-off class="w-5 h-5" />
                    Reset
                </button>
                <button @click="emitFilters"
                    class="px-8 py-3.5 rounded-xl font-bold text-sm text-white transition-all transform active:scale-95 shadow-lg flex items-center gap-2"
                    :class="isDarkMode
                        ? 'bg-indigo-600 hover:bg-indigo-700 shadow-indigo-900/20'
                        : 'bg-indigo-700 hover:bg-indigo-800 shadow-indigo-200'">
                    <i-mdi-filter-variant class="w-5 h-5" />
                    Apply Filters
                </button>
            </div>
        </div>
    </div>
</template>

<script setup>
    import { ref, inject } from 'vue'

    const emit = defineEmits(['update:filters'])
    const isDarkMode = inject('isDarkMode')

    const filters = ref({
        q: '',
        src: 'aii'
    })

    const emitFilters = () => {
        emit('update:filters', { ...filters.value })
    }

    const resetFilters = () => {
        filters.value.q = ''
        filters.value.src = 'aii'
        emitFilters()
    }
</script>

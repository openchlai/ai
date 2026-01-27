<template>
    <div class="rounded-xl border p-5 shadow-sm transition-all hover:shadow-md border-green-500/20"
        :class="isDarkMode ? 'bg-neutral-800/50' : 'bg-green-50/20'">

        <div class="flex items-center gap-3">
            <div class="p-2 rounded-full"
                :class="isDarkMode ? 'bg-green-900/30 text-green-400' : 'bg-green-100 text-green-600'">
                <i-mdi-check-all class="w-5 h-5" />
            </div>
            <div>
                <div class="text-xs font-bold uppercase tracking-widest opacity-60">Processing Complete</div>
                <div class="text-sm font-semibold">
                    All AI tasks for this call have finished.
                </div>
            </div>
            <div class="ml-auto text-xs font-mono opacity-50">{{ formatTime(prediction.created_on) }}</div>
        </div>

    </div>
</template>

<script setup>
    import { inject } from 'vue'

    const props = defineProps({
        prediction: Object,
        payload: Object
    })

    const isDarkMode = inject('isDarkMode')

    const formatTime = (ts) => {
        if (!ts) return ''
        return new Date(ts * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
</script>

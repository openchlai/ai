<template>
    <span v-if="count > 0"
        class="absolute -top-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-red-600 text-[10px] font-bold text-white shadow-sm ring-2 ring-white dark:ring-black animate-pulse">
        {{ displayCount }}
    </span>
</template>

<script setup>
    import { computed } from 'vue'

    const props = defineProps({
        count: {
            type: Number,
            required: true,
            default: 0
        }
    })

    const displayCount = computed(() => {
        return props.count > 99 ? '99+' : props.count
    })
</script>

<style scoped>

    /* Ensure the badge is always on top */
    span {
        z-index: 10;
    }
</style>

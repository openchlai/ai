<template>
    <div class="top-stats-row">
        <div v-for="stat in stats" :key="stat.id" :class="['stat-card', stat.variant]">
            <div class="stat-content">
                <div class="stat-label">{{ stat.title.toUpperCase() }}</div>
                <div class="stat-value">{{ stat.value }}</div>
            </div>
        </div>
    </div>
</template>

<script setup>
/**
 * A component that displays a row of key statistics.
 */
    defineProps({
    /**
     * An array of objects, where each object represents a stat card.
     * @type {Array}
     */
    stats: Array
});
</script>

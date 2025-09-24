<template>
    <div class="cases-grid">
        <div v-for="item in casesTiles" :key="item.id" :class="['case-card', item.variant]">
            <div class="case-inner">
                <div v-if="item.value" class="case-value">{{ item.value }}</div>
                <div class="case-label">{{ item.label }}</div>
            </div>
        </div>
    </div>
</template>

<script setup>
/**
 * A component that displays a grid of case statistics.
 */
    defineProps({
    /**
     * An array of objects, where each object represents a tile in the grid.
     * @type {Array}
     */
    casesTiles: Array
});
</script>

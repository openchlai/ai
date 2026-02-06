<template>
    <div class="w-full h-80 overflow-x-auto">
        <div class="relative h-full" :style="{ minWidth: minWidth + 'px' }">
            <svg :width="width" :height="height" class="w-full h-full">
                <!-- Grid lines -->
                <g>
                    <line v-for="tick in yTicks" :key="tick" :x1="margin.left" :x2="width - margin.right"
                        :y1="yScale(tick)" :y2="yScale(tick)" :stroke="isDarkMode ? '#374151' : '#e5e7eb'"
                        stroke-dasharray="4" />
                </g>

                <!-- Y Axis Labels -->
                <g>
                    <text v-for="tick in yTicks" :key="'label-' + tick" :x="margin.left - 10" :y="yScale(tick)"
                        text-anchor="end" dominant-baseline="middle" class="text-xs"
                        :fill="isDarkMode ? '#9ca3af' : '#4b5563'">
                        {{ tick }}
                    </text>
                </g>

                <!-- Bars -->
                <g v-for="(group, gIndex) in computedData" :key="gIndex">
                    <rect v-for="(stack, sIndex) in group.stacks" :key="sIndex"
                        :x="xScale(group.label) + (barWidth * 0.1)" :y="yScale(stack.end)" :width="barWidth * 0.8"
                        :height="Math.abs(yScale(stack.start) - yScale(stack.end))" :fill="getColor(stack.key)"
                        class="transition-all hover:opacity-80">
                        <title>{{ group.label }} - {{ stack.key }}: {{ stack.value }}</title>
                    </rect>
                </g>

                <!-- X Axis Labels -->
                <g>
                    <text v-for="(group, index) in computedData" :key="index" :x="xScale(group.label) + barWidth / 2"
                        :y="height - margin.bottom + 20" text-anchor="start" class="text-xs font-medium"
                        :fill="isDarkMode ? '#9ca3af' : '#4b5563'"
                        :transform="`rotate(45, ${xScale(group.label) + barWidth / 2}, ${height - margin.bottom + 20})`">
                        {{ truncate(group.label, 20) }}
                    </text>
                </g>

                <!-- Legend -->
                <g :transform="`translate(${margin.left}, 10)`">
                    <g v-for="(key, index) in stackKeys" :key="key" :transform="`translate(${index * 120}, 4)`">
                        <rect width="12" height="12" :fill="getColor(key)" rx="3" />
                        <text x="18" y="10" class="text-xs font-semibold" :fill="isDarkMode ? '#d1d5db' : '#374151'">{{
                            key }}</text>
                    </g>
                </g>
            </svg>
        </div>
    </div>
</template>

<script setup>
    import { computed, toRefs } from 'vue'

    const props = defineProps({
        data: {
            type: Array, // [{ label: 'Abuse 1', Male: 10, Female: 5 }, ...]
            required: true
        },
        keys: {
            type: Array, // ['Male', 'Female']
            default: () => []
        },
        isDarkMode: Boolean
    })

    const { data, keys } = toRefs(props)

    // Increased bottom margin for rotated labels
    const margin = { top: 50, right: 40, bottom: 80, left: 40 }
    const height = 400 // Slightly taller
    const barWidth = 60

    const stackKeys = computed(() => {
        if (props.keys.length) return props.keys
        // Auto-detect keys if not provided (exclude 'label')
        if (data.value.length === 0) return []
        return Object.keys(data.value[0]).filter(k => k !== 'label')
    })

    const width = computed(() => Math.max(800, data.value.length * barWidth + margin.left + margin.right))
    const minWidth = computed(() => width.value)

    const maxY = computed(() => {
        return Math.max(...data.value.map(d => {
            return stackKeys.value.reduce((acc, key) => acc + (d[key] || 0), 0)
        }), 10)
    })

    const yTicks = computed(() => {
        const max = maxY.value
        return [0, max * 0.25, max * 0.5, max * 0.75, max].map(v => Math.round(v))
    })

    const yScale = (val) => {
        const range = height - margin.top - margin.bottom
        return (height - margin.bottom) - (val / maxY.value) * range
    }

    const xScale = (label) => {
        const index = data.value.findIndex(d => d.label === label)
        return margin.left + index * barWidth
    }

    const computedData = computed(() => {
        return data.value.map(d => {
            let currentY = 0
            const stacks = stackKeys.value.map(key => {
                const val = d[key] || 0
                const start = currentY
                const end = currentY + val
                currentY += val
                return { key, value: val, start, end }
            })
            return { label: d.label, stacks }
        })
    })

    const colors = [
        '#f59e0b', '#3b82f6', '#10b981', '#ec4899', '#8b5cf6', '#ef4444', '#6366f1'
    ]

    const getColor = (key) => {
        const index = stackKeys.value.indexOf(key)
        return colors[index % colors.length]
    }

    const truncate = (str, len) => {
        if (!str) return ''
        return str.length > len ? str.substring(0, len) + '...' : str
    }
</script>

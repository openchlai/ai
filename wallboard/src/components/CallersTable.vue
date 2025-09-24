<template>
    <div class="counsellors-section">
        <div class="section-header">
            <h2 class="section-title">Callers Online: {{ count }}</h2>
        </div>
        <div class="counsellors-table">
            <div class="table-header callers-header">
                <div class="col-caller-num">Caller Number</div>
                <div class="col-caller-name">Caller Name</div>
                <div class="col-vector">Queue</div>
                <div class="col-wait-time">Wait Time</div>
                <div class="col-status">Status</div>
                <div class="col-bridge">Bridge ID</div>
            </div>
            <div class="table-body">
                <div v-if="callers.length === 0" class="no-counsellors-row">
                    <div class="no-counsellors-text">No callers currently online</div>
                </div>
                <div v-for="caller in callers" :key="caller.id" class="table-row callers-row">
                    <div class="col-caller-num">{{ caller.callerNumber || "--" }}</div>
                    <div class="col-caller-name">{{ caller.callerName || "Unknown" }}</div>
                    <div class="col-vector">{{ caller.vector || "--" }}</div>
                    <div class="col-wait-time">{{ caller.waitTime || "--" }}</div>
                    <div :class="['col-status', statusClass(caller.queueStatus)]">
                        {{ caller.queueStatus || "Unknown" }}
                    </div>
                    <div class="col-bridge">{{ caller.bridgeId || "--" }}</div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
/**
 * A component that displays a table of current callers with their details.
 */
defineProps({
        /**
         * An array of caller objects to display in the table.
         * @type {Array}
         */
        callers: {
            type: Array,
            default: () => [],
        },
        /**
         * The total number of online callers.
         * @type {Number}
         */
        count: {
            type: Number,
            default: 0,
        },
        /**
         * A function that returns a CSS class based on the caller's status.
         * @type {Function}
         */
        statusClass: {
            type: Function,
            default: () => () => "status-neutral",
        },
    });
</script>


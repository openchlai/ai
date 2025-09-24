<template>
    <div class="header">
        <div class="title-section">
            <h1>Sauti Helpline Wallboard</h1>
            <p>Real-time counselling and support</p>
        </div>
        <div class="header-controls">
            <div class="connection-status">
                <span :class="['dot', connectionClass]"></span>
                <span class="status-text">{{ connectionLabel }}</span>
                <small v-if="lastUpdate"> · last update: {{ lastUpdate }}</small>
            </div>
            <button class="theme-toggle" @click="$emit('toggleDarkMode')">
                <span class="theme-icon">{{ isDarkMode ? "☀️" : "🌙" }}</span>
            </button>
        </div>
    </div>
</template>

<script setup>
/**
 * The main header of the application.
 * Displays the title, connection status, and a dark mode toggle.
 */
    defineProps({
        /**
         * Whether dark mode is enabled.
         * @type {Boolean}
         */
        isDarkMode: Boolean,
        /**
         * The CSS class for the connection status dot.
         * @type {String}
         */
        connectionClass: String,
        /**
         * The label for the connection status.
         * @type {String}
         */
        connectionLabel: String,
        /**
         * The timestamp of the last update.
         * @type {String}
         */
        lastUpdate: String,
    });

    /**
     * Emitted when the dark mode toggle is clicked.
     * @event toggleDarkMode
     */
</script>

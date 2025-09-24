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
    defineProps({
        isDarkMode: Boolean,
        connectionClass: String,
        connectionLabel: String,
        lastUpdate: String,
    });
</script>

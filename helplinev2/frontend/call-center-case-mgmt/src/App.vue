<template>
  <router-view />
  <button
    class="read-aloud-fab"
    @click="readAloud"
    :aria-pressed="isReading"
    :aria-label="isReading ? 'Stop Read Aloud' : 'Read Aloud'"
  >
    <span v-if="!isReading">🔊 Read Aloud</span>
    <span v-else>⏹️ Stop Read Aloud</span>
  </button>
</template>

<script setup>
import { ref } from 'vue'
import './assets/glassmorphic.css'

const isReading = ref(false)

function readAloud() {
  if (!window.speechSynthesis) return;
  if (isReading.value) {
    window.speechSynthesis.cancel();
    isReading.value = false;
    return;
  }
  // Try to read .main-content, fallback to body
  let content = document.querySelector('.main-content')?.innerText;
  if (!content || content.trim().length < 10) {
    content = document.body.innerText;
  }
  if (content) {
    window.speechSynthesis.cancel();
    const utterance = new window.SpeechSynthesisUtterance(content);
    utterance.rate = 1;
    utterance.pitch = 1;
    utterance.lang = 'en-US';
    utterance.onend = () => { isReading.value = false; };
    utterance.onerror = () => { isReading.value = false; };
    isReading.value = true;
    window.speechSynthesis.speak(utterance);
  }
}
</script>

<style>
body, #app {
  background: var(--background-color, #fff);
  color: var(--text-color, #222);
  min-height: 100vh;
  margin: 0;
  padding: 0;
}
.read-aloud-fab {
  position: fixed;
  bottom: 32px;
  right: 32px;
  z-index: 9999;
  background: var(--accent-color, #964B00);
  color: #fff;
  border: none;
  border-radius: 50px;
  padding: 16px 28px;
  font-size: 1.1rem;
  font-weight: 700;
  box-shadow: 0 4px 16px rgba(150,75,0,0.18);
  cursor: pointer;
  transition: background 0.2s, color 0.2s, box-shadow 0.2s;
  outline: none;
  display: flex;
  align-items: center;
  gap: 10px;
  pointer-events: auto;
}
.read-aloud-fab:hover, .read-aloud-fab:focus {
  background: var(--accent-hover, #b25900);
  color: #fff;
  box-shadow: 0 6px 20px rgba(150,75,0,0.22);
}
</style>

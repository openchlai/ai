<script setup>
import { ref, watch } from "vue";

const props = defineProps({
  modelValue: String, // parent can pass initial value
});

const emit = defineEmits(['update:modelValue', 'send-message']);

const newMessageLocal = ref(props.modelValue || "");

// Keep local value in sync if parent changes it
watch(() => props.modelValue, (val) => {
  newMessageLocal.value = val;
});

const sendMessage = () => {
  if (!newMessageLocal.value.trim()) return;
  emit('send-message', newMessageLocal.value);
  newMessageLocal.value = "";
};
</script>

<template>
  <div class="p-4 border-t flex space-x-2">
    <textarea
      v-model="newMessageLocal"
      rows="2"
      placeholder="Type your message..."
      class="flex-1 border rounded px-2 py-1"
    ></textarea>
    <button
      class="bg-blue-500 text-white px-4 py-1 rounded"
      @click="sendMessage"
    >
      Send
    </button>
  </div>
</template>

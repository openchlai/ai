<template>
  <div 
    class="p-4 border-t"
    :class="isDarkMode 
      ? 'border-transparent bg-gray-800' 
      : 'border-transparent bg-white'"
  >
    <div class="flex gap-3">
      <textarea
        v-model="newMessageLocal"
        rows="2"
        placeholder="Type your message..."
        class="flex-1 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:border-transparent resize-none text-sm"
        :class="isDarkMode 
          ? 'bg-neutral-800 border border-transparent text-gray-100 placeholder-gray-400 focus:ring-amber-500' 
          : 'bg-gray-50 border border-transparent text-gray-900 placeholder-gray-400 focus:ring-amber-600'"
        @keydown.enter.exact.prevent="sendMessage"
      />
      <button 
        @click="sendMessage"
        class="text-white px-6 rounded-lg transition-all duration-200 shadow-lg font-medium flex items-center gap-2 active:scale-95"
        :class="isDarkMode 
          ? 'bg-amber-600 hover:bg-amber-700' 
          : 'bg-amber-700 hover:bg-amber-800'"
      >
        <i-mdi-send class="w-5 h-5" />
        Send
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, inject } from "vue"
import { toast } from 'vue-sonner'

const props = defineProps({
  modelValue: String,
})

const emit = defineEmits(['update:modelValue', 'send-message'])

// Inject theme
const isDarkMode = inject('isDarkMode')

const newMessageLocal = ref(props.modelValue || "")

watch(() => props.modelValue, (val) => {
  newMessageLocal.value = val
})

const sendMessage = () => {
  if (!newMessageLocal.value.trim()) {
    toast.warning('Please enter a message')
    return
  }
  
  // Show error toast with title and description
  toast.error('Service Not Available', {
    description: 'Messaging functionality is currently unavailable.'
  })
  
  // Emit the message
  emit('send-message', newMessageLocal.value)
  
  // Clear input
  newMessageLocal.value = ""
  emit('update:modelValue', "")
}
</script>
<template>
  <div class="main-scroll-content">
    <div class="ai-assistant-container">
      <!-- AI Chat Card -->
      <div class="ai-chat-card glass-card fine-border">
        <div class="card-header">
          <div class="section-title">AI Assistant</div>
          <div class="ai-status">
            <div class="status-dot active"></div>
            Online
          </div>
        </div>
        
        <div class="chat-container">
          <div class="chat-messages" ref="chatMessages">
            <div
              v-for="message in chatMessages"
              :key="message.id"
              class="message"
              :class="message.type"
            >
              <div class="message-avatar">
                <svg v-if="message.type === 'ai'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 2a3 3 0 0 0-3 3c0 1.5 1.5 3 3 3s3-1.5 3-3a3 3 0 0 0-3-3z"></path>
                  <path d="M19 10v-1a7 7 0 0 0-14 0v1"></path>
                  <path d="M5 10v4a3 3 0 0 0 3 3h8a3 3 0 0 0 3-3v-4"></path>
                </svg>
                <span v-else>{{ getInitials('You') }}</span>
              </div>
              <div class="message-content">
                <div class="message-text">{{ message.text }}</div>
                <div class="message-time">{{ formatTime(message.timestamp) }}</div>
              </div>
            </div>
          </div>
          
          <div class="chat-input-container">
            <input
              class="chat-input"
              type="text"
              v-model="newMessage"
              placeholder="Ask me anything about your cases..."
              @keyup.enter="sendMessage"
            />
            <button
              class="send-btn"
              @click="sendMessage"
              :disabled="!newMessage.trim()"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="22" y1="2" x2="11" y2="13"></line>
                <polygon points="22,2 15,22 11,13 2,9"></polygon>
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- AI Suggestions Card -->
      <div class="ai-suggestions-card glass-card fine-border">
        <div class="section-title">Smart Suggestions</div>
        <div class="suggestions-list">
          <button
            v-for="suggestion in aiSuggestions"
            :key="suggestion.id"
            class="suggestion-btn"
            @click="applySuggestion(suggestion)"
          >
            <div class="suggestion-icon">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                <polyline points="22,4 12,14.01 9,11.01"></polyline>
              </svg>
            </div>
            <div class="suggestion-content">
              <div class="suggestion-title">{{ suggestion.title }}</div>
              <div class="suggestion-description">{{ suggestion.description }}</div>
            </div>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'

// Reactive data
const chatMessages = ref([
  {
    id: 1,
    type: 'ai',
    text: 'Hello! I\'m your AI assistant. I can help you analyze case data, generate reports, and provide insights to improve your team\'s performance. How can I assist you today?',
    timestamp: new Date()
  }
])

const newMessage = ref('')
const chatMessagesRef = ref(null)

const aiSuggestions = ref([
  {
    id: 1,
    title: "Review Overdue Cases",
    description: "You have 3 cases that are past their due date"
  },
  {
    id: 2,
    title: "Team Workload Balance",
    description: "Consider redistributing cases for better balance"
  },
  {
    id: 3,
    title: "Generate Monthly Report",
    description: "Monthly performance report is due tomorrow"
  }
])

// Methods
const sendMessage = () => {
  if (!newMessage.value.trim()) return

  const userMessage = {
    id: chatMessages.value.length + 1,
    type: 'user',
    text: newMessage.value,
    timestamp: new Date()
  }

  chatMessages.value.push(userMessage)

  // Simulate AI response
  setTimeout(() => {
    const aiResponse = {
      id: chatMessages.value.length + 1,
      type: 'ai',
      text: generateAIResponse(newMessage.value),
      timestamp: new Date()
    }
    chatMessages.value.push(aiResponse)
    scrollToBottom()
  }, 1000)

  newMessage.value = ''
}

const generateAIResponse = (message) => {
  const responses = [
    "I can help you analyze your case data. Would you like me to generate a report on case resolution times?",
    "Based on your current caseload, I recommend prioritizing the high-priority cases assigned to John Doe.",
    "Your team's performance has improved by 15% this month. The average case resolution time is now 8.5 days.",
    "I notice you have 3 overdue cases. Would you like me to help you create a plan to address them?",
    "Your organization is performing well with an 87% case resolution rate. This is above the industry average."
  ]
  return responses[Math.floor(Math.random() * responses.length)]
}

const applySuggestion = (suggestion) => {
  console.log('Apply suggestion:', suggestion)
  alert(`Applied suggestion: ${suggestion.title}`)
}

const formatTime = (date) => {
  return new Date(date).toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getInitials = (name) => {
  if (!name || typeof name !== 'string') return ''
  return name
    .split(' ')
    .map(part => part[0])
    .join('')
    .toUpperCase()
}

const scrollToBottom = async () => {
  await nextTick()
  if (chatMessagesRef.value) {
    chatMessagesRef.value.scrollTop = chatMessagesRef.value.scrollHeight
  }
}

onMounted(() => {
  scrollToBottom()
})
</script>

<style scoped>
/* AI Assistant specific styles are inherited from global components.css */
</style>

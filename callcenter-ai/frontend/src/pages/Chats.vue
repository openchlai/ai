<template>
  <div class="app-container">
    <!-- SidePanel Component -->
    <SidePanel 
      :userRole="userRole"
      :isInQueue="isInQueue"
      :isProcessingQueue="isProcessingQueue"
      :currentCall="currentCall"
      @toggle-queue="handleQueueToggle"
      @logout="handleLogout"
      @sidebar-toggle="handleSidebarToggle"
    />

    <!-- Main Content -->
    <div class="main-content">
      <div class="calls-container" :class="{ 'chat-panel-open': showChatPanel }">
        <div class="header">
          <h1 class="page-title">All Chats</h1>
              <div class="header-actions">
            <button class="theme-toggle" @click="toggleTheme" id="theme-toggle">
              <svg v-if="currentTheme === 'dark'" id="moon-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
              <svg v-else id="sun-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="12" y1="1" x2="12" y2="3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="12" y1="21" x2="12" y2="23" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="1" y1="12" x2="3" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="21" y1="12" x2="23" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
              <span id="theme-text">{{ currentTheme === 'dark' ? 'Light Mode' : 'Dark Mode' }}</span>
                </button>
              </div>
            </div>
        <!-- Channel Filters as View Tabs -->
        <div class="channel-filters" role="tablist" aria-label="Chat Channels">
          <div v-for="platform in channelFilters" :key="platform.id" :class="['channel-pill', { active: activePlatform === platform.id }]" @click="setActivePlatform(platform.id)" role="tab" :aria-selected="activePlatform === platform.id" tabindex="0">
            {{ platform.name }}
          </div>
          </div>
        <!-- Search and Toggle Row -->
        <div class="search-and-toggle-row">
            <div class="search-container">
              <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none">
                <circle cx="11" cy="11" r="8" stroke="currentColor" stroke-width="2"/>
                <path d="M21 21l-4.35-4.35" stroke="currentColor" stroke-width="2"/>
              </svg>
          <input v-model="searchQuery" type="text" class="search-input" placeholder="Search conversations..." @input="handleSearch" />
              <button v-if="searchQuery" class="search-clear" @click="clearSearch">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                  <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="2"/>
                  <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="2"/>
                </svg>
              </button>
            </div>
          <div class="view-toggle-pills" role="tablist" aria-label="View Mode">
            <div class="view-toggle-pill" :class="{ active: activeView === 'timeline' }" @click="activeView = 'timeline'" role="tab" :aria-selected="activeView === 'timeline'" tabindex="0">Timeline</div>
            <div class="view-toggle-pill" :class="{ active: activeView === 'table' }" @click="activeView = 'table'" role="tab" :aria-selected="activeView === 'table'" tabindex="0">Table View</div>
          </div>
            </div>
        <!-- Timeline View -->
        <div class="view-container" v-show="activeView === 'timeline'">
          <div v-if="groupedMessagesByDayWithDummy['Today'].length === 0 && groupedMessagesByDayWithDummy['Yesterday'].length === 0" class="no-chats">No chats to display.</div>
          <div class="time-section" v-for="(group, label) in groupedMessagesByDayWithDummy" :key="label">
            <h2 class="time-section-title">{{ label }}</h2>
            <div class="call-list">
              <div v-for="message in group" :key="message.id" :class="['call-item', 'glass-card', 'fine-border', { selected: selectedMessageId === message.id }]" @click="openChatPanel(message)">
                <div class="call-icon">
                  <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                  </svg>
                  </div>
                <div class="call-details">
                  <div class="call-type">{{ message.senderName }} ({{ getPlatformShortName(message.platform) }})</div>
                  <div class="call-time">{{ message.time }}</div>
                  <div class="call-meta">
                    <span class="case-link">{{ message.text }}</span>
                </div>
                      </div>
                    </div>
                  </div>
                    </div>
                  </div>
        <!-- Table View -->
        <div class="view-container" v-show="activeView === 'table'">
          <div v-if="filteredChats.length > 0" class="calls-table-container">
            <table class="calls-table">
              <thead>
                <tr>
                  <th>Contact</th>
                  <th>Platform</th>
                  <th>Last Message</th>
                  <th>Time</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="contact in filteredChats" :key="contact.id">
                  <td>{{ contact.senderName }}</td>
                  <td>{{ getPlatformShortName(contact.platform) }}</td>
                  <td>{{ contact.text }}</td>
                  <td>{{ contact.time }}</td>
                  <td><span :class="['status-badge', contact.status]">{{ contact.status }}</span></td>
                </tr>
              </tbody>
            </table>
                </div>
          <tbody v-else>
            <tr><td colspan="5" class="no-chats">No chats to display.</td></tr>
          </tbody>
              </div>
            </div>
      <!-- Chat Panel Modal (Centered) -->
      <div v-if="showChatPanel" class="chat-modal-overlay" @click.self="closeChatPanel" role="dialog" aria-modal="true">
        <div class="chat-modal-panel">
          <div class="chat-details-header">
            <div class="chat-details-avatar">
              <div class="avatar-circle" :style="{ background: getAvatarColor(selectedMessage?.senderName || '') }">
                {{ selectedMessage?.senderName?.charAt(0) || '?' }}
          </div>
              <div class="chat-details-title">
                <span class="contact-name">{{ selectedMessage?.senderName || 'Chat Details' }}</span>
                <span class="chat-channel-badge">{{ getPlatformShortName(selectedMessage?.platform) }}</span>
                <span class="chat-status">{{ selectedMessage?.status || 'Active' }}</span>
        </div>
              </div>
            <div class="chat-header-actions">
              <button class="end-chat-btn" @click="endChat" title="End Chat (Archive)">
                <svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
              </button>
              <button class="close-details" @click="closeChatPanel" aria-label="Close chat panel">×</button>
            </div>
          </div>
          <div class="chat-details-actions">
            <button class="chat-action-btn view" @click="viewCase" title="View Case">
              <svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="4"/><circle cx="12" cy="12" r="1"/></svg>
              </button>
            <button class="chat-action-btn link" @click="linkToCase" title="Link to Case">
              <svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><path d="M10 13a5 5 0 0 1 7 7l-3 3a5 5 0 0 1-7-7l1-1"/><path d="M14 11a5 5 0 0 0-7-7l-3 3a5 5 0 0 0 7 7l1-1"/></svg>
              </button>
            <button class="chat-action-btn create" @click="createCase" title="Create Case">
              <svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M9 12h6"/><path d="M12 9v6"/></svg>
              </button>
            <button class="chat-action-btn reporter" @click="editReporter" title="Add/Edit Reporter">
              <svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><circle cx="12" cy="7" r="4"/><path d="M5.5 21a8.38 8.38 0 0 1 13 0"/></svg>
            </button>
            <button class="chat-action-btn archive" @click="archiveChat" title="Archive">
              <svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><rect x="3" y="7" width="18" height="13" rx="2"/><path d="M16 3v4"/><path d="M8 3v4"/><path d="M3 7h18"/></svg>
              </button>
            </div>
          <div class="chat-details-content">
            <div class="chat-thread whatsapp-style">
              <div v-for="msg in simulatedChatThread" :key="msg.id" :class="['chat-bubble', msg.sender === 'counsellor' ? 'sent' : 'received']">
                <div class="bubble-text">{{ msg.text }}</div>
                <div class="bubble-time">{{ msg.time }}</div>
          </div>
        </div>
            <div class="message-input-area chat-panel-input">
            <div class="input-container">
                <input v-model="newMessageText" type="text" class="message-input" placeholder="Type a message..." @keypress.enter="sendMessage" />
                <button v-if="newMessageText.trim()" class="send-btn" @click="sendMessage" title="Send">Send</button>
              </div>
            </div>
            </div>
          </div>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import SidePanel from '@/components/SidePanel.vue'
import { applyTheme } from '@/utils/theme.js'

const router = useRouter()
const isSidebarCollapsed = ref(false)

// Reactive state
const searchQuery = ref('')
const activePlatform = ref('all')
const newMessageText = ref('')
const currentTheme = ref(localStorage.getItem('theme') || 'dark')
const showContactInfo = ref(false)
const showEndChatModal = ref(false)
const showCallModal = ref(false)
const callStatus = ref('Calling...')
const isMuted = ref(false)

// SidePanel related state
const userRole = ref('super-admin')
const isInQueue = ref(false)
const isProcessingQueue = ref(false)
const currentCall = ref(null)

// Refs
const messagesArea = ref(null)

// Platform definitions
const platforms = ref([
  { id: 'whatsapp', name: 'WhatsApp' },
  { id: 'sms', name: 'SMS' },
  { id: 'messenger', name: 'Messenger' },
  { id: 'telegram', name: 'Telegram' },
  { id: 'past', name: 'Archive' }
])

// Dummy chat records for each channel
const dummyChats = [
  // WhatsApp
  { id: 101, senderName: 'Alice Mwangi', platform: 'whatsapp', status: 'Active', date: 'Today', time: '09:00AM', text: 'Hi, I need help with my case.' },
  { id: 102, senderName: 'Brian Otieno', platform: 'whatsapp', status: 'Active', date: 'Today', time: '09:30AM', text: 'Can I get an update on my report?' },
  { id: 103, senderName: 'Cynthia Wanjiku', platform: 'whatsapp', status: 'Pending', date: 'Yesterday', time: '10:00AM', text: 'Thank you for your assistance.' },
  { id: 104, senderName: 'David Kimani', platform: 'whatsapp', status: 'Active', date: 'Today', time: '10:45AM', text: 'Is my case being processed?' },
  { id: 105, senderName: 'Esther Njeri', platform: 'whatsapp', status: 'Closed', date: 'Yesterday', time: '11:15AM', text: 'My issue was resolved, thanks.' },
  // SMS
  { id: 201, senderName: 'Faith Ouma', platform: 'sms', status: 'Active', date: 'Today', time: '09:10AM', text: 'I have a new concern.' },
  { id: 202, senderName: 'George Kariuki', platform: 'sms', status: 'Pending', date: 'Yesterday', time: '10:20AM', text: 'Please call me back.' },
  { id: 203, senderName: 'Helen Achieng', platform: 'sms', status: 'Active', date: 'Today', time: '11:00AM', text: 'How do I follow up?' },
  { id: 204, senderName: 'Isaac Mutua', platform: 'sms', status: 'Closed', date: 'Yesterday', time: '11:30AM', text: 'Thank you for your support.' },
  { id: 205, senderName: 'Janet Waweru', platform: 'sms', status: 'Active', date: 'Today', time: '12:00PM', text: 'I need urgent help.' },
  // Messenger
  { id: 301, senderName: 'Kevin Maina', platform: 'messenger', status: 'Active', date: 'Today', time: '09:20AM', text: 'Can I get more information?' },
  { id: 302, senderName: 'Lydia Chebet', platform: 'messenger', status: 'Pending', date: 'Yesterday', time: '10:40AM', text: 'I am waiting for a response.' },
  { id: 303, senderName: 'Martin Otieno', platform: 'messenger', status: 'Active', date: 'Today', time: '12:15PM', text: 'Please update me.' },
  { id: 304, senderName: 'Nancy Wambui', platform: 'messenger', status: 'Closed', date: 'Yesterday', time: '01:00PM', text: 'Case closed, thank you.' },
  { id: 305, senderName: 'Oscar Kiptoo', platform: 'messenger', status: 'Active', date: 'Today', time: '01:30PM', text: 'I have a question.' },
  // Telegram
  { id: 401, senderName: 'Pauline Njeri', platform: 'telegram', status: 'Active', date: 'Today', time: '09:50AM', text: 'How do I escalate my case?' },
  { id: 402, senderName: 'Quincy Mwenda', platform: 'telegram', status: 'Pending', date: 'Yesterday', time: '11:10AM', text: 'Still waiting for feedback.' },
  { id: 403, senderName: 'Ruth Muthoni', platform: 'telegram', status: 'Active', date: 'Today', time: '12:45PM', text: 'Can I speak to an agent?' },
  { id: 404, senderName: 'Samuel Karanja', platform: 'telegram', status: 'Closed', date: 'Yesterday', time: '01:20PM', text: 'Issue resolved.' },
  { id: 405, senderName: 'Terry Wainaina', platform: 'telegram', status: 'Active', date: 'Today', time: '02:00PM', text: 'I need more details.' },
  // Archive
  { id: 501, senderName: 'Ursula Mwende', platform: 'archive', status: 'Closed', date: 'Yesterday', time: '09:00AM', text: 'Thank you for your help.' },
  { id: 502, senderName: 'Victor Ochieng', platform: 'archive', status: 'Closed', date: 'Yesterday', time: '09:30AM', text: 'Case archived.' },
  { id: 503, senderName: 'Winnie Naliaka', platform: 'archive', status: 'Closed', date: 'Yesterday', time: '10:00AM', text: 'No further action needed.' },
  { id: 504, senderName: 'Xavier Kiplangat', platform: 'archive', status: 'Closed', date: 'Yesterday', time: '10:30AM', text: 'All done, thanks.' },
  { id: 505, senderName: 'Yvonne Atieno', platform: 'archive', status: 'Closed', date: 'Yesterday', time: '11:00AM', text: 'Appreciate your support.' },
];

// Timeline view: always show all chats grouped by day
const groupedMessagesByDayWithDummy = computed(() => {
  const groups = {};
  filteredChats.value.forEach(chat => {
    const day = chat.date;
    if (!groups[day]) groups[day] = [];
    groups[day].push(chat);
  });
  return {
    'Today': groups['Today'] || [],
    'Yesterday': groups['Yesterday'] || []
  };
});

// Helper functions
const getPlatformUnreadCount = (platformId) => {
  // Dummy implementation: count active chats for the platform
  return dummyChats.filter(chat => chat.platform === platformId && chat.status.toLowerCase() === 'active').length;
}

const getPlatformShortName = (platform) => {
  const shortNames = {
    whatsapp: 'WA',
    sms: 'SMS',
    messenger: 'MSG',
    telegram: 'TG'
  }
  return shortNames[platform] || platform.toUpperCase()
}

const getAvatarColor = (name) => {
  const colors = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
    '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'
  ]
  const index = name.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
  return colors[index % colors.length]
}

const getRiskLevelClass = (riskLevel) => {
  if (!riskLevel) return ''
  if (riskLevel.toLowerCase().includes('high')) return 'high-risk'
  if (riskLevel.toLowerCase().includes('medium')) return 'medium-risk'
  if (riskLevel.toLowerCase().includes('low')) return 'low-risk'
  return ''
}

// SidePanel event handlers
const handleQueueToggle = () => {
  isInQueue.value = !isInQueue.value
}

const handleLogout = () => {
  router.push('/')
}

const handleSidebarToggle = (collapsed) => {
  isSidebarCollapsed.value = collapsed
}

// Methods
const toggleTheme = () => {
  const newTheme = currentTheme.value === 'dark' ? 'light' : 'dark'
  localStorage.setItem('theme', newTheme)
  currentTheme.value = newTheme
  applyTheme(newTheme)
}

const setActivePlatform = (platformId) => {
  activePlatform.value = platformId
  searchQuery.value = ''
}

const selectContact = (contactId) => {
  selectedMessageId.value = contactId;
  // No unread count to clear in dummy data
  nextTick(() => {
    scrollToBottom();
  });
}

const deselectContact = () => {
  selectedMessageId.value = null
  showContactInfo.value = false
}

const toggleContactInfo = () => {
  showContactInfo.value = !showContactInfo.value
}

const endChat = () => {
  if (selectedMessage) {
    const chat = dummyChats.find(c => c.id === selectedMessage.id);
    if (chat) {
      chat.status = 'Closed';
      chat.platform = 'archive';
    }
  }
  closeChatPanel();
}

const cancelEndChat = () => {
  showEndChatModal.value = false
}

const sendMessage = () => {
  if (newMessageText.value.trim() !== '' && selectedMessageId.value !== null) {
    // Find the chat in dummyChats
    const chat = dummyChats.find(c => c.id === selectedMessageId.value);
    if (chat && chat.status.toLowerCase() === 'active') {
      // For demo, just update the selectedMessageThread
      selectedMessageThread.value.push({
        id: selectedMessageThread.value.length + 1,
        text: newMessageText.value,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        sender: 'me'
      });
      newMessageText.value = '';
      nextTick(() => {
        scrollToBottom();
      });
    }
  }
}

const scrollToBottom = () => {
  if (messagesArea.value) {
    messagesArea.value.scrollTop = messagesArea.value.scrollHeight
  }
}

const clearSearch = () => {
  searchQuery.value = ''
}

const handleSearch = () => {
  // Filtering handled by computed property
}

const handleTyping = () => {
  // Handle typing indicator
}

// Placeholder methods
const showNewChatModal = () => console.log('Show new chat modal')
const showAttachmentMenu = () => console.log('Show attachment menu')
const startVoiceMessage = () => console.log('Start voice message')
const viewFullProfile = () => console.log('View full profile')

// Lifecycle
onMounted(() => {
  const savedTheme = localStorage.getItem('theme') || 'dark'
    currentTheme.value = savedTheme
  applyTheme(savedTheme)
})

const queueStatus = computed(() => {
  return isInQueue ? 'In Queue' : 'Not in queue'
})

const showChatPanel = ref(false)
const selectedMessageId = ref(null)
const selectedMessage = ref(null)
const selectedMessageThread = ref([])

function openChatPanel(message) {
  selectedMessageId.value = message.id
  selectedMessage.value = message
  // Dummy thread for now, could be replaced with real data
  selectedMessageThread.value = [
    { id: 1, text: message.text, time: message.time },
    { id: 2, text: 'This is a reply.', time: '10:35 AM' }
  ]
  showChatPanel.value = true
}
function closeChatPanel() {
  showChatPanel.value = false
  selectedMessageId.value = null
  selectedMessage.value = null
  selectedMessageThread.value = []
}

// In script, define channelFilters with an 'All' option:
const channelFilters = [
  { id: 'all', name: 'All' },
  { id: 'whatsapp', name: 'WhatsApp' },
  { id: 'sms', name: 'SMS' },
  { id: 'messenger', name: 'Messenger' },
  { id: 'telegram', name: 'Telegram' },
  { id: 'archive', name: 'Archive' }
];

// For table view, filter by activePlatform unless 'all'
const filteredChats = computed(() => {
  if (activePlatform.value === 'all') return dummyChats;
  return dummyChats.filter(chat => chat.platform === activePlatform.value);
});

// Set timeline as the default view on load
const activeView = ref('timeline');

// In <script setup>, add dummy functions for actions:
function linkToCase() { alert('Link to Case (dummy)'); }
function createCase() {
  // Navigate to case creation with chat data
  router.push({
    path: '/case-creation',
    query: {
      reporter: selectedMessage?.senderName,
      platform: selectedMessage?.platform,
      chatId: selectedMessage?.id
    }
  });
}
function archiveChat() { alert('Archive Chat (dummy)'); }
function editReporter() { alert('Add/Edit Reporter (dummy)'); }

// In <script setup>, add a simulated chat thread:
const simulatedChatThread = computed(() => [
  { id: 1, sender: 'user', text: selectedMessage?.text || 'Hi, I need help with my case.', time: selectedMessage?.time || '09:00AM' },
  { id: 2, sender: 'counsellor', text: 'Hello, how can I assist you today?', time: '09:01AM' },
  { id: 3, sender: 'user', text: 'I want to know the status of my report.', time: '09:02AM' },
  { id: 4, sender: 'counsellor', text: 'Your report is being processed. We will update you soon.', time: '09:03AM' },
  { id: 5, sender: 'user', text: 'Thank you!', time: '09:04AM' },
  { id: 6, sender: 'counsellor', text: 'You are welcome!', time: '09:05AM' },
  ...selectedMessageThread.value
]);

// In <script setup>, update viewCase and createCase to navigate to real pages:
function viewCase() {
  // If selectedMessage has a caseId, navigate to /cases/:id, else alert
  if (selectedMessage?.caseId) {
    router.push(`/cases/${selectedMessage.caseId}`);
  } else {
    alert('No case linked to this chat.');
  }
}
</script>

<style>
  /* Root theme variables and resets */
  :root, body, html {
    --background-color: #f5f5f5;
    --content-bg: #fff;
    --text-color: #222;
    --text-secondary: #666;
    --border-color: #ddd;
  --accent-color: #964B00;
  --accent-hover: #b25900;
    --success-color: #4CAF50;
    --pending-color: #FFA500;
    --unassigned-color: #808080;
    --highlight-color: #ff3b30;
    --card-bg: #fff;
    font-family: 'Inter', sans-serif;
    font-size: 16px;
    box-sizing: border-box;
  }
  [data-theme="dark"], body.dark, :root.dark {
    --background-color: #000;
    --content-bg: #181818;
    --text-color: #fff;
    --text-secondary: #bbb;
    --border-color: #333;
    --card-bg: #181818;
  --accent-color: #964B00;
  --accent-hover: #b25900;
    --success-color: #4CAF50;
    --pending-color: #FFA500;
    --unassigned-color: #808080;
    --highlight-color: #ff3b30;
  }
  *, *:before, *:after {
    box-sizing: inherit;
  }
  body, html {
    background-color: var(--background-color);
    color: var(--text-color);
  margin: 0;
  padding: 0;
    min-height: 100vh;
    transition: background-color 0.3s, color 0.3s;
  }

  /* Main layout */
.main-content {
    background-color: var(--background-color);
    min-height: 100vh;
  display: flex;
  flex-direction: column;
    transition: background-color 0.3s;
  height: 100vh;
  overflow: hidden;
}
  .calls-container {
    background-color: var(--background-color);
  flex: 1;
    padding: 0 0 40px 0;
  display: flex;
  flex-direction: column;
    transition: background-color 0.3s;
  overflow-y: auto;
  min-height: 0;
  }

  /* Header */
  .header {
  display: flex;
  justify-content: space-between;
  align-items: center;
    padding: 32px 32px 0 32px;
    background: var(--background-color);
    flex-shrink: 0;
  }
  .page-title {
    font-size: 2rem;
    font-weight: 800;
    color: var(--text-color);
    margin: 0;
  }
.header-actions {
  display: flex;
    align-items: center;
    gap: 20px;
  }
  .theme-toggle {
    background-color: var(--content-bg);
    color: var(--text-color);
    border: 1px solid var(--border-color);
    border-radius: 30px;
    padding: 8px 15px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
  display: flex;
  align-items: center;
    gap: 8px;
    transition: all 0.3s ease;
    white-space: nowrap;
    min-width: 120px;
  }
  .theme-toggle:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  }
  .theme-toggle svg {
    width: 16px;
    height: 16px;
  }

  /* Tabs */
  .view-toggle-pills {
    display: flex;
    flex-shrink: 0;
    gap: 12px;
    min-width: 0;
    height: 48px;
  }
  .view-toggle-pill {
    border-radius: 30px;
    height: 48px;
    min-width: 110px;
    max-width: 160px;
    width: auto;
  display: flex;
  align-items: center;
  justify-content: center;
    font-size: 16px;
    font-weight: 600;
    border: 1.5px solid var(--border-color);
  white-space: nowrap;
    background: var(--content-bg);
    color: var(--text-color);
    transition: background 0.2s, color 0.2s;
    padding: 0 22px;
  }
  .view-toggle-pill.active {
    background: var(--accent-color);
    color: #fff;
    border: 1.5px solid var(--accent-color);
    z-index: 1;
  }

  /* Search Bar */
.search-and-toggle-row {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 24px;
    margin: 0 32px 18px 32px;
    flex-wrap: wrap;
  }
.search-container {
    width: 100%;
    border-radius: 30px;
    margin: 0;
  display: flex;
  align-items: center;
    background: var(--content-bg);
    border: 1px solid var(--border-color);
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    padding: 0 18px;
}
.search-icon {
    color: var(--text-secondary);
    margin-right: 10px;
    flex-shrink: 0;
  }
.search-input {
    flex: 1;
  border: none;
    background: transparent;
    color: var(--text-color);
    font-size: 15px;
    outline: none;
    padding: 14px 0;
    border-radius: 30px;
    box-shadow: none;
    height: 48px;
    line-height: 1.4;
    display: flex;
    align-items: center;
  }
.search-input:focus {
  outline: none;
    box-shadow: none;
}
.search-clear {
    background: none;
  border: none;
    color: var(--text-secondary);
    cursor: pointer;
    margin-left: 8px;
    font-size: 16px;
  display: flex;
  align-items: center;
}
.search-clear:hover {
    color: var(--accent-color);
}

  /* Timeline View */
  .view-container {
    margin: 0 32px;
  flex: 1;
  display: flex;
  flex-direction: column;
}
  .time-section-title {
  font-size: 16px;
    font-weight: 700;
    color: var(--accent-color);
    margin: 18px 0 10px 0;
  }
  .call-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  .call-item {
    background: var(--content-bg);
    color: var(--text-color);
    border-radius: 20px;
  display: flex;
  align-items: center;
    padding: 16px 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    transition: background 0.3s, color 0.3s, border 0.3s;
    border: 1.5px solid transparent;
  cursor: pointer;
    font-size: 15px;
  }
  .call-item.selected {
    border: 2px solid var(--accent-color);
    background: rgba(150,75,0,0.07);
    box-shadow: 0 2px 8px rgba(150,75,0,0.08);
  }
  .call-item:hover {
    background: rgba(150,75,0,0.04);
  }
  .call-item .call-icon {
    margin-right: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: var(--accent-color);
    color: #fff;
    flex-shrink: 0;
  }
  .call-details {
  flex: 1;
  min-width: 0;
  }
  .call-type, .call-time, .call-meta, .case-link {
    color: var(--text-color);
    font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
  .call-meta {
    font-size: 13px;
    color: var(--text-secondary);
    margin-top: 2px;
    white-space: normal;
  }

  /* Table View */
  .calls-table-container {
    background: var(--content-bg);
    border-radius: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    margin-top: 20px;
    overflow-x: auto;
  }
  .calls-table {
    width: 100%;
    background: var(--content-bg);
    color: var(--text-color);
    border-radius: 20px;
    border: 1px solid var(--border-color);
  font-size: 14px;
    border-collapse: separate;
    border-spacing: 0;
  overflow: hidden;
  }
  .calls-table th, .calls-table td {
    padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
    text-align: left;
  }
  .calls-table th {
    background: var(--background-color);
  color: var(--text-secondary);
    font-weight: 700;
  }
  .calls-table tr:last-child td {
    border-bottom: none;
  }
  .status-badge {
    color: #fff;
    padding: 6px 16px;
    border-radius: 30px;
    font-size: 12px;
    display: inline-block;
    font-weight: 700;
    text-align: center;
    min-width: 100px;
    transition: all 0.3s ease;
    background: var(--accent-color);
  }

  /* Chat Details Panel (see previous code for details) */
  .chat-details-panel {
    position: fixed;
    top: 0;
    right: 0;
    width: 400px;
    max-width: 100vw;
    height: 100vh;
    background: var(--content-bg);
    border-left: 1px solid var(--border-color);
    z-index: 2000;
    box-shadow: -5px 0 15px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
    transform: translateX(100%);
    transition: transform 0.3s ease;
  }
  .chat-details-panel.active {
    transform: translateX(0);
  }
  .chat-details-header {
  display: flex;
  align-items: center;
    justify-content: space-between;
    padding: 20px 24px 16px 24px;
  border-bottom: 1px solid var(--border-color);
    background: var(--content-bg);
    flex-shrink: 0;
}
  .chat-details-avatar {
  display: flex;
  align-items: center;
    gap: 16px;
  }
  .avatar-circle {
    width: 44px;
    height: 44px;
    border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
    font-size: 22px;
    font-weight: 700;
    color: #fff;
  }
  .chat-details-title {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
  .contact-name {
  font-size: 18px;
    font-weight: 700;
    color: var(--text-color);
  }
  .chat-channel-badge {
    background: var(--accent-color);
    color: #fff;
    border-radius: 12px;
    padding: 2px 10px;
    font-size: 13px;
    font-weight: 700;
    margin-left: 0;
    margin-top: 4px;
    align-self: flex-start;
  }
  .chat-status {
  font-size: 13px;
  color: var(--text-secondary);
    margin-top: 2px;
  }
  .close-details {
    background: none;
    border: none;
    color: var(--text-color);
    cursor: pointer;
    font-size: 24px;
    font-weight: 700;
    width: 32px;
    height: 32px;
    border-radius: 50%;
  display: flex;
  align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
  }
  .close-details:hover {
    background-color: rgba(255, 255, 255, 0.1);
  }
  .chat-details-actions {
  display: flex;
    gap: 10px;
    padding: 12px 24px;
    background: var(--content-bg);
    border-bottom: 1px solid var(--border-color);
    flex-shrink: 0;
  }
  .chat-action-btn {
    background: #f5f5f5;
    color: #222;
  border: none;
    border-radius: 12px;
    width: 44px;
    height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
    font-size: 22px;
    margin: 0 2px;
    transition: background 0.2s, color 0.2s, border 0.2s;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  }
  .chat-action-btn.view { background: #2196f3; color: #fff; }
  .chat-action-btn.link { background: #ff9800; color: #fff; }
  .chat-action-btn.create { background: #4caf50; color: #fff; }
  .chat-action-btn.reporter { background: #757575; color: #fff; }
  .chat-action-btn.archive { background: #e53935; color: #fff; }
  .chat-action-btn:hover { filter: brightness(1.1); }
  .chat-details-content {
  flex: 1;
  overflow-y: auto;
    overflow-x: hidden;
    padding: 24px 24px 0 24px;
  display: flex;
  flex-direction: column;
    gap: 18px;
    scrollbar-width: thin;
    scrollbar-color: rgba(255, 255, 255, 0.3) transparent;
  }
  .chat-thread.whatsapp-style {
    flex: 1;
    overflow-y: auto;
    margin: 0 0 10px 0;
  display: flex;
  flex-direction: column;
    gap: 10px;
    max-height: 350px;
    padding-bottom: 10px;
  }
  .chat-bubble {
    max-width: 80%;
    padding: 12px 18px;
    border-radius: 18px;
    font-size: 15px;
    background: var(--background-color);
    color: var(--text-color);
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    align-self: flex-start;
  position: relative;
    word-break: break-word;
  }
  .chat-bubble.sent {
    align-self: flex-end;
    background: var(--accent-color);
    color: #fff;
  }
  .bubble-text {
  margin-bottom: 4px;
}
  .bubble-time {
    font-size: 12px;
    color: var(--text-secondary);
    text-align: right;
  }
  .chat-panel-input {
    margin-top: 10px;
    background: var(--content-bg);
  border-top: 1px solid var(--border-color);
    padding-top: 10px;
    position: sticky;
    bottom: 0;
    z-index: 2;
}
.input-container {
  display: flex;
    align-items: center;
  gap: 8px;
  }
.message-input {
  flex: 1;
    border: 1px solid var(--border-color);
    border-radius: 24px;
    padding: 10px 16px;
  font-size: 15px;
    background: var(--content-bg);
    color: var(--text-color);
  outline: none;
    transition: border 0.2s;
  }
  .send-btn {
    background: var(--accent-color);
    color: #fff;
  border: none;
    border-radius: 18px;
    padding: 8px 18px;
    font-size: 15px;
    font-weight: 600;
  cursor: pointer;
    transition: background 0.2s;
  }
.send-btn:hover {
    background: var(--accent-hover);
  }
  @media (max-width: 600px) {
    .chat-details-panel {
      width: 100vw;
      max-width: 100vw;
      border-radius: 0;
    }
    .chat-details-header, .chat-details-actions, .chat-details-content {
      padding-left: 10px;
      padding-right: 10px;
    }
  }

  /* Empty state */
  .call-list:empty::before, .calls-table tbody:empty::before {
    content: 'No messages yet.';
  color: var(--text-secondary);
    font-size: 15px;
  text-align: center;
    display: block;
    margin: 40px 0;
  }

  /* Add or update this in the <style> section */
  .read-aloud-btn, .read-aloud-btn, button.read-aloud-btn {
    position: fixed;
    right: 32px;
    bottom: 32px;
    background: var(--accent-color);
    color: #fff;
  border: none;
    border-radius: 16px;
    padding: 8px 18px;
    font-size: 15px;
    font-weight: 700;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    cursor: pointer;
    z-index: 1000;
  display: flex;
  align-items: center;
    gap: 8px;
    transition: background 0.2s, box-shadow 0.2s;
  }
  .read-aloud-btn:hover {
    background: var(--accent-hover);
    box-shadow: 0 4px 16px rgba(150,75,0,0.12);
  }

  /* Channel filter pills */
  .channel-filters {
  display: flex;
    gap: 16px;
    margin: 0 32px 18px 32px;
    padding-top: 10px;
    padding-bottom: 0;
  }
  .channel-pill {
    padding: 10px 22px;
    border-radius: 24px;
    background: var(--content-bg);
    color: var(--text-color);
    border: 1.5px solid var(--border-color);
    font-size: 15px;
  font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    outline: none;
  }
  .channel-pill.active {
    background: var(--accent-color);
    color: #fff;
    border: 1.5px solid var(--accent-color);
  }
  .channel-pill:not(.active):hover {
    background: var(--accent-light);
    color: var(--accent-color);
    border: 1.5px solid var(--accent-color);
  }
  /* No chats fallback */
  .no-chats {
    text-align: center;
    color: var(--text-secondary);
  font-size: 16px;
    padding: 40px 0;
  }

  .main-content, .calls-container, .view-container, .call-item, .calls-table-container, .chat-details-panel, .channel-pill, .view-toggle-pill {
    background-color: var(--background-color) !important;
    color: var(--text-color) !important;
  }
  .channel-pill, .view-toggle-pill {
    background: var(--content-bg) !important;
    color: var(--text-color) !important;
  }
  .channel-pill.active, .view-toggle-pill.active {
    background: var(--accent-color) !important;
    color: #fff !important;
  }
  .call-item, .calls-table, .calls-table th, .calls-table td {
    background: var(--content-bg) !important;
    color: var(--text-color) !important;
  }

  /* Search and Toggle Row */
  .search-and-toggle-row {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 24px;
    margin: 0 32px 18px 32px;
    flex-wrap: wrap;
  }
  .search-section {
    flex: 0 1 400px;
    max-width: 400px;
    min-width: 200px;
    margin-right: 0;
  }
  .search-container {
    width: 100%;
    border-radius: 30px;
    margin: 0;
  display: flex;
  align-items: center;
    background: var(--content-bg);
  border: 1px solid var(--border-color);
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    padding: 0 18px;
  }
  .search-icon {
    color: var(--text-secondary);
    margin-right: 10px;
    flex-shrink: 0;
  }
  .search-input {
    flex: 1;
    border: none;
    background: transparent;
    color: var(--text-color);
    font-size: 15px;
    outline: none;
    padding: 14px 0;
    border-radius: 30px;
    box-shadow: none;
    height: 48px;
    line-height: 1.4;
  display: flex;
  align-items: center;
  }
  .search-input:focus {
    outline: none;
    box-shadow: none;
  }
  .search-clear {
    background: none;
    border: none;
  color: var(--text-secondary);
    cursor: pointer;
    margin-left: 8px;
    font-size: 16px;
    display: flex;
    align-items: center;
  }
  .search-clear:hover {
  color: var(--accent-color);
}
  .view-toggle-pills {
  display: flex;
    flex-shrink: 0;
    gap: 12px;
    min-width: 0;
    height: 48px;
  }
  .view-toggle-pill {
  border-radius: 30px;
    height: 48px;
    min-width: 110px;
    max-width: 160px;
    width: auto;
  display: flex;
  align-items: center;
  justify-content: center;
    font-size: 16px;
    font-weight: 600;
    border: 1.5px solid var(--border-color);
    white-space: nowrap;
    background: var(--content-bg);
    color: var(--text-color);
    transition: background 0.2s, color 0.2s;
    padding: 0 22px;
  }
  .view-toggle-pill.active {
    background: var(--accent-color);
    color: #fff;
    border: 1.5px solid var(--accent-color);
    z-index: 1;
  }
  @media (max-width: 900px) {
    .search-and-toggle-row {
      flex-direction: column;
      align-items: stretch;
      gap: 12px;
      margin: 0 10px 18px 10px;
    }
    .search-section {
      max-width: 100%;
    }
    .search-container, .view-toggle-pills, .view-toggle-pill {
      border-radius: 30px;
      min-width: 0;
      width: 100%;
      margin: 0;
    }
    .view-toggle-pills {
      flex-direction: row;
      width: 100%;
      gap: 12px;
      height: auto;
    }
    .view-toggle-pill {
      border-radius: 30px;
      margin: 0;
      min-width: 0;
      max-width: none;
      width: 100%;
    }
  }

  /* Chat Modal Overlay */
  .chat-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(0,0,0,0.25);
    z-index: 3000;
  display: flex;
  align-items: center;
  justify-content: center;
  }
  .chat-modal-panel {
    background: var(--content-bg);
    border-radius: 28px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.18);
    width: 100%;
    max-width: 420px;
    max-height: 90vh;
  display: flex;
    flex-direction: column;
    overflow: hidden;
    animation: fadeInScale 0.25s cubic-bezier(.4,1.4,.6,1) 1;
  }
  @keyframes fadeInScale {
    from { opacity: 0; transform: scale(0.95); }
    to { opacity: 1; transform: scale(1); }
  }
  .chat-details-header {
    border-radius: 28px 28px 0 0;
  }
  .chat-details-content {
    border-radius: 0 0 28px 28px;
    padding-bottom: 0;
  }
  .chat-details-actions {
    justify-content: center;
    gap: 18px;
    padding: 14px 0 10px 0;
    border-bottom: none;
  }
  .chat-action-btn {
    background: var(--content-bg);
    color: var(--accent-color);
    border: 2px solid var(--accent-color);
  border-radius: 50%;
    width: 44px;
    height: 44px;
  display: flex;
  align-items: center;
    justify-content: center;
    font-size: 22px;
    margin: 0 2px;
    transition: background 0.2s, color 0.2s, border 0.2s;
  }
  .chat-action-btn:hover {
    background: var(--accent-color);
  color: #fff;
    border-color: var(--accent-color);
  }
  .action-icon {
  display: flex;
    align-items: center;
  justify-content: center;
}
.chat-header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}
.end-chat-btn {
  background: #e53935;
  color: #fff;
  border: none;
  border-radius: 50%;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  margin-right: 4px;
  transition: background 0.2s, color 0.2s;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
  cursor: pointer;
}
.end-chat-btn:hover {
  background: #b71c1c;
}
</style>
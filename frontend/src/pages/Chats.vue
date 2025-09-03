<template>
  <div>
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
      <div class="page-container">
        <!-- Header -->
        <div class="header">
          <div class="header-content">
            <h1>Chats</h1>
            <p>Manage conversations and communications across all channels</p>
        </div>
        </div>

        <!-- Channel Filters -->
        <div class="channel-filters">
          <div
            v-for="platform in channelFilters"
            :key="platform.id"
            :class="[
              'channel-pill',
              { active: activePlatform === platform.id },
            ]"
            @click="setActivePlatform(platform.id)"
          >
            {{ platform.name }}
          </div>
        </div>

        <!-- Search and View Controls -->
        <div class="controls-section">
          <div class="search-container">
            <svg
              class="search-icon"
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
            >
              <circle
                cx="11"
                cy="11"
                r="8"
                stroke="currentColor"
                stroke-width="2"
              />
              <path
                d="M21 21l-4.35-4.35"
                stroke="currentColor"
                stroke-width="2"
              />
            </svg>
            <input
              v-model="searchQuery"
              type="text"
              class="search-input"
              placeholder="Search conversations..."
              @input="handleSearch"
            />
            <button
              v-if="searchQuery"
              class="search-clear"
              @click="clearSearch"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                <line
                  x1="18"
                  y1="6"
                  x2="6"
                  y2="18"
                  stroke="currentColor"
                  stroke-width="2"
                />
                <line
                  x1="6"
                  y1="6"
                  x2="18"
                  y2="18"
                  stroke="currentColor"
                  stroke-width="2"
                />
              </svg>
            </button>
          </div>

          <div class="view-toggle">
            <button
              class="view-btn"
          :class="{ active: activeView === 'timeline' }"
          @click="activeView = 'timeline'"
        >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2"/>
                <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2"/>
                <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2"/>
              </svg>
          Timeline
            </button>
            <button
              class="view-btn"
          :class="{ active: activeView === 'table' }"
          @click="activeView = 'table'"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2" stroke="currentColor" stroke-width="2"/>
                <line x1="9" y1="9" x2="15" y2="9" stroke="currentColor" stroke-width="2"/>
                <line x1="9" y1="13" x2="15" y2="13" stroke="currentColor" stroke-width="2"/>
                <line x1="9" y1="17" x2="15" y2="17" stroke="currentColor" stroke-width="2"/>
              </svg>
              Table
            </button>
        </div>
      </div>

    <!-- Timeline View -->
    <div class="view-container" v-show="activeView === 'timeline'">
      <div
        v-if="Object.keys(groupedMessagesByDate).length === 0"
            class="empty-state"
          >
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
              <path d="M21 15C21 15.5304 20.7893 16.0391 20.4142 16.4142C20.0391 16.7893 19.5304 17 19 17H7L3 21V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H19C19.5304 3 20.0391 3.21071 20.4142 3.58579C20.7893 3.96086 21 4.46957 21 5V15Z" stroke="currentColor" stroke-width="2"/>
              <path d="M8 9H16" stroke="currentColor" stroke-width="2"/>
              <path d="M8 13H14" stroke="currentColor" stroke-width="2"/>
            </svg>
            <h3>No chats to display</h3>
            <p>Start a conversation or check back later for new messages.</p>
      </div>

      <div
        class="time-section"
        v-for="(group, label) in groupedMessagesByDate"
        :key="label"
      >
        <h2 class="time-section-title">{{ label }}</h2>

            <div class="chat-list">
          <div
            v-for="message in group"
                  :key="message[messagesStore.pmessages_k.id?.[0] || 'id']"
            :class="[
                    'chat-item',
              {
                selected:
                  selectedMessageId ===
                        message[messagesStore.pmessages_k.id?.[0] || 'id'],
              },
            ]"
            @click="openChatPanel(message)"
          >
                  <div class="chat-avatar">
                    <div
                      class="avatar-circle"
                      :style="{
                        background: getAvatarColor(
                          message[messagesStore.pmessages_k.created_by?.[0] || 'created_by'] || ''
                        ),
                      }"
                    >
                      {{
                        message[messagesStore.pmessages_k.created_by?.[0] || 'created_by']?.charAt(0) || "?"
                      }}
                    </div>
            </div>

                  <div class="chat-details">
                    <div class="chat-header">
                      <div class="chat-name">
                        {{ message[messagesStore.pmessages_k.created_by?.[0] || 'created_by'] }}
              </div>
                      <div class="chat-time">
                {{
                          message[messagesStore.pmessages_k.dth?.[0] || 'dth']
                    ? new Date(
                                message[messagesStore.pmessages_k.dth?.[0] || 'dth'] * 1000
                              ).toLocaleTimeString()
                    : "N/A"
                }}
              </div>
                    </div>
                    <div class="chat-meta">
                      <span class="chat-platform">
                        {{ message[messagesStore.pmessages_k.src?.[0] || 'src'] }}
                      </span>
                      <span class="chat-status"
                            :class="[
                              'status-pill',
                              statusClass(message[messagesStore.pmessages_k.src_status?.[0] || 'src_status'])
                            ]"
                      >
                        <span class="status-dot" :class="dotClass(message[messagesStore.pmessages_k.src_status?.[0] || 'src_status'])"></span>
                        {{ message[messagesStore.pmessages_k.src_status?.[0] || 'src_status'] || "Active" }}
                </span>
                </div>
                    <div class="chat-preview">
                      {{ message[messagesStore.pmessages_k.src_msg?.[0] || 'src_msg'] }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Table View -->
    <div class="view-container" v-show="activeView === 'table'">
      <div
        v-if="messagesStore.pmessages.length > 0"
            class="chats-table-container"
      >
            <div class="chats-table-wrapper card">
              <table class="chats-table">
          <thead>
            <tr>
                    <th>Contact</th>
                    <th>Platform</th>
                    <th>Message</th>
                    <th>Time</th>
                    <th>Status</th>
                    <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr
                     v-for="message in filteredMessages"
                     :key="message[messagesStore.pmessages_k.id?.[0] || 'id']"
                     :class="{
                       selected:
                         selectedMessageId ===
                         message[messagesStore.pmessages_k.id?.[0] || 'id'],
                     }"
                     @click="openChatPanel(message)"
                   >
                     <td>
                       <div class="contact-cell">
                         <div
                           class="contact-avatar"
                           :style="{
                             background: getAvatarColor(
                               message[messagesStore.pmessages_k.created_by?.[0] || 'created_by'] || ''
                             ),
                           }"
                         >
                           {{
                             message[messagesStore.pmessages_k.created_by?.[0] || 'created_by']?.charAt(0) || "?"
                           }}
                         </div>
                         <span>{{ message[messagesStore.pmessages_k.created_by?.[0] || 'created_by'] }}</span>
                       </div>
                     </td>
                     <td>
                       <span class="platform-badge">
                         {{ message[messagesStore.pmessages_k.src?.[0] || 'src'] }}
                       </span>
                     </td>
                     <td class="message-cell">
                       {{ message[messagesStore.pmessages_k.src_msg?.[0] || 'src_msg'] }}
                     </td>
                     <td>
                       {{
                         message[messagesStore.pmessages_k.dth?.[0] || 'dth']
                    ? new Date(
                               message[messagesStore.pmessages_k.dth?.[0] || 'dth'] * 1000
                      ).toLocaleString()
                    : "N/A"
                }}
              </td>
              <td>
                <span
                         class="status-badge"
                         :class="statusClass(message[messagesStore.pmessages_k.src_status?.[0] || 'src_status'], true)"
                       >
                         {{ message[messagesStore.pmessages_k.src_status?.[0] || 'src_status'] || "Active" }}
                </span>
              </td>
                     <td>
                       <button
                         class="action-btn"
                         @click.stop="openChatPanel(message)"
                         title="Open Chat"
                       >
                         <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                           <path d="M21 15C21 15.5304 20.7893 16.0391 20.4142 16.4142C20.0391 16.7893 19.5304 17 19 17H7L3 21V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H19C19.5304 3 20.0391 3.21071 20.4142 3.58579C20.7893 3.96086 21 4.46957 21 5V15Z" stroke="currentColor" stroke-width="2"/>
                           <path d="M8 9H16" stroke="currentColor" stroke-width="2"/>
                           <path d="M8 13H14" stroke="currentColor" stroke-width="2"/>
                         </svg>
                       </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Chat Popup Panel -->
    <div class="chat-popup-overlay" v-if="showChatPanel" @click="closeChatPanel">
      <div class="chat-popup" @click.stop>
        <!-- Header -->
        <div class="chat-popup-header">
          <div class="chat-popup-avatar">
          <div
            class="avatar-circle"
            :style="{
              background: getAvatarColor(
                  selectedMessage?.[messagesStore.pmessages_k.created_by?.[0] || 'created_by'] || ''
              ),
            }"
          >
            {{
              selectedMessage?.[
                  messagesStore.pmessages_k.created_by?.[0] || 'created_by'
              ]?.charAt(0) || "?"
            }}
          </div>
          </div>
          <div class="chat-popup-info">
            <div class="chat-popup-name">
              {{ selectedMessage?.[messagesStore.pmessages_k.created_by?.[0] || 'created_by'] || "Chat" }}
        </div>
            <div class="chat-popup-meta">
              <span class="chat-popup-platform">
                {{ selectedMessage?.[messagesStore.pmessages_k.src?.[0] || 'src'] }}
            </span>
              <span class="chat-popup-status"
                    :class="[
                      'status-pill',
                      statusClass(selectedMessage?.[messagesStore.pmessages_k.src_status?.[0] || 'src_status'])
                    ]"
              >
                <span class="status-dot" :class="dotClass(selectedMessage?.[messagesStore.pmessages_k.src_status?.[0] || 'src_status'])"></span>
                {{ selectedMessage?.[messagesStore.pmessages_k.src_status?.[0] || 'src_status'] || "Active" }}
              </span>
        </div>
      </div>
          <div class="chat-popup-actions">
            <button class="popup-action-btn primary" @click="createCase" title="Create Case">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <path d="M12 5V19" stroke="currentColor" stroke-width="2"/>
                <path d="M5 12H19" stroke="currentColor" stroke-width="2"/>
          </svg>
              <span>Create Case</span>
        </button>
            <button class="popup-action-btn" @click="linkToCase" title="Link to Case">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" stroke="currentColor" stroke-width="2"/>
                <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" stroke="currentColor" stroke-width="2"/>
          </svg>
        </button>
            <button class="popup-action-btn danger" @click="endChat" title="End Chat">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <path d="M3 6H5H21" stroke="currentColor" stroke-width="2"/>
                <path d="M8 6V4C8 3.46957 8.21071 2.96086 8.58579 2.58579C8.96086 2.21071 9.46957 2 10 2H14C14.5304 2 15.0391 2.21071 15.4142 2.58579C15.7893 2.96086 16 3.46957 16 4V6M19 6V20C19 20.5304 18.7893 21.0391 18.4142 21.4142C18.0391 21.7893 17.5304 22 17 22H7C6.46957 22 5.96086 21.7893 5.58579 21.4142C5.21071 21.0391 5 20.5304 5 20V6H19Z" stroke="currentColor" stroke-width="2"/>
          </svg>
        </button>
            <button class="popup-close-btn" @click="closeChatPanel" title="Close">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="2"/>
                <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="2"/>
          </svg>
        </button>
          </div>
      </div>

        <!-- Content -->
        <div class="chat-popup-content">
          <!-- Message Display -->
          <div class="chat-messages">
            <div class="message-item">
              <div class="message-avatar">
                <div
                  class="avatar-circle small"
                  :style="{
                    background: getAvatarColor(
                      selectedMessage?.[messagesStore.pmessages_k.created_by?.[0] || 'created_by'] || ''
                    ),
                  }"
                >
                  {{
                    selectedMessage?.[
                      messagesStore.pmessages_k.created_by?.[0] || 'created_by'
                    ]?.charAt(0) || "?"
                  }}
                </div>
              </div>
              <div class="message-content">
                <div class="message-header">
                  <span class="message-sender">
                    {{ selectedMessage?.[messagesStore.pmessages_k.created_by?.[0] || 'created_by'] }}
                  </span>
                  <span class="message-time">
                    {{
                      selectedMessage?.[messagesStore.pmessages_k.dth?.[0] || 'dth']
                        ? new Date(
                            selectedMessage?.[messagesStore.pmessages_k.dth?.[0] || 'dth'] * 1000
                          ).toLocaleString()
                        : "N/A"
                    }}
                  </span>
                </div>
                <div class="message-text">
                  {{ selectedMessage?.[messagesStore.pmessages_k.src_msg?.[0] || 'src_msg'] }}
                </div>
              </div>
          </div>
        </div>

          <!-- Message Input -->
          <div class="chat-input-area">
          <div class="input-container">
              <textarea
                v-model="newMessage"
                placeholder="Type your message..."
              class="message-input"
                rows="3"
              ></textarea>
              <div class="input-actions">
                <button class="send-btn" @click="sendMessage" :disabled="!newMessage.trim()">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                    <path d="M22 2L11 13" stroke="currentColor" stroke-width="2"/>
                    <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" stroke-width="2"/>
                  </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
    </div>
    </div>  
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import SidePanel from "@/components/SidePanel.vue";
import { useMessagesStore } from "@/stores/messages";

const messagesStore = useMessagesStore();
const router = useRouter();

// SidePanel props and state
const userRole = ref("admin");
const isInQueue = ref(false);
const isProcessingQueue = ref(false);
const currentCall = ref(null);

// SidePanel event handlers
const handleQueueToggle = () => {
  isInQueue.value = !isInQueue.value;
};

const handleLogout = () => {
  // Handle logout logic
  console.log("Logout clicked");
};

const handleSidebarToggle = () => {
  // Handle sidebar toggle logic
  console.log("Sidebar toggle clicked");
};

// Chat state
const searchQuery = ref("");
const activePlatform = ref("all");
const activeView = ref("timeline");
const showChatPanel = ref(false);
const selectedMessage = ref(null);
const selectedMessageId = ref(null);
const newMessage = ref("");

// Channel filters
const channelFilters = ref([
  { id: "all", name: "All Channels" },
  { id: "whatsapp", name: "WhatsApp" },
  { id: "sms", name: "SMS" },
  { id: "messenger", name: "Messenger" },
  { id: "telegram", name: "Telegram" },
]);

// Computed
const filteredMessages = computed(() => {
  let messages = messagesStore.pmessages;
  
  // If no messages from API, use sample data
  if (!messages || messages.length === 0) {
    messages = [
      {
        id: 1,
        created_by: "John Doe",
        src: "whatsapp",
        src_msg: "Hello, I need help with my case.",
        dth: Math.floor(Date.now() / 1000) - 3600, // 1 hour ago
        src_status: "active"
      },
      {
        id: 2,
        created_by: "Jane Smith",
        src: "sms",
        src_msg: "Thank you for your assistance.",
        dth: Math.floor(Date.now() / 1000) - 7200, // 2 hours ago
        src_status: "active"
      },
      {
        id: 3,
        created_by: "Mike Johnson",
        src: "messenger",
        src_msg: "Can you provide an update on my case?",
        dth: Math.floor(Date.now() / 1000) - 86400, // 1 day ago
        src_status: "pending"
      },
      {
        id: 4,
        created_by: "Sarah Wilson",
        src: "telegram",
        src_msg: "I have some new information to share.",
        dth: Math.floor(Date.now() / 1000) - 172800, // 2 days ago
        src_status: "active"
      },
      {
        id: 5,
        created_by: "David Brown",
        src: "whatsapp",
        src_msg: "When will my case be reviewed?",
        dth: Math.floor(Date.now() / 1000) - 259200, // 3 days ago
        src_status: "active"
      }
    ];
  }
  
  // Filter by platform
  if (activePlatform.value !== "all") {
    messages = messages.filter(
      (msg) => msg[messagesStore.pmessages_k.src?.[0] || 'src'] === activePlatform.value
    );
  }
  
  // Filter by search query
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase();
    messages = messages.filter((msg) => {
      const sender = msg[messagesStore.pmessages_k.created_by?.[0] || 'created_by'] || "";
      const message = msg[messagesStore.pmessages_k.src_msg?.[0] || 'src_msg'] || "";
      return (
        sender.toLowerCase().includes(query) ||
        message.toLowerCase().includes(query)
      );
    });
  }
  
  return messages;
});

const groupedMessagesByDate = computed(() => {
  const messages = filteredMessages.value;
  const timeKey = messagesStore.pmessages_k?.dth?.[0] || 'dth';

  if (!Array.isArray(messages) || messages.length === 0) return {};

  const groups = {};
  for (const msg of messages) {
    const timestamp = msg[timeKey];
    if (!timestamp) continue;
    
    const date = new Date(timestamp * 1000);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    
    let label;
    if (date.toDateString() === today.toDateString()) {
      label = "Today";
    } else if (date.toDateString() === yesterday.toDateString()) {
      label = "Yesterday";
    } else {
      label = date.toLocaleDateString();
    }
    
    if (!groups[label]) groups[label] = [];
    groups[label].push(msg);
  }
  
  return groups;
});

// Methods
const setActivePlatform = (platformId) => {
  activePlatform.value = platformId;
};

const handleSearch = () => {
  // Search is handled by computed property
};

const clearSearch = () => {
  searchQuery.value = "";
};

const openChatPanel = (message) => {
  selectedMessage.value = message;
  selectedMessageId.value = message[messagesStore.pmessages_k.id?.[0] || 'id'];
  showChatPanel.value = true;
};

const closeChatPanel = () => {
  showChatPanel.value = false;
  selectedMessage.value = null;
  selectedMessageId.value = null;
  newMessage.value = "";
};

const sendMessage = () => {
  if (!newMessage.value.trim() || !selectedMessage.value) return;
  
  // Here you would typically send the message to your backend
  console.log("Sending message:", newMessage.value);
  
  // For now, just clear the input
  newMessage.value = "";
};

const createCase = () => {
  if (selectedMessage.value) {
    // Navigate to case creation with chat data
    console.log("Creating case from chat:", selectedMessage.value);
    router.push({
      name: 'CaseCreation',
      query: {
        chatId: selectedMessage.value[messagesStore.pmessages_k.id?.[0] || 'id'],
        contact: selectedMessage.value[messagesStore.pmessages_k.created_by?.[0] || 'created_by'],
        platform: selectedMessage.value[messagesStore.pmessages_k.src?.[0] || 'src'],
        message: selectedMessage.value[messagesStore.pmessages_k.src_msg?.[0] || 'src_msg']
      }
    });
    closeChatPanel();
  }
};

const viewCase = () => {
  if (selectedMessage.value) {
    // Navigate to case details or open case modal
    console.log("Viewing case for message:", selectedMessage.value);
  }
};

const linkToCase = () => {
  if (selectedMessage.value) {
    // Navigate to cases page
    console.log("Linking chat to case:", selectedMessage.value);
  router.push({
      name: 'Cases'
    });
    closeChatPanel();
  }
};

const endChat = () => {
  if (selectedMessage.value) {
    // End/archive the chat
    console.log("Ending chat:", selectedMessage.value);
    closeChatPanel();
  }
};

const getAvatarColor = (name) => {
  // Use the same brown color as buttons
  return 'var(--color-primary)';
};

const statusClass = (raw, isTable = false) => {
  const v = String(raw || 'active').toLowerCase()
  const map = {
    active: isTable ? 'status--active' : 'status--active',
    pending: isTable ? 'status--pending' : 'status--pending',
    inactive: 'status--inactive',
    busy: 'status--busy',
    away: 'status--away'
  }
  return map[v] || map.active
}

const dotClass = (raw) => {
  const v = String(raw || 'active').toLowerCase()
  const map = { active: 'dot--active', pending: 'dot--pending', inactive: 'dot--inactive', busy: 'dot--busy', away: 'dot--away' }
  return map[v] || map.active
}

// Lifecycle
onMounted(async () => {
  // Initialize messages data
  try {
    await messagesStore.fetchAllMessages();
  } catch (error) {
    console.error('Failed to fetch messages:', error);
  }
});
</script>

<style scoped>
/* Main content layout with SidePanel */
.main-content {
  margin-left: 280px;
  min-height: 100vh;
  background: var(--color-surface);
  transition: margin-left 0.3s ease;
}

@media (max-width: 768px) {
.main-content {
    margin-left: 0;
  }
}

.page-container {
  padding: 20px;
  min-height: 100vh;
}

/* Header */
.header {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  margin-bottom: 24px;
}

.header-content h1 {
  margin: 0;
  font-size: 26px;
  font-weight: 900;
  color: var(--text-color);
}

.header-content p {
  margin: 6px 0 0;
  color: var(--color-muted);
  font-size: 14px;
}

/* Channel Filters */
.channel-filters {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.channel-pill {
  padding: 8px 16px;
  border-radius: 20px;
  background: var(--color-surface);
  color: var(--text-color);
  border: 1px solid var(--color-border);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.channel-pill.active {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.channel-pill:hover:not(.active) {
  background: var(--color-surface-muted);
  border-color: var(--color-primary);
}

/* Controls Section */
.controls-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  margin-bottom: 24px;
}

.search-container {
  position: relative;
  flex: 1;
  max-width: 400px;
}

.search-container svg {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-muted);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 10px 12px 10px 40px;
  border: 1px solid var(--color-border);
  border-radius: 12px;
  background: var(--color-surface);
  color: var(--text-color);
  font-size: 14px;
  transition: border-color 0.2s ease;
}

.search-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px color-mix(in oklab, var(--color-primary) 10%, transparent);
}

.search-clear {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--color-muted);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.search-clear:hover {
  background: var(--color-surface-muted);
  color: var(--text-color);
}

.view-toggle {
  display: flex;
  gap: 8px;
}

.view-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border: 1px solid var(--color-border);
  border-radius: 10px;
  background: var(--color-surface);
  color: var(--text-color);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.view-btn.active {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.view-btn:hover:not(.active) {
  background: var(--color-surface-muted);
  border-color: var(--color-primary);
}

/* View Container */
.view-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
  color: var(--color-muted);
}

.empty-state svg {
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-state h3 {
  margin: 0 0 8px;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-color);
}

.empty-state p {
  margin: 0;
  font-size: 14px;
  line-height: 1.5;
}

/* Time Section */
.time-section {
  margin-bottom: 24px;
}

.time-section-title {
  margin: 0 0 16px;
  font-size: 16px;
  font-weight: 700;
  color: var(--text-color);
  padding-bottom: 8px;
  border-bottom: 1px solid var(--color-border);
}

/* Chat List */
.chat-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chat-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.chat-item:hover {
  background: var(--color-surface-muted);
  border-color: var(--color-primary);
  transform: translateY(-1px);
}

.chat-item.selected {
  background: color-mix(in oklab, var(--color-primary) 8%, transparent);
  border-color: var(--color-primary);
}

.chat-avatar {
  flex-shrink: 0;
}

.avatar-circle {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  font-size: 18px;
}

.avatar-circle.small {
  width: 36px;
  height: 36px;
  font-size: 14px;
}

.chat-details {
  flex: 1;
  min-width: 0;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.chat-name {
  font-weight: 600;
  color: var(--text-color);
  font-size: 15px;
}

.chat-time {
  color: var(--color-muted);
  font-size: 12px;
}

.chat-meta {
  display: flex;
  gap: 8px;
  margin-bottom: 6px;
}

.chat-platform,
.chat-status {
  padding: 2px 8px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.chat-platform {
  background: color-mix(in oklab, var(--color-primary) 10%, transparent);
  color: var(--color-primary);
}

.chat-status {
  background: color-mix(in oklab, var(--success-color) 10%, transparent);
  color: var(--success-color);
}

.chat-preview {
  color: var(--color-muted);
  font-size: 13px;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

/* Table View */
.chats-table-container {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.chats-table-wrapper {
  overflow-x: auto;
}

.chats-table {
  width: 100%;
  border-collapse: collapse;
}

.chats-table th {
  background: var(--color-surface-muted);
  color: var(--text-color);
  font-weight: 600;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 16px;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}

.chats-table td {
  padding: 16px;
  border-bottom: 1px solid var(--color-border);
  color: var(--text-color);
  font-size: 14px;
}

.chats-table tr:hover {
  background: var(--color-surface-muted);
}

.chats-table tr.selected {
  background: color-mix(in oklab, var(--color-primary) 4%, transparent);
}

.chats-table tr:last-child td {
  border-bottom: none;
}

.contact-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.contact-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 12px;
}

.platform-badge {
  padding: 4px 8px;
  border-radius: 6px;
  background: color-mix(in oklab, var(--color-primary) 10%, transparent);
  color: var(--color-primary);
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.message-cell {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-badge.status-active {
  background: color-mix(in oklab, var(--success-color) 10%, transparent);
  color: var(--success-color);
}

.status-badge.status-pending {
  background: color-mix(in oklab, var(--warning-color) 10%, transparent);
  color: var(--warning-color);
}

.action-btn {
  background: none;
  border: none;
  color: var(--color-muted);
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background: var(--color-surface-muted);
  color: var(--text-color);
}

/* Chat Popup Panel */
.chat-popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.3);
  z-index: 3000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chat-popup {
  background: var(--color-surface);
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  width: 100%;
  max-width: 480px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-popup-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface);
}

.chat-popup-avatar {
  flex-shrink: 0;
}

.chat-popup-info {
  flex: 1;
  min-width: 0;
}

.chat-popup-name {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-color);
  margin-bottom: 4px;
}

.chat-popup-meta {
  display: flex;
  gap: 8px;
}

.chat-popup-platform,
.chat-popup-status {
  padding: 2px 8px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.chat-popup-platform {
  background: color-mix(in oklab, var(--color-primary) 10%, transparent);
  color: var(--color-primary);
}

.chat-popup-status {
  background: color-mix(in oklab, var(--success-color) 10%, transparent);
  color: var(--success-color);
}

.chat-popup-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.popup-action-btn,
.popup-close-btn {
  background: var(--color-surface-muted);
  border: none;
  color: var(--text-color);
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.popup-action-btn:hover,
.popup-close-btn:hover {
  background: var(--color-surface);
  transform: translateY(-1px);
}

.popup-action-btn.primary {
  background: var(--color-primary);
  color: white;
  padding: 8px 12px;
  gap: 6px;
  font-size: 13px;
  font-weight: 500;
}

.popup-action-btn.primary:hover {
  background: color-mix(in oklab, var(--color-primary) 80%, black);
  color: white;
}

.popup-action-btn.danger {
  background: var(--error-color);
  color: white;
}

.popup-action-btn.danger:hover {
  background: color-mix(in oklab, var(--error-color) 80%, black);
  color: white;
}

.popup-close-btn:hover {
  background: var(--error-color);
  color: white;
}

.chat-popup-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-messages {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.message-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 16px;
}

.message-avatar {
  flex-shrink: 0;
}

.message-content {
  flex: 1;
  background: var(--color-surface-muted);
  border-radius: 16px;
  padding: 12px 16px;
  min-width: 0;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.message-sender {
  font-weight: 600;
  color: var(--text-color);
  font-size: 13px;
}

.message-time {
  color: var(--color-muted);
  font-size: 11px;
}

.message-text {
  color: var(--text-color);
  font-size: 14px;
  line-height: 1.4;
  word-break: break-word;
  background: var(--color-surface-muted);
  padding: 12px 16px;
  border-radius: 12px;
}

.chat-input-area {
  padding: 20px;
  border-top: 1px solid var(--color-border);
  background: var(--color-surface);
}

.input-container {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.message-input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid var(--color-border);
  border-radius: 12px;
  background: var(--color-surface);
  color: var(--text-color);
  font-size: 14px;
  font-family: inherit;
  resize: none;
  min-height: 44px;
  max-height: 120px;
  line-height: 1.4;
  transition: border-color 0.2s ease;
}

.message-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px color-mix(in oklab, var(--color-primary) 10%, transparent);
}

.input-actions {
  flex-shrink: 0;
}

.send-btn {
  background: var(--color-primary);
  color: white;
  border: none;
  padding: 12px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
}

.send-btn:hover:not(:disabled) {
  background: color-mix(in oklab, var(--color-primary) 80%, black);
  transform: translateY(-1px);
}

.send-btn:disabled {
  background: var(--color-muted);
  cursor: not-allowed;
  opacity: 0.6;
}

/* Responsive */
@media (max-width: 768px) {
  .controls-section {
  flex-direction: column;
    align-items: stretch;
  }
  
  .search-container {
    max-width: none;
  }
  
  .view-toggle {
    justify-content: center;
  }
  
  .chat-popup {
    margin: 20px;
    max-height: calc(100vh - 40px);
  }
}

/* Dark mode adjustments */
@media (prefers-color-scheme: dark) {
  .chat-popup-overlay {
    background: rgba(0, 0, 0, 0.7);
  }
}
</style>

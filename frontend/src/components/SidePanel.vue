<template>
  <div>
    <!-- Mobile Menu Button -->
    <button class="mobile-menu-btn" id="mobile-menu-btn" @click="toggleMobileMenu">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M3 12H21M3 6H21M3 18H21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </button>

    <!-- Sidebar -->
    <div class="sidebar glass-panel fine-border" :class="{ collapsed: isSidebarCollapsed, 'mobile-open': mobileOpen }" id="sidebar">
      <div class="toggle-btn" @click="toggleSidebar">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M3 12H21M3 6H21M3 18H21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>

      <div class="sidebar-content">
        <div class="sidepanel-coatofarms">
          <img src="@/assets/images/coat of arms.png" alt="Kenya Coat of Arms" />
        </div>
        <div class="sidebar-header">
          <!-- Logo removed as requested -->
        </div>
        
        <div class="nav-section">
          <router-link to="/dashboard" class="nav-item" :class="{ active: $route.path === '/dashboard' }">
            <div class="nav-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M3 9L12 2L21 9V20C21 20.5304 20.7893 21.0391 20.4142 21.4142C20.0391 21.7893 19.5304 22 19 22H5C4.46957 22 3.96086 21.7893 3.58579 21.4142C3.21071 21.0391 3 20.5304 3 20V9Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <polyline points="9,22 9,12 15,12 15,22" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div class="nav-text">Dashboard</div>
          </router-link>
          
          <router-link to="/calls" class="nav-item" :class="{ active: $route.path === '/calls' }">
            <div class="nav-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M22 16.92V19C22 20.1046 21.1046 21 20 21C10.6112 21 3 13.3888 3 4C3 2.89543 3.89543 2 5 2H7.08C7.55607 2 7.95823 2.33718 8.02513 2.80754L8.7 7.5C8.76694 7.97036 8.53677 8.42989 8.12 8.67L6.5 9.5C7.84 12.16 11.84 16.16 14.5 17.5L15.33 15.88C15.5701 15.4632 16.0296 15.2331 16.5 15.3L21.1925 16.0249C21.6628 16.0918 22 16.4939 22 16.97V16.92Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div class="nav-text">Calls</div>
          </router-link>
          
          <router-link to="/cases" class="nav-item" :class="{ active: $route.path === '/cases' }">
            <div class="nav-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <polyline points="14,2 14,8 20,8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="16" y1="13" x2="8" y2="13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="16" y1="17" x2="8" y2="17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <polyline points="10,9 9,9 8,9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div class="nav-text">Cases</div>
          </router-link>
          
          <router-link to="/reviews" class="nav-item" :class="{ active: $route.path === '/reviews' }">
            <div class="nav-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M14 2H6C5.47 2 4.96 2.21 4.59 2.59C4.21 2.96 4 3.47 4 4V20C4 20.53 4.21 21.04 4.59 21.41C4.96 21.79 5.47 22 6 22H18C18.53 22 19.04 21.79 19.41 21.41C19.79 21.04 20 20.53 20 20V8L14 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M9 12H15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M9 16H13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div class="nav-text">Reviews</div>
          </router-link>
          
          <router-link to="/chats" class="nav-item" :class="{ active: $route.path === '/chats' }">
            <div class="nav-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M21 15C21 15.5304 20.7893 16.0391 20.4142 16.4142C20.0391 16.7893 19.5304 17 19 17H7L3 21V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H19C19.5304 3 20.0391 3.21071 20.4142 3.58579C20.7893 3.96086 21 4.46957 21 5V15Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M8 9H16" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M8 13H14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div class="nav-text">Chats</div>
          </router-link>
          
          <router-link to="/qa-statistics" class="nav-item" :class="{ active: $route.path === '/qa-statistics' }">
            <div class="nav-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <line x1="18" y1="20" x2="18" y2="10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="12" y1="20" x2="12" y2="4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="6" y1="20" x2="6" y2="14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div class="nav-text">QA Statistics</div>
          </router-link>
          
          <router-link to="/wallboard" class="nav-item" :class="{ active: $route.path === '/wallboard' }">
            <div class="nav-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="2" y="3" width="20" height="14" rx="2" ry="2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="8" y1="21" x2="16" y2="21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="12" y1="17" x2="12" y2="21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div class="nav-text">Wallboard</div>
          </router-link>

          <router-link to="/reports" class="nav-item" :class="{ active: $route.path === '/reports' }">
            <div class="nav-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M3 3H21V21H3V3Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M7 7H17V9H7V7Z" fill="currentColor"/>
                <path d="M7 11H17V13H7V11Z" fill="currentColor"/>
                <path d="M7 15H13V17H7V15Z" fill="currentColor"/>
              </svg>
            </div>
            <div class="nav-text">Reports</div>
          </router-link>
          
          <router-link to="/settings" class="nav-item" :class="{ active: $route.path === '/settings' }">
            <div class="nav-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M19.4 15C19.2669 15.3016 19.2272 15.6362 19.286 15.9606C19.3448 16.285 19.4995 16.5843 19.73 16.82L19.79 16.88C19.976 17.0657 20.1235 17.2863 20.2241 17.5291C20.3248 17.7719 20.3766 18.0322 20.3766 18.295C20.3766 18.5578 20.3248 18.8181 20.2241 19.0609C20.1235 19.3037 19.976 19.5243 19.71 19.71C19.6043 19.896 19.3837 20.0435 19.1409 20.1441C18.8981 20.2448 18.6378 20.2966 18.375 20.2966C18.1122 20.2966 17.8519 20.2448 17.6091 20.1441C17.3663 20.0435 17.1457 19.896 16.96 19.71L16.9 19.65C16.6643 19.4195 16.365 19.2648 16.0406 19.206C15.7162 19.1472 15.3816 19.1869 15.08 19.32C14.7842 19.4468 14.532 19.6572 14.3543 19.9255C14.1766 20.1938 14.0813 20.5082 14.08 20.83V21C14.08 21.5304 13.8693 22.0391 13.4942 22.4142C13.1191 22.7893 12.6104 23 12.08 23C11.5496 23 11.0409 22.7893 10.6658 22.4142C10.2907 22.0391 10.08 21.5304 10.08 21V20.91C10.0723 20.579 9.96512 20.2573 9.77251 19.9887C9.5799 19.7201 9.31074 19.5176 9 19.41C8.69838 19.2769 8.36381 19.2372 8.03941 19.296C7.71502 19.3548 7.41568 19.5095 7.18 19.74L7.12 19.8C6.93425 19.986 6.71368 20.1335 6.47088 20.2341C6.22808 20.3348 5.96783 20.3866 5.705 20.3866C5.44217 20.3866 5.18192 20.3348 4.93912 20.2341C4.69632 20.1335 4.47575 19.986 4.29 19.8C4.10405 19.6143 3.95653 19.3937 3.85588 19.1509C3.75523 18.9081 3.70343 18.6478 3.70343 18.385C3.70343 18.1222 3.75523 17.8619 3.85588 17.6191C3.95653 17.3763 4.10405 17.1557 4.29 16.97L4.35 16.91C4.58054 16.6743 4.73519 16.375 4.794 16.0506C4.85282 15.7262 4.81312 15.3916 4.68 15.09C4.55324 14.7942 4.34276 14.542 4.07447 14.3643C3.80618 14.1866 3.49179 14.0913 3.17 14.09H3C2.46957 14.09 1.96086 13.8793 1.58579 13.5042C1.21071 13.1291 1 12.6204 1 12.09C1 11.5596 1.21071 11.0509 1.58579 10.6758C1.96086 10.3007 2.46957 10.09 3 10.09H3.09C3.42099 10.0823 3.742 9.97512 4.01062 9.78251C4.27925 9.5899 4.48167 9.32074 4.59 9.01C4.72312 8.70838 4.76282 8.37381 4.704 8.04941C4.64519 7.72502 4.49054 7.42568 4.26 7.19L4.2 7.13C4.01405 6.94425 3.86653 6.72368 3.76588 6.48088C3.66523 6.23808 3.61343 5.97783 3.61343 5.715C3.61343 5.45217 3.66523 5.19192 3.76588 4.94912C3.86653 4.70632 4.01405 4.48575 4.2 4.3C4.38575 4.11405 4.60632 3.96653 4.84912 3.86588C5.09192 3.76523 5.35217 3.71343 5.615 3.71343C5.87783 3.71343 6.13808 3.76523 6.38088 3.86588C6.62368 3.96653 6.84425 4.11405 7.03 4.3L7.09 4.36C7.32568 4.59054 7.62502 4.74519 7.94941 4.804C8.27381 4.86282 8.60838 4.82312 8.91 4.69H9C9.29577 4.56324 9.54802 4.35276 9.72569 4.08447C9.90337 3.81618 9.99872 3.50179 10 3.18V3C10 2.46957 10.2107 1.96086 10.5858 1.58579C10.9609 1.21071 11.4696 1 12 1C12.5304 1 13.0391 1.21071 13.4142 1.58579C13.7893 1.96086 14 2.46957 14 3V3.09C14.0013 3.41179 14.0966 3.72618 14.2743 3.99447C14.452 4.26276 14.7042 4.47324 15 4.6C15.3016 4.73312 15.6362 4.77282 15.9606 4.714C16.285 4.65519 16.5843 4.50054 16.82 4.27L16.88 4.21C17.0657 4.02405 17.2863 3.87653 17.5291 3.77588C17.7719 3.67523 18.0322 3.62343 18.295 3.62343C18.5578 3.62343 18.8181 3.67523 19.0609 3.77588C19.3037 3.87653 19.5243 4.02405 19.71 4.21C19.896 4.39575 20.0435 4.61632 20.1441 4.85912C20.2448 5.10192 20.2966 5.36217 20.2966 5.625C20.2966 5.88783 20.2448 6.14808 20.1441 6.39088C20.0435 6.63368 19.896 6.85425 19.71 7.04L19.65 7.1C19.4195 7.33568 19.2648 7.63502 19.206 7.95941C19.1472 8.28381 19.1869 8.61838 19.32 8.92V9C19.4468 9.29577 19.6572 9.54802 19.9255 9.72569C20.1938 9.90337 20.5082 9.99872 20.83 10H21C21.5304 10 22.0391 10.2107 22.4142 10.5858C22.7893 10.9609 23 11.4696 23 12C23 12.5304 22.7893 13.0391 22.4142 13.4142C22.0391 13.7893 21.5304 14 21 14H20.91C20.5882 14.0013 20.2738 14.0966 20.0055 14.2743C19.7372 14.452 19.5268 14.7042 19.4 15Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div class="nav-text">Settings</div>
          </router-link>
        </div>
        
        <div class="sidebar-bottom">
          <div class="user-profile">
            <router-link to="/edit-profile" class="user-avatar">
              <svg viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 12C14.2091 12 16 10.2091 16 8C16 5.79086 14.2091 4 12 4C9.79086 4 8 5.79086 8 8C8 10.2091 9.79086 12 12 12Z"/>
                <path d="M12 14C7.58172 14 4 17.5817 4 22H20C20 17.5817 16.4183 14 12 14Z"/>
              </svg>
            </router-link>
          </div>
          
          <div class="status">
            <div class="status-dot" :class="{ 'in-queue': isInQueue }"></div>
            <span>{{ queueStatus }}</span>
          </div>
          
          <div class="button-container">
            <button 
              class="join-queue-btn" 
              :class="{ 'in-queue': isInQueue, 'has-call': currentCall }"
              @click="handleQueueToggle"
              :disabled="isProcessingQueue"
            >
              {{ queueButtonText }}
            </button>
            <button class="logout-btn" @click="handleLogout">Logout</button>
          </div>
        </div>
      </div>
    </div>

    <button class="expand-btn" @click="expandSidebar" id="expand-btn">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M3 12H21M3 6H21M3 18H21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

// Router setup
const router = useRouter()
const route = useRoute()

// Props
const props = defineProps({
  userRole: {
    type: String,
    default: 'user'
  },
  isInQueue: {
    type: Boolean,
    default: false
  },
  isProcessingQueue: {
    type: Boolean,
    default: false
  },
  currentCall: {
    type: Object,
    default: null
  }
})

// Emits
const emit = defineEmits([
  'toggle-queue',
  'logout',
  'sidebar-toggle'
])

// Local state
const isSidebarCollapsed = ref(false)
const mobileOpen = ref(false)

// Computed properties
const queueStatus = computed(() => {
  if (props.currentCall) {
    return props.currentCall.status === 'incoming' ? 'Incoming Call' : 'On Call'
  }
  return props.isInQueue ? 'In Queue' : 'Offline'
})

const queueButtonText = computed(() => {
  if (props.isProcessingQueue) return 'Processing...'
  if (props.currentCall) return 'End Call'
  return props.isInQueue ? 'Leave Queue' : 'Join Queue'
})

// Methods
const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
  emit('sidebar-toggle', isSidebarCollapsed.value)
}

const expandSidebar = () => {
  isSidebarCollapsed.value = false
  emit('sidebar-toggle', isSidebarCollapsed.value)
}

const toggleMobileMenu = () => {
  mobileOpen.value = !mobileOpen.value
}

const handleQueueToggle = () => {
  // Simply emit to parent component - let parent handle notifications and SIP logic
  emit('toggle-queue')
}

const handleLogout = () => {
  emit('logout')
}

// Close mobile menu after navigation
onMounted(() => {
  router.afterEach(() => {
    if (window.innerWidth <= 1024) {
      mobileOpen.value = false
    }
  })
})
</script>

<style scoped>
/* Sidebar styles */
.sidebar {
  width: 250px;
  background-color: var(--sidebar-bg);
  color: var(--text-color);
  height: 100vh;
  position: fixed;
  transition: width 0.3s ease, transform 0.3s ease, background-color 0.3s;
  overflow: hidden;
  border-radius: 0 30px 30px 0;
  z-index: 100;
  display: flex;
  flex-direction: column;
  border: none;
  box-shadow: 0 8px 32px 0 rgba(0,0,0,0.18);
}

.sidebar-content {
  width: 250px;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sidebar-header {
  flex-shrink: 0;
  padding: 20px;
  text-align: center;
  border-bottom: none;
}

.nav-section {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 0 15px;
  margin-bottom: 0;
  min-height: 0;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.nav-section::-webkit-scrollbar {
  display: none;
}

.sidebar-bottom {
  padding: 15px;
  flex-shrink: 0;
  background: transparent;
  border-top: none;
}

.toggle-btn {
  position: absolute;
  top: 50px;
  right: -15px;
  width: 30px;
  height: 30px;
  background-color: #ffffff;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  z-index: 10;
  border: none;
  color: #333333;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  transition: all 0.3s ease;
}

.toggle-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

.expand-btn {
  position: fixed;
  top: 50px;
  left: 5px;
  width: 30px;
  height: 30px;
  background-color: #ffffff;
  border-radius: 50%;
  display: none;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  z-index: 101;
  border: none;
  color: #333333;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  transition: all 0.3s ease;
}

.expand-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

.sidebar.collapsed ~ .expand-btn {
  display: flex;
}

.sidebar.collapsed {
  width: 20px;
  transform: translateX(-230px);
}

.sidebar.collapsed .sidebar-content {
  opacity: 0;
  pointer-events: none;
}

.logo-container {
  display: flex;
  justify-content: center;
}

.logo {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background-color: var(--logo-bg);
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
}

.logo img {
  width: 30px;
  height: 30px;
  object-fit: contain;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  cursor: pointer;
  margin-bottom: 4px;
  border-radius: 12px;
  text-decoration: none;
  color: var(--text-color);
  transition: all 0.3s ease;
  min-height: 44px;
  background: transparent;
}

.nav-item:hover {
  background-color: rgba(255, 255, 255, 0.05);
  transform: translateX(3px);
}

.nav-item.active {
  background: #8B4513 !important;
  color: #fff !important;
  border-radius: 16px !important;
  box-shadow: none !important;
  padding: 10px 18px !important;
}

.nav-item.active .nav-icon svg,
.nav-item.active .nav-text {
  color: #fff !important;
  stroke: #fff !important;
}

.nav-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  border-radius: 8px;
  background-color: rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.nav-item:hover .nav-icon {
  background-color: rgba(255, 255, 255, 0.2);
  transform: scale(1.05);
}

.nav-icon svg {
  color: var(--text-color);
  stroke: var(--text-color);
  width: 18px;
  height: 18px;
  transition: color 0.3s, stroke 0.3s;
}

.nav-item.active .nav-icon {
  background: rgba(255, 140, 0, 0.10);
}

.nav-text {
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-profile {
  display: flex;
  justify-content: center;
  margin-bottom: 12px;
}

.user-avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background-color: var(--text-color);
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  overflow: hidden;
  text-decoration: none;
  transition: all 0.3s ease;
}

.user-avatar:hover {
  transform: scale(1.05);
}

.user-avatar svg {
  width: 24px;
  height: 24px;
  fill: var(--background-color);
}

.status {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 12px;
  color: var(--text-secondary);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: var(--unassigned-color);
  margin-right: 6px;
  transition: all 0.3s ease;
}

.status-dot.in-queue {
  background-color: var(--accent-color);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

.button-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.join-queue-btn {
  background-color: var(--accent-color);
  color: white;
  border: none;
  border-radius: 25px;
  padding: 10px 14px;
  width: 100%;
  font-weight: 700;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.join-queue-btn:hover {
  background-color: var(--accent-hover);
  transform: translateY(-1px);
}

.join-queue-btn.in-queue {
  background-color: var(--success-color);
}

.join-queue-btn.has-call {
  background-color: var(--danger-color);
}

.join-queue-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.logout-btn {
  background-color: #8B0000;
  color: white;
  border: none;
  border-radius: 25px;
  padding: 10px 14px;
  width: 100%;
  font-weight: 700;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.logout-btn:hover {
  background-color: #8B0000;
  transform: translateY(-1px);
}

.mobile-menu-btn {
  display: none;
  position: fixed;
  top: 20px;
  left: 20px;
  width: 40px;
  height: 40px;
  background-color: var(--content-bg);
  border: 1px solid var(--border-color);
  border-radius: 50%;
  color: var(--text-color);
  cursor: pointer;
  z-index: 102;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.mobile-menu-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

/* Responsive Design */
@media (max-width: 1200px) {
  .sidebar {
    width: 200px;
  }
}
@media (max-width: 1024px) {
  .mobile-menu-btn {
    display: flex;
  }
  .sidebar {
    position: fixed;
    left: -250px;
    top: 0;
    height: 100vh;
    z-index: 200;
    width: 250px;
    transform: translateX(-100%);
    transition: transform 0.3s;
  }
  .sidebar.mobile-open {
    transform: translateX(0);
    left: 0;
  }
  .main-content {
    margin-left: 0 !important;
    width: 100vw !important;
  }
}
@media (max-width: 900px) {
  .sidebar {
    width: 180px;
  }
}
@media (max-width: 768px) {
  .sidebar {
    width: 100vw;
    left: -100vw;
  }
  .sidebar.mobile-open {
    left: 0;
    width: 100vw;
  }
  .main-content {
    margin-left: 0 !important;
    width: 100vw !important;
    padding: 10px 2vw;
  }
}
@media (max-width: 480px) {
  .sidebar {
    width: 100vw;
    left: -100vw;
  }
  .sidebar.mobile-open {
    left: 0;
    width: 100vw;
  }
  .main-content {
    margin-left: 0 !important;
    width: 100vw !important;
    padding: 6px 1vw;
  }
}

.sidepanel-coatofarms {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 1.5rem 0 1rem 0;
}

.sidepanel-coatofarms img {
  max-width: 60px;
  max-height: 90px;
  object-fit: contain;
  display: block;
}
</style>

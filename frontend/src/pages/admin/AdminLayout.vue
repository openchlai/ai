<template>
  <div class="admin-layout">
    <!-- Sidebar -->
    <aside
      id="sidebar"
      class="sidebar glass-panel fine-border"
      :class="{ collapsed: isSidebarCollapsed, 'mobile-open': mobileOpen }"
    >
      <div class="toggle-btn" @click="toggleSidebar">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="15,18 9,12 15,6"></polyline>
        </svg>
      </div>

      <div class="sidebar-content">
        <!-- Sidebar Header -->
        <div class="sidebar-header">
          <div class="logo-container">
            <div class="logo">
              <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2a3 3 0 0 0-3 3c0 1.5 1.5 3 3 3s3-1.5 3-3a3 3 0 0 0-3-3z"></path>
                <path d="M19 10v-1a7 7 0 0 0-14 0v1"></path>
                <path d="M5 10v4a3 3 0 0 0 3 3h8a3 3 0 0 0 3-3v-4"></path>
              </svg>
            </div>
          </div>
          <div class="org-info">
            <div class="org-name">Children First Kenya</div>
            <div class="org-location">Nairobi, Kenya</div>
          </div>
        </div>

        <!-- Navigation -->
        <nav class="nav-section">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="nav-item"
            :class="{ active: $route.path === item.path }"
            @click="setActiveTab(item.tab)"
          >
            <div class="nav-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" v-html="item.icon">
              </svg>
            </div>
            <div class="nav-text">{{ item.name }}</div>
          </router-link>
        </nav>

        <!-- Sidebar Bottom -->
        <div class="sidebar-bottom">
          <div class="user-profile">
            <div class="user-avatar">
              {{ getInitials('Admin User') }}
            </div>
          </div>
          <div class="user-info">
            <div class="user-name">Admin User</div>
            <div class="user-role">Administrator</div>
          </div>
          <div class="status">
            <div class="status-dot active"></div>
            Online
          </div>
          <div class="button-container">
            <button class="logout-btn" @click="logout">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                <polyline points="16,17 21,12 16,7"></polyline>
                <line x1="21" y1="12" x2="9" y2="12"></line>
              </svg>
              Logout
            </button>
          </div>
        </div>
      </div>
    </aside>

    <!-- Expand Button (when sidebar is collapsed) -->
    <button class="expand-btn" @click="expandSidebar">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="9,18 15,12 9,6"></polyline>
      </svg>
    </button>

    <!-- Main Content -->
    <main class="main-content">
      <!-- Header -->
      <header class="header">
        <h1 class="page-title">{{ getPageTitle() }}</h1>
        <div class="header-actions">
          <button class="notification-btn" @click="toggleNotifications">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
              <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
            </svg>
            <span v-if="unreadNotifications > 0" class="notification-badge">
              {{ unreadNotifications }}
            </span>
          </button>
          
          <!-- Theme Toggle Slider -->
          <div class="theme-toggle-container" :title="currentTheme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'">
            <label class="theme-toggle-switch">
              <input 
                type="checkbox" 
                :checked="currentTheme === 'dark'"
                @change="toggleTheme"
              />
              <span class="toggle-slider">
                <svg v-if="currentTheme === 'dark'" class="toggle-icon sun-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="5"></circle>
                  <line x1="12" y1="1" x2="12" y2="3"></line>
                  <line x1="12" y1="21" x2="12" y2="23"></line>
                  <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
                  <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
                  <line x1="1" y1="12" x2="3" y2="12"></line>
                  <line x1="21" y1="12" x2="23" y2="12"></line>
                  <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
                  <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
                </svg>
                <svg v-else class="toggle-icon moon-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
                </svg>
              </span>
            </label>
          </div>
        </div>
      </header>

      <!-- Page Content -->
      <router-view></router-view>
    </main>

    <!-- Mobile Menu Button -->
    <button
      id="mobile-menu-btn"
      class="mobile-menu-btn"
      @click="toggleMobileMenu"
    >
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="3" y1="6" x2="21" y2="6"></line>
        <line x1="3" y1="12" x2="21" y2="12"></line>
        <line x1="3" y1="18" x2="21" y2="18"></line>
      </svg>
    </button>

    <!-- Notification Panel -->
    <div class="notification-panel" :class="{ open: showNotifications }">
      <div class="notification-header">
        <h3>Notifications</h3>
        <button class="close-notifications" @click="toggleNotifications">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
      <div class="notifications-list">
        <div
          v-for="notification in notifications"
          :key="notification.id"
          class="notification-item"
          :class="{ unread: !notification.read }"
        >
          <div class="notification-icon" :class="notification.type">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14,2 14,8 20,8"></polyline>
              <line x1="16" y1="13" x2="8" y2="13"></line>
              <line x1="16" y1="17" x2="8" y2="17"></line>
              <polyline points="10,9 9,9 8,9"></polyline>
            </svg>
          </div>
          <div class="notification-content">
            <div class="notification-title">{{ notification.title }}</div>
            <div class="notification-message">{{ notification.message }}</div>
            <div class="notification-time">{{ notification.time }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// Reactive data
const isSidebarCollapsed = ref(false)
const mobileOpen = ref(false)
const showNotifications = ref(false)
const currentTheme = ref('light')
const unreadNotifications = ref(3)

// Navigation items
const navItems = [
  {
    name: 'Dashboard',
    path: '/admin/dashboard',
    tab: 'dashboard',
    icon: '<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9,22 9,12 15,12 15,22"></polyline>'
  },
  {
    name: 'Case Management',
    path: '/admin/cases',
    tab: 'cases',
    icon: '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14,2 14,8 20,8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10,9 9,9 8,9"></polyline>'
  },
  {
    name: 'Team Management',
    path: '/admin/users',
    tab: 'users',
    icon: '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path>'
  },
  {
    name: 'Reports & Analytics',
    path: '/admin/reports',
    tab: 'reports',
    icon: '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14,2 14,8 20,8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10,9 9,9 8,9"></polyline>'
  },
  {
    name: 'AI Assistant',
    path: '/admin/ai-assistant',
    tab: 'ai-assistant',
    icon: '<path d="M12 2a3 3 0 0 0-3 3c0 1.5 1.5 3 3 3s3-1.5 3-3a3 3 0 0 0-3-3z"></path><path d="M19 10v-1a7 7 0 0 0-14 0v1"></path><path d="M5 10v4a3 3 0 0 0 3 3h8a3 3 0 0 0 3-3v-4"></path>'
  },
  {
    name: 'Categories',
    path: '/admin/categories',
    tab: 'categories',
    icon: '<path d="M3 3h18v18H3z"></path><path d="M9 9h6v6H9z"></path>'
  },
  {
    name: 'Workflows',
    path: '/admin/workflows',
    tab: 'workflows',
    icon: '<polyline points="9,11 12,14 22,4"></polyline><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>'
  },
  {
    name: 'Settings',
    path: '/admin/settings',
    tab: 'settings',
    icon: '<circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>'
  }
]

// Mock notifications
const notifications = ref([
  {
    id: 1,
    title: 'New Case Assigned',
    message: 'Case CASE-2024-001 has been assigned to you',
    type: 'case',
    time: '2 hours ago',
    read: false
  },
  {
    id: 2,
    title: 'Team Member Joined',
    message: 'Sarah Johnson has joined the team',
    type: 'user',
    time: '1 day ago',
    read: false
  },
  {
    id: 3,
    title: 'System Update',
    message: 'New features have been added to the platform',
    type: 'system',
    time: '3 days ago',
    read: false
  }
])

// Methods
const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
}

const expandSidebar = () => {
  isSidebarCollapsed.value = false
}

const toggleMobileMenu = () => {
  mobileOpen.value = !mobileOpen.value
}

const setActiveTab = (tab) => {
  mobileOpen.value = false
}

const getPageTitle = () => {
  const titles = {
    dashboard: "Dashboard",
    cases: "Case Management",
    users: "Team Management",
    reports: "Reports & Analytics",
    "ai-assistant": "AI Assistant",
    categories: "Categories",
    workflows: "Workflows",
    settings: "Settings",
  }
  const currentPath = router.currentRoute.value.path
  const tab = currentPath.split('/').pop()
  return titles[tab] || "Dashboard"
}

const toggleNotifications = () => {
  showNotifications.value = !showNotifications.value
  if (showNotifications.value) {
    unreadNotifications.value = 0
  }
}

const applyTheme = (theme) => {
  const root = document.documentElement

  if (theme === "light") {
    root.style.setProperty("--background-color", "#f7f7f9")
    root.style.setProperty("--sidebar-bg", "#ffffff")
    root.style.setProperty("--content-bg", "#ffffff")
    root.style.setProperty("--text-color", "#1f2328")
    root.style.setProperty("--text-secondary", "#6b7280")
    root.style.setProperty("--border-color", "rgba(0,0,0,0.12)")
    root.style.setProperty("--card-bg", "#ffffff")
    root.setAttribute("data-theme", "light")
  } else {
    root.style.setProperty("--background-color", "#0a0a0a")
    root.style.setProperty("--sidebar-bg", "#111")
    root.style.setProperty("--content-bg", "#222")
    root.style.setProperty("--text-color", "#fff")
    root.style.setProperty("--text-secondary", "#aaa")
    root.style.setProperty("--border-color", "#333")
    root.style.setProperty("--card-bg", "#222")
    root.setAttribute("data-theme", "dark")
  }

  // Use dark brown theme colors instead of bright orange
  root.style.setProperty("--accent-color", "#8B4513")
  root.style.setProperty("--accent-hover", "#A0522D")
  root.style.setProperty("--danger-color", "#cc2f2f")
  root.style.setProperty("--success-color", "#15803d")
  root.style.setProperty("--pending-color", "#FFA500")
  root.style.setProperty("--warning-color", "#FF9500")
}

const toggleTheme = () => {
  currentTheme.value = currentTheme.value === "dark" ? "light" : "dark"
  localStorage.setItem("theme", currentTheme.value)
  applyTheme(currentTheme.value)
  console.log('Theme toggled to:', currentTheme.value)
}

const logout = () => {
  console.log("Logging out...")
  router.push('/')
}

const getInitials = (name) => {
  if (!name || typeof name !== 'string') return ''
  return name
    .split(' ')
    .map(part => part[0])
    .join('')
    .toUpperCase()
}

onMounted(() => {
  const savedTheme = localStorage.getItem("theme")
  if (savedTheme) {
    currentTheme.value = savedTheme
  }

  applyTheme(currentTheme.value)

  const handleResize = () => {
    if (window.innerWidth > 1024) {
      mobileOpen.value = false
    }
  }
  window.addEventListener("resize", handleResize)

  const handleClickOutside = (event) => {
    const isMobileOrTablet = window.innerWidth <= 1024
    const sidebar = document.getElementById("sidebar")
    const mobileMenuBtn = document.getElementById("mobile-menu-btn")

    if (
      isMobileOrTablet &&
      sidebar &&
      !sidebar.contains(event.target) &&
      event.target !== mobileMenuBtn
    ) {
      mobileOpen.value = false
    }

    // Close notifications when clicking outside
    if (
      showNotifications.value &&
      !event.target.closest(".notification-panel") &&
      !event.target.closest(".notification-btn")
    ) {
      showNotifications.value = false
    }
  }
  document.addEventListener("click", handleClickOutside)
})
</script>

<style scoped>
/* Admin layout specific styles to match SidePanel design with dark brown theme */
.admin-layout {
  display: flex;
  min-height: 100vh;
  background-color: var(--color-bg);
  color: var(--color-fg);
}

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

.sidebar.collapsed {
  width: 20px;
  transform: translateX(-230px);
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

.sidebar-content {
  width: 250px;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sidebar.collapsed .sidebar-content {
  opacity: 0;
  pointer-events: none;
}

.sidebar-header {
  flex-shrink: 0;
  padding: 20px;
  text-align: center;
  border-bottom: none;
}

.logo-container {
  display: flex;
  justify-content: center;
  margin-bottom: 15px;
}

.logo {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background-color: var(--accent-color);
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
}

.logo svg {
  color: white;
  stroke: white;
}

.org-info {
  text-align: center;
}

.org-name {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 4px;
  color: var(--text-color);
}

.org-location {
  font-size: 12px;
  color: var(--text-secondary);
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
}

.nav-item:hover {
  background-color: rgba(139, 69, 19, 0.05);
  transform: translateX(3px);
}

.nav-item.active {
  background-color: rgba(139, 69, 19, 0.1);
  border-left: 3px solid var(--accent-color);
}

.nav-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  border-radius: 8px;
  background-color: rgba(139, 69, 19, 0.1);
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.nav-item:hover .nav-icon {
  background-color: rgba(139, 69, 19, 0.2);
  transform: scale(1.05);
}

.nav-item.active .nav-icon {
  background-color: var(--accent-color);
}

.nav-item.active .nav-icon svg {
  color: white;
  stroke: white;
}

.nav-icon svg {
  color: var(--text-color);
  stroke: var(--text-color);
  width: 18px;
  height: 18px;
}

.nav-text {
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-bottom {
  padding: 15px;
  flex-shrink: 0;
  background: transparent;
  border-top: none;
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
  background-color: var(--accent-color);
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  overflow: hidden;
  text-decoration: none;
  transition: all 0.3s ease;
  color: white;
  font-weight: 600;
  font-size: 16px;
}

.user-avatar:hover {
  transform: scale(1.05);
}

.user-info {
  text-align: center;
  margin-bottom: 12px;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 2px;
  color: var(--text-color);
}

.user-role {
  font-size: 12px;
  color: var(--text-secondary);
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

.status-dot.active {
  background-color: var(--success-color);
  box-shadow: 0 0 6px rgba(21, 128, 61, 0.5);
}

.button-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
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
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.logout-btn:hover {
  background-color: #8B0000;
  transform: translateY(-1px);
}

.main-content {
  flex: 1;
  margin-left: 250px;
  height: 100vh;
  background-color: var(--color-bg);
  transition: margin-left 0.3s ease, width 0.3s ease;
  width: calc(100% - 250px);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sidebar.collapsed ~ .main-content {
  margin-left: 20px;
  width: calc(100% - 20px);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 20px 0 20px;
  flex-shrink: 0;
  background-color: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--color-fg);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

.notification-btn {
  position: relative;
  background-color: var(--color-surface);
  color: var(--color-fg);
  border: 1px solid var(--color-border);
  border-radius: 50%;
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.notification-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.notification-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  background-color: var(--color-danger);
  color: white;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 600;
}

/* Theme Toggle Slider */
.theme-toggle-container {
  display: flex;
  align-items: center;
  margin-left: 16px;
}

.theme-toggle-switch {
  position: relative;
  display: inline-block;
  width: 60px;
  height: 32px;
  cursor: pointer;
}

.theme-toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--color-surface);
  border: 2px solid var(--color-border);
  border-radius: 32px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 4px 6px;
}

.toggle-slider:before {
  content: "";
  height: 20px;
  width: 20px;
  left: 4px;
  bottom: 4px;
  background-color: var(--accent-color);
  border-radius: 50%;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: absolute;
  z-index: 2;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.theme-toggle-switch input:checked + .toggle-slider {
  background-color: var(--color-surface);
  border-color: var(--accent-color);
}

.theme-toggle-switch input:checked + .toggle-slider:before {
  transform: translateX(28px);
}

.toggle-icon {
  position: relative;
  z-index: 1;
  transition: all 0.3s ease;
  color: var(--color-muted);
}

.sun-icon {
  margin-left: 2px;
}

.moon-icon {
  margin-right: 2px;
}

.theme-toggle-switch:hover .toggle-slider {
  border-color: var(--accent-color);
  box-shadow: 0 0 0 2px rgba(139, 69, 19, 0.1);
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

.notification-panel {
  position: fixed;
  top: 0;
  right: -400px;
  width: 400px;
  height: 100vh;
  background: var(--color-surface);
  border-left: 1px solid var(--color-border);
  box-shadow: -4px 0 12px rgba(0,0,0,0.1);
  transition: right 0.3s ease;
  z-index: 1001;
  display: flex;
  flex-direction: column;
}

.notification-panel.open {
  right: 0;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid var(--color-border);
}

.notification-header h3 {
  font-size: 18px;
  font-weight: 700;
  margin: 0;
  color: var(--color-fg);
}

.close-notifications {
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  color: var(--color-muted);
  transition: all 0.3s ease;
}

.close-notifications:hover {
  background-color: var(--color-surface-muted);
  color: var(--color-fg);
}

.notifications-list {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.notification-item {
  display: flex;
  gap: 12px;
  padding: 15px;
  border-radius: 12px;
  margin-bottom: 12px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.notification-item:hover {
  background: var(--color-surface-muted);
}

.notification-item.unread {
  background: rgba(93, 64, 55, 0.05);
  border-left: 3px solid var(--accent-color);
}

.notification-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.notification-icon.case {
  background: rgba(59, 130, 246, 0.1);
  color: #2563eb;
}

.notification-icon.user {
  background: rgba(21, 128, 61, 0.1);
  color: var(--color-success);
}

.notification-icon.system {
  background: rgba(93, 64, 55, 0.1);
  color: var(--accent-color);
}

.notification-content {
  flex: 1;
}

.notification-title {
  font-weight: 600;
  margin-bottom: 4px;
  color: var(--color-fg);
}

.notification-message {
  font-size: 14px;
  color: var(--color-muted);
  margin-bottom: 8px;
  line-height: 1.4;
}

.notification-time {
  font-size: 12px;
  color: var(--color-muted);
}

@media (max-width: 1024px) {
  .mobile-menu-btn {
    display: flex;
  }

  .sidebar {
    transform: translateX(-250px);
    z-index: 1000;
  }

  .sidebar.mobile-open {
    transform: translateX(0);
  }

  .main-content {
    margin-left: 0;
    width: 100%;
  }

  .expand-btn {
    display: none !important;
  }

  .notification-panel {
    width: 100%;
    right: -100%;
  }
}

@media (max-width: 768px) {
  .header {
    padding: 15px;
  }

  .page-title {
    font-size: 24px;
  }

  .notification-panel {
    width: 100%;
    right: -100%;
  }

  .theme-toggle-container {
    margin-left: 12px;
  }

  .theme-toggle-switch {
    width: 52px;
    height: 28px;
  }

  .toggle-slider:before {
    height: 18px;
    width: 18px;
  }

  .theme-toggle-switch input:checked + .toggle-slider:before {
    transform: translateX(24px);
  }

  .toggle-icon {
    width: 12px;
    height: 12px;
  }
}

@media (min-width: 1025px) {
  .mobile-menu-btn {
    display: none;
  }
}
</style>

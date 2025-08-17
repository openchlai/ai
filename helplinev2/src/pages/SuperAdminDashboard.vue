<template>
<div>
  <button class="mobile-menu-btn" id="mobile-menu-btn" @click="toggleMobileMenu">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M3 12H21M3 6H21M3 18H21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  </button>

  <div class="sidebar" :class="{ collapsed: isSidebarCollapsed, 'mobile-open': mobileOpen }" id="sidebar">
    <div class="toggle-btn" @click="toggleSidebar">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M3 12H21M3 6H21M3 18H21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </div>

    <div class="sidebar-content">
      <div class="sidebar-header">
        <div class="logo-container">
          <div class="logo">
            <img src="/placeholder.svg?height=30&width=30" alt="OpenCHS Logo">
          </div>
        </div>
      </div>
      
      <div class="nav-section">
        <a href="/dashboard" class="nav-item" :class="{ active: activeTab === 'dashboard' }" @click.prevent="setActiveTab('dashboard')">
          <div class="nav-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M3 9L12 2L21 9V20C21 20.5304 20.7893 21.0391 20.4142 21.4142C20.0391 21.7893 19.5304 22 19 22H5C4.46957 22 3.96086 21.7893 3.58579 21.4142C3.21071 21.0391 3 20.5304 3 20V9Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <polyline points="9,22 9,12 15,12 15,22" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="nav-text">Dashboard</div>
        </a>
        
        <a href="/system-config" class="nav-item" :class="{ active: activeTab === 'system-config' }" @click.prevent="setActiveTab('system-config')">
          <div class="nav-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/>
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" stroke="currentColor" stroke-width="2"/>
            </svg>
          </div>
          <div class="nav-text">System Config</div>
        </a>

        <a href="/tenant-management" class="nav-item" :class="{ active: activeTab === 'tenant-management' }" @click.prevent="setActiveTab('tenant-management')">
          <div class="nav-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M3 21h18M5 21V7l8-4v18M19 21V11l-6-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="nav-text">Tenant Management</div>
        </a>

        <a href="/audit-logs" class="nav-item" :class="{ active: activeTab === 'audit-logs' }" @click.prevent="setActiveTab('audit-logs')">
          <div class="nav-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" stroke-width="2"/>
              <polyline points="14,2 14,8 20,8" stroke="currentColor" stroke-width="2"/>
              <line x1="16" y1="13" x2="8" y2="13" stroke="currentColor" stroke-width="2"/>
              <line x1="16" y1="17" x2="8" y2="17" stroke="currentColor" stroke-width="2"/>
            </svg>
          </div>
          <div class="nav-text">Audit Logs</div>
        </a>

        <a href="/category-management" class="nav-item" :class="{ active: activeTab === 'category-management' }" @click.prevent="setActiveTab('category-management')">
          <div class="nav-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect x="3" y="3" width="7" height="7" stroke="currentColor" stroke-width="2"/>
              <rect x="14" y="3" width="7" height="7" stroke="currentColor" stroke-width="2"/>
              <rect x="14" y="14" width="7" height="7" stroke="currentColor" stroke-width="2"/>
              <rect x="3" y="14" width="7" height="7" stroke="currentColor" stroke-width="2"/>
            </svg>
          </div>
          <div class="nav-text">Categories</div>
        </a>

        <a href="/notifications" class="nav-item" :class="{ active: activeTab === 'notifications' }" @click.prevent="setActiveTab('notifications')">
          <div class="nav-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" stroke="currentColor" stroke-width="2"/>
              <path d="M13.73 21a2 2 0 0 1-3.46 0" stroke="currentColor" stroke-width="2"/>
            </svg>
          </div>
          <div class="nav-text">Notifications</div>
        </a>

        <a href="/user-management" class="nav-item" :class="{ active: activeTab === 'user-management' }" @click.prevent="setActiveTab('user-management')">
          <div class="nav-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" stroke="currentColor" stroke-width="2"/>
              <circle cx="9" cy="7" r="4" stroke="currentColor" stroke-width="2"/>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87" stroke="currentColor" stroke-width="2"/>
              <path d="M16 3.13a4 4 0 0 1 0 7.75" stroke="currentColor" stroke-width="2"/>
            </svg>
          </div>
          <div class="nav-text">User Management</div>
        </a>

        <a href="/role-management" class="nav-item" :class="{ active: activeTab === 'role-management' }" @click.prevent="setActiveTab('role-management')">
          <div class="nav-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 15l3-3-3-3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <polyline points="16,17 21,12 16,7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="nav-text">Role Management</div>
        </a>
      </div>
      
      <div class="sidebar-bottom">
        <div class="user-profile">
          <a href="/edit-profile" class="user-avatar" @click.prevent="navigateTo('/edit-profile')">
            <svg viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 12C14.2091 12 16 10.2091 16 8C16 5.79086 14.2091 4 12 4C9.79086 4 8 5.79086 8 8C8 10.2091 9.79086 12 12 12Z"/>
              <path d="M12 14C7.58172 14 4 17.5817 4 22H20C20 17.5817 16.4183 14 12 14Z"/>
            </svg>
          </a>
        </div>
        
        <div class="status">
          <div class="status-dot"></div>
          <span>Online</span>
        </div>
        
        <div class="button-container">
          <button class="logout-btn" @click="logout">Logout</button>
        </div>
      </div>
    </div>
  </div>

  <button class="expand-btn" @click="expandSidebar" id="expand-btn">
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M3 12H21M3 6H21M3 18H21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  </button>

  <div class="main-content">
    <div class="header">
      <h1 class="page-title">{{ getPageTitle() }}</h1>
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

    <div class="main-scroll-content">
      <div v-if="activeTab === 'dashboard'">
        <div class="dashboard-grid">
          <div class="dashboard-card">
            <div class="card-header">
              <div class="card-title">Organizations</div>
              <div class="card-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M3 21h18M5 21V7l8-4v18M19 21V11l-6-4" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </div>
            </div>
            <div class="card-value">{{ dashboardStats.organizations }}</div>
            <div class="card-subtitle">+12.5% from last month</div>
          </div>
          
          <div class="dashboard-card">
            <div class="card-header">
              <div class="card-title">Active Users</div>
              <div class="card-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <circle cx="9" cy="7" r="4" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M23 21v-2a4 4 0 0 0-3-3.87" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M16 3.13a4 4 0 0 1 0 7.75" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </div>
            </div>
            <div class="card-value">{{ dashboardStats.activeUsers }}</div>
            <div class="card-subtitle">+8.2% from last month</div>
          </div>
          
          <div class="dashboard-card">
            <div class="card-header">
              <div class="card-title">System Health</div>
              <div class="card-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M22 12h-4l-3 9L9 3l-3 9H2" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </div>
            </div>
            <div class="card-value">{{ dashboardStats.systemHealth }}%</div>
            <div class="card-subtitle">+0.1% from last week</div>
          </div>
          
          <div class="dashboard-card">
            <div class="card-header">
              <div class="card-title">Growth</div>
              <div class="card-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M23 6l-9.5 9.5-5-5L1 18" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M17 6h6v6" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </div>
            </div>
            <div class="card-value">+{{ dashboardStats.growth }}%</div>
            <div class="card-subtitle">+3.2% from last month</div>
          </div>
        </div>

        <div class="quick-actions-section">
          <div class="section-header">
            <div class="section-title">Quick Actions</div>
          </div>
          
          <div class="quick-actions-grid">
            <div class="action-card" @click="handleQuickAction('create-org')">
              <div class="action-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </div>
              <div class="action-content">
                <h3 class="action-title">Create Organization</h3>
                <p class="action-description">Add a new organization to the system</p>
                <button class="action-button">
                  Create New
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <polyline points="9 18 15 12 9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </button>
              </div>
            </div>
            
            <div class="action-card" @click="handleQuickAction('add-admin')">
              <div class="action-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <circle cx="9" cy="7" r="4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M19 8v6M16 11h6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </div>
              <div class="action-content">
                <h3 class="action-title">Add Admin</h3>
                <p class="action-description">Invite a new administrator</p>
                <button class="action-button">
                  Add Admin
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <polyline points="9 18 15 12 9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </button>
              </div>
            </div>
            
            <div class="action-card" @click="setActiveTab('system-config')">
              <div class="action-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </div>
              <div class="action-content">
                <h3 class="action-title">System Settings</h3>
                <p class="action-description">Configure global system settings</p>
                <button class="action-button">
                  Open Settings
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <polyline points="9 18 15 12 9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="management-grid">
          <div class="management-card">
            <div class="card-header">
              <div class="section-title">Recent Organizations</div>
              <button class="view-all-btn" @click="setActiveTab('tenant-management')">View All</button>
            </div>
            <div class="organizations-list">
              <div v-for="org in recentOrganizations" :key="org.id" class="organization-item">
                <div class="org-avatar">
                  <span>{{ org.name.charAt(0) }}</span>
                </div>
                <div class="org-info">
                  <h4 class="org-name">{{ org.name }}</h4>
                  <p class="org-details">{{ org.users }} users • {{ org.status }}</p>
                </div>
                <div class="org-actions">
                  <button class="org-action-btn" @click="toggleFavorite(org.id)">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div class="management-card">
            <div class="card-header">
              <div class="section-title">Usage Analytics</div>
              <select class="time-filter" v-model="selectedTimeframe">
                <option value="7days">Last 7 days</option>
                <option value="30days">Last 30 days</option>
                <option value="90days">Last 90 days</option>
              </select>
            </div>
            <div class="analytics-content">
              <div class="chart-placeholder">
                <div class="chart-bars">
                  <div class="chart-bar" style="height: 60%"></div>
                  <div class="chart-bar" style="height: 80%"></div>
                  <div class="chart-bar" style="height: 45%"></div>
                  <div class="chart-bar" style="height: 90%"></div>
                  <div class="chart-bar" style="height: 70%"></div>
                  <div class="chart-bar" style="height: 85%"></div>
                  <div class="chart-bar" style="height: 95%"></div>
                </div>
              </div>
              <div class="analytics-stats">
                <div class="stat-item">
                  <span class="stat-label">Total Sessions</span>
                  <span class="stat-value">12,847</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">Avg. Duration</span>
                  <span class="stat-value">24m 32s</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'system-config'" class="config-section">
        <div class="config-container">
          <div class="config-header">
            <div class="section-title">System Configuration</div>
            <button class="save-btn" @click="saveSystemConfig">Save Changes</button>
          </div>
          
          <div class="config-grid-expanded">
            <div class="config-group">
              <h3 class="config-group-title">General Settings</h3>
              <div class="config-items">
                <div class="config-item">
                  <label class="config-label">
                    <input type="checkbox" v-model="systemConfig.maintenanceMode">
                    <span class="checkmark"></span>
                    Maintenance Mode
                  </label>
                  <p class="config-description">Enable to prevent user access during maintenance</p>
                </div>
                
                <div class="config-item">
                  <label class="config-label">
                    <input type="checkbox" v-model="systemConfig.allowNewSignups">
                    <span class="checkmark"></span>
                    Allow New Signups
                  </label>
                  <p class="config-description">Allow new organizations to register</p>
                </div>

                <div class="config-item">
                  <label class="config-label">
                    <input type="checkbox" v-model="systemConfig.enableNotifications">
                    <span class="checkmark"></span>
                    Enable System Notifications
                  </label>
                  <p class="config-description">Send system-wide notifications to users</p>
                </div>
              </div>
            </div>

            <div class="config-group">
              <h3 class="config-group-title">AI Configuration</h3>
              <div class="config-items">
                <div class="config-item">
                  <label class="form-label">Default AI Provider</label>
                  <select v-model="systemConfig.defaultAiProvider" class="form-select">
                    <option value="OPENAI">OpenAI</option>
                    <option value="ANTHROPIC">Anthropic</option>
                    <option value="GOOGLE">Google AI</option>
                    <option value="AZURE">Azure OpenAI</option>
                  </select>
                  <p class="config-description">Primary AI service for system operations</p>
                </div>

                <div class="config-item">
                  <label class="form-label">AI Response Timeout (seconds)</label>
                  <input type="number" v-model="systemConfig.aiTimeout" class="form-input" min="5" max="300">
                  <p class="config-description">Maximum time to wait for AI responses</p>
                </div>
              </div>
            </div>

            <div class="config-group">
              <h3 class="config-group-title">Case Management</h3>
              <div class="config-items">
                <div class="config-item">
                  <label class="form-label">Case Number Prefix</label>
                  <input type="text" v-model="systemConfig.caseNumberPrefix" class="form-input" placeholder="CASE">
                  <p class="config-description">Prefix for auto-generated case numbers</p>
                </div>

                <div class="config-item">
                  <label class="form-label">Case Number Counter</label>
                  <input type="number" v-model="systemConfig.caseNumberCounter" class="form-input" min="1">
                  <p class="config-description">Starting number for case sequence</p>
                </div>

                <div class="config-item">
                  <label class="form-label">Default Case Priority</label>
                  <select v-model="systemConfig.defaultCasePriority" class="form-select">
                    <option value="LOW">Low</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="HIGH">High</option>
                    <option value="CRITICAL">Critical</option>
                  </select>
                  <p class="config-description">Default priority for new cases</p>
                </div>
              </div>
            </div>

            <div class="config-group">
              <h3 class="config-group-title">Security Settings</h3>
              <div class="config-items">
                <div class="config-item">
                  <label class="form-label">Session Timeout (minutes)</label>
                  <input type="number" v-model="systemConfig.sessionTimeout" class="form-input" min="5" max="480">
                  <p class="config-description">Automatic logout after inactivity</p>
                </div>

                <div class="config-item">
                  <label class="form-label">Password Minimum Length</label>
                  <input type="number" v-model="systemConfig.passwordMinLength" class="form-input" min="6" max="32">
                  <p class="config-description">Minimum characters required for passwords</p>
                </div>

                <div class="config-item">
                  <label class="config-label">
                    <input type="checkbox" v-model="systemConfig.requireTwoFactor">
                    <span class="checkmark"></span>
                    Require Two-Factor Authentication
                  </label>
                  <p class="config-description">Mandatory 2FA for all admin accounts</p>
                </div>
              </div>
            </div>

            <div class="config-group">
              <h3 class="config-group-title">Data Retention</h3>
              <div class="config-items">
                <div class="config-item">
                  <label class="form-label">Audit Log Retention (days)</label>
                  <input type="number" v-model="systemConfig.auditRetention" class="form-input" min="30" max="2555">
                  <p class="config-description">How long to keep audit log entries</p>
                </div>

                <div class="config-item">
                  <label class="form-label">Backup Frequency</label>
                  <select v-model="systemConfig.backupFrequency" class="form-select">
                    <option value="DAILY">Daily</option>
                    <option value="WEEKLY">Weekly</option>
                    <option value="MONTHLY">Monthly</option>
                  </select>
                  <p class="config-description">Automated backup schedule</p>
                </div>
              </div>
            </div>

            <div class="config-group">
              <h3 class="config-group-title">Email Configuration</h3>
              <div class="config-items">
                <div class="config-item">
                  <label class="form-label">SMTP Server</label>
                  <input type="text" v-model="systemConfig.smtpServer" class="form-input" placeholder="smtp.example.com">
                  <p class="config-description">Email server for system notifications</p>
                </div>

                <div class="config-item">
                  <label class="form-label">From Email Address</label>
                  <input type="email" v-model="systemConfig.fromEmail" class="form-input" placeholder="noreply@openchs.org">
                  <p class="config-description">Default sender for system emails</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'tenant-management'" class="tenant-section">
        <div class="table-card">
          <div class="card-header">
            <div class="section-title">Tenant Management</div>
            <div class="table-controls">
              <button class="create-tenant-btn" @click="showCreateTenantModal = true">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                Create Tenant
              </button>
              <button class="filter-btn" @click="toggleTenantFilters">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <polygon points="22,3 2,3 10,12.46 10,19 14,21 14,12.46" stroke="currentColor" stroke-width="2"/>
                </svg>
                Filter
              </button>
              <button class="export-btn" @click="exportTenantData">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" stroke="currentColor" stroke-width="2"/>
                  <polyline points="7,10 12,15 17,10" stroke="currentColor" stroke-width="2"/>
                  <line x1="12" y1="15" x2="12" y2="3" stroke="currentColor" stroke-width="2"/>
                </svg>
                Export
              </button>
            </div>
          </div>
          <div class="table-container">
            <table class="tenant-table">
              <thead>
                <tr>
                  <th>Organization</th>
                  <th>Domain</th>
                  <th>Users</th>
                  <th>Modules</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="tenant in tenants" :key="tenant.id" class="tenant-row">
                  <td class="tenant-cell">
                    <div class="tenant-info">
                      <div class="tenant-avatar">
                        <span>{{ tenant.name.charAt(0) }}</span>
                      </div>
                      <div class="tenant-details">
                        <span class="tenant-name">{{ tenant.name }}</span>
                        <span class="tenant-location">{{ tenant.location }}</span>
                      </div>
                    </div>
                  </td>
                  <td>{{ tenant.customDomain || 'Default' }}</td>
                  <td>{{ tenant.userCount }}</td>
                  <td>
                    <div class="modules-list">
                      <span v-for="module in tenant.enabledModules" :key="module" class="module-badge">
                        {{ module }}
                      </span>
                    </div>
                  </td>
                  <td>
                    <span class="status-badge" :class="tenant.status.toLowerCase()">{{ tenant.status }}</span>
                  </td>
                  <td>
                    <div class="action-buttons">
                      <button class="action-btn edit-btn" @click="editTenant(tenant.id)">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" stroke="currentColor" stroke-width="2"/>
                          <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" stroke="currentColor" stroke-width="2"/>
                        </svg>
                        Edit
                      </button>
                      <button class="action-btn impersonate-btn" @click="impersonateTenant(tenant.id)">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" stroke="currentColor" stroke-width="2"/>
                        </svg>
                        Impersonate
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'audit-logs'" class="audit-section">
        <div class="table-card">
          <div class="card-header">
            <div class="section-title">Audit Logs</div>
            <div class="audit-filters-horizontal">
              <select v-model="auditFilters.action" class="filter-select">
                <option value="">All Actions</option>
                <option value="CREATE">Create</option>
                <option value="UPDATE">Update</option>
                <option value="DELETE">Delete</option>
                <option value="LOGIN">Login</option>
                <option value="LOGOUT">Logout</option>
              </select>
              <select v-model="auditFilters.model" class="filter-select">
                <option value="">All Models</option>
                <option value="Case">Case</option>
                <option value="User">User</option>
                <option value="Organization">Organization</option>
                <option value="Category">Category</option>
                <option value="System">System</option>
              </select>
              <input type="date" v-model="auditFilters.date" class="filter-input">
              <input type="text" v-model="auditFilters.user" class="filter-input" placeholder="Search user...">
              <button class="export-btn" @click="exportAuditData">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" stroke="currentColor" stroke-width="2"/>
                  <polyline points="7,10 12,15 17,10" stroke="currentColor" stroke-width="2"/>
                  <line x1="12" y1="15" x2="12" y2="3" stroke="currentColor" stroke-width="2"/>
                </svg>
                Export
              </button>
            </div>
          </div>
          <div class="table-container">
            <table class="audit-table">
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>User</th>
                  <th>Action</th>
                  <th>Model</th>
                  <th>Object ID</th>
                  <th>IP Address</th>
                  <th>Details</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="log in filteredAuditLogs" :key="log.id" class="audit-row">
                  <td>{{ formatDate(log.timestamp) }}</td>
                  <td>{{ log.user }}</td>
                  <td>
                    <span class="action-badge" :class="log.action.toLowerCase()">{{ log.action }}</span>
                  </td>
                  <td>{{ log.modelName }}</td>
                  <td class="object-id">{{ log.objectId }}</td>
                  <td>{{ log.ipAddress }}</td>
                  <td>
                    <button class="details-btn" @click="viewAuditDetails(log)">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                        <path d="M12 16v-4" stroke="currentColor" stroke-width="2"/>
                        <path d="M12 8h.01" stroke="currentColor" stroke-width="2"/>
                      </svg>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'category-management'" class="category-section">
        <div class="category-header">
          <div class="category-title-section">
            <div class="category-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="3" y="3" width="7" height="7" stroke="currentColor" stroke-width="2"/>
                <rect x="14" y="3" width="7" height="7" stroke="currentColor" stroke-width="2"/>
                <rect x="14" y="14" width="7" height="7" stroke="currentColor" stroke-width="2"/>
                <rect x="3" y="14" width="7" height="7" stroke="currentColor" stroke-width="2"/>
              </svg>
            </div>
            <div class="category-title-content">
              <h2 class="category-main-title">Case Categories</h2>
              <p class="category-description">Case categories are used to categorize cases into different types. They can be used for reporting and to help manage your cases.</p>
            </div>
          </div>
          <div class="category-actions">
            <button class="download-template-btn" @click="downloadCsvTemplate">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" stroke="currentColor" stroke-width="2"/>
                <polyline points="7,10 12,15 17,10" stroke="currentColor" stroke-width="2"/>
                <line x1="12" y1="15" x2="12" y2="3" stroke="currentColor" stroke-width="2"/>
              </svg>
              Download Template
            </button>
            <button class="upload-csv-btn" @click="showUploadCsvModal = true">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" stroke="currentColor" stroke-width="2"/>
                <polyline points="17,8 12,3 7,8" stroke="currentColor" stroke-width="2"/>
                <line x1="12" y1="3" x2="12" y2="15" stroke="currentColor" stroke-width="2"/>
              </svg>
              Upload CSV
            </button>
            <button class="new-category-btn" @click="showAddCategoryModal = true">
              New
            </button>
          </div>
        </div>

        <div class="categories-list">
          <div v-for="category in categories" :key="category.id" class="category-list-item">
            <div class="category-bullet"></div>
            <div class="category-item-content">
              <h3 class="category-item-name">{{ category.name }}</h3>
              <p class="category-item-description">{{ category.description }}</p>
            </div>
            <div class="category-item-actions">
              <button class="category-edit-btn" @click="editCategory(category.id)">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" stroke="currentColor" stroke-width="2"/>
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" stroke="currentColor" stroke-width="2"/>
                </svg>
              </button>
              <button class="category-toggle-btn" :class="{ active: category.isActive }" @click="toggleCategory(category.id)">
                {{ category.isActive ? 'Active' : 'Inactive' }}
              </button>
            </div>
          </div>
        </div>

        <div class="category-pagination">
          <span class="pagination-info">{{ categories.length }} / {{ categories.length }}</span>
        </div>
      </div>

      <div v-if="activeTab === 'notifications'" class="notifications-section">
        <div class="notifications-grid">
          <div class="notification-card">
            <div class="card-header">
              <div class="section-title">Create Notification</div>
            </div>
            <div class="notification-form">
              <div class="form-group">
                <label class="form-label">Title</label>
                <input type="text" v-model="newNotification.title" class="form-input" placeholder="Notification title">
              </div>
              <div class="form-group">
                <label class="form-label">Message</label>
                <textarea v-model="newNotification.message" class="form-textarea" placeholder="Notification message" rows="3"></textarea>
              </div>
              <div class="form-group">
                <label class="form-label">Severity</label>
                <select v-model="newNotification.severity" class="form-select">
                  <option value="INFO">Info</option>
                  <option value="WARNING">Warning</option>
                  <option value="ERROR">Error</option>
                  <option value="CRITICAL">Critical</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Start Date</label>
                <input type="datetime-local" v-model="newNotification.startDate" class="form-input">
              </div>
              <div class="form-group">
                <label class="form-label">End Date</label>
                <input type="datetime-local" v-model="newNotification.endDate" class="form-input">
              </div>
              <div class="form-group">
                <label class="form-label">Affected Tenants</label>
                <select multiple v-model="newNotification.affectedTenants" class="form-select">
                  <option v-for="tenant in tenants" :key="tenant.id" :value="tenant.id">
                    {{ tenant.name }}
                  </option>
                </select>
              </div>
              <button class="submit-btn" @click="createNotification">Create Notification</button>
            </div>
          </div>

          <div class="notification-card">
            <div class="card-header">
              <div class="section-title">Active Notifications</div>
            </div>
            <div class="notifications-list">
              <div v-for="notification in systemNotifications" :key="notification.id" class="notification-item">
                <div class="notification-content">
                  <div class="notification-header">
                    <h4 class="notification-title">{{ notification.title }}</h4>
                    <span class="severity-badge" :class="notification.severity.toLowerCase()">
                      {{ notification.severity }}
                    </span>
                  </div>
                  <p class="notification-message">{{ notification.message }}</p>
                  <div class="notification-meta">
                    <span class="notification-date">{{ formatDate(notification.startDate) }}</span>
                    <span class="notification-tenants">{{ notification.affectedTenants.length }} tenants</span>
                  </div>
                </div>
                <div class="notification-actions">
                  <button class="edit-btn" @click="editNotification(notification.id)">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" stroke="currentColor" stroke-width="2"/>
                      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" stroke="currentColor" stroke-width="2"/>
                    </svg>
                  </button>
                  <button class="delete-btn" @click="deleteNotification(notification.id)">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <polyline points="3,6 5,6 21,6" stroke="currentColor" stroke-width="2"/>
                      <path d="m19,6v14a2,2 0 0,1-2,2H7a2,2 0 0,1-2-2V6m3,0V4a2,2 0 0,1,2-2h4a2,2 0 0,1,2,2v2" stroke="currentColor" stroke-width="2"/>
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'user-management'" class="user-management-section">
        <div class="table-card">
          <div class="card-header">
            <div class="section-title">User Management</div>
            <div class="table-controls">
              <button class="create-user-btn" @click="showCreateUserModal = true">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                Create User
              </button>
              <button class="export-btn" @click="exportUserData">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <polyline points="7,10 12,15 17,10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <line x1="12" y1="15" x2="12" y2="3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                Export
              </button>
            </div>
          </div>
          
          <div class="user-filters-horizontal">
            <select v-model="userFilters.organization" class="filter-select">
              <option value="">All Organizations</option>
              <option v-for="org in recentOrganizations" :key="org.id" :value="org.name">
                {{ org.name }}
              </option>
            </select>
            <select v-model="userFilters.role" class="filter-select">
              <option value="">All Roles</option>
              <option v-for="role in availableRoles" :key="role" :value="role">
                {{ role }}
              </option>
            </select>
            <select v-model="userFilters.status" class="filter-select">
              <option value="">All Status</option>
              <option value="Active">Active</option>
              <option value="Inactive">Inactive</option>
              <option value="Pending">Pending</option>
            </select>
            <select v-model="userFilters.verified" class="filter-select">
              <option value="">All Verification</option>
              <option value="true">Verified</option>
              <option value="false">Unverified</option>
            </select>
            <input type="text" v-model="userFilters.search" class="filter-input" placeholder="Search users...">
          </div>

          <div class="table-container">
            <table class="user-table">
              <thead>
                <tr>
                  <th>User</th>
                  <th>Organization</th>
                  <th>Role</th>
                  <th>Status</th>
                  <th>Session</th>
                  <th>Verified</th>
                  <th>Last Active</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in filteredUsers" :key="user.id" class="user-row">
                  <td class="user-cell">
                    <div class="user-info">
                      <div class="user-avatar">
                        <span>{{ user.name.split(' ').map(n => n[0]).join('') }}</span>
                      </div>
                      <div class="user-details">
                        <span class="user-name">{{ user.name }}</span>
                        <span class="user-email">{{ user.email }}</span>
                        <span class="user-phone" v-if="user.phone">{{ user.phone }}</span>
                      </div>
                    </div>
                  </td>
                  <td>{{ user.organization }}</td>
                  <td>
                    <span class="role-badge" :class="user.role.toLowerCase()">{{ user.role }}</span>
                  </td>
                  <td>
                    <div class="status-indicator-container">
                      <span class="status-indicator" :class="user.status.toLowerCase()"></span>
                      <span>{{ user.status }}</span>
                    </div>
                  </td>
                  <td>
                    <div class="session-status">
                      <span class="session-indicator" :class="user.sessionStatus.toLowerCase()"></span>
                      <span class="session-text">{{ user.sessionStatus }}</span>
                      <span v-if="user.queuePosition" class="queue-position">(#{{ user.queuePosition }})</span>
                    </div>
                  </td>
                  <td>
                    <span class="verification-badge" :class="user.isVerified ? 'verified' : 'unverified'">
                      {{ user.isVerified ? 'Verified' : 'Unverified' }}
                    </span>
                  </td>
                  <td>{{ user.lastActive }}</td>
                  <td>
                    <div class="user-actions-dropdown" :class="{ open: openDropdown === user.id }">
                      <button class="user-actions-trigger" @click="toggleUserDropdown(user.id)">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <circle cx="12" cy="12" r="1" stroke="currentColor" stroke-width="2"/>
                          <circle cx="12" cy="5" r="1" stroke="currentColor" stroke-width="2"/>
                          <circle cx="12" cy="19" r="1" stroke="currentColor" stroke-width="2"/>
                        </svg>
                      </button>
                      <div class="user-actions-menu" v-if="openDropdown === user.id">
                        <button class="dropdown-item edit-item" @click="editUser(user.id)">
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" stroke="currentColor" stroke-width="2"/>
                            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" stroke="currentColor" stroke-width="2"/>
                          </svg>
                          Edit User
                        </button>
                        
                        <button 
                          class="dropdown-item activate-item" 
                          :disabled="user.status === 'Active'"
                          @click="handleUserAction('activate', user.id)"
                        >
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            <polyline points="22,4 12,14.01 9,11.01" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                          </svg>
                          Activate
                        </button>
                        
                        <button 
                          class="dropdown-item deactivate-item" 
                          :disabled="user.status === 'Inactive'"
                          @click="handleUserAction('deactivate', user.id)"
                        >
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            <line x1="15" y1="9" x2="9" y2="15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            <line x1="9" y1="9" x2="15" y2="15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                          </svg>
                          Deactivate
                        </button>
                        
                        <button 
                          class="dropdown-item verify-item"
                          :disabled="user.isVerified"
                          @click="handleUserAction('verify', user.id)"
                        >
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M9 12l2 2 4-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M21 12c-1 0-3-1-3-3s2-3 3-3 3 1 3 3-2 3-3 3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M3 12c1 0 3-1 3-3s-2-3-3-3-3 1-3 3 2 3 3 3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                          </svg>
                          Verify
                        </button>

                        <div class="dropdown-divider"></div>
                        
                        <div class="dropdown-submenu">
                          <button class="dropdown-item session-item" @click="toggleSessionSubmenu(user.id)">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                              <rect x="2" y="3" width="20" height="14" rx="2" ry="2" stroke="currentColor" stroke-width="2"/>
                              <line x1="8" y1="21" x2="16" y2="21" stroke="currentColor" stroke-width="2"/>
                              <line x1="12" y1="17" x2="12" y2="21" stroke="currentColor" stroke-width="2"/>
                            </svg>
                            Session Management
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="submenu-arrow">
                              <polyline points="9,18 15,12 9,6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            </svg>
                          </button>
                          
                          <div class="submenu-content" v-if="openSessionSubmenu === user.id">
                            <button 
                              class="submenu-item start-session-item"
                              :disabled="user.sessionStatus === 'Active'"
                              @click="handleSessionAction('start', user.id)"
                            >
                              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <polygon points="5,3 19,12 5,21" stroke="currentColor" stroke-width="2"/>
                              </svg>
                              Start Session
                            </button>
                            
                            <button 
                              class="submenu-item end-session-item"
                              :disabled="user.sessionStatus !== 'Active'"
                              @click="handleSessionAction('end', user.id)"
                            >
                              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <rect x="6" y="6" width="12" height="12" stroke="currentColor" stroke-width="2"/>
                              </svg>
                              End Session
                            </button>
                            
                            <button 
                              class="submenu-item join-queue-item"
                              :disabled="user.sessionStatus === 'In Queue'"
                              @click="handleSessionAction('joinQueue', user.id)"
                            >
                              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <line x1="3" y1="6" x2="21" y2="6" stroke="currentColor" stroke-width="2"/>
                                <line x1="3" y1="12" x2="21" y2="12" stroke="currentColor" stroke-width="2"/>
                                <line x1="3" y1="18" x2="21" y2="18" stroke="currentColor" stroke-width="2"/>
                              </svg>
                              Join Queue
                            </button>
                            
                            <button 
                              class="submenu-item leave-queue-item"
                              :disabled="user.sessionStatus !== 'In Queue'"
                              @click="handleSessionAction('leaveQueue', user.id)"
                            >
                              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="2"/>
                                <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="2"/>
                              </svg>
                              Leave Queue
                            </button>
                          </div>
                        </div>

                        <div class="dropdown-divider"></div>
                        
                        <button 
                          class="dropdown-item delete-item"
                          @click="handleUserAction('delete', user.id)"
                        >
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <polyline points="3,6 5,6 21,6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="m19,6v14a2,2 0 0,1-2,2H7a2,2 0 0,1-2-2V6m3,0V4a2,2 0 0,1,2-2h4a2,2 0 0,1,2,2v2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            <line x1="10" y1="11" x2="10" y2="17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            <line x1="14" y1="11" x2="14" y2="17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                          </svg>
                          Delete User
                        </button>
                      </div>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'role-management'" class="role-management-section">
        <div class="table-card">
          <div class="card-header">
            <div class="section-title">Role Management</div>
            <div class="table-controls">
              <button class="create-role-btn" @click="showCreateRoleModal = true">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                Create Role
              </button>
              <button class="export-btn" @click="exportRoleData">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <polyline points="7,10 12,15 17,10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <line x1="12" y1="15" x2="12" y2="3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                Export
              </button>
            </div>
          </div>
          <div class="table-container">
            <table class="role-table">
              <thead>
                <tr>
                  <th>Role Name</th>
                  <th>Permissions</th>
                  <th>Users Count</th>
                  <th>Created</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="role in roles" :key="role.id" class="role-row">
                  <td>
                    <div class="role-info">
                      <span class="role-name">{{ role.name }}</span>
                      <span class="role-description">{{ role.description }}</span>
                    </div>
                  </td>
                  <td>
                    <div class="permissions-list">
                      <span v-for="permission in role.permissions.slice(0, 3)" :key="permission" class="permission-badge">
                        {{ permission }}
                      </span>
                      <span v-if="role.permissions.length > 3" class="permission-count">
                        +{{ role.permissions.length - 3 }} more
                      </span>
                    </div>
                  </td>
                  <td>{{ role.userCount }}</td>
                  <td>{{ formatDate(role.createdAt) }}</td>
                  <td>
                    <div class="action-buttons">
                      <button class="action-btn edit-btn" @click="editRole(role.id)">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" stroke="currentColor" stroke-width="2"/>
                          <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" stroke="currentColor" stroke-width="2"/>
                        </svg>
                        Edit
                      </button>
                      <button class="action-btn delete-btn" @click="deleteRole(role.id)">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <polyline points="3,6 5,6 21,6" stroke="currentColor" stroke-width="2"/>
                          <path d="m19,6v14a2,2 0 0,1-2,2H7a2,2 0 0,1-2-2V6m3,0V4a2,2 0 0,1,2-2h4a2,2 0 0,1,2,2v2" stroke="currentColor" stroke-width="2"/>
                        </svg>
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div class="modal" v-if="showCreateOrgModal">
        <div class="modal-content">
          <div class="modal-header">
            <h2>Create New Organization</h2>
            <button class="close-btn" @click="showCreateOrgModal = false">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>
          <div class="modal-body">
            <div class="form-grid">
              <div class="form-group">
                <label for="org-name" class="form-label">Organization Name *</label>
                <input type="text" id="org-name" v-model="newOrg.name" class="form-input" placeholder="Enter organization name">
              </div>
              <div class="form-group">
                <label for="org-type" class="form-label">Organization Type *</label>
                <select id="org-type" v-model="newOrg.type" class="form-select">
                  <option value="">Select type</option>
                  <option value="ngo">NGO</option>
                  <option value="government">Government</option>
                  <option value="private">Private</option>
                  <option value="healthcare">Healthcare</option>
                  <option value="education">Education</option>
                  <option value="other">Other</option>
                </select>
              </div>
              <div class="form-group">
                <label for="org-location" class="form-label">Location *</label>
                <input type="text" id="org-location" v-model="newOrg.location" class="form-input" placeholder="City, Country">
              </div>
              <div class="form-group">
                <label for="org-domain" class="form-label">Custom Domain</label>
                <input type="text" id="org-domain" v-model="newOrg.customDomain" class="form-input" placeholder="subdomain.openchs.org">
              </div>
              <div class="form-group">
                <label for="org-admin" class="form-label">Admin Email *</label>
                <input type="email" id="org-admin" v-model="newOrg.adminEmail" class="form-input" placeholder="admin@organization.com">
              </div>
              <div class="form-group">
                <label for="org-phone" class="form-label">Phone Number</label>
                <input type="tel" id="org-phone" v-model="newOrg.phone" class="form-input" placeholder="+1 (555) 123-4567">
              </div>
              <div class="form-group full-width">
                <label for="org-description" class="form-label">Description</label>
                <textarea id="org-description" v-model="newOrg.description" class="form-textarea" placeholder="Brief description of the organization" rows="3"></textarea>
              </div>
              <div class="form-group full-width">
                <label class="form-label">Enabled Modules</label>
                <div class="checkbox-grid">
                  <label class="checkbox-label" v-for="module in availableModules" :key="module">
                    <input type="checkbox" v-model="newOrg.enabledModules" :value="module">
                    <span class="checkmark"></span>
                    {{ module }}
                  </label>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="cancel-btn" @click="showCreateOrgModal = false">Cancel</button>
            <button class="submit-btn" @click="createOrganization">Create Organization</button>
          </div>
        </div>
      </div>

      <div class="modal" v-if="showCreateTenantModal">
        <div class="modal-content">
          <div class="modal-header">
            <h2>Create New Tenant</h2>
            <button class="close-btn" @click="showCreateTenantModal = false">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>
          <div class="modal-body">
            <div class="form-grid">
              <div class="form-group">
                <label for="tenant-name" class="form-label">Tenant Name *</label>
                <input type="text" id="tenant-name" v-model="newTenant.name" class="form-input" placeholder="Enter tenant name">
              </div>
              <div class="form-group">
                <label for="tenant-location" class="form-label">Location *</label>
                <input type="text" id="tenant-location" v-model="newTenant.location" class="form-input" placeholder="City, Country">
              </div>
              <div class="form-group">
                <label for="tenant-domain" class="form-label">Custom Domain</label>
                <input type="text" id="tenant-domain" v-model="newTenant.customDomain" class="form-input" placeholder="subdomain.openchs.org">
              </div>
              <div class="form-group">
                <label for="tenant-admin" class="form-label">Admin Email *</label>
                <input type="email" id="tenant-admin" v-model="newTenant.adminEmail" class="form-input" placeholder="admin@tenant.com">
              </div>
              <div class="form-group full-width">
                <label class="form-label">Enabled Modules</label>
                <div class="checkbox-grid">
                  <label class="checkbox-label" v-for="module in availableModules" :key="module">
                    <input type="checkbox" v-model="newTenant.enabledModules" :value="module">
                    <span class="checkmark"></span>
                    {{ module }}
                  </label>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="cancel-btn" @click="showCreateTenantModal = false">Cancel</button>
            <button class="submit-btn" @click="createTenant">Create Tenant</button>
          </div>
        </div>
      </div>

      <div class="modal" v-if="showCreateUserModal">
        <div class="modal-content">
          <div class="modal-header">
            <h2>Create New User</h2>
            <button class="close-btn" @click="showCreateUserModal = false">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>
          <div class="modal-body">
            <div class="form-grid">
              <div class="form-group">
                <label for="user-username" class="form-label">Username *</label>
                <input type="text" id="user-username" v-model="newUser.username" class="form-input" placeholder="Enter username">
              </div>
              <div class="form-group">
                <label for="user-email" class="form-label">Email *</label>
                <input type="email" id="user-email" v-model="newUser.email" class="form-input" placeholder="Enter email">
              </div>
              <div class="form-group">
                <label for="user-phone" class="form-label">Phone</label>
                <input type="tel" id="user-phone" v-model="newUser.phone" class="form-input" placeholder="+1 (555) 123-4567">
              </div>
              <div class="form-group">
                <label for="user-password" class="form-label">Password *</label>
                <input type="password" id="user-password" v-model="newUser.password" class="form-input" placeholder="Enter password">
              </div>
              <div class="form-group">
                <label for="user-org" class="form-label">Organization *</label>
                <select id="user-org" v-model="newUser.organization" class="form-select">
                  <option value="">Select organization</option>
                  <option v-for="org in recentOrganizations" :key="org.id" :value="org.name">
                    {{ org.name }}
                  </option>
                </select>
              </div>
              <div class="form-group">
                <label for="user-role" class="form-label">Role *</label>
                <select id="user-role" v-model="newUser.role" class="form-select">
                  <option value="">Select role</option>
                  <option v-for="role in availableRoles" :key="role" :value="role">
                    {{ role }}
                  </option>
                </select>
              </div>
              <div class="form-group full-width">
                <label class="checkbox-label">
                  <input type="checkbox" v-model="newUser.isVerified">
                  <span class="checkmark"></span>
                  Mark as Verified
                </label>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="cancel-btn" @click="showCreateUserModal = false">Cancel</button>
            <button class="submit-btn" @click="createUser">Create User</button>
          </div>
        </div>
      </div>

      <div class="modal" v-if="showCreateRoleModal">
        <div class="modal-content">
          <div class="modal-header">
            <h2>Create New Role</h2>
            <button class="close-btn" @click="showCreateRoleModal = false">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label for="role-name" class="form-label">Role Name *</label>
              <input type="text" id="role-name" v-model="newRole.name" class="form-input" placeholder="Enter role name">
            </div>
            <div class="form-group">
              <label for="role-description" class="form-label">Description</label>
              <textarea id="role-description" v-model="newRole.description" class="form-textarea" placeholder="Enter role description" rows="3"></textarea>
            </div>
            <div class="form-group">
              <label class="form-label">Super Admin Permissions</label>
              <p class="form-description">Select system-level permissions for this role. These are global permissions that apply across all organizations.</p>
              <div class="permissions-grid">
                <label class="checkbox-label" v-for="permission in superAdminPermissions" :key="permission">
                  <input type="checkbox" v-model="newRole.permissions" :value="permission">
                  <span class="checkmark"></span>
                  {{ permission }}
                </label>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="cancel-btn" @click="showCreateRoleModal = false">Cancel</button>
            <button class="submit-btn" @click="createRole">Create Role</button>
          </div>
        </div>
      </div>

      <div class="modal" v-if="showUploadCsvModal">
        <div class="modal-content">
          <div class="modal-header">
            <h2>Upload Categories CSV</h2>
            <button class="close-btn" @click="showUploadCsvModal = false">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>
          <div class="modal-body">
            <div class="csv-upload-section">
              <div class="upload-instructions">
                <h4>CSV Format Requirements:</h4>
                <ul>
                  <li>Column 1: Category Name (required)</li>
                  <li>Column 2: Description (optional)</li>
                  <li>File must be in CSV format</li>
                  <li>Maximum 1000 categories per upload</li>
                </ul>
              </div>
              
              <div class="file-upload-area" @click="triggerFileInput" @dragover.prevent @drop.prevent="handleFileDrop">
                <input type="file" ref="csvFileInput" @change="handleFileSelect" accept=".csv" style="display: none;">
                <div class="upload-icon">
                  <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" stroke="currentColor" stroke-width="2"/>
                    <polyline points="17,8 12,3 7,8" stroke="currentColor" stroke-width="2"/>
                    <line x1="12" y1="3" x2="12" y2="15" stroke="currentColor" stroke-width="2"/>
                  </svg>
                </div>
                <p class="upload-text">
                  <span v-if="!selectedCsvFile">Click to select CSV file or drag and drop</span>
                  <span v-else>{{ selectedCsvFile.name }}</span>
                </p>
                <p class="upload-subtext">Supported format: CSV</p>
              </div>

              <div v-if="csvPreview.length > 0" class="csv-preview">
                <h4>Preview (First 5 rows):</h4>
                <div class="preview-table">
                  <table>
                    <thead>
                      <tr>
                        <th>Category Name</th>
                        <th>Description</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(row, index) in csvPreview.slice(0, 5)" :key="index">
                        <td>{{ row.name }}</td>
                        <td>{{ row.description || 'N/A' }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <p class="preview-info">{{ csvPreview.length }} categories will be imported</p>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="cancel-btn" @click="showUploadCsvModal = false">Cancel</button>
            <button class="submit-btn" @click="uploadCsvCategories" :disabled="!selectedCsvFile">Upload Categories</button>
          </div>
        </div>
      </div>

      <div class="modal" v-if="showAddAdminModal">
        <div class="modal-content">
          <div class="modal-header">
            <h2>Add New Admin</h2>
            <button class="close-btn" @click="showAddAdminModal = false">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>
          <div class="modal-body">
            <div class="form-grid">
              <div class="form-group">
                <label for="admin-name" class="form-label">Full Name *</label>
                <input type="text" id="admin-name" v-model="newAdmin.name" class="form-input" placeholder="Enter full name">
              </div>
              <div class="form-group">
                <label for="admin-email" class="form-label">Email *</label>
                <input type="email" id="admin-email" v-model="newAdmin.email" class="form-input" placeholder="Enter email">
              </div>
              <div class="form-group">
                <label for="admin-org" class="form-label">Organization *</label>
                <select id="admin-org" v-model="newAdmin.organization" class="form-select">
                  <option value="">Select organization</option>
                  <option v-for="org in recentOrganizations" :key="org.id" :value="org.name">
                    {{ org.name }}
                  </option>
                </select>
              </div>
              <div class="form-group">
                <label for="admin-role" class="form-label">Role *</label>
                <select id="admin-role" v-model="newAdmin.role" class="form-select">
                  <option value="">Select role</option>
                  <option value="Admin">Admin</option>
                  <option value="Manager">Manager</option>
                  <option value="User">User</option>
                </select>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="cancel-btn" @click="showAddAdminModal = false">Cancel</button>
            <button class="submit-btn" @click="addAdmin">Add Admin</button>
          </div>
        </div>
      </div>

      <div class="modal" v-if="showAddCategoryModal">
        <div class="modal-content">
          <div class="modal-header">
            <h2>Add Category</h2>
            <button class="close-btn" @click="showAddCategoryModal = false">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label for="category-name" class="form-label">Category Name *</label>
              <input type="text" id="category-name" v-model="newCategory.name" class="form-input" placeholder="Enter category name">
            </div>
            <div class="form-group">
              <label for="category-description" class="form-label">Description</label>
              <textarea id="category-description" v-model="newCategory.description" class="form-textarea" placeholder="Enter description" rows="3"></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button class="cancel-btn" @click="showAddCategoryModal = false">Cancel</button>
            <button class="submit-btn" @click="addCategory">Add Category</button>
          </div>
        </div>
      </div>

      <div class="modal" v-if="showAuditDetailsModal">
        <div class="modal-content">
          <div class="modal-header">
            <h2>Audit Log Details</h2>
            <button class="close-btn" @click="showAuditDetailsModal = false">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>
          <div class="modal-body">
            <div v-if="selectedAuditLog" class="audit-details">
              <div class="detail-group">
                <label>Timestamp:</label>
                <span>{{ formatDate(selectedAuditLog.timestamp) }}</span>
              </div>
              <div class="detail-group">
                <label>User:</label>
                <span>{{ selectedAuditLog.user }}</span>
              </div>
              <div class="detail-group">
                <label>Action:</label>
                <span class="action-badge" :class="selectedAuditLog.action.toLowerCase()">{{ selectedAuditLog.action }}</span>
              </div>
              <div class="detail-group">
                <label>Model:</label>
                <span>{{ selectedAuditLog.modelName }}</span>
              </div>
              <div class="detail-group">
                <label>Object ID:</label>
                <span>{{ selectedAuditLog.objectId }}</span>
              </div>
              <div class="detail-group">
                <label>IP Address:</label>
                <span>{{ selectedAuditLog.ipAddress }}</span>
              </div>
              <div class="detail-group">
                <label>User Agent:</label>
                <span>{{ selectedAuditLog.userAgent }}</span>
              </div>
              <div v-if="selectedAuditLog.metadata" class="detail-group">
                <label>Metadata:</label>
                <pre class="metadata-display">{{ JSON.stringify(selectedAuditLog.metadata, null, 2) }}</pre>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="cancel-btn" @click="showAuditDetailsModal = false">Close</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'

const isSidebarCollapsed = ref(false)
const mobileOpen = ref(false)
const currentTheme = ref('dark')
const activeTab = ref('dashboard')
const selectedTimeframe = ref('7days')

const showCreateOrgModal = ref(false)
const showCreateTenantModal = ref(false)
const showCreateUserModal = ref(false)
const showCreateRoleModal = ref(false)
const showAddAdminModal = ref(false)
const showAddCategoryModal = ref(false)
const showUploadCsvModal = ref(false)
const showAuditDetailsModal = ref(false)

const selectedCsvFile = ref(null)
const csvPreview = ref([])
const csvFileInput = ref(null)

const openDropdown = ref(null)
const openSessionSubmenu = ref(null)

const availableModules = ref([
  'AI Chatbot',
  'Case Management',
  'Analytics',
  'Reports',
  'Document Management',
  'Communication Tools',
  'Workflow Automation'
])

const availableRoles = ref([
  'Admin',
  'Manager',
  'Case Worker',
  'Supervisor',
  'User'
])

const superAdminPermissions = ref([
  'Full System Access',
  'Read Only Access',
  'User Management',
  'Organization Management',
  'System Configuration',
  'Audit Log Access',
  'Data Export',
  'Backup Management',
  'Security Settings',
  'API Access',
  'Integration Management',
  'Report Generation'
])

const newOrg = ref({
  name: '',
  location: '',
  adminEmail: '',
  type: '',
  customDomain: '',
  phone: '',
  description: '',
  enabledModules: ['Case Management']
})

const newTenant = ref({
  name: '',
  location: '',
  adminEmail: '',
  customDomain: '',
  enabledModules: ['Case Management']
})

const newUser = ref({
  username: '',
  email: '',
  phone: '',
  password: '',
  organization: '',
  role: '',
  isVerified: false
})

const newRole = ref({
  name: '',
  description: '',
  permissions: []
})

const newAdmin = ref({
  name: '',
  email: '',
  organization: '',
  role: ''
})

const newCategory = ref({
  name: '',
  description: ''
})

const newNotification = ref({
  title: '',
  message: '',
  severity: 'INFO',
  startDate: '',
  endDate: '',
  affectedTenants: []
})

const systemConfig = ref({
  maintenanceMode: false,
  allowNewSignups: true,
  enableNotifications: true,
  defaultAiProvider: 'OPENAI',
  aiTimeout: 30,
  caseNumberPrefix: 'CASE',
  caseNumberCounter: 102,
  defaultCasePriority: 'MEDIUM',
  sessionTimeout: 60,
  passwordMinLength: 8,
  requireTwoFactor: false,
  auditRetention: 365,
  backupFrequency: 'DAILY',
  smtpServer: '',
  fromEmail: ''
})

const auditFilters = ref({
  action: '',
  model: '',
  date: '',
  user: ''
})

const userFilters = ref({
  organization: '',
  role: '',
  status: '',
  verified: '',
  search: ''
})

const dashboardStats = ref({
  organizations: 247,
  activeUsers: 12847,
  systemHealth: 99.9,
  growth: 24.7
})

const recentOrganizations = ref([
  {
    id: 1,
    name: 'Children First Kenya',
    users: 45,
    status: 'Active'
  },
  {
    id: 2,
    name: 'Safe Haven Uganda',
    users: 32,
    status: 'Active'
  },
  {
    id: 3,
    name: 'Hope Foundation',
    users: 28,
    status: 'Pending'
  },
  {
    id: 4,
    name: 'Care Network',
    users: 67,
    status: 'Active'
  }
])

const tenants = ref([
  {
    id: 1,
    name: 'Children First Kenya',
    location: 'Nairobi, Kenya',
    customDomain: 'cfk.openchs.org',
    userCount: 45,
    enabledModules: ['AI Chatbot', 'Case Management', 'Analytics'],
    status: 'Active'
  },
  {
    id: 2,
    name: 'Safe Haven Uganda',
    location: 'Kampala, Uganda',
    customDomain: null,
    userCount: 32,
    enabledModules: ['Case Management', 'Reports'],
    status: 'Active'
  },
  {
    id: 3,
    name: 'Hope Foundation',
    location: 'Lagos, Nigeria',
    customDomain: 'hope.openchs.org',
    userCount: 28,
    enabledModules: ['AI Chatbot', 'Case Management'],
    status: 'Pending'
  }
])

const users = ref([
  {
    id: 1,
    name: 'John Doe',
    email: 'john.doe@example.com',
    phone: '+1-555-0123',
    organization: 'Children First Kenya',
    role: 'Admin',
    status: 'Active',
    sessionStatus: 'Active',
    queuePosition: null,
    isVerified: true,
    lastActive: '2 hours ago'
  },
  {
    id: 2,
    name: 'Sarah Wilson',
    email: 'sarah.wilson@example.com',
    phone: '+1-555-0124',
    organization: 'Safe Haven Uganda',
    role: 'Manager',
    status: 'Active',
    sessionStatus: 'In Queue',
    queuePosition: 3,
    isVerified: true,
    lastActive: '1 day ago'
  },
  {
    id: 3,
    name: 'Michael Brown',
    email: 'michael.brown@example.com',
    phone: '+1-555-0125',
    organization: 'Hope Foundation',
    role: 'Case Worker',
    status: 'Inactive',
    sessionStatus: 'Offline',
    queuePosition: null,
    isVerified: false,
    lastActive: '1 week ago'
  },
  {
    id: 4,
    name: 'Emily Davis',
    email: 'emily.davis@example.com',
    phone: '+1-555-0126',
    organization: 'Care Network',
    role: 'Admin',
    status: 'Active',
    sessionStatus: 'Active',
    queuePosition: null,
    isVerified: true,
    lastActive: '30 minutes ago'
  },
  {
    id: 5,
    name: 'David Johnson',
    email: 'david.johnson@example.com',
    phone: '+1-555-0127',
    organization: 'Children First Kenya',
    role: 'User',
    status: 'Pending',
    sessionStatus: 'Offline',
    queuePosition: null,
    isVerified: false,
    lastActive: '3 days ago'
  }
])

const roles = ref([
  {
    id: 1,
    name: 'Super Admin',
    description: 'Full system access with all permissions',
    permissions: ['Full System Access', 'User Management', 'Organization Management', 'System Configuration'],
    userCount: 2,
    createdAt: '2025-01-01T00:00:00Z'
  },
  {
    id: 2,
    name: 'System Admin',
    description: 'System administration with limited access',
    permissions: ['User Management', 'Organization Management', 'Audit Log Access'],
    userCount: 5,
    createdAt: '2025-01-02T00:00:00Z'
  },
  {
    id: 3,
    name: 'Read Only Admin',
    description: 'View-only access to system data',
    permissions: ['Read Only Access', 'Report Generation'],
    userCount: 8,
    createdAt: '2025-01-03T00:00:00Z'
  }
])

const auditLogs = ref([
  {
    id: 1,
    timestamp: '2025-06-05T14:30:00Z',
    user: 'John Doe',
    action: 'CREATE',
    modelName: 'Case',
    objectId: 'CASE-001',
    ipAddress: '192.168.1.100',
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    metadata: {
      fieldChanged: 'status',
      oldValue: null,
      newValue: 'open'
    }
  },
  {
    id: 2,
    timestamp: '2025-06-05T13:15:00Z',
    user: 'Sarah Wilson',
    action: 'UPDATE',
    modelName: 'User',
    objectId: 'USER-123',
    ipAddress: '192.168.1.101',
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    metadata: {
      fieldChanged: 'role',
      oldValue: 'User',
      newValue: 'Manager'
    }
  },
  {
    id: 3,
    timestamp: '2025-06-05T12:00:00Z',
    user: 'Emily Davis',
    action: 'DELETE',
    modelName: 'Organization',
    objectId: 'ORG-456',
    ipAddress: '192.168.1.102',
    userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
    metadata: {
      reason: 'Duplicate entry'
    }
  }
])

const categories = ref([
  {
    id: 1,
    name: 'Aggravated assault',
    description: 'Involves serious bodily harm or use of weapons',
    isActive: true
  },
  {
    id: 2,
    name: 'Abuse',
    description: 'Physical, emotional, or psychological harm',
    isActive: true
  },
  {
    id: 3,
    name: 'Battering and beating',
    description: 'Repeated physical violence',
    isActive: true
  },
  {
    id: 4,
    name: 'Beating with an object',
    description: 'Physical violence using weapons or objects',
    isActive: true
  },
  {
    id: 5,
    name: 'Child Abuse',
    description: 'Harm or neglect of minors',
    isActive: true
  },
  {
    id: 6,
    name: 'Burglary',
    description: 'Unlawful entry with intent to commit crime',
    isActive: true
  },
  {
    id: 7,
    name: 'Cyber bullying',
    description: 'Online harassment and intimidation',
    isActive: true
  },
  {
    id: 8,
    name: 'Child trafficking',
    description: 'Illegal movement and exploitation of children',
    isActive: true
  }
])

const systemNotifications = ref([
  {
    id: 1,
    title: 'System Maintenance',
    message: 'Scheduled maintenance will occur from 10 PM to 12 AM tonight.',
    severity: 'WARNING',
    startDate: '2025-06-10T22:00:00Z',
    endDate: '2025-06-11T00:00:00Z',
    affectedTenants: [1, 2, 3],
    isActive: true
  },
  {
    id: 2,
    title: 'New Feature Release',
    message: 'AI-powered case analysis is now available for all tenants.',
    severity: 'INFO',
    startDate: '2025-06-05T09:00:00Z',
    endDate: '2025-06-12T23:59:59Z',
    affectedTenants: [1, 2, 3],
    isActive: true
  }
])

const selectedAuditLog = ref(null)

const filteredAuditLogs = computed(() => {
  return auditLogs.value.filter(log => {
    if (auditFilters.value.action && log.action !== auditFilters.value.action) return false
    if (auditFilters.value.model && log.modelName !== auditFilters.value.model) return false
    if (auditFilters.value.user && !log.user.toLowerCase().includes(auditFilters.value.user.toLowerCase())) return false
    if (auditFilters.value.date) {
      const logDate = new Date(log.timestamp).toISOString().split('T')[0]
      if (logDate !== auditFilters.value.date) return false
    }
    return true
  })
})

const filteredUsers = computed(() => {
  return users.value.filter(user => {
    if (userFilters.value.organization && user.organization !== userFilters.value.organization) return false
    if (userFilters.value.role && user.role !== userFilters.value.role) return false
    if (userFilters.value.status && user.status !== userFilters.value.status) return false
    if (userFilters.value.verified !== '' && user.isVerified.toString() !== userFilters.value.verified) return false
    if (userFilters.value.search) {
      const search = userFilters.value.search.toLowerCase()
      if (!user.name.toLowerCase().includes(search) && 
          !user.email.toLowerCase().includes(search) &&
          !user.organization.toLowerCase().includes(search)) return false
    }
    return true
  })
})

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
  activeTab.value = tab
  mobileOpen.value = false
}

const getPageTitle = () => {
  const titles = {
    'dashboard': 'Super Admin Dashboard',
    'system-config': 'System Configuration',
    'tenant-management': 'Tenant Management',
    'audit-logs': 'Audit Logs',
    'category-management': 'Categories',
    'notifications': 'System Notifications',
    'user-management': 'User Management',
    'role-management': 'Role Management'
  }
  return titles[activeTab.value] || 'Super Admin Dashboard'
}

const navigateTo = (path) => {
  console.log(`Navigating to: ${path}`)
}

const applyTheme = (theme) => {
  const root = document.documentElement

  if (theme === 'light') {
    root.style.setProperty('--background-color', '#f5f5f5')
    root.style.setProperty('--sidebar-bg', '#ffffff')
    root.style.setProperty('--content-bg', '#ffffff')
    root.style.setProperty('--text-color', '#333')
    root.style.setProperty('--text-secondary', '#666')
    root.style.setProperty('--border-color', '#ddd')
    root.style.setProperty('--card-bg', '#ffffff')
    root.style.setProperty('--logo-bg', '#ffffff')
    root.style.setProperty('--logo-color', '#333')
    root.setAttribute('data-theme', 'light')
  } else {
    root.style.setProperty('--background-color', '#0a0a0a')
    root.style.setProperty('--sidebar-bg', '#111')
    root.style.setProperty('--content-bg', '#222')
    root.style.setProperty('--text-color', '#fff')
    root.style.setProperty('--text-secondary', '#aaa')
    root.style.setProperty('--border-color', '#333')
    root.style.setProperty('--card-bg', '#222')
    root.style.setProperty('--logo-bg', '#fff')
    root.style.setProperty('--logo-color', '#0a0a0a')
    root.setAttribute('data-theme', 'dark')
  }

  root.style.setProperty('--accent-color', '#FF8C00')
  root.style.setProperty('--accent-hover', '#FF7700')
  root.style.setProperty('--danger-color', '#ff3b30')
  root.style.setProperty('--success-color', '#4CAF50')
  root.style.setProperty('--pending-color', '#FFA500')
  root.style.setProperty('--unassigned-color', '#808080')
  root.style.setProperty('--highlight-color', '#ff3b30')
}

const toggleTheme = () => {
  currentTheme.value = currentTheme.value === 'dark' ? 'light' : 'dark'
  localStorage.setItem('theme', currentTheme.value)
  applyTheme(currentTheme.value)
}

const logout = () => {
  console.log('Logging out...')
  alert('Logged out successfully!')
}

const handleQuickAction = (action) => {
  if (action === 'create-org') {
    showCreateOrgModal.value = true
  } else if (action === 'add-admin') {
    showAddAdminModal.value = true
  }
}

const toggleUserDropdown = (userId) => {
  if (openDropdown.value === userId) {
    openDropdown.value = null
    openSessionSubmenu.value = null
  } else {
    openDropdown.value = userId
    openSessionSubmenu.value = null
  }
}

const toggleSessionSubmenu = (userId) => {
  if (openSessionSubmenu.value === userId) {
    openSessionSubmenu.value = null
  } else {
    openSessionSubmenu.value = userId
  }
}

const handleUserAction = (action, userId) => {
  const userIndex = users.value.findIndex(user => user.id === userId)
  if (userIndex !== -1) {
    if (action === 'activate') {
      users.value[userIndex].status = 'Active'
      alert(`User ${users.value[userIndex].name} has been activated.`)
    } else if (action === 'deactivate') {
      users.value[userIndex].status = 'Inactive'
      alert(`User ${users.value[userIndex].name} has been deactivated.`)
    } else if (action === 'verify') {
      users.value[userIndex].isVerified = true
      alert(`User ${users.value[userIndex].name} has been verified.`)
    } else if (action === 'delete') {
      if (confirm(`Are you sure you want to delete ${users.value[userIndex].name}?`)) {
        users.value = users.value.filter(user => user.id !== userId)
        alert('User has been deleted.')
      }
    }
  }
  openDropdown.value = null
  openSessionSubmenu.value = null
}

const handleSessionAction = (action, userId) => {
  const userIndex = users.value.findIndex(user => user.id === userId)
  if (userIndex !== -1) {
    const user = users.value[userIndex]
    
    if (action === 'start') {
      user.sessionStatus = 'Active'
      user.queuePosition = null
      alert(`Session started for ${user.name}.`)
    } else if (action === 'end') {
      user.sessionStatus = 'Offline'
      user.queuePosition = null
      alert(`Session ended for ${user.name}.`)
    } else if (action === 'joinQueue') {
      user.sessionStatus = 'In Queue'
      user.queuePosition = Math.floor(Math.random() * 10) + 1
      alert(`${user.name} has joined the queue at position ${user.queuePosition}.`)
    } else if (action === 'leaveQueue') {
      user.sessionStatus = 'Offline'
      user.queuePosition = null
      alert(`${user.name} has left the queue.`)
    }
  }
  openDropdown.value = null
  openSessionSubmenu.value = null
}

const editUser = (userId) => {
  console.log('Edit user:', userId)
  alert(`Edit user ${userId} functionality would be implemented here.`)
  openDropdown.value = null
}

const toggleFavorite = (orgId) => {
  alert(`Organization ${orgId} has been added to favorites.`)
}

const toggleTenantFilters = () => {
  alert('Tenant filters functionality would be implemented here.')
}

const exportUserData = () => {
  alert('User data would be exported here.')
}

const exportTenantData = () => {
  alert('Tenant data would be exported here.')
}

const exportAuditData = () => {
  alert('Audit data would be exported here.')
}

const exportRoleData = () => {
  alert('Role data would be exported here.')
}

const downloadCsvTemplate = () => {
  const csvContent = 'Category Name,Description\nExample Category,This is an example description\nAnother Category,Another example description'
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', 'categories_template.csv')
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  alert('CSV template downloaded successfully!')
}

const triggerFileInput = () => {
  csvFileInput.value.click()
}

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file && file.type === 'text/csv') {
    selectedCsvFile.value = file
    parseCsvFile(file)
  } else {
    alert('Please select a valid CSV file.')
  }
}

const handleFileDrop = (event) => {
  const file = event.dataTransfer.files[0]
  if (file && file.type === 'text/csv') {
    selectedCsvFile.value = file
    parseCsvFile(file)
  } else {
    alert('Please drop a valid CSV file.')
  }
}

const parseCsvFile = (file) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    const csv = e.target.result
    const lines = csv.split('\n')
    const preview = []
    
    for (let i = 1; i < lines.length && i <= 1000; i++) {
      const line = lines[i].trim()
      if (line) {
        const columns = line.split(',')
        if (columns[0]) {
          preview.push({
            name: columns[0].replace(/"/g, '').trim(),
            description: columns[1] ? columns[1].replace(/"/g, '').trim() : ''
          })
        }
      }
    }
    
    csvPreview.value = preview
  }
  reader.readAsText(file)
}

const uploadCsvCategories = () => {
  if (!selectedCsvFile.value || csvPreview.value.length === 0) {
    alert('Please select a valid CSV file with categories.')
    return
  }

  let addedCount = 0
  csvPreview.value.forEach(csvCategory => {
    if (csvCategory.name && !categories.value.find(cat => cat.name.toLowerCase() === csvCategory.name.toLowerCase())) {
      const newId = categories.value.length + addedCount + 1
      categories.value.push({
        id: newId,
        name: csvCategory.name,
        description: csvCategory.description || '',
        isActive: true
      })
      addedCount++
    }
  })

  selectedCsvFile.value = null
  csvPreview.value = []
  showUploadCsvModal.value = false
  alert(`Successfully imported ${addedCount} categories from CSV.`)
}

const createOrganization = () => {
  if (!newOrg.value.name || !newOrg.value.location || !newOrg.value.adminEmail || !newOrg.value.type) {
    alert('Please fill in all required fields.')
    return
  }

  const newId = recentOrganizations.value.length + 1
  recentOrganizations.value.unshift({
    id: newId,
    name: newOrg.value.name,
    users: 1,
    status: 'Active'
  })

  tenants.value.unshift({
    id: newId,
    name: newOrg.value.name,
    location: newOrg.value.location,
    customDomain: newOrg.value.customDomain || null,
    userCount: 1,
    enabledModules: newOrg.value.enabledModules,
    status: 'Active'
  })

  newOrg.value = {
    name: '',
    location: '',
    adminEmail: '',
    type: '',
    customDomain: '',
    phone: '',
    description: '',
    enabledModules: ['Case Management']
  }

  showCreateOrgModal.value = false
  alert('Organization created successfully!')
}

const createTenant = () => {
  if (!newTenant.value.name || !newTenant.value.location || !newTenant.value.adminEmail) {
    alert('Please fill in all required fields.')
    return
  }

  const newId = tenants.value.length + 1
  tenants.value.unshift({
    id: newId,
    name: newTenant.value.name,
    location: newTenant.value.location,
    customDomain: newTenant.value.customDomain || null,
    userCount: 1,
    enabledModules: newTenant.value.enabledModules,
    status: 'Active'
  })

  newTenant.value = {
    name: '',
    location: '',
    adminEmail: '',
    customDomain: '',
    enabledModules: ['Case Management']
  }

  showCreateTenantModal.value = false
  alert('Tenant created successfully!')
}

const createUser = () => {
  if (!newUser.value.username || !newUser.value.email || !newUser.value.password || !newUser.value.organization || !newUser.value.role) {
    alert('Please fill in all required fields.')
    return
  }

  const newId = users.value.length + 1
  users.value.unshift({
    id: newId,
    name: newUser.value.username,
    email: newUser.value.email,
    phone: newUser.value.phone,
    organization: newUser.value.organization,
    role: newUser.value.role,
    status: 'Active',
    sessionStatus: 'Offline',
    queuePosition: null,
    isVerified: newUser.value.isVerified,
    lastActive: 'Just now'
  })

  newUser.value = {
    username: '',
    email: '',
    phone: '',
    password: '',
    organization: '',
    role: '',
    isVerified: false
  }

  showCreateUserModal.value = false
  alert('User created successfully!')
}

const createRole = () => {
  if (!newRole.value.name || newRole.value.permissions.length === 0) {
    alert('Please fill in all required fields and select at least one permission.')
    return
  }

  const newId = roles.value.length + 1
  roles.value.unshift({
    id: newId,
    name: newRole.value.name,
    description: newRole.value.description,
    permissions: newRole.value.permissions,
    userCount: 0,
    createdAt: new Date().toISOString()
  })

  newRole.value = {
    name: '',
    description: '',
    permissions: []
  }

  showCreateRoleModal.value = false
  alert('Role created successfully!')
}

const editRole = (roleId) => {
  console.log('Edit role:', roleId)
  alert(`Edit role ${roleId} functionality would be implemented here.`)
}

const deleteRole = (roleId) => {
  if (confirm('Are you sure you want to delete this role?')) {
    roles.value = roles.value.filter(role => role.id !== roleId)
    alert('Role deleted successfully!')
  }
}

const addAdmin = () => {
  if (!newAdmin.value.name || !newAdmin.value.email || !newAdmin.value.organization || !newAdmin.value.role) {
    alert('Please fill in all required fields.')
    return
  }

  const newId = users.value.length + 1
  users.value.unshift({
    id: newId,
    name: newAdmin.value.name,
    email: newAdmin.value.email,
    phone: '',
    organization: newAdmin.value.organization,
    role: newAdmin.value.role,
    status: 'Active',
    sessionStatus: 'Offline',
    queuePosition: null,
    isVerified: true,
    lastActive: 'Just now'
  })

  newAdmin.value = {
    name: '',
    email: '',
    organization: '',
    role: ''
  }

  showAddAdminModal.value = false
  alert('Admin added successfully!')
}

const saveSystemConfig = () => {
  console.log('Saving system config:', systemConfig.value)
  alert('System configuration saved successfully!')
}

const editTenant = (tenantId) => {
  console.log('Edit tenant:', tenantId)
  alert(`Edit tenant ${tenantId} functionality would be implemented here.`)
}

const impersonateTenant = (tenantId) => {
  console.log('Impersonate tenant:', tenantId)
  alert(`Impersonating tenant ${tenantId}. This would redirect to their dashboard.`)
}

const viewAuditDetails = (log) => {
  selectedAuditLog.value = log
  showAuditDetailsModal.value = true
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString()
}

const addCategory = () => {
  if (!newCategory.value.name) {
    alert('Please fill in all required fields.')
    return
  }

  const newId = categories.value.length + 1
  categories.value.push({
    id: newId,
    name: newCategory.value.name,
    description: newCategory.value.description,
    isActive: true
  })

  newCategory.value = {
    name: '',
    description: ''
  }

  showAddCategoryModal.value = false
  alert('Category added successfully!')
}

const toggleCategory = (categoryId) => {
  const category = categories.value.find(c => c.id === categoryId)
  if (category) {
    category.isActive = !category.isActive
    alert(`Category ${category.name} has been ${category.isActive ? 'activated' : 'deactivated'}.`)
  }
}

const editCategory = (categoryId) => {
  console.log('Edit category:', categoryId)
  alert(`Edit category ${categoryId} functionality would be implemented here.`)
}

const createNotification = () => {
  if (!newNotification.value.title || !newNotification.value.message) {
    alert('Please fill in all required fields.')
    return
  }

  const newId = systemNotifications.value.length + 1
  systemNotifications.value.unshift({
    id: newId,
    title: newNotification.value.title,
    message: newNotification.value.message,
    severity: newNotification.value.severity,
    startDate: newNotification.value.startDate,
    endDate: newNotification.value.endDate,
    affectedTenants: newNotification.value.affectedTenants,
    isActive: true
  })

  newNotification.value = {
    title: '',
    message: '',
    severity: 'INFO',
    startDate: '',
    endDate: '',
    affectedTenants: []
  }

  alert('Notification created successfully!')
}

const editNotification = (notificationId) => {
  console.log('Edit notification:', notificationId)
  alert(`Edit notification ${notificationId} functionality would be implemented here.`)
}

const deleteNotification = (notificationId) => {
  if (confirm('Are you sure you want to delete this notification?')) {
    systemNotifications.value = systemNotifications.value.filter(n => n.id !== notificationId)
    alert('Notification deleted successfully!')
  }
}

onMounted(() => {
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme) {
    currentTheme.value = savedTheme
  }

  applyTheme(currentTheme.value)

  const handleResize = () => {
    if (window.innerWidth > 1024) {
      mobileOpen.value = false
    }
  }
  window.addEventListener('resize', handleResize)

  const handleClickOutside = (event) => {
    const isMobileOrTablet = window.innerWidth <= 1024
    const sidebar = document.getElementById('sidebar')
    const mobileMenuBtn = document.getElementById('mobile-menu-btn')
    
    if (isMobileOrTablet && sidebar && !sidebar.contains(event.target) && event.target !== mobileMenuBtn) {
      mobileOpen.value = false
    }

    // Close dropdowns when clicking outside
    if (!event.target.closest('.user-actions-dropdown')) {
      openDropdown.value = null
      openSessionSubmenu.value = null
    }
  }
  document.addEventListener('click', handleClickOutside)
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: 'Inter', sans-serif;
}

body {
  background-color: var(--background-color);
  color: var(--text-color);
  min-height: 100vh;
  margin: 0;
  padding: 0;
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

.nav-section {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 0 15px;
  margin-bottom: 15px;
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
  background-color: rgba(255, 255, 255, 0.05);
  transform: translateX(3px);
}

.nav-item.active {
  background-color: rgba(255, 255, 255, 0.1);
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
}

.nav-text {
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-bottom {
  padding: 0 15px 20px 15px;
  flex-shrink: 0;
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
  background-color: var(--success-color);
  margin-right: 6px;
}

.button-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.logout-btn {
  background-color: var(--danger-color);
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
  background-color: #e60000;
  transform: translateY(-1px);
}

.main-content {
  flex: 1;
  margin-left: 250px;
  height: 100vh;
  background-color: var(--background-color);
  transition: margin-left 0.3s ease, width 0.3s ease, background-color 0.3s;
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
}

.page-title {
  font-size: 28px;
  font-weight: 700;
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
}

.theme-toggle:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.theme-toggle svg {
  width: 16px;
  height: 16px;
}

.main-scroll-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  overflow-x: hidden;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.main-scroll-content::-webkit-scrollbar {
  display: none;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.dashboard-card {
  background-color: var(--card-bg);
  border-radius: 30px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s, background-color 0.3s;
}

.dashboard-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.card-title {
  font-size: 16px;
  font-weight: 700;
}

.card-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: var(--accent-color);
  display: flex;
  justify-content: center;
  align-items: center;
}

.card-icon svg {
  stroke: white;
}

.card-value {
  font-size: 32px;
  font-weight: 800;
  margin-bottom: 5px;
}

.card-subtitle {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
}

.quick-actions-section {
  margin-bottom: 30px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-title {
  font-size: 20px;
  font-weight: 700;
}

.quick-actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 20px;
}

.action-card {
  background-color: var(--card-bg);
  border-radius: 30px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s, background-color 0.3s;
  cursor: pointer;
}

.action-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

.action-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background-color: rgba(255, 140, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 15px;
}

.action-icon svg {
  width: 24px;
  height: 24px;
  color: var(--accent-color);
}

.action-title {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 8px;
}

.action-description {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 15px;
  line-height: 1.5;
}

.action-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background-color: var(--accent-color);
  color: white;
  border: none;
  border-radius: 25px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 100%;
  justify-content: center;
}

.action-button:hover {
  background-color: var(--accent-hover);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255, 140, 0, 0.3);
}

.action-button svg {
  width: 16px;
  height: 16px;
}

.management-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.management-card {
  background-color: var(--card-bg);
  border-radius: 30px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: background-color 0.3s;
}

.view-all-btn {
  padding: 8px 16px;
  background: none;
  border: 1px solid var(--border-color);
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  background: var(--background-color);
}

.view-all-btn:hover {
  border-color: var(--accent-color);
  color: var(--accent-color);
}

.organizations-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.organization-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  border: 1px solid var(--border-color);
  border-radius: 20px;
  transition: all 0.3s ease;
}

.organization-item:hover {
  border-color: var(--accent-color);
  background-color: rgba(255, 140, 0, 0.05);
}

.org-avatar {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background-color: var(--accent-color);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 14px;
}

.org-info {
  flex: 1;
}

.org-name {
  font-weight: 600;
  margin-bottom: 4px;
}

.org-details {
  font-size: 12px;
  color: var(--text-secondary);
}

.org-actions {
  display: flex;
  gap: 8px;
}

.org-action-btn {
  padding: 8px;
  border: none;
  background: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  color: var(--text-secondary);
}

.org-action-btn:hover {
  background-color: var(--background-color);
  color: var(--text-color);
}

.org-action-btn svg {
  width: 16px;
  height: 16px;
}

.time-filter {
  padding: 8px 12px;
  background: var(--background-color);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-color);
  cursor: pointer;
  transition: all 0.3s ease;
}

.analytics-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.chart-placeholder {
  height: 200px;
  background-color: var(--background-color);
  border-radius: 15px;
  display: flex;
  align-items: end;
  justify-content: center;
  padding: 20px;
}

.chart-bars {
  display: flex;
  align-items: end;
  gap: 8px;
  height: 100%;
}

.chart-bar {
  width: 20px;
  background: linear-gradient(to top, var(--accent-color), #FF7700);
  border-radius: 4px 4px 0 0;
  transition: all 0.3s ease;
}

.chart-bar:hover {
  transform: scaleY(1.1);
}

.analytics-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-label {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
}

.config-section {
  margin-bottom: 30px;
}

.config-container {
  background-color: var(--card-bg);
  border-radius: 30px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: background-color 0.3s;
  min-height: calc(100vh - 140px);
}

.config-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--border-color);
}

.config-grid-expanded {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 30px;
}

.config-group {
  background-color: var(--background-color);
  border-radius: 20px;
  padding: 20px;
  border: 1px solid var(--border-color);
}

.config-group-title {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 20px;
  color: var(--accent-color);
}

.config-items {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.config-item {
  padding: 15px;
  border: 1px solid var(--border-color);
  border-radius: 15px;
  transition: all 0.3s ease;
}

.config-item:hover {
  border-color: var(--accent-color);
  background-color: rgba(255, 140, 0, 0.05);
}

.config-label {
  display: flex;
  align-items: center;
  font-weight: 600;
  cursor: pointer;
  position: relative;
  padding-left: 30px;
}

.config-label input[type="checkbox"] {
  position: absolute;
  opacity: 0;
  cursor: pointer;
  height: 0;
  width: 0;
}

.checkmark {
  position: absolute;
  left: 0;
  height: 20px;
  width: 20px;
  background-color: var(--background-color);
  border: 2px solid var(--border-color);
  border-radius: 4px;
  transition: all 0.3s ease;
}

.config-label:hover input ~ .checkmark {
  border-color: var(--accent-color);
}

.config-label input:checked ~ .checkmark {
  background-color: var(--accent-color);
  border-color: var(--accent-color);
}

.checkmark:after {
  content: "";
  position: absolute;
  display: none;
}

.config-label input:checked ~ .checkmark:after {
  display: block;
}

.config-label .checkmark:after {
  left: 6px;
  top: 2px;
  width: 6px;
  height: 10px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.config-description {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 8px;
  line-height: 1.4;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  font-size: 14px;
}

.form-description {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 15px;
  line-height: 1.4;
}

.form-input,
.form-select,
.form-textarea {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  font-size: 14px;
  background-color: var(--background-color);
  color: var(--text-color);
  transition: all 0.3s ease;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--accent-color);
  box-shadow: 0 0 0 3px rgba(255, 140, 0, 0.1);
}

.save-btn {
  padding: 10px 20px;
  background-color: var(--accent-color);
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.save-btn:hover {
  background-color: var(--accent-hover);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255, 140, 0, 0.3);
}

.tenant-section {
  margin-bottom: 30px;
}

.table-card {
  background-color: var(--card-bg);
  border-radius: 30px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: background-color 0.3s;
}

.table-controls {
  display: flex;
  gap: 10px;
  align-items: center;
}

.create-tenant-btn,
.create-user-btn,
.create-role-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background-color: var(--accent-color);
  color: white;
  border: none;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.create-tenant-btn:hover,
.create-user-btn:hover,
.create-role-btn:hover {
  background-color: var(--accent-hover);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255, 140, 0, 0.3);
}

.create-tenant-btn svg,
.create-user-btn svg,
.create-role-btn svg {
  width: 16px;
  height: 16px;
}

.filter-btn,
.export-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: 1px solid var(--border-color);
  border-radius: 20px;
  background: var(--background-color);
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
}

.filter-btn:hover,
.export-btn:hover {
  border-color: var(--accent-color);
  color: var(--accent-color);
}

.filter-btn svg,
.export-btn svg {
  width: 16px;
  height: 16px;
}

.table-container {
  overflow-x: auto;
  margin-top: 20px;
}

.tenant-table,
.user-table,
.audit-table,
.role-table {
  width: 100%;
  border-collapse: collapse;
}

.tenant-table th,
.user-table th,
.audit-table th,
.role-table th {
  text-align: left;
  padding: 15px 20px;
  font-weight: 600;
  font-size: 14px;
  color: var(--text-secondary);
  border-bottom: 1px solid var(--border-color);
  background: var(--background-color);
}

.tenant-table td,
.user-table td,
.audit-table td,
.role-table td {
  padding: 15px 20px;
  border-bottom: 1px solid var(--border-color);
  font-size: 14px;
}

.tenant-row,
.user-row,
.audit-row,
.role-row {
  transition: all 0.3s ease;
}

.tenant-row:hover,
.user-row:hover,
.audit-row:hover,
.role-row:hover {
  background-color: rgba(255, 140, 0, 0.05);
}

.tenant-info,
.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.tenant-avatar,
.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background-color: var(--accent-color);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 12px;
}

.tenant-details,
.user-details {
  display: flex;
  flex-direction: column;
}

.tenant-name,
.user-name {
  font-weight: 600;
  margin-bottom: 2px;
}

.tenant-location,
.user-email {
  font-size: 12px;
  color: var(--text-secondary);
}

.user-phone {
  font-size: 11px;
  color: var(--text-secondary);
}

.modules-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.module-badge {
  padding: 2px 8px;
  background-color: rgba(255, 140, 0, 0.1);
  color: var(--accent-color);
  border-radius: 12px;
  font-size: 10px;
  font-weight: 600;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.status-badge.active {
  background: rgba(34, 197, 94, 0.1);
  color: #16a34a;
}

.status-badge.pending {
  background: rgba(245, 158, 11, 0.1);
  color: #d97706;
}

.status-badge.inactive {
  background: rgba(107, 114, 128, 0.1);
  color: #6b7280;
}

.role-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.role-badge.admin {
  background: rgba(239, 68, 68, 0.1);
  color: #dc2626;
}

.role-badge.manager {
  background: rgba(245, 158, 11, 0.1);
  color: #d97706;
}

.role-badge.user {
  background: rgba(59, 130, 246, 0.1);
  color: #2563eb;
}

.role-badge.case {
  background: rgba(34, 197, 94, 0.1);
  color: #16a34a;
}

.role-badge.supervisor {
  background: rgba(168, 85, 247, 0.1);
  color: #7c3aed;
}

.verification-badge {
  padding: 4px 8px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 600;
}

.verification-badge.verified {
  background: rgba(34, 197, 94, 0.1);
  color: #16a34a;
}

.verification-badge.unverified {
  background: rgba(239, 68, 68, 0.1);
  color: #dc2626;
}

.status-indicator-container {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-indicator.active {
  background: var(--success-color);
}

.status-indicator.inactive {
  background: #6b7280;
}

.status-indicator.pending {
  background: var(--pending-color);
}

.session-status {
  display: flex;
  align-items: center;
  gap: 6px;
}

.session-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.session-indicator.active {
  background: #22c55e;
  box-shadow: 0 0 6px rgba(34, 197, 94, 0.5);
}

.session-indicator.offline {
  background: #6b7280;
}

.session-indicator.in {
  background: #f59e0b;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.session-text {
  font-size: 12px;
  font-weight: 500;
}

.queue-position {
  font-size: 10px;
  color: var(--text-secondary);
  font-weight: 600;
}

.user-actions-dropdown {
  position: relative;
  display: inline-block;
}

.user-actions-trigger {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  background: var(--background-color);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  color: var(--text-secondary);
}

.user-actions-trigger:hover {
  background: var(--accent-color);
  color: white;
  transform: scale(1.1);
}

.user-actions-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  min-width: 200px;
  padding: 8px 0;
  margin-top: 4px;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 10px 16px;
  border: none;
  background: none;
  text-align: left;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-color);
  cursor: pointer;
  transition: all 0.3s ease;
}

.dropdown-item:hover:not(:disabled) {
  background: var(--background-color);
}

.dropdown-item:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.dropdown-item svg {
  width: 14px;
  height: 14px;
}

.edit-item:hover:not(:disabled) {
  color: #2563eb;
}

.activate-item:hover:not(:disabled) {
  color: #16a34a;
}

.deactivate-item:hover:not(:disabled) {
  color: #d97706;
}

.verify-item:hover:not(:disabled) {
  color: #16a34a;
}

.session-item:hover:not(:disabled) {
  color: var(--accent-color);
}

.delete-item:hover:not(:disabled) {
  color: #dc2626;
}

.dropdown-divider {
  height: 1px;
  background: var(--border-color);
  margin: 8px 0;
}

.dropdown-submenu {
  position: relative;
}

.submenu-arrow {
  margin-left: auto;
  transition: transform 0.3s ease;
}

.dropdown-submenu:hover .submenu-arrow {
  transform: rotate(90deg);
}

.submenu-content {
  position: absolute;
  left: 100%;
  top: 0;
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  min-width: 160px;
  padding: 4px 0;
  margin-left: 4px;
}

.submenu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 8px 12px;
  border: none;
  background: none;
  text-align: left;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-color);
  cursor: pointer;
  transition: all 0.3s ease;
}

.submenu-item:hover:not(:disabled) {
  background: var(--background-color);
}

.submenu-item:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.submenu-item svg {
  width: 12px;
  height: 12px;
}

.start-session-item:hover:not(:disabled) {
  color: #16a34a;
}

.end-session-item:hover:not(:disabled) {
  color: #dc2626;
}

.join-queue-item:hover:not(:disabled) {
  color: #f59e0b;
}

.leave-queue-item:hover:not(:disabled) {
  color: #6b7280;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border: none;
  border-radius: 15px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.action-btn:hover {
  transform: translateY(-1px);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.edit-btn {
  background: rgba(59, 130, 246, 0.1);
  color: #2563eb;
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.edit-btn:hover:not(:disabled) {
  background: #2563eb;
  color: white;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.impersonate-btn {
  background: rgba(168, 85, 247, 0.1);
  color: #7c3aed;
  border: 1px solid rgba(168, 85, 247, 0.2);
}

.impersonate-btn:hover:not(:disabled) {
  background: #7c3aed;
  color: white;
  box-shadow: 0 4px 12px rgba(168, 85, 247, 0.3);
}

.activate-btn {
  background: rgba(34, 197, 94, 0.1);
  color: #16a34a;
  border: 1px solid rgba(34, 197, 94, 0.2);
}

.activate-btn:hover:not(:disabled) {
  background: #16a34a;
  color: white;
  box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);
}

.deactivate-btn {
  background: rgba(245, 158, 11, 0.1);
  color: #d97706;
  border: 1px solid rgba(245, 158, 11, 0.2);
}

.deactivate-btn:hover:not(:disabled) {
  background: #d97706;
  color: white;
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}

.verify-btn {
  background: rgba(34, 197, 94, 0.1);
  color: #16a34a;
  border: 1px solid rgba(34, 197, 94, 0.2);
}

.verify-btn:hover:not(:disabled) {
  background: #16a34a;
  color: white;
  box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);
}

.delete-btn {
  background: rgba(239, 68, 68, 0.1);
  color: #dc2626;
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.delete-btn:hover:not(:disabled) {
  background: #dc2626;
  color: white;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

.action-btn svg {
  width: 14px;
  height: 14px;
}

.audit-section {
  margin-bottom: 30px;
}

.audit-filters-horizontal {
  display: flex;
  gap: 15px;
  align-items: center;
  flex-wrap: wrap;
}

.user-filters-horizontal {
  display: flex;
  gap: 15px;
  align-items: center;
  flex-wrap: wrap;
  margin-bottom: 20px;
  padding: 20px;
  background-color: var(--background-color);
  border-radius: 15px;
  border: 1px solid var(--border-color);
}

.filter-select,
.filter-input {
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--card-bg);
  color: var(--text-color);
  font-size: 14px;
  transition: all 0.3s ease;
  min-width: 150px;
}

.filter-select:focus,
.filter-input:focus {
  outline: none;
  border-color: var(--accent-color);
  box-shadow: 0 0 0 3px rgba(255, 140, 0, 0.1);
}

.action-badge {
  padding: 4px 8px;
  border-radius: 8px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
}

.action-badge.create {
  background: rgba(34, 197, 94, 0.1);
  color: #16a34a;
}

.action-badge.update {
  background: rgba(245, 158, 11, 0.1);
  color: #d97706;
}

.action-badge.delete {
  background: rgba(239, 68, 68, 0.1);
  color: #dc2626;
}

.action-badge.login {
  background: rgba(59, 130, 246, 0.1);
  color: #2563eb;
}

.action-badge.logout {
  background: rgba(107, 114, 128, 0.1);
  color: #6b7280;
}

.object-id {
  font-family: monospace;
  font-size: 12px;
  color: var(--text-secondary);
}

.details-btn {
  padding: 6px;
  border: none;
  background: rgba(59, 130, 246, 0.1);
  color: #2563eb;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.details-btn:hover {
  background: #2563eb;
  color: white;
}

.category-section {
  margin-bottom: 30px;
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 30px;
  padding: 30px;
  background-color: var(--card-bg);
  border-radius: 30px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.category-title-section {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.category-icon {
  width: 60px;
  height: 60px;
  background-color: var(--accent-color);
  border-radius: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.category-icon svg {
  width: 24px;
  height: 24px;
  color: white;
}

.category-title-content {
  flex: 1;
}

.category-main-title {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 8px;
}

.category-description {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.5;
  max-width: 600px;
}

.category-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.download-template-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background-color: var(--background-color);
  color: var(--text-color);
  border: 1px solid var(--border-color);
  border-radius: 25px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.download-template-btn:hover {
  border-color: var(--success-color);
  color: var(--success-color);
  transform: translateY(-1px);
}

.download-template-btn svg {
  width: 16px;
  height: 16px;
}

.upload-csv-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background-color: var(--background-color);
  color: var(--text-color);
  border: 1px solid var(--border-color);
  border-radius: 25px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.upload-csv-btn:hover {
  border-color: var(--accent-color);
  color: var(--accent-color);
  transform: translateY(-1px);
}

.upload-csv-btn svg {
  width: 16px;
  height: 16px;
}

.new-category-btn {
  padding: 12px 24px;
  background-color: var(--accent-color);
  color: white;
  border: none;
  border-radius: 25px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.new-category-btn:hover {
  background-color: var(--accent-hover);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255, 140, 0, 0.3);
}

.categories-list {
  background-color: var(--card-bg);
  border-radius: 30px;
  padding: 30px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.category-list-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px 0;
  border-bottom: 1px solid var(--border-color);
  transition: all 0.3s ease;
}

.category-list-item:last-child {
  border-bottom: none;
}

.category-list-item:hover {
  background-color: rgba(255, 140, 0, 0.05);
  border-radius: 15px;
  padding: 15px;
  margin: 0 -15px;
}

.category-bullet {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--text-color);
  flex-shrink: 0;
}

.category-item-content {
  flex: 1;
}

.category-item-name {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 4px;
}

.category-item-description {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.4;
}

.category-item-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.category-edit-btn {
  padding: 8px;
  border: none;
  background: rgba(59, 130, 246, 0.1);
  color: #2563eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.category-edit-btn:hover {
  background: #2563eb;
  color: white;
}

.category-toggle-btn {
  padding: 6px 12px;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--background-color);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.category-toggle-btn.active {
  background: var(--success-color);
  color: white;
  border-color: var(--success-color);
}

.category-toggle-btn:not(.active) {
  color: var(--text-secondary);
}

.category-toggle-btn:hover {
  border-color: var(--accent-color);
}

.category-pagination {
  display: flex;
  justify-content: center;
  padding: 20px;
}

.pagination-info {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
}

.user-management-section,
.role-management-section {
  margin-bottom: 30px;
}

.role-info {
  display: flex;
  flex-direction: column;
}

.role-name {
  font-weight: 600;
  margin-bottom: 4px;
}

.role-description {
  font-size: 12px;
  color: var(--text-secondary);
}

.permissions-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.permission-badge {
  padding: 2px 8px;
  background-color: rgba(59, 130, 246, 0.1);
  color: #2563eb;
  border-radius: 12px;
  font-size: 10px;
  font-weight: 600;
}

.permission-count {
  padding: 2px 8px;
  background-color: rgba(107, 114, 128, 0.1);
  color: #6b7280;
  border-radius: 12px;
  font-size: 10px;
  font-weight: 600;
}

.notifications-section {
  margin-bottom: 30px;
}

.notifications-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
}

.notification-card {
  background-color: var(--card-bg);
  border-radius: 30px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: background-color 0.3s;
}

.notification-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.notifications-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.notification-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 15px;
  border: 1px solid var(--border-color);
  border-radius: 15px;
  transition: all 0.3s ease;
}

.notification-item:hover {
  border-color: var(--accent-color);
  background-color: rgba(255, 140, 0, 0.05);
}

.notification-content {
  flex: 1;
}

.notification-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.notification-title {
  font-weight: 600;
  margin: 0;
}

.severity-badge {
  padding: 4px 8px;
  border-radius: 8px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
}

.severity-badge.info {
  background: rgba(59, 130, 246, 0.1);
  color: #2563eb;
}

.severity-badge.warning {
  background: rgba(245, 158, 11, 0.1);
  color: #d97706;
}

.severity-badge.error {
  background: rgba(239, 68, 68, 0.1);
  color: #dc2626;
}

.severity-badge.critical {
  background: rgba(147, 51, 234, 0.1);
  color: #9333ea;
}

.notification-message {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 8px;
  line-height: 1.4;
}

.notification-meta {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: var(--text-secondary);
}

.notification-actions {
  display: flex;
  gap: 8px;
  margin-left: 15px;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: var(--card-bg);
  border-radius: 20px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 20px 0 20px;
  margin-bottom: 20px;
}

.modal-header h2 {
  font-size: 20px;
  font-weight: 700;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  color: var(--text-secondary);
  transition: all 0.3s ease;
}

.close-btn:hover {
  background-color: var(--background-color);
  color: var(--text-color);
}

.modal-body {
  padding: 0 20px;
}

.modal-footer {
  display: flex;
  gap: 12px;
  padding: 20px;
  justify-content: flex-end;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.form-grid .form-group.full-width {
  grid-column: 1 / -1;
}

.checkbox-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
}

.permissions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
  max-height: 200px;
  overflow-y: auto;
  padding: 10px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  font-weight: 500;
  cursor: pointer;
  position: relative;
  padding-left: 25px;
  font-size: 14px;
}

.checkbox-label input[type="checkbox"] {
  position: absolute;
  opacity: 0;
  cursor: pointer;
  height: 0;
  width: 0;
}

.checkbox-label .checkmark {
  position: absolute;
  left: 0;
  height: 16px;
  width: 16px;
  background-color: var(--background-color);
  border: 2px solid var(--border-color);
  border-radius: 3px;
  transition: all 0.3s ease;
}

.checkbox-label:hover input ~ .checkmark {
  border-color: var(--accent-color);
}

.checkbox-label input:checked ~ .checkmark {
  background-color: var(--accent-color);
  border-color: var(--accent-color);
}

.checkbox-label .checkmark:after {
  left: 4px;
  top: 1px;
  width: 4px;
  height: 8px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.csv-upload-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.upload-instructions {
  background-color: var(--background-color);
  padding: 15px;
  border-radius: 10px;
  border: 1px solid var(--border-color);
}

.upload-instructions h4 {
  margin-bottom: 10px;
  color: var(--accent-color);
}

.upload-instructions ul {
  margin-left: 20px;
  color: var(--text-secondary);
}

.upload-instructions li {
  margin-bottom: 5px;
}

.file-upload-area {
  border: 2px dashed var(--border-color);
  border-radius: 15px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.file-upload-area:hover {
  border-color: var(--accent-color);
  background-color: rgba(255, 140, 0, 0.05);
}

.upload-icon {
  margin-bottom: 15px;
  color: var(--accent-color);
}

.upload-text {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 5px;
}

.upload-subtext {
  font-size: 14px;
  color: var(--text-secondary);
}

.csv-preview {
  background-color: var(--background-color);
  padding: 15px;
  border-radius: 10px;
  border: 1px solid var(--border-color);
}

.csv-preview h4 {
  margin-bottom: 15px;
  color: var(--accent-color);
}

.preview-table {
  overflow-x: auto;
  margin-bottom: 10px;
}

.preview-table table {
  width: 100%;
  border-collapse: collapse;
}

.preview-table th,
.preview-table td {
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  text-align: left;
}

.preview-table th {
  background-color: var(--card-bg);
  font-weight: 600;
}

.preview-info {
  font-size: 12px;
  color: var(--text-secondary);
  font-style: italic;
}

.cancel-btn {
  padding: 10px 20px;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--background-color);
  color: var(--text-color);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.cancel-btn:hover {
  border-color: var(--accent-color);
  color: var(--accent-color);
}

.submit-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 12px;
  background: var(--accent-color);
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.submit-btn:hover {
  background: var(--accent-hover);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255, 140, 0, 0.3);
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.audit-details {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.detail-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-group label {
  font-weight: 600;
  font-size: 12px;
  color: var(--text-secondary);
  text-transform: uppercase;
}

.metadata-display {
  background: var(--background-color);
  padding: 12px;
  border-radius: 8px;
  font-size: 12px;
  color: var(--text-color);
  overflow-x: auto;
  white-space: pre-wrap;
}

.mobile-menu-btn {
  display: none;
  position: fixed;
  top: 20px;
  left: 20px;
  z-index: 101;
  background-color: #ffffff;
  color: #333333;
  border: none;
  border-radius: 50%;
  width: 44px;
  height: 44px;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.mobile-menu-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
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

  .dashboard-grid {
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 15px;
  }

  .expand-btn {
    display: none !important;
  }

  .management-grid,
  .notifications-grid {
    grid-template-columns: 1fr;
  }

  .quick-actions-grid {
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  }

  .config-grid-expanded {
    grid-template-columns: 1fr;
  }

  .audit-filters-horizontal,
  .user-filters-horizontal {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-select,
  .filter-input {
    min-width: auto;
  }
}

@media (max-width: 768px) {
  body {
    overflow: auto;
  }

  .header {
    padding: 15px;
  }

  .main-scroll-content {
    padding: 15px;
  }

  .dashboard-grid {
    grid-template-columns: 1fr;
  }

  .quick-actions-grid {
    grid-template-columns: 1fr;
  }

  .page-title {
    font-size: 24px;
  }

  .action-buttons {
    flex-direction: column;
  }

  .action-btn {
    justify-content: center;
  }

  .modal-content {
    width: 95%;
    margin: 20px;
  }

  .table-controls {
    flex-direction: column;
    align-items: stretch;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .checkbox-grid,
  .permissions-grid {
    grid-template-columns: 1fr;
  }

  .category-header {
    flex-direction: column;
    gap: 20px;
    align-items: flex-start;
  }

  .category-title-section {
    flex-direction: column;
    gap: 15px;
  }

  .category-actions {
    flex-direction: column;
    width: 100%;
  }

  .download-template-btn,
  .upload-csv-btn,
  .new-category-btn {
    width: 100%;
    justify-content: center;
  }

  .category-icon {
    width: 50px;
    height: 50px;
  }

  .category-main-title {
    font-size: 20px;
  }

  .user-actions-menu {
    right: auto;
    left: 0;
  }

  .submenu-content {
    left: auto;
    right: 100%;
    margin-left: 0;
    margin-right: 4px;
  }
}

@media (min-width: 1025px) {
  .mobile-menu-btn {
    display: none;
  }
}

@media (max-width: 1024px) {
  .sidebar-content {
    overflow-y: auto;
    overflow-x: hidden;
    scrollbar-width: none;
    -ms-overflow-style: none;
  }

  .sidebar-content::-webkit-scrollbar {
    display: none;
  }

  .nav-section {
    margin-bottom: 10px;
  }

  .nav-item {
    padding: 8px 10px;
    margin-bottom: 3px;
    min-height: 40px;
  }

  .nav-icon {
    width: 30px;
    height: 30px;
    margin-right: 10px;
  }

  .nav-icon svg {
    width: 16px;
    height: 16px;
  }

  .nav-text {
    font-size: 13px;
  }

  .sidebar-bottom {
    padding: 0 15px 15px 15px;
  }

  .user-avatar {
    width: 40px;
    height: 40px;
  }

  .user-avatar svg {
    width: 22px;
    height: 22px;
  }

  .status {
    font-size: 11px;
    margin-bottom: 10px;
  }

  .button-container {
    gap: 8px;
  }

  .logout-btn {
    padding: 8px 12px;
    font-size: 12px;
  }
}

@media (max-width: 1024px) and (max-height: 700px) {
  .sidebar-header {
    padding: 15px;
  }

  .logo {
    width: 45px;
    height: 45px;
  }

  .logo img {
    width: 28px;
    height: 28px;
  }

  .nav-item {
    padding: 6px 8px;
    margin-bottom: 2px;
    min-height: 36px;
  }

  .nav-icon {
    width: 28px;
    height: 28px;
    margin-right: 8px;
  }

  .nav-icon svg {
    width: 15px;
    height: 15px;
  }

  .nav-text {
    font-size: 12px;
  }

  .user-avatar {
    width: 36px;
    height: 36px;
  }

  .user-avatar svg {
    width: 20px;
    height: 20px;
  }

  .status {
    font-size: 10px;
    margin-bottom: 8px;
  }

  .button-container {
    gap: 6px;
  }

  .logout-btn {
    padding: 6px 10px;
    font-size: 11px;
  }
}

@media (max-width: 768px) and (max-height: 600px) {
  .sidebar-header {
    padding: 12px;
  }

  .logo {
    width: 40px;
    height: 40px;
  }

  .logo img {
    width: 25px;
    height: 25px;
  }

  .nav-item {
    padding: 5px 6px;
    margin-bottom: 1px;
    min-height: 32px;
  }

  .nav-icon {
    width: 24px;
    height: 24px;
    margin-right: 6px;
  }

  .nav-icon svg {
    width: 13px;
    height: 13px;
  }

  .nav-text {
    font-size: 11px;
  }

  .sidebar-bottom {
    padding: 0 12px 12px 12px;
  }

  .user-avatar {
    width: 32px;
    height: 32px;
  }

  .user-avatar svg {
    width: 18px;
    height: 18px;
  }

  .status {
    font-size: 9px;
    margin-bottom: 6px;
  }

  .status-dot {
    width: 4px;
    height: 4px;
    margin-right: 3px;
  }

  .button-container {
    gap: 5px;
  }

  .logout-btn {
    padding: 5px 8px;
    font-size: 10px;
  }
}

.main-content, .dashboard-container, .dashboard-card, .status-badge, .view-tab, .dashboard-table {
  background: var(--content-bg);
  color: var(--text-color);
  border-color: var(--border-color);
}

.status-badge, .view-tab.active {
  background: var(--accent-color) !important;
  color: #fff !important;
  border-color: var(--accent-color) !important;
}
</style>

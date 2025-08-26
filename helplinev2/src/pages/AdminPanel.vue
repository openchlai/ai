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
            <img src="/placeholder.svg?height=30&width=30" alt="Organization Logo">
          </div>
        </div>
        <div class="org-info" v-if="!isSidebarCollapsed">
          <h3 class="org-name">{{ currentOrganization.name }}</h3>
          <p class="org-location">{{ currentOrganization.location }}</p>
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
        
        <a href="/cases" class="nav-item" :class="{ active: activeTab === 'cases' }" @click.prevent="setActiveTab('cases')">
          <div class="nav-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" stroke-width="2"/>
              <polyline points="14,2 14,8 20,8" stroke="currentColor" stroke-width="2"/>
              <line x1="16" y1="13" x2="8" y2="13" stroke="currentColor" stroke-width="2"/>
              <line x1="16" y1="17" x2="8" y2="17" stroke="currentColor" stroke-width="2"/>
            </svg>
          </div>
          <div class="nav-text">Case Management</div>
        </a>

        <a href="/users" class="nav-item" :class="{ active: activeTab === 'users' }" @click.prevent="setActiveTab('users')">
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

        <a href="/reports" class="nav-item" :class="{ active: activeTab === 'reports' }" @click.prevent="setActiveTab('reports')">
          <div class="nav-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M3 3v18h18" stroke="currentColor" stroke-width="2"/>
              <path d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3" stroke="currentColor" stroke-width="2"/>
            </svg>
          </div>
          <div class="nav-text">Reports & Analytics</div>
        </a>

        <a href="/ai-assistant" class="nav-item" :class="{ active: activeTab === 'ai-assistant' }" @click.prevent="setActiveTab('ai-assistant')">
          <div class="nav-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L2 7l10 5 10-5-10-5z" stroke="currentColor" stroke-width="2"/>
              <path d="M2 17l10 5 10-5" stroke="currentColor" stroke-width="2"/>
              <path d="M2 12l10 5 10-5" stroke="currentColor" stroke-width="2"/>
            </svg>
          </div>
          <div class="nav-text">AI Assistant</div>
        </a>

        <a href="/categories" class="nav-item" :class="{ active: activeTab === 'categories' }" @click.prevent="setActiveTab('categories')">
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

        <a href="/workflows" class="nav-item" :class="{ active: activeTab === 'workflows' }" @click.prevent="setActiveTab('workflows')">
          <div class="nav-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" stroke="currentColor" stroke-width="2"/>
              <polyline points="7.5,4.21 12,6.81 16.5,4.21" stroke="currentColor" stroke-width="2"/>
              <polyline points="7.5,19.79 7.5,14.6 3,12" stroke="currentColor" stroke-width="2"/>
              <polyline points="21,12 16.5,14.6 16.5,19.79" stroke="currentColor" stroke-width="2"/>
              <polyline points="12,22.81 12,17" stroke="currentColor" stroke-width="2"/>
            </svg>
          </div>
          <div class="nav-text">Workflows</div>
        </a>

        <a href="/settings" class="nav-item" :class="{ active: activeTab === 'settings' }" @click.prevent="setActiveTab('settings')">
          <div class="nav-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/>
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" stroke="currentColor" stroke-width="2"/>
            </svg>
          </div>
          <div class="nav-text">Settings</div>
        </a>
      </div>
      
      <div class="sidebar-bottom">
        <div class="user-profile">
          <a href="/profile" class="user-avatar" @click.prevent="navigateTo('/profile')">
            <span>{{ currentUser.initials }}</span>
          </a>
        </div>
        
        <div class="user-info" v-if="!isSidebarCollapsed">
          <div class="user-name">{{ currentUser.name }}</div>
          <div class="user-role">{{ currentUser.role }}</div>
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
      <div class="header-actions">
        <button class="notification-btn" @click="toggleNotifications">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" stroke="currentColor" stroke-width="2"/>
            <path d="M13.73 21a2 2 0 0 1-3.46 0" stroke="currentColor" stroke-width="2"/>
          </svg>
          <span class="notification-badge" v-if="unreadNotifications > 0">{{ unreadNotifications }}</span>
        </button>
        <button class="theme-toggle" @click="toggleTheme" id="theme-toggle">
          <svg v-if="currentTheme === 'dark'" id="moon-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <svg v-else id="sun-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
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
          <span id="theme-text">{{ currentTheme === 'dark' ? 'Light' : 'Dark' }}</span>
        </button>
      </div>
    </div>

    <div class="main-scroll-content">
      <!-- Dashboard -->
      <div v-if="activeTab === 'dashboard'">
        <div class="dashboard-grid">
          <div class="dashboard-card">
            <div class="card-header">
              <div class="card-title">Total Cases</div>
              <div class="card-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="white" stroke-width="2"/>
                  <polyline points="14,2 14,8 20,8" stroke="white" stroke-width="2"/>
                </svg>
              </div>
            </div>
            <div class="card-value">{{ dashboardStats.totalCases }}</div>
            <div class="card-subtitle">+{{ dashboardStats.newCasesThisMonth }} this month</div>
          </div>
          
          <div class="dashboard-card">
            <div class="card-header">
              <div class="card-title">Active Cases</div>
              <div class="card-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="12" cy="12" r="10" stroke="white" stroke-width="2"/>
                  <polyline points="12,6 12,12 16,14" stroke="white" stroke-width="2"/>
                </svg>
              </div>
            </div>
            <div class="card-value">{{ dashboardStats.activeCases }}</div>
            <div class="card-subtitle">{{ dashboardStats.urgentCases }} urgent cases</div>
          </div>
          
          <div class="dashboard-card">
            <div class="card-header">
              <div class="card-title">Team Members</div>
              <div class="card-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" stroke="white" stroke-width="2"/>
                  <circle cx="9" cy="7" r="4" stroke="white" stroke-width="2"/>
                  <path d="M23 21v-2a4 4 0 0 0-3-3.87" stroke="white" stroke-width="2"/>
                  <path d="M16 3.13a4 4 0 0 1 0 7.75" stroke="white" stroke-width="2"/>
                </svg>
              </div>
            </div>
            <div class="card-value">{{ dashboardStats.teamMembers }}</div>
            <div class="card-subtitle">{{ dashboardStats.activeUsers }} online now</div>
          </div>
          
          <div class="dashboard-card">
            <div class="card-header">
              <div class="card-title">Resolution Rate</div>
              <div class="card-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" stroke="white" stroke-width="2"/>
                  <polyline points="22,4 12,14.01 9,11.01" stroke="white" stroke-width="2"/>
                </svg>
              </div>
            </div>
            <div class="card-value">{{ dashboardStats.resolutionRate }}%</div>
            <div class="card-subtitle">+5.2% from last month</div>
          </div>
        </div>

        <div class="dashboard-content-grid">
          <div class="recent-cases-card">
            <div class="card-header">
              <div class="section-title">Recent Cases</div>
              <button class="view-all-btn" @click="setActiveTab('cases')">View All</button>
            </div>
            <div class="cases-list">
              <div v-for="case_ in recentCases" :key="case_.id" class="case-item" @click="viewCase(case_.id)">
                <div class="case-priority" :class="case_.priority.toLowerCase()"></div>
                <div class="case-info">
                  <h4 class="case-title">{{ case_.title }}</h4>
                  <p class="case-details">{{ case_.caseNumber }} • {{ case_.assignedTo }}</p>
                  <p class="case-date">{{ formatDate(case_.createdAt) }}</p>
                </div>
                <div class="case-status">
                  <span class="status-badge" :class="case_.status.toLowerCase()">{{ case_.status }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="quick-actions-card">
            <div class="card-header">
              <div class="section-title">Quick Actions</div>
            </div>
            <div class="quick-actions-list">
              <button class="quick-action-btn" @click="showCreateCaseModal = true">
                <div class="action-icon">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2"/>
                  </svg>
                </div>
                <span>Create New Case</span>
              </button>
              <button class="quick-action-btn" @click="showInviteUserModal = true">
                <div class="action-icon">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" stroke="currentColor" stroke-width="2"/>
                    <circle cx="9" cy="7" r="4" stroke="currentColor" stroke-width="2"/>
                    <path d="M19 8v6M16 11h6" stroke="currentColor" stroke-width="2"/>
                  </svg>
                </div>
                <span>Invite Team Member</span>
              </button>
              <button class="quick-action-btn" @click="setActiveTab('reports')">
                <div class="action-icon">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M3 3v18h18" stroke="currentColor" stroke-width="2"/>
                    <path d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3" stroke="currentColor" stroke-width="2"/>
                  </svg>
                </div>
                <span>Generate Report</span>
              </button>
              <button class="quick-action-btn" @click="setActiveTab('ai-assistant')">
                <div class="action-icon">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2L2 7l10 5 10-5-10-5z" stroke="currentColor" stroke-width="2"/>
                    <path d="M2 17l10 5 10-5" stroke="currentColor" stroke-width="2"/>
                  </svg>
                </div>
                <span>AI Assistant</span>
              </button>
            </div>
          </div>
        </div>

        <div class="analytics-section">
          <div class="analytics-card">
            <div class="card-header">
              <div class="section-title">Case Analytics</div>
              <select class="time-filter" v-model="selectedTimeframe">
                <option value="7days">Last 7 days</option>
                <option value="30days">Last 30 days</option>
                <option value="90days">Last 90 days</option>
              </select>
            </div>
            <div class="chart-container">
              <div class="chart-placeholder">
                <div class="chart-bars">
                  <div class="chart-bar" style="height: 60%" data-label="Mon"></div>
                  <div class="chart-bar" style="height: 80%" data-label="Tue"></div>
                  <div class="chart-bar" style="height: 45%" data-label="Wed"></div>
                  <div class="chart-bar" style="height: 90%" data-label="Thu"></div>
                  <div class="chart-bar" style="height: 70%" data-label="Fri"></div>
                  <div class="chart-bar" style="height: 85%" data-label="Sat"></div>
                  <div class="chart-bar" style="height: 55%" data-label="Sun"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Case Management -->
      <div v-if="activeTab === 'cases'">
        <div class="table-card">
          <div class="card-header">
            <div class="section-title">Case Management</div>
            <div class="table-controls">
              <button class="create-case-btn" @click="showCreateCaseModal = true">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2"/>
                </svg>
                New Case
              </button>
              <button class="filter-btn" @click="toggleCaseFilters">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <polygon points="22,3 2,3 10,12.46 10,19 14,21 14,12.46" stroke="currentColor" stroke-width="2"/>
                </svg>
                Filter
              </button>
              <button class="export-btn" @click="exportCases">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" stroke="currentColor" stroke-width="2"/>
                  <polyline points="7,10 12,15 17,10" stroke="currentColor" stroke-width="2"/>
                  <line x1="12" y1="15" x2="12" y2="3" stroke="currentColor" stroke-width="2"/>
                </svg>
                Export
              </button>
            </div>
          </div>

          <div class="case-filters" v-if="showCaseFilters">
            <div class="filters-row">
              <select v-model="caseFilters.status" class="filter-select">
                <option value="">All Status</option>
                <option value="Open">Open</option>
                <option value="In Progress">In Progress</option>
                <option value="Resolved">Resolved</option>
                <option value="Closed">Closed</option>
              </select>
              <select v-model="caseFilters.priority" class="filter-select">
                <option value="">All Priority</option>
                <option value="Low">Low</option>
                <option value="Medium">Medium</option>
                <option value="High">High</option>
                <option value="Critical">Critical</option>
              </select>
              <select v-model="caseFilters.assignedTo" class="filter-select">
                <option value="">All Assignees</option>
                <option v-for="user in teamMembers" :key="user.id" :value="user.name">
                  {{ user.name }}
                </option>
              </select>
              <input type="text" v-model="caseFilters.search" class="filter-input" placeholder="Search cases...">
            </div>
          </div>

          <div class="table-container">
            <table class="cases-table">
              <thead>
                <tr>
                  <th>Case</th>
                  <th>Priority</th>
                  <th>Status</th>
                  <th>Assigned To</th>
                  <th>Category</th>
                  <th>Created</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="case_ in filteredCases" :key="case_.id" class="case-row">
                  <td class="case-cell">
                    <div class="case-info">
                      <div class="case-number">{{ case_.caseNumber }}</div>
                      <div class="case-title">{{ case_.title }}</div>
                      <div class="case-client">{{ case_.clientName }}</div>
                    </div>
                  </td>
                  <td>
                    <span class="priority-badge" :class="case_.priority.toLowerCase()">
                      {{ case_.priority }}
                    </span>
                  </td>
                  <td>
                    <span class="status-badge" :class="case_.status.toLowerCase().replace(' ', '-')">
                      {{ case_.status }}
                    </span>
                  </td>
                  <td>
                    <div class="assignee-info">
                      <div class="assignee-avatar">
                        <span>{{ getInitials(case_.assignedTo) }}</span>
                      </div>
                      <span>{{ case_.assignedTo }}</span>
                    </div>
                  </td>
                  <td>{{ case_.category }}</td>
                  <td>{{ formatDate(case_.createdAt) }}</td>
                  <td>
                    <div class="case-actions">
                      <button class="action-btn view-btn" @click="viewCase(case_.id)">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" stroke="currentColor" stroke-width="2"/>
                          <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/>
                        </svg>
                        View
                      </button>
                      <button class="action-btn edit-btn" @click="editCase(case_.id)">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" stroke="currentColor" stroke-width="2"/>
                          <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" stroke="currentColor" stroke-width="2"/>
                        </svg>
                        Edit
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- User Management -->
      <div v-if="activeTab === 'users'">
        <div class="table-card">
          <div class="card-header">
            <div class="section-title">Team Management</div>
            <div class="table-controls">
              <button class="create-user-btn" @click="showInviteUserModal = true">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2"/>
                </svg>
                Invite User
              </button>
              <button class="export-btn" @click="exportUsers">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" stroke="currentColor" stroke-width="2"/>
                  <polyline points="7,10 12,15 17,10" stroke="currentColor" stroke-width="2"/>
                  <line x1="12" y1="15" x2="12" y2="3" stroke="currentColor" stroke-width="2"/>
                </svg>
                Export
              </button>
            </div>
          </div>

          <div class="user-filters">
            <div class="filters-row">
              <select v-model="userFilters.role" class="filter-select">
                <option value="">All Roles</option>
                <option value="Admin">Admin</option>
                <option value="Manager">Manager</option>
                <option value="Case Worker">Case Worker</option>
                <option value="Supervisor">Supervisor</option>
              </select>
              <select v-model="userFilters.status" class="filter-select">
                <option value="">All Status</option>
                <option value="Active">Active</option>
                <option value="Inactive">Inactive</option>
                <option value="Pending">Pending</option>
              </select>
              <input type="text" v-model="userFilters.search" class="filter-input" placeholder="Search users...">
            </div>
          </div>

          <div class="table-container">
            <table class="users-table">
              <thead>
                <tr>
                  <th>User</th>
                  <th>Role</th>
                  <th>Status</th>
                  <th>Cases Assigned</th>
                  <th>Last Active</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in filteredUsers" :key="user.id" class="user-row">
                  <td class="user-cell">
                    <div class="user-info">
                      <div class="user-avatar">
                        <span>{{ getInitials(user.name) }}</span>
                      </div>
                      <div class="user-details">
                        <div class="user-name">{{ user.name }}</div>
                        <div class="user-email">{{ user.email }}</div>
                      </div>
                    </div>
                  </td>
                  <td>
                    <div class="role-cell">
                      <select 
                        v-if="editingRole === user.id" 
                        v-model="user.role" 
                        @change="saveUserRole(user.id, user.role)"
                        @blur="editingRole = null"
                        class="role-select"
                      >
                        <option value="Admin">Admin</option>
                        <option value="Manager">Manager</option>
                        <option value="Case Worker">Case Worker</option>
                        <option value="Supervisor">Supervisor</option>
                      </select>
                      <div v-else class="role-display" @click="startEditingRole(user.id)">
                        <span class="role-badge" :class="user.role.toLowerCase().replace(' ', '-')">{{ user.role }}</span>
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="edit-icon">
                          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" stroke="currentColor" stroke-width="2"/>
                          <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" stroke="currentColor" stroke-width="2"/>
                        </svg>
                      </div>
                    </div>
                  </td>
                  <td>
                    <span class="status-badge" :class="user.status.toLowerCase()">
                      {{ user.status }}
                    </span>
                  </td>
                  <td>{{ user.casesAssigned }}</td>
                  <td>{{ user.lastActive }}</td>
                  <td>
                    <div class="user-actions">
                      <button class="action-btn edit-btn" @click="editUser(user.id)">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" stroke="currentColor" stroke-width="2"/>
                          <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" stroke="currentColor" stroke-width="2"/>
                        </svg>
                        Edit
                      </button>
                      <button class="action-btn deactivate-btn" @click="toggleUserStatus(user.id)" :class="{ 'activate-btn': user.status === 'Inactive' }">
                        <svg v-if="user.status === 'Active'" width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                          <line x1="15" y1="9" x2="9" y2="15" stroke="currentColor" stroke-width="2"/>
                          <line x1="9" y1="9" x2="15" y2="15" stroke="currentColor" stroke-width="2"/>
                        </svg>
                        <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" stroke="currentColor" stroke-width="2"/>
                          <polyline points="22,4 12,14.01 9,11.01" stroke="currentColor" stroke-width="2"/>
                        </svg>
                        {{ user.status === 'Active' ? 'Deactivate' : 'Activate' }}
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Reports & Analytics -->
      <div v-if="activeTab === 'reports'">
        <div class="reports-grid">
          <div class="report-card">
            <div class="card-header">
              <div class="section-title">Case Statistics</div>
              <button class="generate-btn" @click="generateReport('cases')">Generate Report</button>
            </div>
            <div class="report-content">
              <div class="stats-grid">
                <div class="stat-item">
                  <div class="stat-value">{{ reportStats.totalCases }}</div>
                  <div class="stat-label">Total Cases</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ reportStats.resolvedCases }}</div>
                  <div class="stat-label">Resolved</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ reportStats.avgResolutionTime }}</div>
                  <div class="stat-label">Avg Resolution Time</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ reportStats.satisfactionRate }}%</div>
                  <div class="stat-label">Satisfaction Rate</div>
                </div>
              </div>
            </div>
          </div>

          <div class="report-card">
            <div class="card-header">
              <div class="section-title">Team Performance</div>
              <button class="generate-btn" @click="generateReport('team')">Generate Report</button>
            </div>
            <div class="report-content">
              <div class="performance-list">
                <div v-for="member in teamPerformance" :key="member.id" class="performance-item">
                  <div class="member-info">
                    <div class="member-avatar">
                      <span>{{ getInitials(member.name) }}</span>
                    </div>
                    <div class="member-details">
                      <div class="member-name">{{ member.name }}</div>
                      <div class="member-role">{{ member.role }}</div>
                    </div>
                  </div>
                  <div class="performance-stats">
                    <div class="stat">
                      <span class="stat-value">{{ member.casesResolved }}</span>
                      <span class="stat-label">Resolved</span>
                    </div>
                    <div class="stat">
                      <span class="stat-value">{{ member.avgTime }}</span>
                      <span class="stat-label">Avg Time</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="charts-section">
          <div class="chart-card">
            <div class="card-header">
              <div class="section-title">Case Trends</div>
              <select class="time-filter" v-model="reportTimeframe">
                <option value="30days">Last 30 days</option>
                <option value="90days">Last 90 days</option>
                <option value="6months">Last 6 months</option>
                <option value="1year">Last year</option>
              </select>
            </div>
            <div class="chart-container">
              <div class="trend-chart">
                <div class="chart-placeholder">
                  <div class="trend-line"></div>
                  <div class="chart-points">
                    <div class="chart-point" style="left: 10%; bottom: 30%"></div>
                    <div class="chart-point" style="left: 25%; bottom: 45%"></div>
                    <div class="chart-point" style="left: 40%; bottom: 60%"></div>
                    <div class="chart-point" style="left: 55%; bottom: 40%"></div>
                    <div class="chart-point" style="left: 70%; bottom: 75%"></div>
                    <div class="chart-point" style="left: 85%; bottom: 65%"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- AI Assistant -->
      <div v-if="activeTab === 'ai-assistant'">
        <div class="ai-assistant-container">
          <div class="ai-chat-card">
            <div class="card-header">
              <div class="section-title">AI Assistant</div>
              <div class="ai-status">
                <div class="status-dot active"></div>
                <span>Online</span>
              </div>
            </div>
            <div class="chat-container">
              <div class="chat-messages" ref="chatMessages">
                <div v-for="message in chatMessages" :key="message.id" class="message" :class="message.type">
                  <div class="message-avatar" v-if="message.type === 'ai'">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M12 2L2 7l10 5 10-5-10-5z" stroke="currentColor" stroke-width="2"/>
                      <path d="M2 17l10 5 10-5" stroke="currentColor" stroke-width="2"/>
                    </svg>
                  </div>
                  <div class="message-content">
                    <div class="message-text">{{ message.text }}</div>
                    <div class="message-time">{{ formatTime(message.timestamp) }}</div>
                  </div>
                </div>
              </div>
              <div class="chat-input-container">
                <input 
                  type="text" 
                  v-model="newMessage" 
                  @keyup.enter="sendMessage"
                  placeholder="Ask me anything about your cases, analytics, or organization..."
                  class="chat-input"
                >
                <button @click="sendMessage" class="send-btn" :disabled="!newMessage.trim()">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <line x1="22" y1="2" x2="11" y2="13" stroke="currentColor" stroke-width="2"/>
                    <polygon points="22,2 15,22 11,13 2,9" stroke="currentColor" stroke-width="2"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <div class="ai-suggestions-card">
            <div class="card-header">
              <div class="section-title">Suggested Actions</div>
            </div>
            <div class="suggestions-list">
              <button v-for="suggestion in aiSuggestions" :key="suggestion.id" class="suggestion-btn" @click="applySuggestion(suggestion)">
                <div class="suggestion-icon">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M9 11l3 3L22 4" stroke="currentColor" stroke-width="2"/>
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

      <!-- Categories -->
      <div v-if="activeTab === 'categories'">
        <div class="categories-container">
          <div class="categories-header">
            <div class="section-title">Case Categories</div>
            <button class="create-category-btn" @click="showCreateCategoryModal = true">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2"/>
              </svg>
              Add Category
            </button>
          </div>

          <div class="categories-grid">
            <div v-for="category in categories" :key="category.id" class="category-card">
              <div class="category-header">
                <div class="category-icon" :style="{ backgroundColor: category.color }">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <rect x="3" y="3" width="7" height="7" stroke="white" stroke-width="2"/>
                    <rect x="14" y="3" width="7" height="7" stroke="white" stroke-width="2"/>
                    <rect x="14" y="14" width="7" height="7" stroke="white" stroke-width="2"/>
                    <rect x="3" y="14" width="7" height="7" stroke="white" stroke-width="2"/>
                  </svg>
                </div>
                <div class="category-actions">
                  <button class="action-btn edit-btn" @click="editCategory(category.id)">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" stroke="currentColor" stroke-width="2"/>
                      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" stroke="currentColor" stroke-width="2"/>
                    </svg>
                  </button>
                </div>
              </div>
              <div class="category-content">
                <h3 class="category-name">{{ category.name }}</h3>
                <p class="category-description">{{ category.description }}</p>
                <div class="category-stats">
                  <span class="case-count">{{ category.caseCount }} cases</span>
                  <span class="status-indicator" :class="{ active: category.isActive }">
                    {{ category.isActive ? 'Active' : 'Inactive' }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Workflows -->
      <div v-if="activeTab === 'workflows'">
        <div class="workflows-container">
          <div class="workflows-header">
            <div class="section-title">Workflow Management</div>
            <button class="create-workflow-btn" @click="showCreateWorkflowModal = true">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2"/>
              </svg>
              Create Workflow
            </button>
          </div>

          <div class="workflows-list">
            <div v-for="workflow in workflows" :key="workflow.id" class="workflow-card">
              <div class="workflow-header">
                <div class="workflow-info">
                  <h3 class="workflow-name">{{ workflow.name }}</h3>
                  <p class="workflow-description">{{ workflow.description }}</p>
                </div>
                <div class="workflow-status">
                  <span class="status-badge" :class="workflow.status.toLowerCase()">{{ workflow.status }}</span>
                </div>
              </div>
              <div class="workflow-steps">
                <div v-for="(step, index) in workflow.steps" :key="index" class="workflow-step">
                  <div class="step-number">{{ index + 1 }}</div>
                  <div class="step-content">
                    <div class="step-name">{{ step.name }}</div>
                    <div class="step-assignee">{{ step.assignee }}</div>
                  </div>
                  <div class="step-connector" v-if="index < workflow.steps.length - 1"></div>
                </div>
              </div>
              <div class="workflow-actions">
                <button class="action-btn edit-btn" @click="editWorkflow(workflow.id)">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" stroke="currentColor" stroke-width="2"/>
                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" stroke="currentColor" stroke-width="2"/>
                  </svg>
                  Edit
                </button>
                <button class="action-btn toggle-btn" @click="toggleWorkflow(workflow.id)" :class="{ active: workflow.status === 'Active' }">
                  {{ workflow.status === 'Active' ? 'Deactivate' : 'Activate' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Settings -->
      <div v-if="activeTab === 'settings'">
        <div class="settings-container">
          <div class="settings-header">
            <div class="section-title">Organization Settings</div>
            <button class="save-settings-btn" @click="saveSettings">Save Changes</button>
          </div>

          <div class="settings-grid">
            <div class="settings-group">
              <h3 class="group-title">Organization Information</h3>
              <div class="settings-items">
                <div class="setting-item">
                  <label class="setting-label">Organization Name</label>
                  <input type="text" v-model="settings.organizationName" class="setting-input">
                </div>
                <div class="setting-item">
                  <label class="setting-label">Location</label>
                  <input type="text" v-model="settings.location" class="setting-input">
                </div>
                <div class="setting-item">
                  <label class="setting-label">Contact Email</label>
                  <input type="email" v-model="settings.contactEmail" class="setting-input">
                </div>
                <div class="setting-item">
                  <label class="setting-label">Phone Number</label>
                  <input type="tel" v-model="settings.phoneNumber" class="setting-input">
                </div>
              </div>
            </div>

            <div class="settings-group">
              <h3 class="group-title">Case Management</h3>
              <div class="settings-items">
                <div class="setting-item">
                  <label class="setting-label">Case Number Prefix</label>
                  <input type="text" v-model="settings.casePrefix" class="setting-input">
                </div>
                <div class="setting-item">
                  <label class="setting-label">Auto-assign Cases</label>
                  <label class="toggle-switch">
                    <input type="checkbox" v-model="settings.autoAssign">
                    <span class="toggle-slider"></span>
                  </label>
                </div>
                <div class="setting-item">
                  <label class="setting-label">Default Priority</label>
                  <select v-model="settings.defaultPriority" class="setting-select">
                    <option value="Low">Low</option>
                    <option value="Medium">Medium</option>
                    <option value="High">High</option>
                    <option value="Critical">Critical</option>
                  </select>
                </div>
              </div>
            </div>

            <div class="settings-group">
              <h3 class="group-title">Notifications</h3>
              <div class="settings-items">
                <div class="setting-item">
                  <label class="setting-label">Email Notifications</label>
                  <label class="toggle-switch">
                    <input type="checkbox" v-model="settings.emailNotifications">
                    <span class="toggle-slider"></span>
                  </label>
                </div>
                <div class="setting-item">
                  <label class="setting-label">Case Assignment Alerts</label>
                  <label class="toggle-switch">
                    <input type="checkbox" v-model="settings.assignmentAlerts">
                    <span class="toggle-slider"></span>
                  </label>
                </div>
                <div class="setting-item">
                  <label class="setting-label">Deadline Reminders</label>
                  <label class="toggle-switch">
                    <input type="checkbox" v-model="settings.deadlineReminders">
                    <span class="toggle-slider"></span>
                  </label>
                </div>
              </div>
            </div>

            <div class="settings-group">
              <h3 class="group-title">Security</h3>
              <div class="settings-items">
                <div class="setting-item">
                  <label class="setting-label">Two-Factor Authentication</label>
                  <label class="toggle-switch">
                    <input type="checkbox" v-model="settings.twoFactorAuth">
                    <span class="toggle-slider"></span>
                  </label>
                </div>
                <div class="setting-item">
                  <label class="setting-label">Session Timeout (minutes)</label>
                  <input type="number" v-model="settings.sessionTimeout" class="setting-input" min="5" max="480">
                </div>
                <div class="setting-item">
                  <label class="setting-label">Password Requirements</label>
                  <select v-model="settings.passwordStrength" class="setting-select">
                    <option value="basic">Basic</option>
                    <option value="medium">Medium</option>
                    <option value="strong">Strong</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Modals -->
      <div class="modal" v-if="showCreateCaseModal">
        <div class="modal-content">
          <div class="modal-header">
            <h2>Create New Case</h2>
            <button class="close-btn" @click="showCreateCaseModal = false">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="2"/>
                <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="2"/>
              </svg>
            </button>
          </div>
          <div class="modal-body">
            <div class="form-grid">
              <div class="form-group">
                <label class="form-label">Case Title *</label>
                <input type="text" v-model="newCase.title" class="form-input" placeholder="Enter case title">
              </div>
              <div class="form-group">
                <label class="form-label">Client Name *</label>
                <input type="text" v-model="newCase.clientName" class="form-input" placeholder="Enter client name">
              </div>
              <div class="form-group">
                <label class="form-label">Category *</label>
                <select v-model="newCase.category" class="form-select">
                  <option value="">Select category</option>
                  <option v-for="category in categories" :key="category.id" :value="category.name">
                    {{ category.name }}
                  </option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Priority *</label>
                <select v-model="newCase.priority" class="form-select">
                  <option value="Low">Low</option>
                  <option value="Medium">Medium</option>
                  <option value="High">High</option>
                  <option value="Critical">Critical</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Assign To</label>
                <select v-model="newCase.assignedTo" class="form-select">
                  <option value="">Unassigned</option>
                  <option v-for="member in teamMembers" :key="member.id" :value="member.name">
                    {{ member.name }}
                  </option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Due Date</label>
                <input type="date" v-model="newCase.dueDate" class="form-input">
              </div>
              <div class="form-group full-width">
                <label class="form-label">Description</label>
                <textarea v-model="newCase.description" class="form-textarea" placeholder="Enter case description" rows="4"></textarea>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="cancel-btn" @click="showCreateCaseModal = false">Cancel</button>
            <button class="submit-btn" @click="createCase">Create Case</button>
          </div>
        </div>
      </div>

      <div class="modal" v-if="showInviteUserModal">
        <div class="modal-content">
          <div class="modal-header">
            <h2>Invite Team Member</h2>
            <button class="close-btn" @click="showInviteUserModal = false">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="2"/>
                <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="2"/>
              </svg>
            </button>
          </div>
          <div class="modal-body">
            <div class="form-grid">
              <div class="form-group">
                <label class="form-label">Full Name *</label>
                <input type="text" v-model="newUser.name" class="form-input" placeholder="Enter full name">
              </div>
              <div class="form-group">
                <label class="form-label">Email Address *</label>
                <input type="email" v-model="newUser.email" class="form-input" placeholder="Enter email address">
              </div>
              <div class="form-group">
                <label class="form-label">Role *</label>
                <select v-model="newUser.role" class="form-select">
                  <option value="">Select role</option>
                  <option value="Admin">Admin</option>
                  <option value="Manager">Manager</option>
                  <option value="Case Worker">Case Worker</option>
                  <option value="Supervisor">Supervisor</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Phone Number</label>
                <input type="tel" v-model="newUser.phone" class="form-input" placeholder="Enter phone number">
              </div>
              <div class="form-group full-width">
                <label class="form-label">Welcome Message</label>
                <textarea v-model="newUser.welcomeMessage" class="form-textarea" placeholder="Optional welcome message" rows="3"></textarea>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="cancel-btn" @click="showInviteUserModal = false">Cancel</button>
            <button class="submit-btn" @click="inviteUser">Send Invitation</button>
          </div>
        </div>
      </div>

      <div class="modal" v-if="showCreateCategoryModal">
        <div class="modal-content">
          <div class="modal-header">
            <h2>Create Category</h2>
            <button class="close-btn" @click="showCreateCategoryModal = false">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="2"/>
                <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="2"/>
              </svg>
            </button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label">Category Name *</label>
              <input type="text" v-model="newCategory.name" class="form-input" placeholder="Enter category name">
            </div>
            <div class="form-group">
              <label class="form-label">Description</label>
              <textarea v-model="newCategory.description" class="form-textarea" placeholder="Enter description" rows="3"></textarea>
            </div>
            <div class="form-group">
              <label class="form-label">Color</label>
              <div class="color-picker">
                <div v-for="color in categoryColors" :key="color" 
                     class="color-option" 
                     :style="{ backgroundColor: color }"
                     :class="{ selected: newCategory.color === color }"
                     @click="newCategory.color = color">
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="cancel-btn" @click="showCreateCategoryModal = false">Cancel</button>
            <button class="submit-btn" @click="createCategory">Create Category</button>
          </div>
        </div>
      </div>

      <div class="modal" v-if="showCreateWorkflowModal">
        <div class="modal-content">
          <div class="modal-header">
            <h2>Create Workflow</h2>
            <button class="close-btn" @click="showCreateWorkflowModal = false">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="2"/>
                <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="2"/>
              </svg>
            </button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label">Workflow Name *</label>
              <input type="text" v-model="newWorkflow.name" class="form-input" placeholder="Enter workflow name">
            </div>
            <div class="form-group">
              <label class="form-label">Description</label>
              <textarea v-model="newWorkflow.description" class="form-textarea" placeholder="Enter description" rows="3"></textarea>
            </div>
            <div class="form-group">
              <label class="form-label">Workflow Steps</label>
              <div class="workflow-steps-builder">
                <div v-for="(step, index) in newWorkflow.steps" :key="index" class="step-builder">
                  <div class="step-number">{{ index + 1 }}</div>
                  <input type="text" v-model="step.name" class="step-input" placeholder="Step name">
                  <select v-model="step.assignee" class="step-select">
                    <option value="">Auto-assign</option>
                    <option v-for="member in teamMembers" :key="member.id" :value="member.name">
                      {{ member.name }}
                    </option>
                  </select>
                  <button class="remove-step-btn" @click="removeWorkflowStep(index)" v-if="newWorkflow.steps.length > 1">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="2"/>
                      <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="2"/>
                    </svg>
                  </button>
                </div>
                <button class="add-step-btn" @click="addWorkflowStep">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2"/>
                  </svg>
                  Add Step
                </button>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="cancel-btn" @click="showCreateWorkflowModal = false">Cancel</button>
            <button class="submit-btn" @click="createWorkflow">Create Workflow</button>
          </div>
        </div>
      </div>

      <!-- Notification Panel -->
      <div class="notification-panel" :class="{ open: showNotifications }" v-if="showNotifications">
        <div class="notification-header">
          <h3>Notifications</h3>
          <button class="close-notifications" @click="showNotifications = false">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="2"/>
              <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="2"/>
            </svg>
          </button>
        </div>
        <div class="notifications-list">
          <div v-for="notification in notifications" :key="notification.id" class="notification-item" :class="{ unread: !notification.read }">
            <div class="notification-icon" :class="notification.type">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path v-if="notification.type === 'case'" d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" stroke-width="2"/>
                <path v-else-if="notification.type === 'user'" d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" stroke="currentColor" stroke-width="2"/>
                <circle v-else-if="notification.type === 'user'" cx="9" cy="7" r="4" stroke="currentColor" stroke-width="2"/>
                <path v-else d="M22 11.08V12a10 10 0 1 1-5.93-9.14" stroke="currentColor" stroke-width="2"/>
              </svg>
            </div>
            <div class="notification-content">
              <div class="notification-title">{{ notification.title }}</div>
              <div class="notification-message">{{ notification.message }}</div>
              <div class="notification-time">{{ formatTime(notification.timestamp) }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from 'vue'

const isSidebarCollapsed = ref(false)
const mobileOpen = ref(false)
const currentTheme = ref('dark')
const activeTab = ref('dashboard')
const selectedTimeframe = ref('7days')
const reportTimeframe = ref('30days')
const showNotifications = ref(false)
const unreadNotifications = ref(3)

const showCreateCaseModal = ref(false)
const showInviteUserModal = ref(false)
const showCreateCategoryModal = ref(false)
const showCreateWorkflowModal = ref(false)
const showCaseFilters = ref(false)
const editingRole = ref(null)

const newMessage = ref('')
const chatMessages = ref([
  {
    id: 1,
    type: 'ai',
    text: 'Hello! I\'m your AI assistant. I can help you with case analysis, generate reports, and answer questions about your organization.',
    timestamp: new Date()
  }
])

const currentOrganization = ref({
  name: 'Children First Kenya',
  location: 'Nairobi, Kenya'
})

const currentUser = ref({
  name: 'Sarah Johnson',
  role: 'Admin',
  initials: 'SJ'
})

const dashboardStats = ref({
  totalCases: 247,
  newCasesThisMonth: 23,
  activeCases: 89,
  urgentCases: 12,
  teamMembers: 15,
  activeUsers: 8,
  resolutionRate: 87.3
})

const reportStats = ref({
  totalCases: 247,
  resolvedCases: 198,
  avgResolutionTime: '12 days',
  satisfactionRate: 94
})

const recentCases = ref([
  {
    id: 1,
    caseNumber: 'CASE-2024-001',
    title: 'Child Protection Assessment',
    assignedTo: 'John Doe',
    status: 'In Progress',
    priority: 'High',
    createdAt: '2024-06-05T10:30:00Z'
  },
  {
    id: 2,
    caseNumber: 'CASE-2024-002',
    title: 'Family Reunification',
    assignedTo: 'Jane Smith',
    status: 'Open',
    priority: 'Medium',
    createdAt: '2024-06-04T14:15:00Z'
  },
  {
    id: 3,
    caseNumber: 'CASE-2024-003',
    title: 'Emergency Shelter Placement',
    assignedTo: 'Mike Wilson',
    status: 'Resolved',
    priority: 'Critical',
    createdAt: '2024-06-03T09:45:00Z'
  }
])

const cases = ref([
  {
    id: 1,
    caseNumber: 'CASE-2024-001',
    title: 'Child Protection Assessment',
    clientName: 'Anonymous Client',
    assignedTo: 'John Doe',
    status: 'In Progress',
    priority: 'High',
    category: 'Child Protection',
    createdAt: '2024-06-05T10:30:00Z'
  },
  {
    id: 2,
    caseNumber: 'CASE-2024-002',
    title: 'Family Reunification',
    clientName: 'Maria Santos',
    assignedTo: 'Jane Smith',
    status: 'Open',
    priority: 'Medium',
    category: 'Family Services',
    createdAt: '2024-06-04T14:15:00Z'
  },
  {
    id: 3,
    caseNumber: 'CASE-2024-003',
    title: 'Emergency Shelter Placement',
    clientName: 'David Johnson',
    assignedTo: 'Mike Wilson',
    status: 'Resolved',
    priority: 'Critical',
    category: 'Emergency Services',
    createdAt: '2024-06-03T09:45:00Z'
  }
])

const teamMembers = ref([
  {
    id: 1,
    name: 'John Doe',
    email: 'john.doe@cfk.org',
    role: 'Case Worker',
    status: 'Active',
    casesAssigned: 12,
    lastActive: '2 hours ago'
  },
  {
    id: 2,
    name: 'Jane Smith',
    email: 'jane.smith@cfk.org',
    role: 'Manager',
    status: 'Active',
    casesAssigned: 8,
    lastActive: '1 hour ago'
  },
  {
    id: 3,
    name: 'Mike Wilson',
    email: 'mike.wilson@cfk.org',
    role: 'Supervisor',
    status: 'Active',
    casesAssigned: 15,
    lastActive: '30 minutes ago'
  }
])

const teamPerformance = ref([
  {
    id: 1,
    name: 'John Doe',
    role: 'Case Worker',
    casesResolved: 23,
    avgTime: '8 days'
  },
  {
    id: 2,
    name: 'Jane Smith',
    role: 'Manager',
    casesResolved: 18,
    avgTime: '6 days'
  },
  {
    id: 3,
    name: 'Mike Wilson',
    role: 'Supervisor',
    casesResolved: 31,
    avgTime: '10 days'
  }
])

const categories = ref([
  {
    id: 1,
    name: 'Child Protection',
    description: 'Cases involving child safety and welfare',
    color: '#FF6B6B',
    caseCount: 45,
    isActive: true
  },
  {
    id: 2,
    name: 'Family Services',
    description: 'Family support and reunification services',
    color: '#4ECDC4',
    caseCount: 32,
    isActive: true
  },
  {
    id: 3,
    name: 'Emergency Services',
    description: 'Urgent intervention and emergency placement',
    color: '#45B7D1',
    caseCount: 18,
    isActive: true
  },
  {
    id: 4,
    name: 'Community Outreach',
    description: 'Community education and prevention programs',
    color: '#96CEB4',
    caseCount: 12,
    isActive: true
  }
])

const workflows = ref([
  {
    id: 1,
    name: 'Child Protection Assessment',
    description: 'Standard workflow for child protection cases',
    status: 'Active',
    steps: [
      { name: 'Initial Assessment', assignee: 'Case Worker' },
      { name: 'Safety Planning', assignee: 'Supervisor' },
      { name: 'Service Planning', assignee: 'Manager' },
      { name: 'Case Review', assignee: 'Supervisor' }
    ]
  },
  {
    id: 2,
    name: 'Emergency Response',
    description: 'Rapid response workflow for emergency cases',
    status: 'Active',
    steps: [
      { name: 'Emergency Assessment', assignee: 'On-call Worker' },
      { name: 'Safety Intervention', assignee: 'Supervisor' },
      { name: 'Placement Decision', assignee: 'Manager' }
    ]
  }
])

const notifications = ref([
  {
    id: 1,
    type: 'case',
    title: 'New Case Assigned',
    message: 'CASE-2024-004 has been assigned to you',
    timestamp: new Date(Date.now() - 30 * 60 * 1000),
    read: false
  },
  {
    id: 2,
    type: 'user',
    title: 'Team Member Joined',
    message: 'Alex Rodriguez has joined your organization',
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
    read: false
  },
  {
    id: 3,
    type: 'system',
    title: 'Report Generated',
    message: 'Monthly case report is ready for review',
    timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000),
    read: true
  }
])

const aiSuggestions = ref([
  {
    id: 1,
    title: 'Review Overdue Cases',
    description: 'You have 3 cases that are past their due date'
  },
  {
    id: 2,
    title: 'Team Workload Balance',
    description: 'Consider redistributing cases for better balance'
  },
  {
    id: 3,
    title: 'Generate Monthly Report',
    description: 'Monthly performance report is due tomorrow'
  }
])

const categoryColors = ref([
  '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F'
])

const newCase = ref({
  title: '',
  clientName: '',
  category: '',
  priority: 'Medium',
  assignedTo: '',
  dueDate: '',
  description: ''
})

const newUser = ref({
  name: '',
  email: '',
  role: '',
  phone: '',
  welcomeMessage: ''
})

const newCategory = ref({
  name: '',
  description: '',
  color: '#FF6B6B'
})

const newWorkflow = ref({
  name: '',
  description: '',
  steps: [
    { name: '', assignee: '' }
  ]
})

const caseFilters = ref({
  status: '',
  priority: '',
  assignedTo: '',
  search: ''
})

const userFilters = ref({
  role: '',
  status: '',
  search: ''
})

const settings = ref({
  organizationName: 'Children First Kenya',
  location: 'Nairobi, Kenya',
  contactEmail: 'admin@cfk.org',
  phoneNumber: '+254 700 123 456',
  casePrefix: 'CASE',
  autoAssign: true,
  defaultPriority: 'Medium',
  emailNotifications: true,
  assignmentAlerts: true,
  deadlineReminders: true,
  twoFactorAuth: false,
  sessionTimeout: 60,
  passwordStrength: 'medium'
})

const filteredCases = computed(() => {
  return cases.value.filter(case_ => {
    if (caseFilters.value.status && case_.status !== caseFilters.value.status) return false
    if (caseFilters.value.priority && case_.priority !== caseFilters.value.priority) return false
    if (caseFilters.value.assignedTo && case_.assignedTo !== caseFilters.value.assignedTo) return false
    if (caseFilters.value.search) {
      const search = caseFilters.value.search.toLowerCase()
      if (!case_.title.toLowerCase().includes(search) && 
          !case_.caseNumber.toLowerCase().includes(search) &&
          !case_.clientName.toLowerCase().includes(search)) return false
    }
    return true
  })
})

const filteredUsers = computed(() => {
  return teamMembers.value.filter(user => {
    if (userFilters.value.role && user.role !== userFilters.value.role) return false
    if (userFilters.value.status && user.status !== userFilters.value.status) return false
    if (userFilters.value.search) {
      const search = userFilters.value.search.toLowerCase()
      if (!user.name.toLowerCase().includes(search) && 
          !user.email.toLowerCase().includes(search)) return false
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
    'dashboard': 'Dashboard',
    'cases': 'Case Management',
    'users': 'Team Management',
    'reports': 'Reports & Analytics',
    'ai-assistant': 'AI Assistant',
    'categories': 'Categories',
    'workflows': 'Workflows',
    'settings': 'Settings'
  }
  return titles[activeTab.value] || 'Dashboard'
}

const toggleNotifications = () => {
  showNotifications.value = !showNotifications.value
  if (showNotifications.value) {
    unreadNotifications.value = 0
  }
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
    root.setAttribute('data-theme', 'light')
  } else {
    root.style.setProperty('--background-color', '#0a0a0a')
    root.style.setProperty('--sidebar-bg', '#111')
    root.style.setProperty('--content-bg', '#222')
    root.style.setProperty('--text-color', '#fff')
    root.style.setProperty('--text-secondary', '#aaa')
    root.style.setProperty('--border-color', '#333')
    root.style.setProperty('--card-bg', '#222')
    root.setAttribute('data-theme', 'dark')
  }

  root.style.setProperty('--accent-color', '#FF8C00')
  root.style.setProperty('--accent-hover', '#FF7700')
  root.style.setProperty('--danger-color', '#ff3b30')
  root.style.setProperty('--success-color', '#4CAF50')
  root.style.setProperty('--pending-color', '#FFA500')
  root.style.setProperty('--warning-color', '#FF9500')
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

const navigateTo = (path) => {
  console.log(`Navigating to: ${path}`)
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString()
}

const formatTime = (date) => {
  return new Date(date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const getInitials = (name) => {
  return name.split(' ').map(n => n[0]).join('')
}

const startEditingRole = async (userId) => {
  editingRole.value = userId
  await nextTick()
}

const saveUserRole = (userId, newRole) => {
  const userIndex = teamMembers.value.findIndex(user => user.id === userId)
  if (userIndex !== -1) {
    const oldRole = teamMembers.value[userIndex].role
    teamMembers.value[userIndex].role = newRole
    alert(`User role updated from ${oldRole} to ${newRole}`)
  }
  editingRole.value = null
}

const toggleCaseFilters = () => {
  showCaseFilters.value = !showCaseFilters.value
}

const viewCase = (caseId) => {
  console.log('View case:', caseId)
  alert(`View case ${caseId} functionality would be implemented here.`)
}

const editCase = (caseId) => {
  console.log('Edit case:', caseId)
  alert(`Edit case ${caseId} functionality would be implemented here.`)
}

const editUser = (userId) => {
  console.log('Edit user:', userId)
  alert(`Edit user ${userId} functionality would be implemented here.`)
}

const toggleUserStatus = (userId) => {
  const userIndex = teamMembers.value.findIndex(user => user.id === userId)
  if (userIndex !== -1) {
    const user = teamMembers.value[userIndex]
    user.status = user.status === 'Active' ? 'Inactive' : 'Active'
    alert(`User ${user.name} has been ${user.status.toLowerCase()}.`)
  }
}

const createCase = () => {
  if (!newCase.value.title || !newCase.value.clientName || !newCase.value.category) {
    alert('Please fill in all required fields.')
    return
  }

  const caseNumber = `CASE-${new Date().getFullYear()}-${String(cases.value.length + 1).padStart(3, '0')}`
  const newCaseObj = {
    id: cases.value.length + 1,
    caseNumber,
    title: newCase.value.title,
    clientName: newCase.value.clientName,
    assignedTo: newCase.value.assignedTo || 'Unassigned',
    status: 'Open',
    priority: newCase.value.priority,
    category: newCase.value.category,
    createdAt: new Date().toISOString()
  }

  cases.value.unshift(newCaseObj)
  recentCases.value.unshift(newCaseObj)

  newCase.value = {
    title: '',
    clientName: '',
    category: '',
    priority: 'Medium',
    assignedTo: '',
    dueDate: '',
    description: ''
  }

  showCreateCaseModal.value = false
  alert('Case created successfully!')
}

const inviteUser = () => {
  if (!newUser.value.name || !newUser.value.email || !newUser.value.role) {
    alert('Please fill in all required fields.')
    return
  }

  const newUserObj = {
    id: teamMembers.value.length + 1,
    name: newUser.value.name,
    email: newUser.value.email,
    role: newUser.value.role,
    status: 'Pending',
    casesAssigned: 0,
    lastActive: 'Never'
  }

  teamMembers.value.unshift(newUserObj)

  newUser.value = {
    name: '',
    email: '',
    role: '',
    phone: '',
    welcomeMessage: ''
  }

  showInviteUserModal.value = false
  alert('Invitation sent successfully!')
}

const createCategory = () => {
  if (!newCategory.value.name) {
    alert('Please fill in all required fields.')
    return
  }

  const newCategoryObj = {
    id: categories.value.length + 1,
    name: newCategory.value.name,
    description: newCategory.value.description,
    color: newCategory.value.color,
    caseCount: 0,
    isActive: true
  }

  categories.value.push(newCategoryObj)

  newCategory.value = {
    name: '',
    description: '',
    color: '#FF6B6B'
  }

  showCreateCategoryModal.value = false
  alert('Category created successfully!')
}

const editCategory = (categoryId) => {
  console.log('Edit category:', categoryId)
  alert(`Edit category ${categoryId} functionality would be implemented here.`)
}

const addWorkflowStep = () => {
  newWorkflow.value.steps.push({ name: '', assignee: '' })
}

const removeWorkflowStep = (index) => {
  newWorkflow.value.steps.splice(index, 1)
}

const createWorkflow = () => {
  if (!newWorkflow.value.name || newWorkflow.value.steps.some(step => !step.name)) {
    alert('Please fill in all required fields.')
    return
  }

  const newWorkflowObj = {
    id: workflows.value.length + 1,
    name: newWorkflow.value.name,
    description: newWorkflow.value.description,
    status: 'Active',
    steps: [...newWorkflow.value.steps]
  }

  workflows.value.push(newWorkflowObj)

  newWorkflow.value = {
    name: '',
    description: '',
    steps: [{ name: '', assignee: '' }]
  }

  showCreateWorkflowModal.value = false
  alert('Workflow created successfully!')
}

const editWorkflow = (workflowId) => {
  console.log('Edit workflow:', workflowId)
  alert(`Edit workflow ${workflowId} functionality would be implemented here.`)
}

const toggleWorkflow = (workflowId) => {
  const workflowIndex = workflows.value.findIndex(w => w.id === workflowId)
  if (workflowIndex !== -1) {
    const workflow = workflows.value[workflowIndex]
    workflow.status = workflow.status === 'Active' ? 'Inactive' : 'Active'
    alert(`Workflow ${workflow.name} has been ${workflow.status.toLowerCase()}.`)
  }
}

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

const generateReport = (type) => {
  console.log('Generate report:', type)
  alert(`Generating ${type} report...`)
}

const exportCases = () => {
  alert('Exporting cases data...')
}

const exportUsers = () => {
  alert('Exporting users data...')
}

const saveSettings = () => {
  console.log('Saving settings:', settings.value)
  alert('Settings saved successfully!')
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

    // Close notifications when clicking outside
    if (showNotifications.value && !event.target.closest('.notification-panel') && !event.target.closest('.notification-btn')) {
      showNotifications.value = false
    }

    // Close role editing when clicking outside
    if (!event.target.closest('.role-cell')) {
      editingRole.value = null
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
  display: flex;
  min-height: 100vh;
  transition: background-color 0.3s, color 0.3s;
  overflow: hidden;
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

.logo img {
  width: 30px;
  height: 30px;
  object-fit: contain;
}

.org-info {
  text-align: center;
}

.org-name {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 4px;
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
  background-color: rgba(255, 140, 0, 0.2);
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
  background-color: var(--success-color);
  margin-right: 6px;
}

.status-dot.active {
  background-color: var(--success-color);
  box-shadow: 0 0 6px rgba(76, 175, 80, 0.5);
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

.header-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

.notification-btn {
  position: relative;
  background-color: var(--content-bg);
  color: var(--text-color);
  border: 1px solid var(--border-color);
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
  background-color: var(--danger-color);
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

.dashboard-content-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  margin-bottom: 30px;
}

.recent-cases-card,
.quick-actions-card {
  background-color: var(--card-bg);
  border-radius: 30px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: background-color 0.3s;
}

.section-title {
  font-size: 20px;
  font-weight: 700;
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

.cases-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-top: 20px;
}

.case-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  border: 1px solid var(--border-color);
  border-radius: 20px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.case-item:hover {
  border-color: var(--accent-color);
  background-color: rgba(255, 140, 0, 0.05);
}

.case-priority {
  width: 4px;
  height: 40px;
  border-radius: 2px;
}

.case-priority.low {
  background-color: var(--success-color);
}

.case-priority.medium {
  background-color: var(--warning-color);
}

.case-priority.high {
  background-color: var(--pending-color);
}

.case-priority.critical {
  background-color: var(--danger-color);
}

.case-info {
  flex: 1;
}

.case-title {
  font-weight: 600;
  margin-bottom: 4px;
}

.case-details {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 2px;
}

.case-date {
  font-size: 11px;
  color: var(--text-secondary);
}

.case-status {
  display: flex;
  align-items: center;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.status-badge.open {
  background: rgba(59, 130, 246, 0.1);
  color: #2563eb;
}

.status-badge.in-progress {
  background: rgba(245, 158, 11, 0.1);
  color: #d97706;
}

.status-badge.resolved {
  background: rgba(34, 197, 94, 0.1);
  color: #16a34a;
}

.status-badge.closed {
  background: rgba(107, 114, 128, 0.1);
  color: #6b7280;
}

.status-badge.active {
  background: rgba(34, 197, 94, 0.1);
  color: #16a34a;
}

.status-badge.inactive {
  background: rgba(107, 114, 128, 0.1);
  color: #6b7280;
}

.status-badge.pending {
  background: rgba(245, 158, 11, 0.1);
  color: #d97706;
}

.quick-actions-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 20px;
}

.quick-action-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: var(--background-color);
  border: 1px solid var(--border-color);
  border-radius: 15px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-color);
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: left;
  width: 100%;
}

.quick-action-btn:hover {
  border-color: var(--accent-color);
  background-color: rgba(255, 140, 0, 0.05);
}

.action-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background-color: rgba(255, 140, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--accent-color);
}

.analytics-section {
  margin-bottom: 30px;
}

.analytics-card,
.chart-card {
  background-color: var(--card-bg);
  border-radius: 30px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: background-color 0.3s;
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

.chart-container {
  margin-top: 20px;
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

.table-card {
  background-color: var(--card-bg);
  border-radius: 30px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: background-color 0.3s;
  margin-bottom: 30px;
}

.table-controls {
  display: flex;
  gap: 10px;
  align-items: center;
}

.create-case-btn,
.create-user-btn,
.create-category-btn,
.create-workflow-btn {
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

.create-case-btn:hover,
.create-user-btn:hover,
.create-category-btn:hover,
.create-workflow-btn:hover {
  background-color: var(--accent-hover);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255, 140, 0, 0.3);
}

.filter-btn,
.export-btn,
.generate-btn {
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
.export-btn:hover,
.generate-btn:hover {
  border-color: var(--accent-color);
  color: var(--accent-color);
}

.case-filters,
.user-filters {
  padding: 20px;
  background-color: var(--background-color);
  border-radius: 15px;
  margin: 20px 0;
  border: 1px solid var(--border-color);
}

.filters-row {
  display: flex;
  gap: 15px;
  align-items: center;
  flex-wrap: wrap;
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

.table-container {
  overflow-x: auto;
  margin-top: 20px;
}

.cases-table,
.users-table {
  width: 100%;
  border-collapse: collapse;
}

.cases-table th,
.users-table th {
  text-align: left;
  padding: 15px 20px;
  font-weight: 600;
  font-size: 14px;
  color: var(--text-secondary);
  border-bottom: 1px solid var(--border-color);
  background: var(--background-color);
}

.cases-table td,
.users-table td {
  padding: 15px 20px;
  border-bottom: 1px solid var(--border-color);
  font-size: 14px;
}

.case-row,
.user-row {
  transition: all 0.3s ease;
}

.case-row:hover,
.user-row:hover {
  background-color: rgba(255, 140, 0, 0.05);
}

.case-cell,
.user-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.case-info,
.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.case-number {
  font-family: monospace;
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 2px;
}

.case-title,
.user-name {
  font-weight: 600;
  margin-bottom: 2px;
}

.case-client,
.user-email {
  font-size: 12px;
  color: var(--text-secondary);
}

.user-details {
  display: flex;
  flex-direction: column;
}

.priority-badge {
  padding: 4px 8px;
  border-radius: 8px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
}

.priority-badge.low {
  background: rgba(34, 197, 94, 0.1);
  color: #16a34a;
}

.priority-badge.medium {
  background: rgba(245, 158, 11, 0.1);
  color: #d97706;
}

.priority-badge.high {
  background: rgba(255, 149, 0, 0.1);
  color: #ff9500;
}

.priority-badge.critical {
  background: rgba(239, 68, 68, 0.1);
  color: #dc2626;
}

.assignee-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.assignee-avatar,
.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: var(--accent-color);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 12px;
}

.role-cell {
  position: relative;
}

.role-display {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.role-display:hover {
  background-color: rgba(255, 140, 0, 0.1);
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

.role-badge.case-worker {
  background: rgba(34, 197, 94, 0.1);
  color: #16a34a;
}

.role-badge.supervisor {
  background: rgba(168, 85, 247, 0.1);
  color: #7c3aed;
}

.edit-icon {
  opacity: 0.6;
  transition: opacity 0.3s ease;
}

.role-display:hover .edit-icon {
  opacity: 1;
}

.role-select {
  padding: 6px 12px;
  border: 2px solid var(--accent-color);
  border-radius: 8px;
  background-color: var(--card-bg);
  color: var(--text-color);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  outline: none;
  box-shadow: 0 0 0 3px rgba(255, 140, 0, 0.1);
}

.case-actions,
.user-actions {
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

.view-btn {
  background: rgba(59, 130, 246, 0.1);
  color: #2563eb;
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.view-btn:hover {
  background: #2563eb;
  color: white;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.edit-btn {
  background: rgba(34, 197, 94, 0.1);
  color: #16a34a;
  border: 1px solid rgba(34, 197, 94, 0.2);
}

.edit-btn:hover {
  background: #16a34a;
  color: white;
  box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);
}

.deactivate-btn {
  background: rgba(239, 68, 68, 0.1);
  color: #dc2626;
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.deactivate-btn:hover {
  background: #dc2626;
  color: white;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

.activate-btn {
  background: rgba(34, 197, 94, 0.1);
  color: #16a34a;
  border: 1px solid rgba(34, 197, 94, 0.2);
}

.activate-btn:hover {
  background: #16a34a;
  color: white;
  box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);
}

.toggle-btn {
  background: rgba(245, 158, 11, 0.1);
  color: #d97706;
  border: 1px solid rgba(245, 158, 11, 0.2);
}

.toggle-btn:hover {
  background: #d97706;
  color: white;
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}

.toggle-btn.active {
  background: rgba(34, 197, 94, 0.1);
  color: #16a34a;
  border: 1px solid rgba(34, 197, 94, 0.2);
}

.toggle-btn.active:hover {
  background: #16a34a;
  color: white;
  box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);
}

.reports-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.report-card {
  background-color: var(--card-bg);
  border-radius: 30px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: background-color 0.3s;
}

.report-content {
  margin-top: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.stat-item {
  text-align: center;
  padding: 15px;
  background: var(--background-color);
  border-radius: 15px;
  border: 1px solid var(--border-color);
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
}

.performance-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.performance-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: var(--background-color);
  border-radius: 15px;
  border: 1px solid var(--border-color);
}

.member-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.member-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: var(--accent-color);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 14px;
}

.member-details {
  display: flex;
  flex-direction: column;
}

.member-name {
  font-weight: 600;
  margin-bottom: 2px;
}

.member-role {
  font-size: 12px;
  color: var(--text-secondary);
}

.performance-stats {
  display: flex;
  gap: 20px;
}

.stat {
  text-align: center;
}

.stat .stat-value {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 2px;
}

.stat .stat-label {
  font-size: 10px;
  color: var(--text-secondary);
}

.charts-section {
  margin-bottom: 30px;
}

.trend-chart {
  position: relative;
  height: 200px;
  background: var(--background-color);
  border-radius: 15px;
  padding: 20px;
}

.trend-line {
  position: absolute;
  top: 50%;
  left: 10%;
  right: 15%;
  height: 2px;
  background: linear-gradient(to right, var(--accent-color), #FF7700);
  border-radius: 1px;
}

.chart-points {
  position: relative;
  height: 100%;
}

.chart-point {
  position: absolute;
  width: 8px;
  height: 8px;
  background: var(--accent-color);
  border-radius: 50%;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.ai-assistant-container {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  margin-bottom: 30px;
}

.ai-chat-card,
.ai-suggestions-card {
  background-color: var(--card-bg);
  border-radius: 30px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: background-color 0.3s;
}

.ai-status {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--text-secondary);
}

.chat-container {
  display: flex;
  flex-direction: column;
  height: 400px;
  margin-top: 20px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 15px;
  background: var(--background-color);
  border-radius: 15px;
  margin-bottom: 15px;
  scrollbar-width: thin;
}

.message {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: var(--accent-color);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.message-content {
  max-width: 70%;
}

.message.user .message-content {
  background: var(--accent-color);
  color: white;
  border-radius: 15px 15px 5px 15px;
  padding: 10px 15px;
}

.message.ai .message-content {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 15px 15px 15px 5px;
  padding: 10px 15px;
}

.message-text {
  margin-bottom: 5px;
  line-height: 1.4;
}

.message-time {
  font-size: 10px;
  opacity: 0.7;
}

.chat-input-container {
  display: flex;
  gap: 10px;
}

.chat-input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: 25px;
  background: var(--background-color);
  color: var(--text-color);
  font-size: 14px;
  outline: none;
  transition: all 0.3s ease;
}

.chat-input:focus {
  border-color: var(--accent-color);
  box-shadow: 0 0 0 3px rgba(255, 140, 0, 0.1);
}

.send-btn {
  width: 44px;
  height: 44px;
  border: none;
  border-radius: 50%;
  background: var(--accent-color);
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.send-btn:hover:not(:disabled) {
  background: var(--accent-hover);
  transform: scale(1.05);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.suggestions-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 20px;
}

.suggestion-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 15px;
  background: var(--background-color);
  border: 1px solid var(--border-color);
  border-radius: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: left;
  width: 100%;
}

.suggestion-btn:hover {
  border-color: var(--accent-color);
  background-color: rgba(255, 140, 0, 0.05);
}

.suggestion-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: rgba(34, 197, 94, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #16a34a;
  flex-shrink: 0;
}

.suggestion-content {
  flex: 1;
}

.suggestion-title {
  font-weight: 600;
  margin-bottom: 4px;
}

.suggestion-description {
  font-size: 12px;
  color: var(--text-secondary);
}

.categories-container,
.workflows-container,
.settings-container {
  margin-bottom: 30px;
}

.categories-header,
.workflows-header,
.settings-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 30px;
  background-color: var(--card-bg);
  border-radius: 30px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.categories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.category-card {
  background-color: var(--card-bg);
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.category-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.category-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.category-actions {
  display: flex;
  gap: 8px;
}

.category-content {
  flex: 1;
}

.category-name {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 8px;
}

.category-description {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 15px;
  line-height: 1.4;
}

.category-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.case-count {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
}

.status-indicator {
  padding: 4px 8px;
  border-radius: 8px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
}

.status-indicator.active {
  background: rgba(34, 197, 94, 0.1);
  color: #16a34a;
}

.workflows-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.workflow-card {
  background-color: var(--card-bg);
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.workflow-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

.workflow-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.workflow-info {
  flex: 1;
}

.workflow-name {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 8px;
}

.workflow-description {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.4;
}

.workflow-status {
  display: flex;
  align-items: center;
}

.workflow-steps {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
  overflow-x: auto;
  padding: 10px 0;
}

.workflow-step {
  display: flex;
  align-items: center;
  gap: 10px;
  position: relative;
  min-width: 150px;
}

.step-number {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--accent-color);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.step-content {
  flex: 1;
}

.step-name {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 2px;
}

.step-assignee {
  font-size: 12px;
  color: var(--text-secondary);
}

.step-connector {
  position: absolute;
  right: -20px;
  top: 50%;
  transform: translateY(-50%);
  width: 30px;
  height: 2px;
  background: var(--border-color);
}

.workflow-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 30px;
}

.settings-group {
  background-color: var(--card-bg);
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.group-title {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 20px;
  color: var(--accent-color);
}

.settings-items {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.setting-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.setting-label {
  font-weight: 600;
  font-size: 14px;
}

.setting-input,
.setting-select {
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--background-color);
  color: var(--text-color);
  font-size: 14px;
  transition: all 0.3s ease;
}

.setting-input:focus,
.setting-select:focus {
  outline: none;
  border-color: var(--accent-color);
  box-shadow: 0 0 0 3px rgba(255, 140, 0, 0.1);
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 24px;
}

.toggle-switch input {
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
  background-color: var(--border-color);
  transition: 0.3s;
  border-radius: 24px;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: 0.3s;
  border-radius: 50%;
}

input:checked + .toggle-slider {
  background-color: var(--accent-color);
}

input:checked + .toggle-slider:before {
  transform: translateX(26px);
}

.save-settings-btn {
  padding: 12px 24px;
  background-color: var(--accent-color);
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.save-settings-btn:hover {
  background-color: var(--accent-hover);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255, 140, 0, 0.3);
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

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-weight: 600;
  font-size: 14px;
}

.form-input,
.form-select,
.form-textarea {
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--background-color);
  color: var(--text-color);
  font-size: 14px;
  transition: all 0.3s ease;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--accent-color);
  box-shadow: 0 0 0 3px rgba(255, 140, 0, 0.1);
}

.color-picker {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.color-option {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.3s ease;
}

.color-option:hover,
.color-option.selected {
  border-color: var(--text-color);
  transform: scale(1.1);
}

.workflow-steps-builder {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.step-builder {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 15px;
  background: var(--background-color);
  border-radius: 12px;
  border: 1px solid var(--border-color);
}

.step-input,
.step-select {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--card-bg);
  color: var(--text-color);
  font-size: 14px;
}

.remove-step-btn {
  padding: 6px;
  background: rgba(239, 68, 68, 0.1);
  color: #dc2626;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.remove-step-btn:hover {
  background: #dc2626;
  color: white;
}

.add-step-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: var(--accent-color);
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  align-self: flex-start;
}

.add-step-btn:hover {
  background: var(--accent-hover);
  transform: translateY(-1px);
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

.notification-panel {
  position: fixed;
  top: 0;
  right: -400px;
  width: 400px;
  height: 100vh;
  background: var(--card-bg);
  border-left: 1px solid var(--border-color);
  box-shadow: -4px 0 12px rgba(0, 0, 0, 0.1);
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
  border-bottom: 1px solid var(--border-color);
}

.notification-header h3 {
  font-size: 18px;
  font-weight: 700;
  margin: 0;
}

.close-notifications {
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  color: var(--text-secondary);
  transition: all 0.3s ease;
}

.close-notifications:hover {
  background: var(--background-color);
  color: var(--text-color);
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
  background: var(--background-color);
}

.notification-item.unread {
  background: rgba(255, 140, 0, 0.05);
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
  background: rgba(34, 197, 94, 0.1);
  color: #16a34a;
}

.notification-icon.system {
  background: rgba(245, 158, 11, 0.1);
  color: #d97706;
}

.notification-content {
  flex: 1;
}

.notification-title {
  font-weight: 600;
  margin-bottom: 4px;
}

.notification-message {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 8px;
  line-height: 1.4;
}

.notification-time {
  font-size: 12px;
  color: var(--text-secondary);
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

  .dashboard-content-grid {
    grid-template-columns: 1fr;
  }

  .ai-assistant-container {
    grid-template-columns: 1fr;
  }

  .expand-btn {
    display: none !important;
  }

  .reports-grid {
    grid-template-columns: 1fr;
  }

  .categories-grid {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  }

  .settings-grid {
    grid-template-columns: 1fr;
  }

  .notification-panel {
    width: 100%;
    right: -100%;
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

  .page-title {
    font-size: 24px;
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

  .categories-header,
  .workflows-header,
  .settings-header {
    flex-direction: column;
    gap: 20px;
    align-items: flex-start;
  }

  .categories-grid {
    grid-template-columns: 1fr;
  }

  .workflow-steps {
    flex-direction: column;
    align-items: stretch;
  }

  .workflow-step {
    min-width: auto;
  }

  .step-connector {
    display: none;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .performance-stats {
    flex-direction: column;
    gap: 10px;
  }

  .filters-row {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-select,
  .filter-input {
    min-width: auto;
  }

  .case-actions,
  .user-actions {
    flex-direction: column;
  }

  .action-btn {
    justify-content: center;
  }
}

@media (min-width: 1025px) {
  .mobile-menu-btn {
    display: none;
  }
}
</style>

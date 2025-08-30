<template>
  <div class="page-layout">
    <button class="mobile-menu-btn" id="mobile-menu-btn" @click="toggleMobileMenu">
      <svg fill="none" height="24" viewbox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">
        <path d="M3 12H21M3 6H21M3 18H21" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
        </path>
      </svg>
    </button>
    <SidePanel :userRole="userRole" :isInQueue="isInQueue" :isProcessingQueue="isProcessingQueue" :currentCall="currentCall" @toggle-queue="handleQueueToggle" @logout="handleLogout" @sidebar-toggle="handleSidebarToggle" />
    <div class="main-content" :style="{ marginLeft: mainContentMarginLeft }">
      <div class="header">
        <button class="sidebar-toggle" @click="toggleSidebar">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M4 6H20M4 12H20M4 18H20" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
        <div class="page-title">
          Counselor Wallboard
        </div>
        <button class="theme-toggle" id="theme-toggle" @click="toggleTheme">
          <svg fill="none" height="16" viewbox="0 0 24 24" width="16" xmlns="http://www.w3.org/2000/svg">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
            </path>
          </svg>
          <span>
            Light Mode
          </span>
        </button>
      </div>
      <div class="filter-container">
        <select class="filter-select">
          <option value="today">
            Today
          </option>
          <option value="yesterday">
            Yesterday
          </option>
          <option selected="" value="this-week">
            This Week
          </option>
          <option value="this-month">
            This Month
          </option>
          <option value="last-month">
            Last Month
          </option>
          <option value="custom">
            Custom Range
          </option>
        </select>
        <select class="filter-select">
          <option value="all-teams">
            All Teams
          </option>
          <option value="crisis-response">
            Crisis Response
          </option>
          <option value="counseling">
            Counseling Services
          </option>
          <option value="legal">
            Legal Services
          </option>
          <option value="housing">
            Housing &amp; Resources
          </option>
        </select>
      </div>
      <div class="dashboard-grid">
        <div class="dashboard-card glass-card fine-border">
          <div class="card-header">
            <div class="card-title">
              Total Calls
            </div>
            <div class="card-icon">
              <svg fill="none" height="24" viewbox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">
                <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                </path>
              </svg>
            </div>
          </div>
          <div class="card-value">
            1,248
          </div>
          <div class="card-subtitle">
            +12% from last week
          </div>
        </div>
        <div class="dashboard-card glass-card fine-border">
          <div class="card-header">
            <div class="card-title">
              Average Call Duration
            </div>
            <div class="card-icon">
              <svg fill="none" height="24" viewbox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                </circle>
                <polyline points="12 6 12 12 16 14" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                </polyline>
              </svg>
            </div>
          </div>
          <div class="card-value">
            14:32
          </div>
          <div class="card-subtitle">
            -2:15 from last week
          </div>
        </div>
        <div class="dashboard-card glass-card fine-border">
          <div class="card-header">
            <div class="card-title">
              Average QA Score
            </div>
            <div class="card-icon">
              <svg fill="none" height="24" viewbox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                </path>
                <polyline points="22 4 12 14.01 9 11.01" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                </polyline>
              </svg>
            </div>
          </div>
          <div class="card-value">
            87%
          </div>
          <div class="card-subtitle">
            +5% from last week
          </div>
        </div>
        <div class="dashboard-card glass-card fine-border">
          <div class="card-header">
            <div class="card-title">
              Achievements Unlocked
            </div>
            <div class="card-icon">
              <svg fill="none" height="24" viewbox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="8" r="7" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                </circle>
                <polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                </polyline>
              </svg>
            </div>
          </div>
          <div class="card-value">
            32
          </div>
          <div class="card-subtitle">
            +3 new this week
          </div>
        </div>
      </div>
      <div class="leaderboard-section">
        <div class="section-header">
          <div class="section-title">
            Counselor Leaderboard
          </div>
          <div class="leaderboard-tabs">
            <button class="leaderboard-tab active">
              Call Volume
            </button>
            <button class="leaderboard-tab">
              QA Scores
            </button>
            <button class="leaderboard-tab">
              Resolution Rate
            </button>
          </div>
        </div>
        <div class="leaderboard">
          <div class="leaderboard-item">
            <div class="leaderboard-rank rank-1">
              1
            </div>
            <div class="leaderboard-avatar">
              <img alt="Sarah Mitchell" src="/placeholder.svg?height=40&amp;width=40"/>
            </div>
            <div class="leaderboard-info">
              <div class="leaderboard-name">
                Sarah Mitchell
              </div>
              <div class="leaderboard-stats">
                <div class="leaderboard-stat">
                  <svg fill="none" height="12" viewbox="0 0 24 24" width="12" xmlns="http://www.w3.org/2000/svg">
                    <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                  </path>
                  </svg>
                  187 calls
                </div>
                <div class="leaderboard-stat">
                  <svg fill="none" height="12" viewbox="0 0 24 24" width="12" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                    </circle>
                    <polyline points="12 6 12 12 16 14" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                    </polyline>
                  </svg>
                  Avg 16:42
                </div>
              </div>
              <div class="achievement-badge">
                <svg class="badge-icon" fill="none" viewbox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 15C15.866 15 19 11.866 19 8C19 4.13401 15.866 1 12 1C8.13401 1 5 4.13401 5 8C5 11.866 8.13401 15 12 15Z" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                  </path>
                  <path d="M8.21 13.89L7 23L12 20L17 23L15.79 13.88" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                  </path>
                </svg>
                Call Champion
              </div>
            </div>
            <div class="leaderboard-score">
              187
            </div>
          </div>
          <div class="leaderboard-item">
            <div class="leaderboard-rank rank-2">
              2
            </div>
            <div class="leaderboard-avatar">
              <img alt="Robert Jackson" src="/placeholder.svg?height=40&amp;width=40"/>
            </div>
            <div class="leaderboard-info">
              <div class="leaderboard-name">
                Robert Jackson
              </div>
              <div class="leaderboard-stats">
                <div class="leaderboard-stat">
                  <svg fill="none" height="12" viewbox="0 0 24 24" width="12" xmlns="http://www.w3.org/2000/svg">
                    <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                  </path>
                  </svg>
                  165 calls
                </div>
                <div class="leaderboard-stat">
                  <svg fill="none" height="12" viewbox="0 0 24 24" width="12" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                    </circle>
                    <polyline points="12 6 12 12 16 14" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                    </polyline>
                  </svg>
                  Avg 15:18
                </div>
              </div>
              <div class="achievement-badge">
                <svg class="badge-icon" fill="none" viewbox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                  </path>
                </svg>
                Empathy Expert
              </div>
            </div>
            <div class="leaderboard-score">
              165
            </div>
          </div>
          <div class="leaderboard-item">
            <div class="leaderboard-rank rank-3">
              3
            </div>
            <div class="leaderboard-avatar">
              <img alt="Emily Chan" src="/placeholder.svg?height=40&amp;width=40"/>
            </div>
            <div class="leaderboard-info">
              <div class="leaderboard-name">
                Emily Chan
              </div>
              <div class="leaderboard-stats">
                <div class="leaderboard-stat">
                  <svg fill="none" height="12" viewbox="0 0 24 24" width="12" xmlns="http://www.w3.org/2000/svg">
                    <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                  </path>
                  </svg>
                  142 calls
                </div>
                <div class="leaderboard-stat">
                  <svg fill="none" height="12" viewbox="0 0 24 24" width="12" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                    </circle>
                    <polyline points="12 6 12 12 16 14" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                    </polyline>
                  </svg>
                  Avg 18:05
                </div>
              </div>
              <div class="achievement-badge">
                <svg class="badge-icon" fill="none" viewbox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                  </path>
                  <polyline points="22 4 12 14.01 9 11.01" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                  </polyline>
                </svg>
                Resolution Pro
              </div>
            </div>
            <div class="leaderboard-score">
              142
            </div>
          </div>
          <div class="leaderboard-item">
            <div class="leaderboard-rank rank-other">
              4
            </div>
            <div class="leaderboard-avatar">
              <img alt="Michael Lee" src="/placeholder.svg?height=40&amp;width=40"/>
            </div>
            <div class="leaderboard-info">
              <div class="leaderboard-name">
                Michael Lee
              </div>
              <div class="leaderboard-stats">
                <div class="leaderboard-stat">
                  <svg fill="none" height="12" viewbox="0 0 24 24" width="12" xmlns="http://www.w3.org/2000/svg">
                    <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                  </path>
                  </svg>
                  128 calls
                </div>
                <div class="leaderboard-stat">
                  <svg fill="none" height="12" viewbox="0 0 24 24" width="12" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                    </circle>
                    <polyline points="12 6 12 12 16 14" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                    </polyline>
                  </svg>
                  Avg 12:47
                </div>
              </div>
            </div>
            <div class="leaderboard-score">
              128
            </div>
          </div>
          <div class="leaderboard-item">
            <div class="leaderboard-rank rank-other">
              5
            </div>
            <div class="leaderboard-avatar">
              <img alt="Patience Williams" src="/placeholder.svg?height=40&amp;width=40"/>
            </div>
            <div class="leaderboard-info">
              <div class="leaderboard-name">
                Patience Williams
              </div>
              <div class="leaderboard-stats">
                <div class="leaderboard-stat">
                  <svg fill="none" height="12" viewbox="0 0 24 24" width="12" xmlns="http://www.w3.org/2000/svg">
                    <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                  </path>
                  </svg>
                  115 calls
                </div>
                <div class="leaderboard-stat">
                  <svg fill="none" height="12" viewbox="0 0 24 24" width="12" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                    </circle>
                    <polyline points="12 6 12 12 16 14" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                    </polyline>
                  </svg>
                  Avg 14:32
                </div>
              </div>
            </div>
            <div class="leaderboard-score">
              115
            </div>
          </div>
        </div>
      </div>
      <div class="charts-section">
        <div class="chart-container">
          <div class="chart-header">
            <div class="chart-title">
              Call Volume by Day
            </div>
            <div class="chart-subtitle">
              Last 7 days
            </div>
          </div>
          <div class="chart">
            <div class="chart-bar" style="height: 60%;">
              <div class="chart-bar-label">
                Mon
              </div>
              <div class="chart-bar-value">
                156
              </div>
            </div>
            <div class="chart-bar" style="height: 75%;">
              <div class="chart-bar-label">
                Tue
              </div>
              <div class="chart-bar-value">
                195
              </div>
            </div>
            <div class="chart-bar" style="height: 85%;">
              <div class="chart-bar-label">
                Wed
              </div>
              <div class="chart-bar-value">
                221
              </div>
            </div>
            <div class="chart-bar" style="height: 70%;">
              <div class="chart-bar-label">
                Thu
              </div>
              <div class="chart-bar-value">
                182
              </div>
            </div>
            <div class="chart-bar" style="height: 90%;">
              <div class="chart-bar-label">
                Fri
              </div>
              <div class="chart-bar-value">
                234
              </div>
            </div>
            <div class="chart-bar" style="height: 50%;">
              <div class="chart-bar-label">
                Sat
              </div>
              <div class="chart-bar-value">
                130
              </div>
            </div>
            <div class="chart-bar" style="height: 45%;">
              <div class="chart-bar-label">
                Sun
              </div>
              <div class="chart-bar-value">
                117
              </div>
            </div>
          </div>
        </div>
        <div class="chart-container">
          <div class="chart-header">
            <div class="chart-title">
              Call Categories Distribution
            </div>
            <div class="chart-subtitle">
              This week
            </div>
          </div>
          <div class="pie-chart">
            <div class="pie-chart-center">
              1,248
            </div>
          </div>
          <div class="pie-chart-legend">
            <div class="legend-item">
              <div class="legend-color legend-color-1">
              </div>
              <span>
                Domestic Violence (25%)
              </span>
            </div>
            <div class="legend-item">
              <div class="legend-color legend-color-2">
              </div>
              <span>
                Sexual Assault (30%)
              </span>
            </div>
            <div class="legend-item">
              <div class="legend-color legend-color-3">
              </div>
              <span>
                Human Trafficking (15%)
              </span>
            </div>
            <div class="legend-item">
              <div class="legend-color legend-color-4">
              </div>
              <span>
                Child Abuse (15%)
              </span>
            </div>
            <div class="legend-item">
              <div class="legend-color legend-color-5">
              </div>
              <span>
                Other (15%)
              </span>
            </div>
          </div>
        </div>
      </div>
      <div class="achievements-section">
        <div class="section-header">
          <div class="section-title">
            Available Achievements
          </div>
        </div>
        <div class="achievements-grid">
          <div class="achievement-card achievement-unlocked">
            <div class="achievement-icon">
              <svg fill="none" height="24" viewbox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 15C15.866 15 19 11.866 19 8C19 4.13401 15.866 1 12 1C8.13401 1 5 4.13401 5 8C5 11.866 8.13401 15 12 15Z" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                </path>
                <path d="M8.21 13.89L7 23L12 20L17 23L15.79 13.88" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                </path>
              </svg>
            </div>
            <div class="achievement-title">
              Call Champion
            </div>
            <div class="achievement-description">
              Handle 100+ calls in a week
            </div>
            <div class="achievement-progress">
              <div class="achievement-progress-bar" style="width: 100%;">
              </div>
            </div>
            <div class="achievement-progress-text">
              Completed!
            </div>
          </div>
          <div class="achievement-card">
            <div class="achievement-icon">
              <svg fill="none" height="24" viewbox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">
                <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                </path>
              </svg>
            </div>
            <div class="achievement-title">
              Empathy Expert
            </div>
            <div class="achievement-description">
              Maintain 90%+ listening score for 30 days
            </div>
            <div class="achievement-progress">
              <div class="achievement-progress-bar" style="width: 75%;">
              </div>
            </div>
            <div class="achievement-progress-text">
              75% Complete
            </div>
          </div>
          <div class="achievement-card">
            <div class="achievement-icon">
              <svg fill="none" height="24" viewbox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                </path>
                <polyline points="22 4 12 14.01 9 11.01" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                </polyline>
              </svg>
            </div>
            <div class="achievement-title">
              Resolution Pro
            </div>
            <div class="achievement-description">
              Resolve 50 cases with 90%+ satisfaction
            </div>
            <div class="achievement-progress">
              <div class="achievement-progress-bar" style="width: 60%;">
              </div>
            </div>
            <div class="achievement-progress-text">
              30/50 Cases
            </div>
          </div>
          <div class="achievement-card">
            <div class="achievement-icon">
              <svg fill="none" height="24" viewbox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                </path>
              </svg>
            </div>
            <div class="achievement-title">
              Five-Star Support
            </div>
            <div class="achievement-description">
              Receive 25 five-star ratings from callers
            </div>
            <div class="achievement-progress">
              <div class="achievement-progress-bar" style="width: 40%;">
              </div>
            </div>
            <div class="achievement-progress-text">
              10/25 Ratings
            </div>
          </div>
          <div class="achievement-card">
            <div class="achievement-icon">
              <svg fill="none" height="24" viewbox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">
                <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                </path>
                <path d="M13.73 21a2 2 0 0 1-3.46 0" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                </path>
              </svg>
            </div>
            <div class="achievement-title">
              First Responder
            </div>
            <div class="achievement-description">
              Answer 20 emergency priority calls
            </div>
            <div class="achievement-progress">
              <div class="achievement-progress-bar" style="width: 85%;">
              </div>
            </div>
            <div class="achievement-progress-text">
              17/20 Calls
            </div>
          </div>
          <div class="achievement-card achievement-unlocked">
            <div class="achievement-icon">
              <svg fill="none" height="24" viewbox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">
                <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                </path>
                <circle cx="8.5" cy="7" r="4" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                </circle>
                <path d="M20 8v6" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                </path>
                <path d="M23 11h-6" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                </path>
              </svg>
            </div>
            <div class="achievement-title">
              Team Player
            </div>
            <div class="achievement-description">
              Assist 15 colleagues with their cases
            </div>
            <div class="achievement-progress">
              <div class="achievement-progress-bar" style="width: 100%;">
              </div>
            </div>
            <div class="achievement-progress-text">
              Completed!
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { onMounted, ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import SidePanel from '../components/SidePanel.vue';

export default {
  components: {
    SidePanel,
  },
  setup() {
    const router = useRouter();
    const logout = () => {
      router.push('/');
    };

    const currentTheme = ref(localStorage.getItem('theme') || 'dark');

    const isSidebarCollapsed = ref(false);
    const mobileOpen = ref(false);

    const toggleSidebar = () => {
      isSidebarCollapsed.value = !isSidebarCollapsed.value;
    };

    const toggleMobileMenu = () => {
      mobileOpen.value = !mobileOpen.value;
    };

    const mainContentMarginLeft = computed(() => {
      if (window.innerWidth <= 768) {
        return '0px';
      } else if (isSidebarCollapsed.value) {
        return '80px'; // Collapsed sidebar width
      } else {
        return '250px'; // Expanded sidebar width
      }
    });

    const toggleTheme = () => {
      const newTheme = currentTheme.value === 'dark' ? 'light' : 'dark';
      currentTheme.value = newTheme;
      localStorage.setItem('theme', newTheme);
    };

    onMounted(() => {
      const sidebar = document.getElementById('sidebar');
      const mobileMenuBtn = document.getElementById('mobile-menu-btn');
      const themeToggle = document.getElementById('theme-toggle');
      const html = document.documentElement;
      const leaderboardTabs = document.querySelectorAll('.leaderboard-tab');

      // Mobile menu toggle
      if (mobileMenuBtn && sidebar) {
        mobileMenuBtn.addEventListener('click', function() {
          sidebar.classList.toggle('mobile-open');
        });
      }
      // Close sidebar when clicking outside on mobile
      document.addEventListener('click', function(event) {
        const isMobile = window.innerWidth <= 768;
        if (isMobile && !sidebar.contains(event.target) && event.target !== mobileMenuBtn) {
          sidebar.classList.remove('mobile-open');
        }
      });
      // Theme toggle
      if (themeToggle && html) {
        themeToggle.addEventListener('click', function() {
          const currentTheme = html.getAttribute('data-theme');
          const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
          html.setAttribute('data-theme', newTheme);
          const themeText = themeToggle.querySelector('span');
          if (themeText) {
            themeText.textContent = newTheme === 'dark' ? 'Light Mode' : 'Dark Mode';
          }
          localStorage.setItem('theme', newTheme);
        });
         // Check localStorage for saved theme preference
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
          html.setAttribute('data-theme', savedTheme);
           const themeText = themeToggle.querySelector('span');
          if (themeText) {
            themeText.textContent = savedTheme === 'dark' ? 'Light Mode' : 'Dark Mode';
          }
        }
      }
      // Leaderboard tabs
      if (leaderboardTabs) {
        leaderboardTabs.forEach(tab => {
          tab.addEventListener('click', function() {
            leaderboardTabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
          });
        });
      }
    });

    return {
      logout,
      currentTheme,
      isSidebarCollapsed,
      mobileOpen,
      toggleSidebar,
      toggleMobileMenu,
      mainContentMarginLeft,
      toggleTheme,
    };
  },
};
</script>

<style scoped>
:root {
    /* Dark theme variables */
    --background-color: #0a0a0a;
    --sidebar-bg: #111;
    --content-bg: #222;
    --text-color: #fff;
    --text-secondary: #aaa;
    --border-color: #333;
    --accent-color: #964B00;
    --accent-hover: #b25900;
    --danger-color: #ff3b30;
    --success-color: #4CAF50;
    --pending-color: #FFA500;
    --unassigned-color: #808080;
    --highlight-color: #ff3b30;
    --header-bg: #333;
    --input-bg: #1a1a1a;
    --gold-color: #FFD700;
    --silver-color: #C0C0C0;
    --bronze-color: #CD7F32;
    --chart-color-1: #4CAF50;
    --chart-color-2: #2196F3;
    --chart-color-3: #FFC107;
    --chart-color-4: #9C27B0;
    --chart-color-5: #FF5722;
}

[data-theme="light"] {
    --background-color: #f5f5f5;
    --sidebar-bg: #ffffff;
    --content-bg: #ffffff;
    --text-color: #333;
    --text-secondary: #666;
    --border-color: #ddd;
    --accent-color: #964B00;
    --accent-hover: #b25900;
    --danger-color: #ff3b30;
    --success-color: #4CAF50;
    --pending-color: #FFA500;
    --unassigned-color: #808080;
    --highlight-color: #ff3b30;
    --header-bg: #f0f0f0;
    --input-bg: #f0f0f0;
    --gold-color: #FFD700;
    --silver-color: #C0C0C0;
    --bronze-color: #CD7F32;
    --chart-color-1: #4CAF50;
    --chart-color-2: #2196F3;
    --chart-color-3: #FFC107;
    --chart-color-4: #9C27B0;
    --chart-color-5: #FF5722;
}

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
}

.page-layout {
  display: flex;
  width: 100%;
  height: 100vh;
  background-color: var(--background-color);
  overflow: hidden;
}

.mobile-menu-btn {
  display: none;
  position: fixed;
  top: 10px;
  left: 10px;
  background-color: var(--content-bg);
  color: var(--text-color);
  border: 1px solid var(--border-color);
  border-radius: 50%;
  padding: 10px;
  cursor: pointer;
  z-index: 1000;
}

.sidebar {
  width: 250px;
  flex-shrink: 0;
  background-color: var(--sidebar-bg);
  color: var(--text-color);
  transition: width 0.3s ease, transform 0.3s ease;
  overflow-x: hidden;
  border-radius: 0 30px 30px 0;
  z-index: 100;
  height: 100%;
  display: flex;
  flex-direction: column;
  position: relative;
}

.sidebar.collapsed {
  width: 80px;
}

.sidebar-content {
  padding: 30px 0;
  width: 250px;
  height: 100%;
  overflow-y: auto;
}

.sidebar.collapsed .sidebar-content {
  opacity: 0;
  pointer-events: none;
}

.logo-container {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 30px;
}

.logo {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  background-color: var(--text-color);
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
}

.logo img {
  width: 40px;
  height: 40px;
  object-fit: contain;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  cursor: pointer;
  margin-bottom: 5px;
  border-radius: 30px 0 0 30px;
  text-decoration: none;
  color: var(--text-color);
  transition: background-color 0.3s;
}

.nav-item:hover {
    background-color: rgba(255, 255, 255, 0.05);
}

.nav-item.active {
  background-color: rgba(255, 255, 255, 0.1);
}

.nav-icon {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 2px solid var(--text-color);
  margin-right: 15px;
  flex-shrink: 0;
}

.nav-text {
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar.collapsed .nav-text {
  display: none;
}

.user-profile {
  display: flex;
  justify-content: center;
  margin: 30px 0 20px;
}

.user-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background-color: var(--text-color);
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  overflow: hidden;
}

.user-avatar svg {
  width: 30px;
  height: 30px;
  fill: var(--background-color);
}

.status {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
  font-size: 14px;
}

.status-dot {
  width: 8px;
  height: 8px;
  background-color: green;
  border-radius: 50%;
  margin-right: 8px;
}

.button-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 0 20px;
}

.join-queue-btn, .logout-btn {
  width: 100%;
  padding: 10px;
  border-radius: 20px;
  border: none;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
}

.join-queue-btn {
  background-color: var(--accent-color);
  color: white;
}

.join-queue-btn:hover {
    background-color: var(--accent-hover);
}

.logout-btn {
    background-color: #800000; /* Maroon background */
    color: white;
    border: 1px solid #800000; /* Maroon border */
    border-radius: 30px;
    padding: 10px;
    width: 100%;
    font-weight: 600;
    cursor: pointer;
    transition: background-color 0.3s, border-color 0.3s; /* Add border-color transition */
}

.logout-btn:hover {
    background-color: var(--danger-color); /* Red background on hover */
    border-color: var(--danger-color); /* Red border on hover */
}

.main-content {
  background: rgba(10, 10, 10, 0.92);
  color: #fff;
  border-radius: 24px;
  box-shadow: 0 8px 32px 0 rgba(0,0,0,0.18);
  padding: 32px 24px;
  margin: 0 auto;
  max-width: 1400px;
  min-height: 100vh;
}

.sidebar.collapsed ~ .main-content {
  margin-left: 80px;
}

.header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  gap: 20px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  margin: 0 auto 0 0;
  color: var(--accent-color);
  font-weight: 800;
  letter-spacing: 0.5px;
}

.theme-toggle {
  background-color: var(--content-bg);
  color: var(--text-color);
  border: 1px solid var(--border-color);
  border-radius: 30px;
  padding: 8px 15px;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-container {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
}

.filter-select {
  padding: 8px 15px;
  border-radius: 20px;
  border: 1px solid var(--border-color);
  background-color: var(--content-bg);
  color: var(--text-color);
  font-size: 14px;
  cursor: pointer;
  outline: none;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.dashboard-card, .leaderboard-section, .achievement-card, .chart-container, .pie-chart {
  background: rgba(24, 24, 24, 0.65);
  border-radius: 22px;
  border: 1.5px solid rgba(255, 215, 0, 0.18);
  box-shadow: 0 8px 32px 0 rgba(0,0,0,0.25);
  backdrop-filter: blur(12px) saturate(120%);
  -webkit-backdrop-filter: blur(12px) saturate(120%);
  color: #fff;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-color);
}

.card-icon {
  width: 40px;
  height: 40px;
  background-color: rgba(255, 59, 48, 0.2);
  border-radius: 10px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.card-icon svg {
  width: 24px;
  height: 24px;
  stroke: var(--accent-color);
}

.card-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--accent-color);
  margin-bottom: 5px;
}

.card-subtitle {
  font-size: 12px;
  color: var(--text-secondary);
}

.leaderboard-section {
  margin-top: 30px;
  padding: 32px 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-color);
  color: var(--accent-color);
  font-weight: 800;
  letter-spacing: 0.5px;
}

.leaderboard-tabs {
  display: flex;
  gap: 12px;
}

.leaderboard-tab {
  padding: 10px 24px;
  border-radius: 16px 16px 0 0;
  background: transparent;
  color: var(--text-secondary);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.leaderboard-tab.active {
  color: var(--accent-color);
  background: rgba(255, 140, 0, 0.12);
  box-shadow: 0 4px 16px 0 rgba(255,140,0,0.08);
}

.leaderboard-table-container {
  overflow-x: auto;
}

.leaderboard-table {
  width: 100%;
  border-collapse: collapse;
}

.leaderboard-table th, .leaderboard-table td {
  text-align: left;
  padding: 12px 0;
  border-bottom: 1px solid var(--border-color);
}

.leaderboard-table th {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
}

.leaderboard-table td {
  font-size: 14px;
  color: var(--text-color);
}

.leaderboard-table tbody tr:last-child td {
  border-bottom: none;
}

.charts-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 30px;
}

.chart-container {
  padding: 20px;
}

.chart-header {
  margin-bottom: 20px;
}

.chart-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 5px;
}

.chart-subtitle {
  font-size: 12px;
  color: var(--text-secondary);
}

.chart {
  height: 300px;
  display: flex;
  align-items: flex-end;
  gap: 10px;
  padding-top: 20px;
}

.chart-bar {
  flex: 1;
  background-color: var(--chart-color-1);
  border-radius: 5px 5px 0 0;
  position: relative;
  min-width: 30px;
  transition: height 0.5s ease;
}

.chart-bar:nth-child(2) {
  background-color: var(--chart-color-2);
}

.chart-bar:nth-child(3) {
  background-color: var(--chart-color-3);
}

.chart-bar:nth-child(4) {
  background-color: var(--chart-color-4);
}

.chart-bar:nth-child(5) {
  background-color: var(--chart-color-5);
}

.chart-bar-label {
  position: absolute;
  top: -25px;
  left: 0;
  right: 0;
  text-align: center;
  font-size: 12px;
  font-weight: 500;
}

.chart-bar-value {
  position: absolute;
  bottom: 5px;
  left: 0;
  right: 0;
  text-align: center;
  font-size: 12px;
  font-weight: 700;
  color: white;
}

.pie-chart {
  height: 250px;
  width: 250px;
  margin: 0 auto;
  position: relative;
  border-radius: 50%;
  background: conic-gradient(
      var(--chart-color-1) 0% 25%,
      var(--chart-color-2) 25% 55%,
      var(--chart-color-3) 55% 70%,
      var(--chart-color-4) 70% 85%,
      var(--chart-color-5) 85% 100%
  );
}

.pie-chart-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 100px;
  height: 100px;
  background-color: var(--content-bg);
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 18px;
  font-weight: 700;
}

.pie-chart-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-top: 20px;
  justify-content: center;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 3px;
}

.legend-color-1 {
  background-color: var(--chart-color-1);
}

.legend-color-2 {
  background-color: var(--chart-color-2);
}

.legend-color-3 {
  background-color: var(--chart-color-3);
}

.legend-color-4 {
  background-color: var(--chart-color-4);
}

.legend-color-5 {
  background-color: var(--chart-color-5);
}

.achievements-section {
  margin-bottom: 30px;
}

.achievements-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.leaderboard-name {
  color: var(--accent-color);
  font-weight: 700;
}

/* Responsive styles */
@media (max-width: 1200px) {
  .dashboard-grid {
    grid-template-columns: 1fr 1fr;
  }
}
@media (max-width: 1024px) {
  .main-content {
    margin-left: 0;
    width: 100vw;
  }
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}
@media (max-width: 900px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}
@media (max-width: 768px) {
  .main-content {
    margin-left: 0;
    width: 100vw;
    padding: 10px 2vw;
  }
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  .leaderboard-section {
    padding: 16px 6px;
  }
  .achievements-grid {
    grid-template-columns: 1fr;
  }
}
@media (max-width: 480px) {
  .main-content {
    margin-left: 0;
    width: 100vw;
    padding: 4px 1vw;
  }
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  .leaderboard-section {
    padding: 8px 2px;
  }
  .achievements-grid {
    grid-template-columns: 1fr;
  }
}

/* Added new sidebar-toggle styles */
.sidebar-toggle {
  background-color: var(--content-bg);
  color: var(--text-color);
  border: 1px solid var(--border-color);
  border-radius: 30px;
  padding: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.3s;
}

.sidebar-toggle:hover {
  background-color: var(--background-color);
}

.sidebar-toggle svg {
  width: 20px;
  height: 20px;
}
</style>

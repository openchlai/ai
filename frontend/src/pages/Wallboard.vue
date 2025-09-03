<template>
  <div class="page-layout">
    <SidePanel :userRole="userRole" :isInQueue="isInQueue" :isProcessingQueue="isProcessingQueue" :currentCall="currentCall" @toggle-queue="handleQueueToggle" @logout="handleLogout" @sidebar-toggle="handleSidebarToggle" />
    <div class="main-content" :style="{ marginLeft: mainContentMarginLeft }">
      <div class="header">
        <div class="page-title">
          Counselor Wallboard
        </div>
      </div>

      <div class="main-scroll-content">
        <!-- Filter Container -->
      <div class="filter-container">
          <select class="filter-select" v-model="selectedTimeRange" @change="updateFilters">
            <option value="" disabled>Select Time Range</option>
            <option value="today">Today</option>
            <option value="yesterday">Yesterday</option>
            <option value="this-week">This Week</option>
            <option value="this-month">This Month</option>
            <option value="last-month">Last Month</option>
            <option value="custom">Custom Range</option>
        </select>
          <select class="filter-select" v-model="selectedTeam" @change="updateFilters">
            <option value="" disabled>Select Team</option>
            <option value="all-teams">All Teams</option>
            <option value="crisis-response">Crisis Response</option>
            <option value="counseling">Counseling Services</option>
            <option value="legal">Legal Services</option>
            <option value="housing">Housing & Resources</option>
        </select>
          <button class="btn btn--primary" @click="applyFilters">
            Apply Filters
          </button>
          <button class="btn btn--secondary" @click="resetFilters">
            Reset
          </button>
      </div>

        <!-- Dashboard Grid - Styled like Dashboard landing -->
      <div class="dashboard-grid">
        <div class="dashboard-card glass-card fine-border">
          <div class="card-header">
              <div class="card-title">Total Calls</div>
            <div class="card-icon">
              <svg fill="none" height="24" viewbox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">
                <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                </path>
              </svg>
            </div>
          </div>
            <div class="card-value gold-text">1,248</div>
            <div class="card-subtitle">+12% from last week</div>
          </div>

        <div class="dashboard-card glass-card fine-border">
          <div class="card-header">
              <div class="card-title">Average Call Duration</div>
            <div class="card-icon">
              <svg fill="none" height="24" viewbox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                </circle>
                <polyline points="12 6 12 12 16 14" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                </polyline>
              </svg>
            </div>
          </div>
            <div class="card-value">14:32</div>
            <div class="card-subtitle">-2:15 from last week</div>
          </div>

        <div class="dashboard-card glass-card fine-border">
          <div class="card-header">
              <div class="card-title">Average QA Score</div>
            <div class="card-icon">
              <svg fill="none" height="24" viewbox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                </path>
                <polyline points="22 4 12 14.01 9 11.01" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                </polyline>
              </svg>
            </div>
          </div>
            <div class="card-value">87%</div>
            <div class="card-subtitle">+5% from last week</div>
          </div>

        <div class="dashboard-card glass-card fine-border">
          <div class="card-header">
              <div class="card-title">Achievements Unlocked</div>
            <div class="card-icon">
              <svg fill="none" height="24" viewbox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="8" r="7" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                </circle>
                <polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                </polyline>
              </svg>
            </div>
          </div>
            <div class="card-value">32</div>
            <div class="card-subtitle">+3 new this week</div>
          </div>

          <div class="dashboard-card glass-card fine-border">
            <div class="card-header">
              <div class="card-title">Active Counselors</div>
              <div class="card-icon counsellors-online">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path
                    d="M17 21V19C17 17.9391 16.5786 16.9217 15.8284 16.1716C15.0783 15.4214 14.0609 15 13 15H5C3.93913 15 2.92172 15.4214 2.17157 16.1716C1.42143 16.9217 1 17.9391 1 19V21"
                    stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                  <circle cx="9" cy="7" r="4" stroke="white" stroke-width="2" stroke-linecap="round"
                    stroke-linejoin="round" />
                  <path
                    d="M23 21V19C23 18.1645 22.7155 17.3541 22.2094 16.6977C21.7033 16.0414 20.9999 15.5735 20.2 15.3613"
                    stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                  <path
                    d="M16 3.13C16.8003 3.3422 17.5037 3.81014 18.0098 4.46645C18.5159 5.12277 18.8004 5.93317 18.8004 6.76875C18.8004 7.60433 18.5159 8.41473 18.0098 9.07105C17.5037 9.72736 16.8003 10.1953 16 10.4075"
                    stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                  </svg>
                </div>
                </div>
            <div class="card-value">18</div>
            <div class="card-subtitle">Currently online</div>
              </div>

          <div class="dashboard-card glass-card fine-border">
            <div class="card-header">
              <div class="card-title">Resolution Rate</div>
              <div class="card-icon">
                <svg fill="none" height="24" viewbox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">
                  <path d="M9 12l2 2 4-4" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                  </path>
                    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                    </circle>
                  </svg>
                </div>
              </div>
            <div class="card-value">94%</div>
            <div class="card-subtitle">+2% from last week</div>
              </div>
            </div>

        <!-- Counselor Leaderboard Section - Scrollable -->
        <div class="leaderboard-section">
          <div class="section-header">
            <div class="section-title">Counselor Leaderboard</div>
            </div>
          <div class="leaderboard-container">
            <div class="leaderboard">
              <div class="leaderboard-item" v-for="(counselor, index) in counselors" :key="counselor.name">
                <div class="leaderboard-rank" :class="`rank-${index + 1}`">
                  {{ index + 1 }}
            </div>
            <div class="leaderboard-avatar">
                  <div class="avatar-placeholder">{{ counselor.name.charAt(0) }}</div>
            </div>
            <div class="leaderboard-info">
                  <div class="leaderboard-name">{{ counselor.name }}</div>
              <div class="leaderboard-stats">
                <div class="leaderboard-stat">
                  <svg fill="none" height="12" viewbox="0 0 24 24" width="12" xmlns="http://www.w3.org/2000/svg">
                    <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                  </path>
                  </svg>
                      {{ counselor.calls }} calls
                </div>
                <div class="leaderboard-stat">
                  <svg fill="none" height="12" viewbox="0 0 24 24" width="12" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                    </circle>
                    <polyline points="12 6 12 12 16 14" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                    </polyline>
                  </svg>
                      Avg {{ counselor.avgDuration }}
                </div>
              </div>
                  <div class="achievement-badge" v-if="counselor.achievement">
                <svg class="badge-icon" fill="none" viewbox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path d="M12 15C15.866 15 19 11.866 19 8C19 4.13401 15.866 1 12 1C8.13401 1 5 4.13401 5 8C5 11.866 8.13401 15 12 15Z" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                  </path>
                      <path d="M8.21 13.89L7 23L12 20L17 23L15.79 13.88" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                  </path>
                  </svg>
                    {{ counselor.achievement }}
                </div>
                </div>
                <div class="leaderboard-score">{{ counselor.calls }}</div>
              </div>
            </div>
            </div>
          </div>

        <!-- Charts Section -->
      <div class="charts-section">
        <div class="chart-container">
          <div class="chart-header">
              <div class="chart-title">Call Volume by Day</div>
              <div class="chart-subtitle">Last 7 days</div>
          </div>
          <div class="chart">
            <div class="chart-bar" style="height: 60%;">
                <div class="chart-bar-label">Mon</div>
                <div class="chart-bar-value">156</div>
            </div>
            <div class="chart-bar" style="height: 75%;">
                <div class="chart-bar-label">Tue</div>
                <div class="chart-bar-value">195</div>
            </div>
            <div class="chart-bar" style="height: 85%;">
                <div class="chart-bar-label">Wed</div>
                <div class="chart-bar-value">221</div>
            </div>
            <div class="chart-bar" style="height: 70%;">
                <div class="chart-bar-label">Thu</div>
                <div class="chart-bar-value">182</div>
            </div>
            <div class="chart-bar" style="height: 90%;">
                <div class="chart-bar-label">Fri</div>
                <div class="chart-bar-value">234</div>
            </div>
            <div class="chart-bar" style="height: 50%;">
                <div class="chart-bar-label">Sat</div>
                <div class="chart-bar-value">130</div>
            </div>
            <div class="chart-bar" style="height: 45%;">
                <div class="chart-bar-label">Sun</div>
                <div class="chart-bar-value">117</div>
            </div>
          </div>
        </div>
        <div class="chart-container">
          <div class="chart-header">
              <div class="chart-title">Call Categories Distribution</div>
              <div class="chart-subtitle">This week</div>
          </div>
          <div class="pie-chart">
              <div class="pie-chart-center">1,248</div>
          </div>
          <div class="pie-chart-legend">
            <div class="legend-item">
                <div class="legend-color legend-color-1"></div>
                <span>Domestic Violence (25%)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color legend-color-2"></div>
                <span>Sexual Assault (30%)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color legend-color-3"></div>
                <span>Human Trafficking (15%)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color legend-color-4"></div>
                <span>Child Abuse (15%)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color legend-color-5"></div>
                <span>Other (15%)</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Achievements Section -->
      <div class="achievements-section">
        <div class="section-header">
            <div class="section-title">Available Achievements</div>
        </div>
        <div class="achievements-grid">
            <div class="achievement-card achievement-unlocked" v-for="achievement in achievements" :key="achievement.title">
            <div class="achievement-icon">
              <svg fill="none" height="24" viewbox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 15C15.866 15 19 11.866 19 8C19 4.13401 15.866 1 12 1C8.13401 1 5 4.13401 5 8C5 11.866 8.13401 15 12 15Z" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                </path>
                <path d="M8.21 13.89L7 23L12 20L17 23L15.79 13.88" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                </path>
              </svg>
            </div>
              <div class="achievement-title">{{ achievement.title }}</div>
              <div class="achievement-description">{{ achievement.description }}</div>
            <div class="achievement-progress">
                <div class="achievement-progress-bar" :style="{ width: achievement.progress + '%' }"></div>
              </div>
              <div class="achievement-progress-text">{{ achievement.progressText }}</div>
            </div>
            </div>
          </div>
            </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import SidePanel from '../components/SidePanel.vue';

export default {
  components: {
    SidePanel,
  },
  setup() {
    const router = useRouter();
    
    // SidePanel state
    const userRole = ref('counselor');
    const isInQueue = ref(false);
    const isProcessingQueue = ref(false);
    const currentCall = ref(null);

    // Sidebar state
    const isSidebarCollapsed = ref(false);

    // Filter state
    const selectedTimeRange = ref('');
    const selectedTeam = ref('');

    // Main content margin
    const mainContentMarginLeft = computed(() => {
      if (window.innerWidth <= 768) {
        return '0px';
      } else if (isSidebarCollapsed.value) {
        return '80px';
      } else {
        return '250px';
      }
    });

    // Counselor data
    const counselors = ref([
      {
        name: 'Sarah Mitchell',
        calls: 187,
        avgDuration: '16:42',
        achievement: 'Call Champion'
      },
      {
        name: 'Robert Jackson',
        calls: 165,
        avgDuration: '15:18',
        achievement: 'Empathy Expert'
      },
      {
        name: 'Emily Chan',
        calls: 142,
        avgDuration: '18:05',
        achievement: 'Resolution Pro'
      },
      {
        name: 'Michael Lee',
        calls: 128,
        avgDuration: '12:47'
      },
      {
        name: 'Patience Williams',
        calls: 115,
        avgDuration: '14:32'
      },
      {
        name: 'David Chen',
        calls: 98,
        avgDuration: '13:45'
      },
      {
        name: 'Lisa Rodriguez',
        calls: 87,
        avgDuration: '17:20'
      },
      {
        name: 'James Wilson',
        calls: 76,
        avgDuration: '11:30'
      }
    ]);

    // Achievements data
    const achievements = ref([
      {
        title: 'Call Champion',
        description: 'Handle 100+ calls in a week',
        progress: 100,
        progressText: 'Completed!'
      },
      {
        title: 'Empathy Expert',
        description: 'Maintain 90%+ listening score for 30 days',
        progress: 75,
        progressText: '75% Complete'
      },
      {
        title: 'Resolution Pro',
        description: 'Resolve 50 cases with 90%+ satisfaction',
        progress: 60,
        progressText: '30/50 Cases'
      },
      {
        title: 'Five-Star Support',
        description: 'Receive 25 five-star ratings from callers',
        progress: 40,
        progressText: '10/25 Ratings'
      },
      {
        title: 'First Responder',
        description: 'Answer 20 emergency priority calls',
        progress: 85,
        progressText: '17/20 Calls'
      },
      {
        title: 'Team Player',
        description: 'Assist 15 colleagues with their cases',
        progress: 100,
        progressText: 'Completed!'
      }
    ]);

    // SidePanel event handlers
    const handleQueueToggle = () => {
      isInQueue.value = !isInQueue.value;
    };
    const handleLogout = () => {
      router.push('/');
    };
    const handleSidebarToggle = (collapsed) => {
      isSidebarCollapsed.value = collapsed;
    };

    // Filter methods
    const updateFilters = () => {
      console.log('Filters updated:', { timeRange: selectedTimeRange.value, team: selectedTeam.value });
      // Here you would typically update the data based on filters
      // For now, we'll just log the changes
    };

    const applyFilters = () => {
      console.log('Applying filters:', { timeRange: selectedTimeRange.value, team: selectedTeam.value });
      // Apply the filters to update the dashboard data
      // This would typically make an API call or filter local data
      alert(`Filters applied: ${selectedTimeRange.value} - ${selectedTeam.value}`);
    };

    const resetFilters = () => {
      selectedTimeRange.value = '';
      selectedTeam.value = '';
      console.log('Filters reset to defaults');
    };

    onMounted(() => {
      // No-op
    });

    return {
      userRole,
      isInQueue,
      isProcessingQueue,
      currentCall,
      isSidebarCollapsed,
      mainContentMarginLeft,
      counselors,
      achievements,
      selectedTimeRange,
      selectedTeam,
      handleQueueToggle,
      handleLogout,
      handleSidebarToggle,
      updateFilters,
      applyFilters,
      resetFilters,
    };
  },
};
</script>

<style scoped>
/* Wallboard styles moved to components.css for better organization */
</style>

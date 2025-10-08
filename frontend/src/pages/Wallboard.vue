<template>
  <div>
    <!-- SidePanel Component -->
    <SidePanel :userRole="userRole" :isInQueue="isInQueue" :isProcessingQueue="isProcessingQueue" :currentCall="currentCall" @toggle-queue="handleQueueToggle" @logout="handleLogout" @sidebar-toggle="handleSidebarToggle" />

    <!-- Main Content -->
    <div class="main-content">
      <div class="page-header">
        <div class="header-top">
          <div class="header-left">
            <h1 class="page-title">Counselor Wallboard</h1>
        </div>
      </div>
        
        <div class="search-and-controls-section">
          <div class="search-container">
            <select class="input">
              <option value="today">Today</option>
              <option value="yesterday">Yesterday</option>
              <option selected value="this-week">This Week</option>
              <option value="last-week">Last Week</option>
              <option value="this-month">This Month</option>
        </select>
          </div>
          
          <div class="view-toggle">
            <select class="input">
              <option value="all-teams">All Teams</option>
              <option value="team-a">Team A</option>
              <option value="team-b">Team B</option>
              <option value="team-c">Team C</option>
        </select>
      </div>
            </div>
            </div>

      <div class="wallboard-container">
        <!-- Dashboard Cards -->
        <div class="dashboard-grid">
          <div class="status-card">
            <div class="status-card-label">Total Calls</div>
            <div class="status-card-count">187</div>
          </div>
          <div class="status-card">
            <div class="status-card-label">Average Call Duration</div>
            <div class="status-card-count">14:32</div>
            <div class="status-card-progress">
              <div class="status-card-progress-fill" style="width: 75%"></div>
          </div>
          </div>
          <div class="status-card">
            <div class="status-card-label">Average QA Score</div>
            <div class="status-card-count">87%</div>
            <div class="status-card-progress">
              <div class="status-card-progress-fill" style="width: 87%"></div>
        </div>
            </div>
          <div class="status-card">
            <div class="status-card-label">Achievements Unlocked</div>
            <div class="status-card-count">12</div>
            </div>
          </div>

        <!-- Leaderboard Section -->
      <div class="leaderboard-section">
          <div class="page-header">
            <div class="header-top">
              <div class="header-left">
                <h2 class="page-title">Counselor Leaderboard</h2>
          </div>
          </div>
            
            <div class="filter-section">
              <button class="btn btn--secondary btn--sm active">Call Volume</button>
              <button class="btn btn--secondary btn--sm">QA Scores</button>
              <button class="btn btn--secondary btn--sm">Resolution Rate</button>
        </div>
            </div>

          <div class="leaderboard-container">
            <div class="leaderboard-item" @click="selectCounselor('sarah-mitchell')">
              <div class="leaderboard-rank">1</div>
            <div class="leaderboard-avatar">
                <img alt="Sarah Mitchell" src="/placeholder.svg?height=40&width=40"/>
            </div>
            <div class="leaderboard-info">
                <div class="leaderboard-name">Sarah Mitchell</div>
              <div class="leaderboard-stats">
                  <span>187 calls</span>
                  <span>Avg 16:42</span>
                </div>
                <div class="achievement-badge">Call Champion</div>
                </div>
              <div class="leaderboard-score">187</div>
              </div>

            <div class="leaderboard-item" @click="selectCounselor('robert-jackson')">
              <div class="leaderboard-rank">2</div>
            <div class="leaderboard-avatar">
                <img alt="Robert Jackson" src="/placeholder.svg?height=40&width=40"/>
            </div>
            <div class="leaderboard-info">
                <div class="leaderboard-name">Robert Jackson</div>
              <div class="leaderboard-stats">
                  <span>165 calls</span>
                  <span>Avg 15:18</span>
                </div>
                <div class="achievement-badge">Empathy Expert</div>
                </div>
              <div class="leaderboard-score">165</div>
              </div>

            <div class="leaderboard-item" @click="selectCounselor('emily-chan')">
              <div class="leaderboard-rank">3</div>
            <div class="leaderboard-avatar">
                <img alt="Emily Chan" src="/placeholder.svg?height=40&width=40"/>
            </div>
            <div class="leaderboard-info">
                <div class="leaderboard-name">Emily Chan</div>
              <div class="leaderboard-stats">
                  <span>142 calls</span>
                  <span>Avg 18:05</span>
                </div>
                <div class="achievement-badge">Resolution Pro</div>
                </div>
              <div class="leaderboard-score">142</div>
              </div>

            <div class="leaderboard-item" @click="selectCounselor('michael-lee')">
              <div class="leaderboard-rank">4</div>
            <div class="leaderboard-avatar">
                <img alt="Michael Lee" src="/placeholder.svg?height=40&width=40"/>
            </div>
            <div class="leaderboard-info">
                <div class="leaderboard-name">Michael Lee</div>
              <div class="leaderboard-stats">
                  <span>128 calls</span>
                  <span>Avg 12:47</span>
                </div>
                </div>
              <div class="leaderboard-score">128</div>
              </div>

            <div class="leaderboard-item" @click="selectCounselor('patience-williams')">
              <div class="leaderboard-rank">5</div>
            <div class="leaderboard-avatar">
                <img alt="Patience Williams" src="/placeholder.svg?height=40&width=40"/>
            </div>
            <div class="leaderboard-info">
                <div class="leaderboard-name">Patience Williams</div>
              <div class="leaderboard-stats">
                  <span>115 calls</span>
                  <span>Avg 14:23</span>
                </div>
                </div>
              <div class="leaderboard-score">115</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
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

    // SidePanel event handlers
    const handleQueueToggle = () => {
      isInQueue.value = !isInQueue.value;
    };
    const handleLogout = () => {
      router.push('/');
    };
    const handleSidebarToggle = (collapsed) => {
      // Static sidebar - no collapse functionality
    };

    // Counselor selection handler
    const selectCounselor = (counselorId) => {
      console.log('Selected counselor:', counselorId);
      // You can add more functionality here like opening a modal, navigating to profile, etc.
    };

    onMounted(() => {
      // Component mounted
    });

    return {
      userRole,
      isInQueue,
      isProcessingQueue,
      currentCall,
      selectCounselor,
      handleQueueToggle,
      handleLogout,
      handleSidebarToggle,
    };
  },
};
</script>

<style scoped>
/* Wallboard styles - using global component styles */
.wallboard-container {
    display: flex;
  flex-direction: column;
  gap: 20px;
  padding-top: 20px;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.leaderboard-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.leaderboard-container {
  max-height: 400px;
  overflow-y: auto;
  border-radius: var(--radius-lg);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
}

.leaderboard-container::-webkit-scrollbar {
  width: 6px;
}

.leaderboard-container::-webkit-scrollbar-track {
  background: var(--color-surface-muted);
  border-radius: 3px;
}

.leaderboard-container::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: 3px;
}

.leaderboard-container::-webkit-scrollbar-thumb:hover {
  background: var(--accent-color);
}

.leaderboard-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border-bottom: 1px solid var(--color-border);
  cursor: pointer;
  transition: all 0.2s ease;
}

.leaderboard-item:last-child {
  border-bottom: none;
}

.leaderboard-item:hover {
  background-color: rgba(255, 255, 255, 0.05);
  transform: translateX(4px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.leaderboard-item:active {
  transform: translateX(2px);
  background-color: rgba(255, 255, 255, 0.08);
}

.leaderboard-rank {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-primary);
  min-width: 30px;
}

.leaderboard-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
}

.leaderboard-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.leaderboard-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.leaderboard-name {
    font-weight: 600;
  color: var(--color-fg);
}

.leaderboard-stats {
  display: flex;
  gap: 12px;
  font-size: 14px;
  color: var(--color-muted);
}

.achievement-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 8px;
  background: var(--color-primary);
  color: white;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  margin-top: 4px;
  align-self: flex-start;
}

.leaderboard-score {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-fg);
  margin-left: 16px;
  flex-shrink: 0;
}

/* Responsive styles */
@media (max-width: 1200px) {
  .dashboard-grid {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 768px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  gap: 12px;
}

  .leaderboard-container {
    max-height: 300px;
  }
  
  .leaderboard-item {
    flex-wrap: wrap;
    padding: 12px;
  }
  
  .leaderboard-rank {
    font-size: 16px;
    min-width: 25px;
  }
  
  .leaderboard-avatar {
    width: 32px;
    height: 32px;
  }
  
  .leaderboard-stats {
    flex-direction: column;
    gap: 2px;
  }
  
  .leaderboard-score {
  font-size: 16px;
    margin-left: 8px;
  }
}

@media (max-width: 480px) {
  .leaderboard-container {
    max-height: 250px;
  }
  
  .leaderboard-item {
    padding: 8px;
  }
  
  .leaderboard-rank {
    font-size: 14px;
    min-width: 20px;
  }
  
  .leaderboard-avatar {
    width: 28px;
    height: 28px;
  }
  
  .leaderboard-name {
    font-size: 14px;
  }
  
  .leaderboard-stats {
  font-size: 12px;
  }
  
  .achievement-badge {
    font-size: 10px;
    padding: 2px 6px;
  }
  
  .leaderboard-score {
    font-size: 14px;
  }
}
</style>
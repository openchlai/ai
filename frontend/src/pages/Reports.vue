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
        <div class="header minimal">
          <div class="header-content compact">
            <h1 class="page-h1">Reports</h1>
            <p class="page-sub">Generate and view comprehensive reports across all categories</p>
          </div>
        </div>

        <!-- Report Categories -->
        <div class="reports-toolbar">
          <div class="toolbar-left">
            <h2 class="section-title">Explore</h2>
          </div>
        </div>

        <!-- Center hub + five vertical cards (infographic style) -->
        <div class="reports-orbit">
          <!-- Zigzag lines connecting cards to center -->
          <svg class="orbit-web" viewBox="0 0 600 600" aria-hidden="true">
            <defs>
              <linearGradient id="zigzagLine" x1="0" x2="1">
                <stop offset="0" stop-color="rgba(0,0,0,0.08)"/>
                <stop offset="1" stop-color="rgba(0,0,0,0.02)"/>
              </linearGradient>
            </defs>
            <!-- Zigzag lines connecting cards to center -->
            <g stroke="var(--color-border)" stroke-width="1.5" fill="none" opacity="0.6">
              <!-- Calls Reports (270deg) -->
              <path d="M300,300 L320,280 L340,300 L360,280 L380,300 L400,280 L420,300" stroke-dasharray="4,4"/>
              <!-- Cases Reports (336deg) -->
              <path d="M300,300 L320,320 L340,300 L360,320 L380,300 L400,320 L420,300" stroke-dasharray="4,4"/>
              <!-- Counsellors Reports (48deg) -->
              <path d="M300,300 L320,280 L340,300 L360,280 L380,300 L400,280 L420,300" stroke-dasharray="4,4"/>
              <!-- Channels Reports (120deg) -->
              <path d="M300,300 L320,320 L340,300 L360,320 L380,300 L400,320 L420,300" stroke-dasharray="4,4"/>
              <!-- All Reports (192deg) -->
              <path d="M300,300 L320,280 L340,300 L360,280 L380,300 L400,280 L420,300" stroke-dasharray="4,4"/>
            </g>
          </svg>

          <!-- Center hub -->
          <div class="hub-circle">
            <div class="hub-title">Reports</div>
            <div class="hub-sub">Infographics</div>
          </div>

          <!-- Orbiting cards -->
          <div class="orbit-layer">
            <button class="orbit-card info-card calls" style="--angle: 270deg" @click="navigateToReports('calls')">
              <div class="badge"><svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M22 16.92V19C22 20.1046 21.1046 21 20 21C10.6112 21 3 13.3888 3 4C3 2.89543 3.89543 2 5 2H7.08C7.5561 2 7.9582 2.3372 8.0251 2.8075L8.7 7.5C8.7669 7.9704 8.5368 8.4299 8.12 8.67L6.5 9.5C7.84 12.16 11.84 16.16 14.5 17.5L15.33 15.88C15.5701 15.4632 16.0296 15.2331 16.5 15.3L21.1925 16.0249C21.6628 16.0918 22 16.4939 22 16.97V16.92Z" stroke="currentColor" stroke-width="2"/></svg></div>
              <div class="title">Calls Reports</div>
              <div class="desc">Analytics, durations, SLAs and performance</div>
            </button>
            <button class="orbit-card info-card cases" style="--angle: 336deg" @click="navigateToReports('cases')">
              <div class="badge"><svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M14 2H6V22H18V8L14 2Z" stroke="currentColor" stroke-width="2"/><path d="M14 2V8H20" stroke="currentColor" stroke-width="2"/></svg></div>
              <div class="title">Cases Reports</div>
              <div class="desc">Progress, resolution and outcomes</div>
            </button>
            <button class="orbit-card info-card counsellors" style="--angle: 48deg" @click="navigateToReports('counsellors')">
              <div class="badge"><svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.9391 15 5.9217 15.4214 5.1716 16.1716C4.4214 16.9217 4 17.9391 4 19V21" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="7" r="4" stroke="currentColor" stroke-width="2"/></svg></div>
              <div class="title">Counsellors Reports</div>
              <div class="desc">Performance, QA and workload balance</div>
            </button>
            <button class="orbit-card info-card channels" style="--angle: 120deg" @click="navigateToReports('channels')">
              <div class="badge"><svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M21 15C21 15.53 20.79 16.04 20.41 16.41C20.04 16.79 19.53 17 19 17H7L3 21V5C3 4.47 3.21 3.96 3.59 3.59C3.96 3.21 4.47 3 5 3H19C19.53 3 20.04 3.21 20.41 3.59C20.79 3.96 21 4.47 21 5V15Z" stroke="currentColor" stroke-width="2"/></svg></div>
              <div class="title">Channels Reports</div>
              <div class="desc">Chat/WhatsApp volume, direction, disposition</div>
            </button>
            <button class="orbit-card info-card all" style="--angle: 192deg" @click="navigateToReports('all')">
              <div class="badge"><svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M9 17V7H21V17H9Z" stroke="currentColor" stroke-width="2"/><path d="M3 7H7M3 11H7M3 15H7M3 19H7" stroke="currentColor" stroke-width="2"/></svg></div>
              <div class="title">All Reports</div>
              <div class="desc">System-wide metrics and analytics</div>
            </button>
          </div>
        </div>

        <div v-if="false" class="reports-bento">
          <!-- Calls Reports Card -->
          <div class="bento-card calls-card accent">
            <div class="card-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
                <path d="M22 16.92V19.92C22.0011 20.1985 21.9441 20.4742 21.8325 20.7294C21.7209 20.9846 21.5573 21.2136 21.3521 21.4019C21.1469 21.5902 20.9046 21.7335 20.6407 21.8227C20.3768 21.9119 20.0973 21.9452 19.82 21.92H4.18C3.90273 21.9452 3.62323 21.9119 3.35932 21.8227C3.09542 21.7335 2.85313 21.5902 2.64794 21.4019C2.44275 21.2136 2.27912 20.9846 2.16753 20.7294C2.05594 20.4742 1.99889 20.1985 2 19.92V16.92L8.9 10.02C9.2836 9.63647 9.7662 9.42969 10.27 9.42969C10.7738 9.42969 11.2564 9.63647 11.64 10.02L22 16.92Z" stroke="currentColor" stroke-width="2"/>
                <path d="M2 16.92L8.9 10.02C9.2836 9.63647 9.7662 9.42969 10.27 9.42969C10.7738 9.42969 11.2564 9.63647 11.64 10.02L22 16.92" stroke="currentColor" stroke-width="2"/>
                <path d="M22 16.92V19.92C22.0011 20.1985 21.9441 20.4742 21.8325 20.7294C21.7209 20.9846 21.5573 21.2136 21.3521 21.4019C21.1469 21.5902 20.9046 21.7335 20.6407 21.8227C20.3768 21.9119 20.0973 21.9452 19.82 21.92H4.18C3.90273 21.9452 3.62323 21.9119 3.35932 21.8227C3.09542 21.7335 2.85313 21.5902 2.64794 21.4019C2.44275 21.2136 2.27912 20.9846 2.16753 20.7294C2.05594 20.4742 1.99889 20.1985 2 19.92V16.92" stroke="currentColor" stroke-width="2"/>
              </svg>
            </div>
            <div class="card-content">
              <div class="card-header">
              <h3>Calls Reports</h3>
                <button class="card-cta" @click="navigateToReports('calls')">Open</button>
              </div>
              <p>Detailed call analytics, durations, SLAs, and performance.</p>
              <div class="quick-stats">
                <div class="stat">
                  <div class="stat-value">{{ available }}</div>
                  <div class="stat-label">Active today</div>
                </div>
                <div class="stat">
                  <div class="stat-value">{{ availablePct }}%</div>
                  <div class="stat-label">Service level</div>
                </div>
                <div class="stat">
                  <div class="stat-value">8.5m</div>
                  <div class="stat-label">Avg duration</div>
                </div>
            </div>
            </div>
          </div>

          <!-- Cases Reports Card -->
          <div class="bento-card cases-card">
            <div class="card-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
                <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" stroke-width="2"/>
                <path d="M14 2V8H20" stroke="currentColor" stroke-width="2"/>
                <path d="M16 13H8" stroke="currentColor" stroke-width="2"/>
                <path d="M16 17H8" stroke="currentColor" stroke-width="2"/>
                <path d="M10 9H8" stroke="currentColor" stroke-width="2"/>
              </svg>
            </div>
            <div class="card-content">
              <div class="card-header">
              <h3>Cases Reports</h3>
                <button class="card-cta" @click="navigateToReports('cases')">Open</button>
              </div>
              <p>Track case progress, resolution times, and outcomes.</p>
              <div class="pill-row">
                <span class="pill">SLA</span>
                <span class="pill">Resolution</span>
                <span class="pill">Escalations</span>
            </div>
            </div>
          </div>

          <!-- Counsellors Reports Card -->
          <div class="bento-card counsellors-card">
            <div class="card-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
                <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21" stroke="currentColor" stroke-width="2"/>
                <circle cx="12" cy="7" r="4" stroke="currentColor" stroke-width="2"/>
              </svg>
            </div>
            <div class="card-content">
              <div class="card-header">
              <h3>Counsellors Reports</h3>
                <button class="card-cta" @click="navigateToReports('counsellors')">Open</button>
              </div>
              <p>Performance, workload balance, QA and outcomes.</p>
              <div class="pill-row">
                <span class="pill">Utilization</span>
                <span class="pill">QA</span>
                <span class="pill">Workload</span>
              </div>
            </div>
          </div>

          <!-- Channels (Chats) Reports Card -->
          <div class="bento-card channels-card accent">
            <div class="card-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
                <path d="M21 15C21 15.5304 20.7893 16.0391 20.4142 16.4142C20.0391 16.7893 19.5304 17 19 17H7L3 21V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H19C19.5304 3 20.0391 3.21071 20.4142 3.58579C20.7893 3.96086 21 4.46957 21 5V15Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div class="card-content">
              <div class="card-header">
                <h3>Channels Reports</h3>
                <button class="card-cta" @click="navigateToReports('channels')">Open</button>
              </div>
              <p>Chat, WhatsApp and other channels volume, disposition and direction.</p>
              <div class="pill-row">
                <span class="pill">Hourly</span>
                <span class="pill">Direction</span>
                <span class="pill">Disposition</span>
              </div>
            </div>
          </div>

          <!-- All Reports Card -->
          <div class="bento-card all-card accent">
            <div class="card-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
                <path d="M9 17V7H21V17H9Z" stroke="currentColor" stroke-width="2"/>
                <path d="M3 7H7" stroke="currentColor" stroke-width="2"/>
                <path d="M3 11H7" stroke="currentColor" stroke-width="2"/>
                <path d="M3 15H7" stroke="currentColor" stroke-width="2"/>
                <path d="M3 19H7" stroke="currentColor" stroke-width="2"/>
                <path d="M13 11H17" stroke="currentColor" stroke-width="2"/>
                <path d="M13 15H17" stroke="currentColor" stroke-width="2"/>
                <path d="M13 19H17" stroke="currentColor" stroke-width="2"/>
              </svg>
            </div>
            <div class="card-content">
              <div class="card-header">
              <h3>All Reports</h3>
                <button class="card-cta" @click="navigateToReports('all')">Open</button>
              </div>
              <p>Comprehensive overview of all metrics and analytics.</p>
              <div class="pill-row">
                <span class="pill">Overview</span>
                <span class="pill">Trends</span>
                <span class="pill">Exports</span>
            </div>
            </div>
          </div>
        </div>

        <!-- Center hub + five vertical cards (infographic style) -->
        <div class="reports-orbit">
          <!-- Zigzag lines connecting cards to center -->
          <svg class="orbit-web" viewBox="0 0 600 600" aria-hidden="true">
            <defs>
              <linearGradient id="zigzagLine" x1="0" x2="1">
                <stop offset="0" stop-color="rgba(0,0,0,0.08)"/>
                <stop offset="1" stop-color="rgba(0,0,0,0.02)"/>
              </linearGradient>
            </defs>
            <!-- Zigzag lines connecting cards to center -->
            <g stroke="var(--color-border)" stroke-width="1.5" fill="none" opacity="0.6">
              <!-- Calls Reports (270deg) -->
              <path d="M300,300 L320,280 L340,300 L360,280 L380,300 L400,280 L420,300" stroke-dasharray="4,4"/>
              <!-- Cases Reports (336deg) -->
              <path d="M300,300 L320,320 L340,300 L360,320 L380,300 L400,320 L420,300" stroke-dasharray="4,4"/>
              <!-- Counsellors Reports (48deg) -->
              <path d="M300,300 L320,280 L340,300 L360,280 L380,300 L400,280 L420,300" stroke-dasharray="4,4"/>
              <!-- Channels Reports (120deg) -->
              <path d="M300,300 L320,320 L340,300 L360,320 L380,300 L400,320 L420,300" stroke-dasharray="4,4"/>
              <!-- All Reports (192deg) -->
              <path d="M300,300 L320,280 L340,300 L360,280 L380,300 L400,280 L420,300" stroke-dasharray="4,4"/>
            </g>
          </svg>

          <!-- Center hub -->
          <div class="hub-circle">
            <div class="hub-title">Reports</div>
            <div class="hub-sub">Infographics</div>
          </div>

          <!-- Orbiting cards -->
          <div class="orbit-layer">
            <button class="orbit-card info-card calls" style="--angle: 270deg" @click="navigateToReports('calls')">
              <div class="badge"><svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M22 16.92V19C22 20.1046 21.1046 21 20 21C10.6112 21 3 13.3888 3 4C3 2.89543 3.89543 2 5 2H7.08C7.5561 2 7.9582 2.3372 8.0251 2.8075L8.7 7.5C8.7669 7.9704 8.5368 8.4299 8.12 8.67L6.5 9.5C7.84 12.16 11.84 16.16 14.5 17.5L15.33 15.88C15.5701 15.4632 16.0296 15.2331 16.5 15.3L21.1925 16.0249C21.6628 16.0918 22 16.4939 22 16.97V16.92Z" stroke="currentColor" stroke-width="2"/></svg></div>
              <div class="title">Calls Reports</div>
              <div class="desc">Analytics, durations, SLAs and performance</div>
            </button>
            <button class="orbit-card info-card cases" style="--angle: 336deg" @click="navigateToReports('cases')">
              <div class="badge"><svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M14 2H6V22H18V8L14 2Z" stroke="currentColor" stroke-width="2"/><path d="M14 2V8H20" stroke="currentColor" stroke-width="2"/></svg></div>
              <div class="title">Cases Reports</div>
              <div class="desc">Progress, resolution and outcomes</div>
            </button>
            <button class="orbit-card info-card counsellors" style="--angle: 48deg" @click="navigateToReports('counsellors')">
              <div class="badge"><svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.9391 15 5.9217 15.4214 5.1716 16.1716C4.4214 16.9217 4 17.9391 4 19V21" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="7" r="4" stroke="currentColor" stroke-width="2"/></svg></div>
              <div class="title">Counsellors Reports</div>
              <div class="desc">Performance, QA and workload balance</div>
            </button>
            <button class="orbit-card info-card channels" style="--angle: 120deg" @click="navigateToReports('channels')">
              <div class="badge"><svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M21 15C21 15.53 20.79 16.04 20.41 16.41C20.04 16.79 19.53 17 19 17H7L3 21V5C3 4.47 3.21 3.96 3.59 3.59C3.96 3.21 4.47 3 5 3H19C19.53 3 20.04 3.21 20.41 3.59C20.79 3.96 21 4.47 21 5V15Z" stroke="currentColor" stroke-width="2"/></svg></div>
              <div class="title">Channels Reports</div>
              <div class="desc">Chat/WhatsApp volume, direction, disposition</div>
            </button>
            <button class="orbit-card info-card all" style="--angle: 192deg" @click="navigateToReports('all')">
              <div class="badge"><svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M9 17V7H21V17H9Z" stroke="currentColor" stroke-width="2"/><path d="M3 7H7M3 11H7M3 15H7M3 19H7" stroke="currentColor" stroke-width="2"/></svg></div>
              <div class="title">All Reports</div>
              <div class="desc">System-wide metrics and analytics</div>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import SidePanel from '@/components/SidePanel.vue'

const router = useRouter()

// SidePanel props and state
const userRole = ref("admin")
const isInQueue = ref(false)
const isProcessingQueue = ref(false)
const currentCall = ref(null)

// SidePanel event handlers
const handleQueueToggle = () => {
  isInQueue.value = !isInQueue.value
}

const handleLogout = () => {
  // Handle logout logic
  console.log("Logout clicked")
}

const handleSidebarToggle = () => {
  // Handle sidebar toggle
  console.log("Sidebar toggle clicked")
}

// Navigation function
const navigateToReports = (category) => {
  router.push({
    name: 'ReportsCategory',
    params: { category }
  })
}

// Simple chart demo state
const dateFrom = ref('')
const dateTo = ref('')
const total = ref(122)
const available = ref(54)
const availablePct = computed(() => Math.min(100, Math.max(0, Math.round((available.value/total.value)*100))))
const oooPct = computed(() => Math.max(0, 100 - availablePct.value - 30))

// Wheel/grid switch
const wheelView = ref(false)
</script>

<style scoped>
/* Reports landing styling */
.reports-toolbar { display:flex; align-items:center; justify-content:space-between; margin-bottom:12px; }
.header.minimal { border-bottom:none; padding-bottom: 2px; }
.header-content.compact { gap: 4px; }
.page-h1 { margin: 0; color: var(--color-fg); }
.page-sub { margin: 0; color: var(--color-muted); font-size: 14px; }
.section-title { font-size:18px; margin:0; }
.reports-bento { display:grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap:16px; }
.bento-card { display:flex; gap:14px; align-items:flex-start; background: var(--color-surface); border:1px solid var(--color-border); border-radius: 18px; padding:16px; transition: transform .2s, box-shadow .2s; min-height: 160px; }
.bento-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-sm); }
.bento-card.accent { background: color-mix(in oklab, var(--color-primary) 8%, var(--color-surface)); }
.card-icon { width:48px; height:48px; border-radius:12px; display:flex; align-items:center; justify-content:center; background: var(--color-surface); border:1px solid var(--color-border); flex-shrink:0; }
.card-content { flex:1; display:flex; flex-direction:column; gap:8px; }
.card-header { display:flex; align-items:center; justify-content:space-between; gap:8px; }
.card-cta { border:1px solid var(--color-border); background: var(--color-surface); border-radius: 999px; padding:6px 10px; font-weight:600; cursor:pointer; }
.pill-row { display:flex; gap:6px; flex-wrap:wrap; }
.pill { background: var(--color-surface); border:1px solid var(--color-border); border-radius: 999px; padding:4px 8px; font-size:12px; }
.quick-stats { display:grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap:10px; }
.stat { background: var(--color-surface); border:1px solid var(--color-border); border-radius: 12px; padding:10px; text-align:center; }
.stat-value { font-weight:800; font-size:18px; }
.stat-label { font-size:12px; color: var(--color-muted); }
.mini-chart { display:none; }
.view-switch .active { background: var(--color-primary); border-color: var(--color-primary); color:#fff; }

/* Hub + vertical cards (exact-like infographic) */
.reports-orbit { position: relative; display:grid; grid-template-columns: 1fr; place-items:center; padding: 0; height: calc(100vh - 140px); overflow: visible; }
.hub-circle { position:absolute; left:50%; top:50%; transform: translate(-50%, -50%); width: 260px; height:260px; border-radius:50%; background: radial-gradient(circle at 35% 35%, #fff, #f4f4f4); box-shadow: 0 8px 26px rgba(0,0,0,.08), inset 0 -6px 16px rgba(0,0,0,.06); display:flex; align-items:center; justify-content:center; flex-direction:column; margin:0; z-index: 2; }
.hub-circle::after { content:""; position:absolute; inset:-26px; border-radius:50%; background: radial-gradient(circle at center, rgba(0,0,0,.06), transparent 60%); filter: blur(10px); z-index:-1; }
.hub-title { font-weight:900; font-size:24px; letter-spacing:.4px; }
.hub-sub { color: var(--color-muted); font-size:12px; margin-top:4px; }
.orbit-web { position:absolute; width: min(700px, 65vw); height: min(700px, 65vw); opacity:.55; pointer-events:none; filter: drop-shadow(0 6px 14px rgba(0,0,0,.04)); }
.orbit-layer { position: relative; width: min(700px, 65vw); height: min(700px, 65vw); }
.orbit-card { --radius: calc(min(700px, 65vw) / 2.2); position:absolute; left: 50%; top: 50%; transform: translate(-50%, -50%) rotate(var(--angle)) translate(var(--radius)) rotate(calc(-1 * var(--angle))); }
.info-card { width: 160px; padding:12px 10px 14px; border-radius:20px; background:linear-gradient(180deg,#fff,#f6f6f6); border:1px solid var(--color-border); box-shadow: 0 8px 20px rgba(0,0,0,.06); text-align:center; cursor:pointer; transition: transform .15s ease, box-shadow .15s ease; }
.info-card:hover { transform: translate(-50%, -50%) rotate(var(--angle)) translate(var(--radius)) rotate(calc(-1 * var(--angle))) translateY(-3px); box-shadow: 0 14px 28px rgba(0,0,0,.10); }
.info-card .badge { width:48px; height:48px; border-radius:50%; margin:0 auto 8px; display:grid; place-items:center; background:linear-gradient(180deg,#fafafa,#efefef); border:1px solid var(--color-border); box-shadow: 0 4px 12px rgba(0,0,0,.08); }
.info-card .badge svg { color: var(--color-fg); stroke: var(--color-fg); opacity: 0.95; }
.info-card .title { font-weight:800; font-size:14px; }
.info-card .desc { color: var(--color-muted); font-size:12px; margin-top:6px; }

/* Color accents use system tokens */
.info-card.calls .badge { background: radial-gradient(circle at 40% 35%, #fff, color-mix(in oklab, var(--color-primary) 24%, #ffffff)); border-color: var(--color-primary); }
.info-card.calls .badge svg { color: var(--color-primary); stroke: var(--color-primary); }
.info-card.calls .title { color: var(--color-primary); }

.info-card.cases .badge { background: radial-gradient(circle at 40% 35%, #fff, color-mix(in oklab, var(--success-color) 24%, #ffffff)); border-color: var(--success-color); }
.info-card.cases .badge svg { color: var(--success-color); stroke: var(--success-color); }
.info-card.cases .title { color: var(--success-color); }

.info-card.counsellors .badge { background: radial-gradient(circle at 40% 35%, #fff, color-mix(in oklab, var(--accent-color) 24%, #ffffff)); border-color: var(--accent-color); }
.info-card.counsellors .badge svg { color: var(--accent-color); stroke: var(--accent-color); }
.info-card.counsellors .title { color: var(--accent-color); }

.info-card.channels .badge { background: radial-gradient(circle at 40% 35%, #fff, color-mix(in oklab, var(--color-primary-hover) 24%, #ffffff)); border-color: var(--color-primary-hover); }
.info-card.channels .badge svg { color: var(--color-primary-hover); stroke: var(--color-primary-hover); }
.info-card.channels .title { color: var(--color-primary-hover); }

.info-card.all .badge { background: radial-gradient(circle at 40% 35%, #fff, color-mix(in oklab, var(--color-fg) 10%, #ffffff)); border-color: color-mix(in oklab, var(--color-fg) 30%, #cccccc); }
.info-card.all .badge svg { color: var(--color-fg); stroke: var(--color-fg); }
.info-card.all .title { color: var(--color-fg); }
</style>


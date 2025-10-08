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


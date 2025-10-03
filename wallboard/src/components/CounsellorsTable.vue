<template>
  <div class="counsellors-section">
    <div class="section-header">
      <h2 class="section-title">Counsellors Online: {{ onlineCount }}</h2>
      <div class="filter-buttons">
        <!-- Filter buttons can be added here if needed -->
      </div>
    </div>
    <div class="counsellors-table">
      <div class="table-header">
        <div class="col-ext">Ext.</div>
        <div class="col-name">Name</div>
        <div class="col-caller">Caller</div>
        <div class="col-answered">Answered</div>
        <div class="col-missed">Missed</div>
        <div class="col-talk-time">Talk Time</div>
        <div class="col-queue-status">Queue Status</div>
        <div class="col-duration">Duration</div>
      </div>
      <div class="table-body">
        <div v-if="counsellors.length === 0" class="no-counsellors-row">
          <div class="no-counsellors-text">No counsellors currently online</div>
        </div>
        <div 
          v-for="counsellor in counsellors" 
          :key="counsellor.id"
          class="table-row"
        >
          <div class="col-ext">{{ counsellor.extension }}</div>
          <div class="col-name">
            <span v-if="counsellor.nameLoading" class="name-loading">Loading...</span>
            <span v-else>{{ counsellor.name }}</span>
          </div>
          <div class="col-caller">{{ counsellor.caller || '--' }}</div>
          <div class="col-answered">
            <span v-if="counsellor.statsLoading" class="name-loading">Loading...</span>
            <span v-else>{{ counsellor.answered || '0' }}</span>
          </div>
          <div class="col-missed">
            <span v-if="counsellor.statsLoading" class="name-loading">Loading...</span>
            <span v-else>{{ counsellor.missed || '0' }}</span>
          </div>
          <div class="col-talk-time">{{ counsellor.talkTime || '--' }}</div>
          <div :class="['col-queue-status', getStatusClass(counsellor.queueStatus)]">
            {{ counsellor.queueStatus || 'Offline' }}
          </div>
          <div class="col-duration">{{ counsellor.duration || '--' }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CounsellorsTable',
  props: {
    counsellors: {
      type: Array,
      required: true,
      default: () => []
    },
    onlineCount: {
      type: Number,
      required: true,
      default: 0
    }
  },
  methods: {
    getStatusClass(status) {
      const s = (status || 'Available').toString().toLowerCase()
      if (s.includes('on call')) return 'status-oncall'
      if (s.includes('ring')) return 'status-ringing'
      if (s.includes('queue')) return 'status-inqueue'
      if (s.includes('available')) return 'status-available'
      if (s.includes('offline')) return 'status-offline'
      return 'status-neutral'
    }
  }
}
</script>

<style scoped>
.counsellors-section {
  margin: 30px 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.dark-mode .section-title {
  color: #f9fafb;
}

.counsellors-table {
  background: #ffffff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.dark-mode .counsellors-table {
  background: #2d3748;
}

.table-header {
  display: grid;
  grid-template-columns: 80px 150px 120px 100px 100px 120px 150px 1fr;
  gap: 15px;
  padding: 16px 20px;
  background: #f8fafc;
  font-weight: 600;
  font-size: 0.875rem;
  color: #374151;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.dark-mode .table-header {
  background: #374151;
  color: #d1d5db;
}

.table-body {
  max-height: 400px;
  overflow-y: auto;
}

.table-row {
  display: grid;
  grid-template-columns: 80px 150px 120px 100px 100px 120px 150px 1fr;
  gap: 15px;
  padding: 12px 20px;
  border-bottom: 1px solid #e5e7eb;
  transition: background-color 0.2s ease;
}

.table-row:hover {
  background: #f8fafc;
}

.table-row:last-child {
  border-bottom: none;
}

.dark-mode .table-row {
  border-bottom-color: #4b5563;
  color: #e2e8f0;
}

.dark-mode .table-row:hover {
  background: #374151;
}

.table-header > div,
.table-row > div {
  display: flex;
  align-items: center;
  font-size: 0.875rem;
}

.no-counsellors-row {
  padding: 40px 20px;
  text-align: center;
}

.no-counsellors-text {
  color: #6b7280;
  font-style: italic;
}

.dark-mode .no-counsellors-text {
  color: #9ca3af;
}

.name-loading {
  color: #888;
  font-style: italic;
}

.dark-mode .name-loading {
  color: #9ca3af;
}

/* Status color classes */
.status-oncall {
  color: #10b981;
  font-weight: 600;
}

.status-ringing {
  color: #f59e0b;
  font-weight: 600;
  animation: blink 1.5s ease-in-out infinite;
}

.status-inqueue {
  color: #3b82f6;
  font-weight: 600;
}

.status-available {
  color: #6b7280;
  font-weight: 500;
}

.status-offline {
  color: #ef4444;
  font-weight: 600;
}

.status-neutral {
  color: #6b7280;
}

@keyframes blink {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

/* Responsive design */
@media (max-width: 1200px) {
  .table-header,
  .table-row {
    grid-template-columns: 70px 130px 110px 90px 90px 110px 130px 1fr;
    gap: 12px;
  }
}

@media (max-width: 768px) {
  .counsellors-table {
    overflow-x: auto;
  }
  
  .table-header,
  .table-row {
    display: flex;
    min-width: 800px;
    gap: 10px;
  }
  
  .table-header > div,
  .table-row > div {
    flex: 1;
    min-width: 80px;
  }
  
  .col-name {
    min-width: 120px;
  }
  
  .col-queue-status {
    min-width: 130px;
  }
}

@media (max-width: 480px) {
  .section-header {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }
  
  .counsellors-table {
    margin: 0 -10px;
    border-radius: 8px;
  }
}
</style>
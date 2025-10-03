<template>
  <div class="counsellors-section">
    <div class="section-header">
      <h2 class="section-title">Callers Online: {{ onlineCount }}</h2>
    </div>
    <div class="counsellors-table">
      <div class="table-header callers-header">
        <div class="col-caller-num">Caller Number</div>
        <div class="col-vector">Queue</div>
        <div class="col-wait-time">Wait Time</div>
        <div class="col-status">Status</div>
      </div>
      <div class="table-body">
        <div v-if="callers.length === 0" class="no-counsellors-row">
          <div class="no-counsellors-text">No callers currently online</div>
        </div>
        <div 
          v-for="caller in callers" 
          :key="caller.id"
          class="table-row callers-row"
        >
          <div class="col-caller-num">{{ caller.callerNumber || '--' }}</div>
          <div class="col-vector">{{ caller.vector || '--' }}</div>
          <div class="col-wait-time">{{ caller.waitTime || '--' }}</div>
          <div :class="['col-status', getStatusClass(caller.queueStatus)]">
            {{ caller.queueStatus || 'Unknown' }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CallersTable',
  props: {
    callers: {
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

.callers-header,
.callers-row {
  display: grid !important;
  grid-template-columns: 180px 120px 120px 1fr !important;
  gap: 15px !important;
}

.table-header {
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

.callers-header > div,
.callers-row > div {
  padding: 8px 12px !important;
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
@media (max-width: 768px) {
  .counsellors-table {
    overflow-x: auto;
  }
  
  .callers-header,
  .callers-row {
    display: flex !important;
    min-width: 600px;
    gap: 10px !important;
  }
  
  .callers-header > div,
  .callers-row > div {
    flex: 1;
    min-width: 120px;
    padding: 8px 12px !important;
  }
  
  .col-caller-num {
    min-width: 150px;
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
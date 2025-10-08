<template>
  <div class="calls-cards-section">
    <div class="section-header">
      <h2 class="section-title">Today's Call Status</h2>
    </div>
    <div class="calls-cards-grid">
      <div v-if="loading" class="loading-message">
        Loading call status data...
      </div>
      <div v-else-if="error" class="error-message">
        Error loading call status: {{ error }}
      </div>
      <div v-else-if="cards.length === 0" class="no-data-message">
        No call status data available
      </div>
      <div 
        v-else
        v-for="card in cards" 
        :key="card.id"
        :class="['call-status-card', `card-${card.variant}`]"
      >
        <div class="card-content">
          <div class="card-count">{{ card.count }}</div>
          <div class="card-label">{{ card.label }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CallsStatusCards',
  props: {
    loading: {
      type: Boolean,
      default: false
    },
    error: {
      type: String,
      default: null
    },
    cards: {
      type: Array,
      required: true,
      default: () => []
    }
  }
}
</script>

<style scoped>
.calls-cards-section {
  margin: 20px 0;
}

.section-header {
  margin-bottom: 15px;
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

.calls-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
  margin-top: 15px;
}

.call-status-card {
  background: #ffffff;
  border-radius: 12px;
  padding: 20px;
  transition: transform 0.2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;
}

.call-status-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.dark-mode .call-status-card {
  background: #2d3748;
}

.card-content {
  text-align: center;
  position: relative;
  z-index: 1;
}

.card-count {
  font-size: 2.5rem;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 8px;
}

.card-label {
  font-size: 0.9rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  opacity: 0.8;
}

/* Card variants with enhanced visual styling */
.card-success {
  border-left: 4px solid #10b981;
}

.card-success .card-count {
  color: #10b981;
}

.card-warning {
  border-left: 4px solid #f59e0b;
}

.card-warning .card-count {
  color: #f59e0b;
}

.card-danger {
  border-left: 4px solid #ef4444;
}

.card-danger .card-count {
  color: #ef4444;
}

.card-info {
  border-left: 4px solid #3b82f6;
}

.card-info .card-count {
  color: #3b82f6;
}

.card-primary {
  border-left: 4px solid #8b5cf6;
}

.card-primary .card-count {
  color: #8b5cf6;
}

.card-secondary {
  border-left: 4px solid #6b7280;
}

.card-secondary .card-count {
  color: #6b7280;
}

/* Background gradient effects for cards */
.card-success::after {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.05), transparent);
}

.card-warning::after {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.05), transparent);
}

.card-danger::after {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.05), transparent);
}

.card-info::after {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.05), transparent);
}

.card-primary::after {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.05), transparent);
}

.card-secondary::after {
  background: linear-gradient(135deg, rgba(107, 114, 128, 0.05), transparent);
}

.call-status-card::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  border-radius: 12px;
}

.loading-message, .error-message, .no-data-message {
  grid-column: 1 / -1;
  text-align: center;
  padding: 20px;
  border-radius: 8px;
  background: #f8f9fa;
  color: #6c757d;
  font-weight: 500;
}

.error-message {
  background: #fee;
  color: #dc3545;
}

.dark-mode .loading-message,
.dark-mode .no-data-message {
  background: #374151;
  color: #9ca3af;
}

.dark-mode .error-message {
  background: #450a0a;
  color: #f87171;
}

/* Pulse animation for active cards */
.card-success:hover,
.card-info:hover {
  animation: subtle-glow 0.3s ease-in-out;
}

@keyframes subtle-glow {
  0% {
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }
  100% {
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  }
}

/* Responsive design */
@media (max-width: 768px) {
  .calls-cards-grid {
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 12px;
  }
  
  .call-status-card {
    padding: 16px;
  }
  
  .card-count {
    font-size: 2rem;
  }
  
  .card-label {
    font-size: 0.8rem;
  }
}

@media (max-width: 480px) {
  .calls-cards-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }
  
  .call-status-card {
    padding: 14px;
  }
  
  .card-count {
    font-size: 1.8rem;
  }
  
  .card-label {
    font-size: 0.75rem;
  }
}
</style>
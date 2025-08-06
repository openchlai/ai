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
    <div class="calls-container">
      <div class="header">
        <h1 class="page-title">Calls</h1>
        <div class="header-actions">
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
      </div>
      
      <div class="view-tabs">
        <div class="view-tab" :class="{ active: activeView === 'timeline' }" @click="activeView = 'timeline'">Timeline</div>
        <div class="view-tab" :class="{ active: activeView === 'table' }" @click="activeView = 'table'">Table View</div>
        <div class="view-tab" :class="{ active: activeView === 'queue' }" @click="activeView = 'queue'">Call Queue</div>
      </div>

      <!-- Status Cards - Horizontal Layout -->
      <div class="status-cards">
        <div class="status-card" v-for="status in statusItems" :key="status.label">
          <div class="status-card-header">
            <div class="status-card-label">{{ status.label }}</div>
            <div class="status-card-count">{{ status.count }}</div>
          </div>
          <div class="status-card-progress">
            <div class="status-card-progress-fill" :style="{ width: status.percentage + '%' }"></div>
          </div>
        </div>
      </div>
      
      <!-- Timeline View -->
      <div class="view-container" v-show="activeView === 'timeline'">
        <div class="time-section" v-for="(group, label) in groupedCalls" :key="label">
          <h2 class="time-section-title">{{ label }}</h2>
          <div class="call-list">
            <div 
              v-for="(call, index) in group" 
              :key="call.id" 
              class="call-item glass-card fine-border" 
              :class="{ 
                selected: call.id === selectedCallId,
                'timeline-connector': index < group.length - 1
              }" 
              @click="selectCall(call.id)"
            >
              <div class="call-icon">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M22 16.92V19C22 20.1046 21.1046 21 20 21C10.6112 21 3 13.3888 3 4C3 2.89543 3.89543 2 5 2H7.08C7.55607 2 7.95823 2.33718 8.02513 2.80754L8.7 7.5C8.76694 7.97036 8.53677 8.42989 8.12 8.67L6.5 9.5C7.84 12.16 11.84 16.16 14.5 17.5L15.33 15.88C15.5701 15.4632 16.0296 15.2331 16.5 15.3L21.1925 16.0249C21.6628 16.0918 22 16.4939 22 16.97V16.92Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </div>
              <div class="call-details">
                <div class="call-type">{{ call.title }}</div>
                <div class="call-time">{{ call.time }}</div>
                <div class="call-meta">
                  <span class="case-link">Case: #{{ call.caseId }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Table View -->
      <div class="view-container" v-show="activeView === 'table'">
        <div class="calls-table-container">
          <table class="calls-table">
            <thead>
              <tr>
                <th>Call ID</th>
                <th>Case ID</th>
                <th>Date</th>
                <th>Time</th>
                <th>Status</th>
                <th>Agent</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr 
                v-for="call in allCalls" 
                :key="call.id" 
                :class="{ selected: call.id === selectedCallId }" 
                @click="selectCall(call.id)"
              >
                <td>
                  <span class="call-id">#{{ call.id }}</span>
                </td>
                <td>
                  <span class="case-link">#{{ call.caseId }}</span>
                </td>
                <td>{{ call.dateLabel }}</td>
                <td>{{ call.time }}</td>
                <td>
                  <span :class="['status-badge', getStatusClass(call.status)]">{{ call.status }}</span>
                </td>
                <td>{{ call.agent || 'Unassigned' }}</td>
                <td>
                  <div class="table-actions">
                    <button class="action-btn view-btn" @click.stop="viewCallDetails(call.id)" title="View Details">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M1 12S5 4 12 4s11 8 11 8-4 8-11 8S1 12 1 12z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                      </svg>
                    </button>
                    <button class="action-btn link-btn" @click.stop="linkToCase(call.id)" title="Link to Case">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M10 13C10.4295 13.5741 10.9774 14.0491 11.6066 14.3929C12.2357 14.7367 12.9315 14.9411 13.6467 14.9923C14.3618 15.0435 15.0796 14.9403 15.7513 14.6897C16.4231 14.4392 17.0331 14.047 17.54 13.54L20.54 10.54C21.4508 9.59695 21.9548 8.33394 21.9434 7.02296C21.932 5.71198 21.4061 4.45791 20.4791 3.53087C19.5521 2.60383 18.298 2.07799 16.987 2.0666C15.676 2.0552 14.413 2.55918 13.47 3.47L11.75 5.18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M14 11C13.5705 10.4259 13.0226 9.95085 12.3934 9.60706C11.7643 9.26327 11.0685 9.05885 10.3533 9.00769C9.63819 8.95653 8.92037 9.05973 8.24864 9.31028C7.5769 9.56084 6.9669 9.95303 6.46 10.46L3.46 13.46C2.54918 14.403 2.04520 15.6661 2.0566 16.9771C2.06799 18.288 2.59383 19.5421 3.52087 20.4691C4.44791 21.3962 5.70198 21.922 7.01296 21.9334C8.32394 21.9448 9.58695 21.4408 10.53 20.53L12.24 18.82" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                      </svg>
                    </button>
                    <button class="action-btn case-btn" @click.stop="viewCase(call.caseId)" title="View Case">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        <polyline points="14,2 14,8 20,8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Queue View -->
      <div class="view-container" v-show="activeView === 'queue'">
        <div class="queue-section">
          <h2 class="queue-title">Call Queue Management</h2>
          <div class="queue-stats">
            <div class="queue-stat">
              <div class="stat-value">{{ queueStats.waiting }}</div>
              <div class="stat-label">Waiting</div>
            </div>
            <div class="queue-stat">
              <div class="stat-value">{{ queueStats.active }}</div>
              <div class="stat-label">Active</div>
            </div>
            <div class="queue-stat">
              <div class="stat-value">{{ queueStats.agents }}</div>
              <div class="stat-label">Agents Online</div>
            </div>
          </div>
          
          <div class="queue-calls">
            <h3 class="queue-subtitle">Pending Calls</h3>
            <div class="queue-call-list">
              <div v-for="call in queueCalls" :key="call.id" class="queue-call-item">
                <div class="queue-call-info">
                  <div class="queue-call-type">{{ call.type }}</div>
                  <div class="queue-call-details">
                    <span>Wait Time: {{ call.waitTime }}</span>
                    <span>Case: #{{ call.caseId }}</span>
                  </div>
                </div>
                <div class="queue-call-actions">
                  <button class="queue-action-btn accept" @click="acceptQueueCall(call.id)" v-if="isInQueue">
                    Accept
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- Call Details Panel -->
  <div class="call-details-panel" :class="{ active: showCallDetails }" id="call-details-panel">
    <div class="call-details-header">
      <div class="call-details-title">{{ selectedCallDetails?.title || 'Call Details' }}</div>
      <button class="close-details" @click="closeCallDetails">×</button>
    </div>
    <div class="call-details-content" v-if="selectedCallDetails">
      <div class="detail-item">
        <div class="detail-label">Call ID</div>
        <div class="detail-value">#{{ selectedCallDetails.id }}</div>
      </div>
      <div class="detail-item">
        <div class="detail-label">Case ID</div>
        <div class="detail-value">
          <a href="#" @click.prevent="viewCase(selectedCallDetails.caseId)" class="case-link">
            #{{ selectedCallDetails.caseId }}
          </a>
        </div>
      </div>
      <div class="detail-item">
        <div class="detail-label">Call Title</div>
        <div class="detail-value">{{ selectedCallDetails.callTitle }}</div>
      </div>
      <div class="detail-item">
        <div class="detail-label">Caller</div>
        <div class="detail-value">{{ selectedCallDetails.callerName }}</div>
      </div>
      <div class="detail-item">
        <div class="detail-label">Duration</div>
        <div class="detail-value">{{ selectedCallDetails.duration }}</div>
      </div>
      <div class="detail-item">
        <div class="detail-label">Call Start</div>
        <div class="detail-value">{{ selectedCallDetails.callStart }}</div>
      </div>
      <div class="detail-item">
        <div class="detail-label">Call End</div>
        <div class="detail-value">{{ selectedCallDetails.callEnd }}</div>
      </div>
      <div class="detail-item">
        <div class="detail-label">Disposition</div>
        <div class="detail-value">{{ selectedCallDetails.disposition }}</div>
      </div>
      <div class="detail-item">
        <div class="detail-label">Date</div>
        <div class="detail-value">{{ selectedCallDetails.date }}</div>
      </div>
      <div class="detail-item">
        <div class="detail-label">Escalated to</div>
        <div class="detail-value">{{ selectedCallDetails.escalatedTo }}</div>
      </div>
      <div class="detail-item">
        <div class="detail-label">Priority</div>
        <div class="detail-value">
          <span class="priority-badge" :class="selectedCallDetails.priority">{{ selectedCallDetails.priority }}</span>
        </div>
      </div>
    </div>
  </div>

  <!-- Queue Popup Modal -->
  <div v-if="showQueuePopup" class="modal-overlay" @click="closeQueuePopup">
    <div class="queue-popup" @click.stop>
      <div class="queue-popup-header">
        <h3>Queue Members</h3>
        <button class="modal-close" @click="closeQueuePopup">×</button>
      </div>
      <div class="queue-members">
        <div v-for="member in queueMembers" :key="member.id" class="queue-member-card" @click="confirmJoinQueue">
          <div class="member-avatar">
            <img :src="member.avatar" :alt="member.name" />
            <div class="status-indicator" :class="member.status"></div>
          </div>
          <div class="member-info">
            <div class="member-name">{{ member.name }}</div>
            <div class="member-role">{{ member.role }}</div>
            <div class="member-status">{{ member.statusText }}</div>
          </div>
        </div>
      </div>
      <div class="queue-popup-footer">
        <button class="btn-primary" @click="confirmJoinQueue">Join Queue</button>
      </div>
    </div>
  </div>

  <!-- Ringing Call Interface -->
  <div v-if="showRingingInterface && ringingCall" class="ringing-overlay">
    <div class="ringing-container">
      <div class="ringing-header">
        <div class="call-type-badge" :class="ringingCall.priority">
          {{ ringingCall.type }}
        </div>
      </div>
      
      <div class="caller-info">
        <div class="caller-avatar">
          <svg width="60" height="60" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="12" cy="7" r="4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="caller-name">{{ ringingCall.callerName }}</div>
        <div class="caller-number">{{ ringingCall.number || 'Unknown Number' }}</div>
        <div class="call-duration">{{ ringingDuration }}</div>
      </div>

      <div class="ringing-animation">
        <div class="pulse-ring"></div>
        <div class="pulse-ring delay-1"></div>
        <div class="pulse-ring delay-2"></div>
      </div>

      <div class="call-actions">
        <button class="call-btn decline" @click="declineCall">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M22 16.92V19C22 20.1046 21.1046 21 20 21C10.6112 21 3 13.3888 3 4C3 2.89543 3.89543 2 5 2H7.08C7.55607 2 7.95823 2.33718 8.02513 2.80754L8.7 7.5C8.76694 7.97036 8.53677 8.42989 8.12 8.67L6.5 9.5C7.84 12.16 11.84 16.16 14.5 17.5L15.33 15.88C15.5701 15.4632 16.0296 15.2331 16.5 15.3L21.1925 16.0249C21.6628 16.0918 22 16.4939 22 16.97V16.92Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
        <button class="call-btn answer" @click="answerCall">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M22 16.92V19C22 20.1046 21.1046 21 20 21C10.6112 21 3 13.3888 3 4C3 2.89543 3.89543 2 5 2H7.08C7.55607 2 7.95823 2.33718 8.02513 2.80754L8.7 7.5C8.76694 7.97036 8.53677 8.42989 8.12 8.67L6.5 9.5C7.84 12.16 11.84 16.16 14.5 17.5L15.33 15.88C15.5701 15.4632 16.0296 15.2331 16.5 15.3L21.1925 16.0249C21.6628 16.0918 22 16.4939 22 16.97V16.92Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>
    </div>
  </div>

  <!-- Case Options Modal - Shows after answering call -->
  <div v-if="showCaseOptions" class="modal-overlay" @click="closeCaseOptions">
    <div class="case-options-modal" @click.stop>
      <div class="modal-header">
        <h3>Case Management Options</h3>
        <div class="call-timer-header">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
            <polyline points="12,6 12,12 16,14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          {{ callDuration }}
        </div>
      </div>
      <div class="modal-body">
        <div class="case-options-grid">
          <div class="case-option-card" @click="selectCaseOption('new')">
            <div class="option-icon new-case">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 5V19M5 12H19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div class="option-content">
              <div class="option-title">Open New Case</div>
              <div class="option-description">Create a new case for this call and start documenting the incident</div>
            </div>
            <div class="option-arrow">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M9 18L15 12L9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </div>

          <div class="case-option-card" @click="selectCaseOption('existing')">
            <div class="option-icon existing-case">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <polyline points="14,2 14,8 20,8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M16 13H8M16 17H8M10 9H8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div class="option-content">
              <div class="option-title">Open Existing Case</div>
              <div class="option-description">Link this call to an existing case and edit case details</div>
            </div>
            <div class="option-arrow">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M9 18L15 12L9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </div>

          <div class="case-option-card" @click="selectCaseOption('disposition')">
            <div class="option-icon disposition-call">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M9 12L11 14L15 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div class="option-content">
              <div class="option-title">Disposition Call</div>
              <div class="option-description">Complete call disposition and end the call with proper documentation</div>
            </div>
            <div class="option-arrow">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M9 18L15 12L9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Existing Case Search Modal -->
  <div v-if="showExistingCaseSearch" class="modal-overlay" @click="closeExistingCaseSearch">
    <div class="existing-case-modal" @click.stop>
      <div class="modal-header">
        <h3>Select Existing Case</h3>
        <div class="call-timer-header">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
            <polyline points="12,6 12,12 16,14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          {{ callDuration }}
        </div>
        <button class="modal-close" @click="closeExistingCaseSearch">×</button>
      </div>
      <div class="modal-body">
        <div class="case-search">
          <input 
            type="text" 
            v-model="caseSearchQuery"
            placeholder="Search cases by ID, name, or client..." 
            class="search-input"
          />
        </div>
        <div class="existing-cases-list">
          <div 
            v-for="existingCase in filteredExistingCases" 
            :key="existingCase.id" 
            class="existing-case-item"
            @click="selectExistingCase(existingCase)"
          >
            <div class="case-info">
              <div class="case-header">
                <div class="case-id">#{{ existingCase.id }}</div>
                <div class="case-priority" :class="existingCase.priority.toLowerCase()">{{ existingCase.priority }}</div>
              </div>
              <div class="case-title">{{ existingCase.title }}</div>
              <div class="case-meta">
                <span class="case-client">Client: {{ existingCase.client }}</span>
                <span class="case-date">{{ existingCase.date }}</span>
              </div>
              <div class="case-status">
                <span class="status-badge" :class="existingCase.status.toLowerCase()">{{ existingCase.status }}</span>
              </div>
            </div>
            <div class="case-select-arrow">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M9 18L15 12L9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Case Form During Call -->
  <div v-if="showCaseForm" class="case-form-overlay">
    <div class="case-form-container">
      <div class="case-form-header">
        <div class="form-title">
          <h3>{{ caseFormMode === 'new' ? 'Create New Case' : 'Edit Case' }}</h3>
          <div class="case-id">Case #{{ currentCaseId }}</div>
        </div>
        <div class="call-timer">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
            <polyline points="12,6 12,12 16,14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          {{ callDuration }}
        </div>
        <button class="minimize-btn" @click="minimizeCaseForm">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M6 9L12 15L18 9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>

      <div class="case-form-content">
        <form @submit.prevent="saveCaseForm">
          <div class="form-section">
            <div class="section-title">Basic Information</div>
            <div class="form-group">
              <label for="case-name">Case Name*</label>
              <input 
                v-model="caseFormData.caseName"
                class="form-control" 
                id="case-name" 
                placeholder="Enter case name" 
                required 
                type="text"
              />
            </div>
            <div class="form-group">
              <label for="case-description">Description*</label>
              <textarea 
                v-model="caseFormData.description"
                class="form-control" 
                id="case-description" 
                placeholder="Enter case description" 
                required
                rows="3"
              ></textarea>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label for="case-priority">Priority*</label>
                <select 
                  v-model="caseFormData.priority"
                  class="form-control" 
                  id="case-priority" 
                  required
                >
                  <option value="">Select priority</option>
                  <option value="Critical">Critical</option>
                  <option value="High">High</option>
                  <option value="Medium">Medium</option>
                  <option value="Low">Low</option>
                </select>
              </div>
              <div class="form-group">
                <label for="case-type">Type*</label>
                <select 
                  v-model="caseFormData.type"
                  class="form-control" 
                  id="case-type" 
                  required
                >
                  <option value="">Select type</option>
                  <option value="Domestic Violence">Domestic Violence</option>
                  <option value="Sexual Assault">Sexual Assault</option>
                  <option value="Human Trafficking">Human Trafficking</option>
                  <option value="Child Abuse">Child Abuse</option>
                  <option value="Elder Abuse">Elder Abuse</option>
                  <option value="Stalking">Stalking</option>
                </select>
              </div>
            </div>
            <div class="form-group">
              <label for="caller-info">Caller Information</label>
              <textarea 
                v-model="caseFormData.callerInfo"
                class="form-control" 
                id="caller-info" 
                placeholder="Enter caller information and notes"
                rows="3"
              ></textarea>
            </div>
            <div class="form-group">
              <label for="incident-details">Incident Details</label>
              <textarea 
                v-model="caseFormData.incidentDetails"
                class="form-control" 
                id="incident-details" 
                placeholder="Enter incident details"
                rows="4"
              ></textarea>
            </div>
          </div>
          
          <div class="form-actions">
            <button type="button" class="btn-secondary" @click="saveDraft">Save Draft</button>
            <button type="submit" class="btn-primary">{{ caseFormMode === 'new' ? 'Create Case' : 'Update Case' }}</button>
          </div>
        </form>
      </div>
    </div>
  </div>

  <!-- Minimized Case Form -->
  <div v-if="caseFormMinimized" class="minimized-case-form" @click="restoreCaseForm">
    <div class="minimized-content">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <span>Case #{{ currentCaseId }}</span>
      <span class="timer">{{ callDuration }}</span>
    </div>
  </div>

  <!-- Call Disposition Modal -->
  <div v-if="showDisposition" class="modal-overlay" @click="closeDisposition">
    <div class="disposition-modal" @click.stop>
      <div class="modal-header">
        <h3>Call Disposition</h3>
        <div class="call-timer-header">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
            <polyline points="12,6 12,12 16,14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          {{ callDuration }}
        </div>
        <button class="modal-close" @click="closeDisposition">×</button>
      </div>
      <div class="modal-body">
        <form @submit.prevent="submitDisposition">
          <div class="disposition-grid">
            <div class="form-group">
              <label>Call Outcome*</label>
              <select v-model="disposition.outcome" required class="form-control">
                <option value="">Select Outcome</option>
                <option value="resolved">Resolved</option>
                <option value="escalated">Escalated</option>
                <option value="follow-up">Follow-up Required</option>
                <option value="referred">Referred</option>
                <option value="incomplete">Incomplete</option>
                <option value="prank">Prank Call</option>
                <option value="blank">Blank/Silent Call</option>
                <option value="wrong-number">Wrong Number</option>
                <option value="test-call">Test Call</option>
                <option value="hang-up">Hang Up</option>
              </select>
            </div>
            
            <div class="form-group">
              <label>Call Category*</label>
              <select v-model="disposition.category" required class="form-control">
                <option value="">Select Category</option>
                <option value="domestic-violence">Domestic Violence</option>
                <option value="sexual-assault">Sexual Assault</option>
                <option value="mental-health">Mental Health Crisis</option>
                <option value="substance-abuse">Substance Abuse</option>
                <option value="child-abuse">Child Abuse</option>
                <option value="elder-abuse">Elder Abuse</option>
                <option value="human-trafficking">Human Trafficking</option>
                <option value="stalking">Stalking/Harassment</option>
                <option value="information">Information Request</option>
                <option value="resource-referral">Resource Referral</option>
                <option value="safety-planning">Safety Planning</option>
                <option value="legal-advocacy">Legal Advocacy</option>
                <option value="housing">Housing Assistance</option>
                <option value="financial">Financial Assistance</option>
                <option value="other">Other</option>
              </select>
            </div>

            <div class="form-group">
              <label>Priority Level*</label>
              <select v-model="disposition.priority" required class="form-control">
                <option value="">Select Priority</option>
                <option value="critical">Critical - Immediate Danger</option>
                <option value="high">High - Urgent Response Needed</option>
                <option value="medium">Medium - Standard Response</option>
                <option value="low">Low - Information/Follow-up</option>
              </select>
            </div>

            <div class="form-group">
              <label>Call Duration</label>
              <input 
                type="text" 
                :value="callDuration" 
                readonly 
                class="form-control duration-display"
              />
            </div>
          </div>

          <div class="form-group">
            <label>Disposition Reason*</label>
            <select v-model="disposition.reason" required class="form-control">
              <option value="">Select Reason</option>
              <optgroup label="Completed Calls">
                <option value="crisis-resolved">Crisis Resolved</option>
                <option value="information-provided">Information Provided</option>
                <option value="referral-made">Referral Made</option>
                <option value="safety-plan-created">Safety Plan Created</option>
                <option value="follow-up-scheduled">Follow-up Scheduled</option>
                <option value="escalated-supervisor">Escalated to Supervisor</option>
                <option value="escalated-emergency">Escalated to Emergency Services</option>
              </optgroup>
              <optgroup label="Incomplete Calls">
                <option value="caller-disconnected">Caller Disconnected</option>
                <option value="caller-hung-up">Caller Hung Up</option>
                <option value="technical-issues">Technical Issues</option>
                <option value="language-barrier">Language Barrier</option>
                <option value="caller-not-ready">Caller Not Ready to Talk</option>
              </optgroup>
              <optgroup label="Non-Crisis Calls">
                <option value="prank-call">Prank Call</option>
                <option value="blank-call">Blank/Silent Call</option>
                <option value="wrong-number">Wrong Number</option>
                <option value="test-call">Test Call</option>
                <option value="misdial">Accidental Dial</option>
                <option value="non-crisis">Non-Crisis Call</option>
              </optgroup>
            </select>
          </div>

          <div class="form-group">
            <label>Call Notes*</label>
            <textarea 
              v-model="disposition.notes" 
              rows="4" 
              placeholder="Enter detailed notes about the call, actions taken, and any follow-up needed..."
              required
              class="form-control"
            ></textarea>
          </div>

          <div class="form-group" v-if="disposition.outcome === 'escalated'">
            <label>Escalated To</label>
            <select v-model="disposition.escalatedTo" class="form-control">
              <option value="">Select Escalation Target</option>
              <option value="supervisor">Supervisor</option>
              <option value="police">Police/Law Enforcement</option>
              <option value="ems">Emergency Medical Services</option>
              <option value="cps">Child Protective Services</option>
              <option value="aps">Adult Protective Services</option>
              <option value="mental-health">Mental Health Crisis Team</option>
              <option value="legal-advocate">Legal Advocate</option>
              <option value="other-agency">Other Agency</option>
            </select>
          </div>

          <div class="form-group" v-if="disposition.outcome === 'referred'">
            <label>Referred To</label>
            <input 
              type="text" 
              v-model="disposition.referredTo"
              placeholder="Enter organization or service referred to"
              class="form-control"
            />
          </div>

          <div class="disposition-summary" v-if="disposition.outcome && disposition.category && disposition.priority">
            <h4>Call Summary</h4>
            <div class="summary-grid">
              <div class="summary-item">
                <span class="summary-label">Outcome:</span>
                <span class="summary-value">{{ disposition.outcome }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">Category:</span>
                <span class="summary-value">{{ disposition.category }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">Priority:</span>
                <span class="summary-value priority-indicator" :class="disposition.priority">{{ disposition.priority }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">Duration:</span>
                <span class="summary-value">{{ callDuration }}</span>
              </div>
            </div>
          </div>

          <div class="form-actions">
            <button type="button" class="btn-secondary" @click="closeDisposition">Cancel</button>
            <button type="submit" class="btn-primary">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M9 12L11 14L15 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              Complete Call Disposition
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>

  <!-- Case Link Modal -->
  <div v-if="showCaseLink" class="modal-overlay" @click="closeCaseLink">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>Link Call to Different Case</h3>
        <button class="modal-close" @click="closeCaseLink">×</button>
      </div>
      <div class="modal-body">
        <div class="case-link-options">
          <div class="case-option" @click="selectCaseLinkOption('existing')">
            <div class="option-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M10 13C10.4295 13.5741 10.9774 14.0491 11.6066 14.3929C12.2357 14.7367 12.9315 14.9411 13.6467 14.9923C14.3618 15.0435 15.0796 14.9403 15.7513 14.6897C16.4231 14.4392 17.0331 14.047 17.54 13.54L20.54 10.54C21.4508 9.59695 21.9548 8.33394 21.9434 7.02296C21.932 5.71198 21.4061 4.45791 20.4791 3.53087C19.5521 2.60383 18.298 2.07799 16.987 2.0666C15.676 2.0552 14.413 2.55918 13.47 3.47L11.75 5.18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M14 11C13.5705 10.4259 13.0226 9.95085 12.3934 9.60706C11.7643 9.26327 11.0685 9.05885 10.3533 9.00769C9.63819 8.95653 8.92037 9.05973 8.24864 9.31028C7.5769 9.56084 6.9669 9.95303 6.46 10.46L3.46 13.46C2.54918 14.403 2.04520 15.6661 2.0566 16.9771C2.06799 18.288 2.59383 19.5421 3.52087 20.4691C4.44791 21.3962 5.70198 21.922 7.01296 21.9334C8.32394 21.9448 9.58695 21.4408 10.53 20.53L12.24 18.82" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div class="option-content">
              <div class="option-title">Link to Existing Case</div>
              <div class="option-description">Connect this call to a different existing case</div>
            </div>
          </div>
          <div class="case-option" @click="selectCaseLinkOption('new')">
            <div class="option-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 5V19M5 12H19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div class="option-content">
              <div class="option-title">Create New Case</div>
              <div class="option-description">Create a new case and link this call to it</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Call Options Modal -->
  <div v-if="showCallOptions" class="modal-overlay" @click="closeCallOptions">
    <div class="modal-content call-options-modal" @click.stop>
      <div class="modal-header">
        <h3>Make a Call</h3>
        <button class="modal-close" @click="closeCallOptions">×</button>
      </div>
      <div class="modal-body">
        <div class="call-options">
          <div class="call-option" @click="selectCallOption('contacts')">
            <div class="option-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M17 21V19C17 17.9391 16.5786 16.9217 15.8284 16.1716C15.0783 15.4214 14.0609 15 13 15H5C3.93913 15 2.92172 15.4214 2.17157 16.1716C1.42143 16.9217 1 17.9391 1 19V21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <circle cx="9" cy="7" r="4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M23 21V19C22.9993 18.1137 22.7044 17.2528 22.1614 16.5523C21.6184 15.8519 20.8581 15.3516 20 15.13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M16 3.13C16.8604 3.35031 17.623 3.85071 18.1676 4.55232C18.7122 5.25392 19.0078 6.11683 19.0078 7.005C19.0078 7.89318 18.7122 8.75608 18.1676 9.45769C17.623 10.1593 16.8604 10.6597 16 10.88" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div class="option-content">
              <div class="option-title">Call from Contacts</div>
              <div class="option-description">Select a contact from your saved list</div>
            </div>
          </div>
          <div class="call-option" @click="selectCallOption('new')">
            <div class="option-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M22 16.92V19C22 20.1046 21.1046 21 20 21C10.6112 21 3 13.3888 3 4C3 2.89543 3.89543 2 5 2H7.08C7.55607 2 7.95823 2.33718 8.02513 2.80754L8.7 7.5C8.76694 7.97036 8.53677 8.42989 8.12 8.67L6.5 9.5C7.84 12.16 11.84 16.16 14.5 17.5L15.33 15.88C15.5701 15.4632 16.0296 15.2331 16.5 15.3L21.1925 16.0249C21.6628 16.0918 22 16.4939 22 16.97V16.92Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div class="option-content">
              <div class="option-title">Make New Call</div>
              <div class="option-description">Enter a phone number to call</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Contacts Modal -->
  <div v-if="showContactsModal" class="modal-overlay" @click="closeCallOptions">
    <div class="modal-content contacts-modal" @click.stop>
      <div class="modal-header">
        <h3>Select Contact</h3>
        <button class="modal-close" @click="closeCallOptions">×</button>
      </div>
      <div class="modal-body">
        <div class="contacts-search">
          <input 
            type="text" 
            placeholder="Search contacts..." 
            class="search-input"
          />
        </div>
        <div class="contacts-list">
          <div 
            v-for="contact in contacts" 
            :key="contact.id" 
            class="contact-item"
            @click="callContact(contact)"
          >
            <div class="contact-avatar">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H5C3.93913 15 2.92172 15.4214 2.17157 16.1716C1.42143 16.9217 1 17.9391 1 19V21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <circle cx="12" cy="7" r="4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div class="contact-info">
              <div class="contact-name">{{ contact.name }}</div>
              <div class="contact-phone">{{ contact.phone }}</div>
              <div class="contact-meta">
                <span class="contact-type">{{ contact.type }}</span>
                <span class="contact-last-call">Last call: {{ contact.lastCall }}</span>
              </div>
            </div>
            <div class="contact-priority">
              <span class="priority-indicator" :class="contact.priority"></span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- New Call Modal -->
  <div v-if="showNewCallModal" class="modal-overlay" @click="closeCallOptions">
    <div class="modal-content new-call-modal" @click.stop>
      <div class="modal-header">
        <h3>Make New Call</h3>
        <button class="modal-close" @click="closeCallOptions">×</button>
      </div>
      <div class="modal-body">
        <form @submit.prevent="makeNewCall">
          <div class="form-group">
            <label for="phone-number">Phone Number*</label>
            <input 
              v-model="newCallNumber"
              type="tel" 
              id="phone-number"
              placeholder="Enter phone number (e.g., +1 555 123 4567)"
              required
              class="phone-input"
            />
          </div>
          <div class="call-info">
            <div class="info-item">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                <polyline points="12,6 12,12 16,14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span>Call will be initiated immediately</span>
            </div>
            <div class="info-item">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span>A new case will be created automatically</span>
            </div>
          </div>
          <div class="form-actions">
            <button type="button" class="btn-secondary" @click="closeCallOptions">Cancel</button>
            <button type="submit" class="btn-primary">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M22 16.92V19C22 20.1046 21.1046 21 20 21C10.6112 21 3 13.3888 3 4C3 2.89543 3.89543 2 5 2H7.08C7.55607 2 7.95823 2.33718 8.02513 2.80754L8.7 7.5C8.76694 7.97036 8.53677 8.42989 8.12 8.67L6.5 9.5C7.84 12.16 11.84 16.16 14.5 17.5L15.33 15.88C15.5701 15.4632 16.0296 15.2331 16.5 15.3L21.1925 16.0249C21.6628 16.0918 22 16.4939 22 16.97V16.92Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              Call Now
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>

  <!-- Success/Info Notification -->
  <div v-if="showNotification" class="notification-overlay">
    <div class="notification-container" :class="notificationType">
      <div class="notification-icon">
        <svg v-if="notificationType === 'success'" width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M9 12L11 14L15 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <svg v-else-if="notificationType === 'info'" width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
          <line x1="12" y1="16" x2="12" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <line x1="12" y1="8" x2="12.01" y2="8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <svg v-else width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
          <line x1="15" y1="9" x2="9" y2="15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <line x1="9" y1="9" x2="15" y2="15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      <div class="notification-content">
        <div class="notification-message">{{ notificationMessage }}</div>
      </div>
      <button class="notification-close" @click="showNotification = false">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </div>
  </div>
</div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import SidePanel from '@/components/SidePanel.vue'

const router = useRouter()
const isSidebarCollapsed = ref(false)
function handleSidebarToggle(collapsed) {
  isSidebarCollapsed.value = collapsed
}

// Reactive state
const activeView = ref('timeline')
const selectedCallId = ref('1348456')
const currentTheme = ref('dark')
const selectedTimeRange = ref('all')
const showCallDetails = ref(true)
const userRole = ref('super-admin')

// Queue management state
const isInQueue = ref(false)
const isProcessingQueue = ref(false)
const currentCall = ref(null)
const callStartTime = ref(null)
const callDuration = ref('00:00')

// New modal states
const showQueuePopup = ref(false)
const showRingingInterface = ref(false)
const showCaseForm = ref(false)
const caseFormMinimized = ref(false)

// Case options modal states
const showCaseOptions = ref(false)
const showExistingCaseSearch = ref(false)
const caseSearchQuery = ref('')
const caseFormMode = ref('new') // 'new' or 'edit'

// Modal states
const showDisposition = ref(false)
const showCaseLink = ref(false)
const selectedCallForLink = ref(null)

// Call initiation modal states
const showCallOptions = ref(false)
const showContactsModal = ref(false)
const showNewCallModal = ref(false)
const newCallNumber = ref('')
const selectedContact = ref(null)

// Notification state
const showNotification = ref(false)
const notificationMessage = ref('')
const notificationType = ref('success') // 'success', 'error', 'info'

// Sample existing cases for search
const existingCases = ref([
  {
    id: 'CASE-2025-1001',
    title: 'Domestic Violence Support - Jane Doe',
    client: 'Jane Doe',
    priority: 'High',
    status: 'Open',
    date: '2025-01-15',
    description: 'Ongoing domestic violence case requiring immediate attention'
  },
  {
    id: 'CASE-2025-1002',
    title: 'Child Abuse Investigation',
    client: 'Anonymous',
    priority: 'Critical',
    status: 'In Progress',
    date: '2025-01-14',
    description: 'Child welfare investigation case'
  },
  {
    id: 'CASE-2025-1003',
    title: 'Mental Health Crisis Support',
    client: 'John Smith',
    priority: 'Medium',
    status: 'Open',
    date: '2025-01-13',
    description: 'Mental health crisis intervention and support'
  },
  {
    id: 'CASE-2025-1004',
    title: 'Elder Abuse Report',
    client: 'Mary Johnson',
    priority: 'High',
    status: 'Pending',
    date: '2025-01-12',
    description: 'Elder abuse investigation and support services'
  },
  {
    id: 'CASE-2025-1005',
    title: 'Sexual Assault Support',
    client: 'Anonymous',
    priority: 'Critical',
    status: 'Open',
    date: '2025-01-11',
    description: 'Sexual assault survivor support and advocacy'
  }
])

// Computed property for filtered existing cases
const filteredExistingCases = computed(() => {
  if (!caseSearchQuery.value) return existingCases.value
  
  const query = caseSearchQuery.value.toLowerCase()
  return existingCases.value.filter(caseItem => 
    caseItem.id.toLowerCase().includes(query) ||
    caseItem.title.toLowerCase().includes(query) ||
    caseItem.client.toLowerCase().includes(query)
  )
})

// Sample contacts data
const contacts = ref([
  {
    id: 1,
    name: 'Sarah Johnson',
    phone: '+1 (555) 123-4567',
    type: 'Client',
    lastCall: '2 days ago',
    priority: 'high'
  },
  {
    id: 2,
    name: 'Michael Brown',
    phone: '+1 (555) 987-6543',
    type: 'Emergency Contact',
    lastCall: '1 week ago',
    priority: 'critical'
  },
  {
    id: 3,
    name: 'Emily Davis',
    phone: '+1 (555) 456-7890',
    type: 'Family Member',
    lastCall: '3 days ago',
    priority: 'medium'
  },
  {
    id: 4,
    name: 'Robert Wilson',
    phone: '+1 (555) 321-0987',
    type: 'Legal Advocate',
    lastCall: '5 days ago',
    priority: 'high'
  },
  {
    id: 5,
    name: 'Lisa Anderson',
    phone: '+1 (555) 654-3210',
    type: 'Counselor',
    lastCall: '1 day ago',
    priority: 'medium'
  }
])

// Ringing call state
const ringingCall = ref(null)
const ringingDuration = ref('00:00')
const ringingStartTime = ref(null)

// Case form data
const currentCaseId = ref('')
const caseFormData = ref({
  caseName: '',
  description: '',
  priority: '',
  type: '',
  callerInfo: '',
  incidentDetails: ''
})

// Disposition form
const disposition = ref({
  outcome: '',
  category: '',
  priority: '',
  reason: '',
  notes: '',
  escalatedTo: '',
  referredTo: ''
})

// Queue members data
const queueMembers = ref([
  {
    id: 1,
    name: 'Sarah Davis',
    role: 'Senior Crisis Counselor',
    status: 'available',
    statusText: 'Available',
    avatar: '/placeholder.svg?height=40&width=40'
  },
  {
    id: 2,
    name: 'Mark Reynolds',
    role: 'Crisis Counselor',
    status: 'busy',
    statusText: 'On Call',
    avatar: '/placeholder.svg?height=40&width=40'
  },
  {
    id: 3,
    name: 'Emily Chan',
    role: 'Mental Health Specialist',
    status: 'available',
    statusText: 'Available',
    avatar: '/placeholder.svg?height=40&width=40'
  },
  {
    id: 4,
    name: 'David Lee',
    role: 'Legal Advocate',
    status: 'away',
    statusText: 'Break',
    avatar: '/placeholder.svg?height=40&width=40'
  },
  {
    id: 5,
    name: 'Sophia Clark',
    role: 'Housing Specialist',
    status: 'available',
    statusText: 'Available',
    avatar: '/placeholder.svg?height=40&width=40'
  },
  {
    id: 6,
    name: 'Dr. Lisa Chen',
    role: 'Supervisor',
    status: 'busy',
    statusText: 'In Meeting',
    avatar: '/placeholder.svg?height=40&width=40'
  }
])

// Queue stats
const queueStats = ref({
  waiting: 3,
  active: 12,
  agents: 8
})

// Queue calls with auto-generated case IDs
const queueCalls = ref([
  {
    id: 'queue_001',
    type: 'Emergency Crisis: Domestic Violence',
    waitTime: '2m 15s',
    priority: 'critical',
    callerName: 'Anonymous',
    caseId: generateCaseId()
  },
  {
    id: 'queue_002',
    type: 'Mental Health Support',
    waitTime: '5m 30s',
    priority: 'high',
    callerName: 'Sarah M.',
    caseId: generateCaseId()
  },
  {
    id: 'queue_003',
    type: 'Information Request',
    waitTime: '1m 45s',
    priority: 'medium',
    callerName: 'John D.',
    caseId: generateCaseId()
  }
])

// Helper function to generate case IDs
function generateCaseId() {
  const year = new Date().getFullYear()
  const randomNum = Math.floor(Math.random() * 9000) + 1000
  return `CASE-${year}-${randomNum}`
}

// Call data with auto-generated case IDs
const callData = ref({
  '1348456': {
    id: '1348456',
    title: 'Emergency Crisis: Domestic Violence',
    time: '09:00AM',
    dateLabel: 'Today',
    status: 'In Progress',
    agent: 'Sarah Davis',
    callTitle: 'Emergency call',
    callerName: 'Nelson Adega',
    duration: '3min 5 sec',
    callStart: '09:00 am',
    callEnd: '09:03 am',
    disposition: 'Abusive Call',
    date: '15th Aug 2025',
    escalatedTo: 'Ntaate Kimani',
    group: 'Today',
    caseId: 'CASE-2025-1001',
    priority: 'critical'
  },
  '1348457': {
    id: '1348457',
    title: 'Survivor Follow-Up: Safety Planning',
    time: '10:30AM',
    dateLabel: 'Today',
    status: 'Pending',
    agent: null,
    callTitle: 'Follow-up call',
    callerName: 'Maria Johnson',
    duration: '15min 20 sec',
    callStart: '10:30 am',
    callEnd: '10:45 am',
    disposition: 'Completed',
    date: '15th Aug 2025',
    escalatedTo: 'David Lee',
    group: 'Today',
    caseId: 'CASE-2025-1002',
    priority: 'high'
  },
  '1348458': {
    id: '1348458',
    title: 'Scheduled Support: Therapy Session',
    time: '02:00PM',
    dateLabel: 'Today',
    status: 'In Progress',
    agent: 'Mark Reynolds',
    callTitle: 'Therapy Session',
    callerName: 'James Wilson',
    duration: '45min 10 sec',
    callStart: '02:00 pm',
    callEnd: '02:45 pm',
    disposition: 'Completed',
    date: '15th Aug 2025',
    escalatedTo: 'Dr. Lisa Chen',
    group: 'Today',
    caseId: 'CASE-2025-1003',
    priority: 'medium'
  },
  '1348459': {
    id: '1348459',
    title: 'Resource Request: Shelter Information',
    time: '04:45PM',
    dateLabel: 'Today',
    status: 'Unassigned',
    agent: null,
    callTitle: 'Shelter Information',
    callerName: 'Anonymous',
    duration: '8min 30 sec',
    callStart: '04:45 pm',
    callEnd: '04:53 pm',
    disposition: 'Information Provided',
    date: '15th Aug 2025',
    escalatedTo: 'Unassigned',
    group: 'Today',
    caseId: 'CASE-2025-1004',
    priority: 'low'
  },
  '1348460': {
    id: '1348460',
    title: 'Wellness Check-In: Mental Health Support',
    time: '11:15AM',
    dateLabel: 'Yesterday',
    status: 'Completed',
    agent: 'Emily Chan',
    callTitle: 'Mental Health Support',
    callerName: 'Rebecca Taylor',
    duration: '22min 15 sec',
    callStart: '11:15 am',
    callEnd: '11:37 am',
    disposition: 'Completed',
    date: '14th Aug 2025',
    escalatedTo: 'Dr. Michael Brown',
    group: 'Yesterday',
    caseId: 'CASE-2025-1005',
    priority: 'medium'
  },
  '1348461': {
    id: '1348461',
    title: 'Appointment Booking: Legal Advocacy',
    time: '01:30PM',
    dateLabel: 'Yesterday',
    status: 'Completed',
    agent: 'David Lee',
    callTitle: 'Legal Advocacy',
    callerName: 'Thomas Garcia',
    duration: '12min 40 sec',
    callStart: '01:30 pm',
    callEnd: '01:42 pm',
    disposition: 'Appointment Scheduled',
    date: '14th Aug 2025',
    escalatedTo: 'Legal Team',
    group: 'Yesterday',
    caseId: 'CASE-2025-1006',
    priority: 'high'
  },
  '1348462': {
    id: '1348462',
    title: 'Call Back: Housing Assistance Follow-up',
    time: '05:00PM',
    dateLabel: 'Yesterday',
    status: 'Completed',
    agent: 'Sophia Clark',
    callTitle: 'Housing Assistance',
    callerName: 'Jennifer Lopez',
    duration: '18min 22 sec',
    callStart: '05:00 pm',
    callEnd: '05:18 pm',
    disposition: 'Completed',
    date: '14th Aug 2025',
    escalatedTo: 'Housing Department',
    group: 'Yesterday',
    caseId: 'CASE-2025-1007',
    priority: 'medium'
  }
})

// Status data
const statusItems = ref([
  { label: 'Unassigned', count: 16, percentage: 53 },
  { label: 'Pending', count: 5, percentage: 17 },
  { label: 'In Progress', count: 24, percentage: 80 },
  { label: 'Completed', count: 8, percentage: 27 }
])

// Computed properties
const allCalls = computed(() => {
  return Object.values(callData.value)
})

const groupedCalls = computed(() => {
  const groups = {}

  allCalls.value.forEach(call => {
    if (!groups[call.group]) {
      groups[call.group] = []
    }
    groups[call.group].push(call)
  })

  return groups
})

const selectedCallDetails = computed(() => {
  return callData.value[selectedCallId.value] || null
})

// Methods
const handleQueueToggle = async () => {
  if (currentCall.value) {
    endCall()
    return
  }

  isProcessingQueue.value = true

  try {
    if (isInQueue.value) {
      // Leave queue
      isInQueue.value = false
      
      // Show leave queue notification
      showNotification.value = true
      notificationMessage.value = 'Left the queue successfully!'
      notificationType.value = 'info'
      
      // Auto-hide notification after 3 seconds
      setTimeout(() => {
        showNotification.value = false
      }, 3000)
      
      console.log('Left queue')
    } else {
      // Join queue - show queue popup first
      showQueuePopup.value = true
    }
  } finally {
    isProcessingQueue.value = false
  }
}

const handleLogout = () => {
  console.log('Logging out...')
  alert('Logged out successfully!')
}

const closeQueuePopup = () => {
  showQueuePopup.value = false
}

const confirmJoinQueue = () => {
  isInQueue.value = true
  showQueuePopup.value = false
  
  // Show success notification instead of alert
  showNotification.value = true
  notificationMessage.value = 'Joined the queue successfully! Waiting for incoming calls...'
  notificationType.value = 'success'
  
  // Auto-hide notification after 3 seconds
  setTimeout(() => {
    showNotification.value = false
  }, 3000)
  
  console.log('Joined queue successfully')

  // Simulate receiving a call after joining queue (3 seconds delay)
  setTimeout(() => {
    if (isInQueue.value && !currentCall.value) {
      console.log('Simulating incoming call...')
      simulateIncomingCall()
    }
  }, 3000)
}

const initiateNewCall = () => {
  showCallOptions.value = true
}

const closeCallOptions = () => {
  showCallOptions.value = false
  showContactsModal.value = false
  showNewCallModal.value = false
  newCallNumber.value = ''
  selectedContact.value = null
}

const selectCallOption = (option) => {
  if (option === 'contacts') {
    showCallOptions.value = false
    showContactsModal.value = true
  } else if (option === 'new') {
    showCallOptions.value = false
    showNewCallModal.value = true
  }
}

const callContact = (contact) => {
  selectedContact.value = contact
  showContactsModal.value = false
  
  // Initiate call with contact
  const outgoingCall = {
    id: `CALL-OUT-${Date.now()}`,
    type: 'Outgoing Call',
    callerName: contact.name,
    number: contact.phone,
    status: 'outgoing',
    priority: contact.priority,
    caseId: generateCaseId()
  }

  ringingCall.value = outgoingCall
  showRingingInterface.value = true
  ringingStartTime.value = new Date()
  startRingingTimer()
}

const makeNewCall = () => {
  if (!newCallNumber.value.trim()) {
    alert('Please enter a phone number')
    return
  }

  showNewCallModal.value = false
  
  // Initiate call with new number
  const outgoingCall = {
    id: `CALL-OUT-${Date.now()}`,
    type: 'Outgoing Call',
    callerName: 'Unknown Contact',
    number: newCallNumber.value,
    status: 'outgoing',
    priority: 'medium',
    caseId: generateCaseId()
  }

  ringingCall.value = outgoingCall
  showRingingInterface.value = true
  ringingStartTime.value = new Date()
  startRingingTimer()
  
  newCallNumber.value = ''
}

const simulateIncomingCall = () => {
  console.log('Creating incoming call...')
  const caseId = generateCaseId()
  const incomingCall = {
    id: `CALL-${Date.now()}`,
    type: 'Emergency Crisis: Domestic Violence',
    callerName: 'Anonymous Caller',
    number: '+1 (555) 987-6543',
    status: 'incoming',
    priority: 'critical',
    caseId: caseId
  }

  ringingCall.value = incomingCall
  showRingingInterface.value = true
  ringingStartTime.value = new Date()
  startRingingTimer()
  
  console.log('Incoming call interface should now be visible')
}

const startRingingTimer = () => {
  const timer = setInterval(() => {
    if (!ringingStartTime.value || !showRingingInterface.value) {
      clearInterval(timer)
      return
    }
    
    const now = new Date()
    const diff = now - ringingStartTime.value
    const minutes = Math.floor(diff / 60000)
    const seconds = Math.floor((diff % 60000) / 1000)
    ringingDuration.value = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
  }, 1000)
}

// Modified answerCall to show case options
const answerCall = () => {
  if (ringingCall.value) {
    currentCall.value = {
      ...ringingCall.value,
      status: 'active'
    }
    
    callStartTime.value = new Date()
    currentCaseId.value = ringingCall.value.caseId
    
    showRingingInterface.value = false
    showCaseOptions.value = true // Show case options instead of case form
    startCallTimer()
    
    // Add call to call data
    const newCallId = currentCall.value.id
    callData.value[newCallId] = {
      id: newCallId,
      title: currentCall.value.type,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      dateLabel: 'Today',
      status: 'In Progress',
      agent: 'Current User',
      callTitle: currentCall.value.type,
      callerName: currentCall.value.callerName,
      duration: '0min 0 sec',
      callStart: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      callEnd: '',
      disposition: '',
      date: new Date().toLocaleDateString(),
      escalatedTo: '',
      group: 'Today',
      caseId: currentCall.value.caseId,
      priority: currentCall.value.priority
    }
  }

  ringingCall.value = null
  ringingStartTime.value = null
  ringingDuration.value = '00:00'
}

// Case options methods
const closeCaseOptions = () => {
  showCaseOptions.value = false
}

const selectCaseOption = (option) => {
  showCaseOptions.value = false
  
  if (option === 'new') {
    // Open new case creation form
    caseFormMode.value = 'new'
    currentCaseId.value = generateCaseId()
    
    // Initialize case form data with call info
    caseFormData.value = {
      caseName: currentCall.value?.type || '',
      description: '',
      priority: currentCall.value?.priority || '',
      type: '',
      callerInfo: `Caller: ${currentCall.value?.callerName || 'Unknown'}\nNumber: ${currentCall.value?.number || 'Unknown'}`,
      incidentDetails: ''
    }
    
    showCaseForm.value = true
  } else if (option === 'existing') {
    // Open existing case search
    showExistingCaseSearch.value = true
    caseSearchQuery.value = ''
  } else if (option === 'disposition') {
    // Open disposition form directly
    showDisposition.value = true
  }
}

const closeExistingCaseSearch = () => {
  showExistingCaseSearch.value = false
  caseSearchQuery.value = ''
}

const selectExistingCase = (existingCase) => {
  // Link call to existing case and open edit form
  currentCaseId.value = existingCase.id
  caseFormMode.value = 'edit'
  
  // Pre-populate form with existing case data
  caseFormData.value = {
    caseName: existingCase.title,
    description: existingCase.description,
    priority: existingCase.priority,
    type: '', // Would need to add type to existing cases data
    callerInfo: `Caller: ${currentCall.value?.callerName || 'Unknown'}\nNumber: ${currentCall.value?.number || 'Unknown'}\n\nLinked to existing case for: ${existingCase.client}`,
    incidentDetails: ''
  }
  
  showExistingCaseSearch.value = false
  showCaseForm.value = true
  
  // Update call data to link to selected case
  if (currentCall.value && callData.value[currentCall.value.id]) {
    callData.value[currentCall.value.id].caseId = existingCase.id
  }
}

const declineCall = () => {
  showRingingInterface.value = false
  ringingCall.value = null
  ringingStartTime.value = null
  ringingDuration.value = '00:00'
}

const endCall = () => {
  if (currentCall.value) {
    const callId = currentCall.value.id
    
    // Update call data
    if (callData.value[callId]) {
      callData.value[callId].status = 'Completed'
      callData.value[callId].callEnd = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      callData.value[callId].duration = callDuration.value
    }
    
    currentCall.value = null
    callStartTime.value = null
    callDuration.value = '00:00'
    showCaseForm.value = false
    caseFormMinimized.value = false
  }
}

const startCallTimer = () => {
  const timer = setInterval(() => {
    if (!callStartTime.value || !currentCall.value) {
      clearInterval(timer)
      return
    }
    
    const now = new Date()
    const diff = now - callStartTime.value
    const minutes = Math.floor(diff / 60000)
    const seconds = Math.floor((diff % 60000) / 1000)
    callDuration.value = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
  }, 1000)
}

const minimizeCaseForm = () => {
  showCaseForm.value = false
  caseFormMinimized.value = true
}

const restoreCaseForm = () => {
  caseFormMinimized.value = false
  showCaseForm.value = true
}

const saveCaseForm = () => {
  console.log('Saving case form:', caseFormData.value)
  alert(`Case ${caseFormMode.value === 'new' ? 'created' : 'updated'} successfully!`)
  
  // In a real app, this would save to the backend
  // For demo, we'll just close the form
  showCaseForm.value = false
  caseFormMinimized.value = false
}

const saveDraft = () => {
  console.log('Saving draft:', caseFormData.value)
  alert('Draft saved successfully!')
}

const acceptQueueCall = (callId) => {
  const queueCall = queueCalls.value.find(call => call.id === callId)
  if (queueCall && isInQueue.value) {
    ringingCall.value = {
      id: `CALL-${Date.now()}`,
      type: queueCall.type,
      callerName: queueCall.callerName,
      number: '+1 (555) 123-4567',
      status: 'incoming',
      priority: queueCall.priority,
      caseId: queueCall.caseId
    }
    
    showRingingInterface.value = true
    ringingStartTime.value = new Date()
    startRingingTimer()
    
    // Remove from queue
    queueCalls.value = queueCalls.value.filter(call => call.id !== callId)
    queueStats.value.waiting--
  }
}

const closeDisposition = () => {
  showDisposition.value = false
  disposition.value = {
    outcome: '',
    category: '',
    priority: '',
    reason: '',
    notes: '',
    escalatedTo: '',
    referredTo: ''
  }
}

const submitDisposition = () => {
  console.log('Submitting disposition:', disposition.value)

  // Update the call's case with disposition information
  if (currentCall.value && callData.value[currentCall.value.id]) {
    callData.value[currentCall.value.id].disposition = disposition.value.reason
    callData.value[currentCall.value.id].priority = disposition.value.priority
  }

  // End the call after disposition
  endCall()
  closeDisposition()
  alert('Call disposition saved and call ended successfully!')
}

const viewCallDetails = (callId) => {
  selectedCallId.value = callId
  showCallDetails.value = true
}

const linkToCase = (callId) => {
  selectedCallForLink.value = callId
  showCaseLink.value = true
}

const closeCaseLink = () => {
  showCaseLink.value = false
  selectedCallForLink.value = null
}

const selectCaseLinkOption = (option) => {
  if (option === 'existing') {
    // In a real app, this would open a case search modal
    const caseId = prompt('Enter existing case ID:')
    if (caseId && selectedCallForLink.value) {
      callData.value[selectedCallForLink.value].caseId = caseId
      alert(`Call linked to case ${caseId}`)
    }
  } else if (option === 'new') {
    // Navigate to case creation
    router.push('/case-creation')
  }
  closeCaseLink()
}

const viewCase = (caseId) => {
  console.log('Viewing case:', caseId)
  // Navigate to cases page
  router.push('/cases')
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
    root.style.setProperty('--header-bg', '#f0f0f0')
    root.style.setProperty('--input-bg', '#ffffff')
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
    root.style.setProperty('--header-bg', '#333')
    root.style.setProperty('--input-bg', '#333')
    root.setAttribute('data-theme', 'dark')
  }

  // Set common variables
  root.style.setProperty('--accent-color', '#964B00')
  root.style.setProperty('--accent-hover', '#b25900')
  root.style.setProperty('--danger-color', '#ff3b30')
  root.style.setProperty('--success-color', '#4CAF50')
  root.style.setProperty('--pending-color', '#FFA500')
  root.style.setProperty('--unassigned-color', '#808080')
  root.style.setProperty('--highlight-color', '#ff3b30')
  root.style.setProperty('--critical-color', '#ff3b30')
  root.style.setProperty('--high-color', '#ff9500')
  root.style.setProperty('--medium-color', '#007aff')
  root.style.setProperty('--low-color', '#34c759')
}

const toggleTheme = () => {
  currentTheme.value = currentTheme.value === 'dark' ? 'light' : 'dark'
  localStorage.setItem('theme', currentTheme.value)
  applyTheme(currentTheme.value)
}

const selectCall = (callId) => {
  selectedCallId.value = callId
  showCallDetails.value = true
}

const closeCallDetails = () => {
  showCallDetails.value = false
}

const getStatusClass = (status) => {
  return status.toLowerCase().replace(/\s+/g, '-')
}

// Lifecycle
onMounted(() => {
  // Load saved theme
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme) {
    currentTheme.value = savedTheme
  }

  // Apply theme immediately
  applyTheme(currentTheme.value)
})

onUnmounted(() => {
  // Clean up any timers
  if (callStartTime.value) {
    callStartTime.value = null
  }
  if (ringingStartTime.value) {
    ringingStartTime.value = null
  }
})
</script>

<style scoped>
:root {
  --accent-color: #FF8C00;
}
.main-content {
  transition: margin-left 0.3s, width 0.3s;
  margin-left: 250px;
  width: calc(100% - 250px);
}
.main-content.sidebar-collapsed {
  margin-left: 20px;
  width: calc(100% - 20px);
}
/* Unify accent color usage */
.status-badge,
.view-tab.active,
.queue-action-btn.accept,
.call-btn.answer {
  background: var(--accent-color) !important;
  color: #fff !important;
  border-color: var(--accent-color) !important;
}
.status-badge svg,
.view-tab.active svg,
.queue-action-btn.accept svg,
.call-btn.answer svg {
  color: #fff !important;
  stroke: #fff !important;
}

/* Global styles - not scoped */
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

.main-content {
  flex: 1;
  margin-left: var(--sidebar-width, 250px);
  height: 100vh;
  background-color: var(--background-color);
  transition: margin-left 0.3s ease, background-color 0.3s;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  color: var(--text-color);
}

.calls-container {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  overflow-x: hidden;
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.3) transparent;
  background: var(--background-color);
}

.calls-container::-webkit-scrollbar {
  width: 8px;
}

.calls-container::-webkit-scrollbar-track {
  background: transparent;
}

.calls-container::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: 4px;
}

.calls-container::-webkit-scrollbar-thumb:hover {
  background-color: rgba(255, 255, 255, 0.5);
}

.header {
  margin-bottom: 25px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 20px;
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
  white-space: nowrap;
  min-width: 120px;
}

.theme-toggle:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.theme-toggle svg {
  width: 16px;
  height: 16px;
}

.new-call-btn {
  background-color: var(--success-color);
  color: white;
  border: none;
  border-radius: 30px;
  padding: 8px 15px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  white-space: nowrap;
  min-width: 100px;
}

.new-call-btn:hover {
  background-color: #45a049;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.new-call-btn svg {
  width: 16px;
  height: 16px;
}

.view-tabs {
  display: flex;
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 25px;
  overflow-x: auto;
  white-space: nowrap;
  flex-shrink: 0;
}

.view-tab {
  padding: 12px 24px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
  position: relative;
  transition: all 0.3s ease;
}

.view-tab:hover {
  color: var(--text-color);
}

.view-tab.active {
  color: var(--accent-color);
  font-weight: 700;
  background: rgba(255, 140, 0, 0.12); /* subtle glassmorphic accent */
  border-radius: 16px 16px 0 0;
  box-shadow: 0 4px 16px 0 rgba(255,140,0,0.08);
}

.view-tab.active::after {
  display: none;
}

/* Status Cards - Horizontal Layout */
.status-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 25px;
  padding: 0;
}

.status-card {
  background-color: var(--content-bg);
  border-radius: 15px;
  padding: 20px;
  border: 1px solid var(--border-color);
  transition: all 0.3s ease;
}

.status-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.status-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.status-card-label {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-color);
}

.status-card-count {
  font-size: 24px;
  font-weight: 800;
  color: var(--accent-color);
}

.status-card-progress {
  height: 6px;
  background-color: var(--border-color);
  border-radius: 3px;
  overflow: hidden;
}

.status-card-progress-fill {
  height: 100%;
  background-color: var(--accent-color);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.view-container {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.3) transparent;
}

.view-container::-webkit-scrollbar {
  width: 8px;
}

.view-container::-webkit-scrollbar-track {
  background: transparent;
}

.view-container::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: 4px;
}

.view-container::-webkit-scrollbar-thumb:hover {
  background-color: rgba(255, 255, 255, 0.5);
}

.time-section {
  margin-bottom: 35px;
}

.time-section-title {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 20px;
  color: var(--text-color);
}

.call-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.call-item {
  display: flex;
  align-items: flex-start;
  cursor: pointer;
  padding: 15px;
  border-radius: 15px;
  transition: all 0.3s ease;
  position: relative;
}

.call-item:hover {
  background-color: rgba(255, 255, 255, 0.05);
  transform: translateX(5px);
}

.call-item.selected {
  background-color: rgba(255, 59, 48, 0.1);
  border: 1px solid var(--highlight-color);
}

.call-item.selected .call-type {
  color: var(--highlight-color);
  font-weight: 700;
}

.timeline-connector::after {
  content: '';
  position: absolute;
  top: 45px;
  left: 30px;
  width: 1px;
  height: calc(100% + 12px);
  background-color: var(--border-color);
  z-index: 1;
}

.call-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: var(--content-bg);
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: 15px;
  margin-top: 2px;
  flex-shrink: 0;
  position: relative;
  z-index: 2;
  border: 2px solid var(--background-color);
}

.call-icon svg {
  width: 18px;
  height: 18px;
  stroke: var(--text-color);
}

.call-details {
  flex: 1;
}

.call-type {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 6px;
  line-height: 1.4;
}

.call-time {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.call-meta {
  display: flex;
  gap: 12px;
  align-items: center;
}

.case-link {
  font-size: 12px;
  font-weight: 600;
  color: var(--accent-color);
  text-decoration: none;
  padding: 2px 8px;
  background-color: rgba(150, 75, 0, 0.1);
  border-radius: 8px;
}

.case-link:hover {
  text-decoration: underline;
}

.call-id {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-color);
}

.priority-badge {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  padding: 4px 8px;
  border-radius: 8px;
  color: white;
}

.priority-badge.critical {
  background-color: var(--critical-color);
}

.priority-badge.high {
  background-color: var(--high-color);
}

.priority-badge.medium {
  background-color: var(--medium-color);
}

.priority-badge.low {
  background-color: var(--low-color);
}

/* Queue Section */
.queue-section {
  padding: 20px;
  background-color: var(--card-bg);
  border-radius: 20px;
  margin-bottom: 20px;
}

.queue-title {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 20px;
}

.queue-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  margin-bottom: 30px;
}

.queue-stat {
  text-align: center;
  padding: 15px;
  background-color: var(--background-color);
  border-radius: 12px;
}

.stat-value {
  font-size: 24px;
  font-weight: 800;
  color: var(--accent-color);
  margin-bottom: 5px;
}

.stat-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
}

.queue-subtitle {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 15px;
}

.queue-call-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.queue-call-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background-color: var(--background-color);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.queue-call-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.queue-call-info {
  flex: 1;
}

.queue-call-type {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 5px;
}

.queue-call-details {
  display: flex;
  gap: 15px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
}

.queue-call-actions {
  display: flex;
  gap: 8px;
}

.queue-action-btn {
  background-color: var(--success-color);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 6px 12px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.queue-action-btn:hover {
  background-color: #45a049;
  transform: translateY(-1px);
}

/* Table view styles */
.calls-table-container {
  overflow-x: auto;
  border-radius: 30px;
  background-color: var(--content-bg);
  margin-bottom: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.calls-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
}

.calls-table th {
  text-align: left;
  padding: 18px 20px;
  background-color: var(--header-bg);
  font-weight: 700;
  font-size: 14px;
  position: sticky;
  top: 0;
  z-index: 10;
  color: var(--text-color);
}

.calls-table th:first-child {
  border-top-left-radius: 30px;
}

.calls-table th:last-child {
  border-top-right-radius: 30px;
}

.calls-table td {
  padding: 18px 20px;
  border-bottom: 1px solid var(--border-color);
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.calls-table tr:hover td {
  background-color: rgba(255, 255, 255, 0.05);
}

.calls-table tr:last-child td {
  border-bottom: none;
}

.calls-table tr:last-child td:first-child {
  border-bottom-left-radius: 30px;
}

.calls-table tr:last-child td:last-child {
  border-bottom-right-radius: 30px;
}

.calls-table tr.selected td {
  background-color: rgba(255, 59, 48, 0.1);
  color: var(--highlight-color);
  font-weight: 700;
}

.status-badge {
  color: #fff;
  padding: 6px 16px;
  border-radius: 30px;
  font-size: 12px;
  display: inline-block;
  font-weight: 700;
  text-align: center;
  min-width: 100px;
  transition: all 0.3s ease;
}

.status-badge.in-progress {
  background-color: var(--accent-color);
}

.status-badge.pending {
  background-color: var(--pending-color);
}

.status-badge.unassigned {
  background-color: var(--unassigned-color);
}

.status-badge.completed {
  background-color: var(--success-color);
}

.status-badge.open {
  background-color: var(--success-color);
}

.table-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  background-color: var(--accent-color);
  color: white;
  border: none;
  border-radius: 6px;
  padding: 6px 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-btn:hover {
  background-color: var(--accent-hover);
  transform: scale(1.1);
}

.action-btn.view-btn {
  background-color: var(--medium-color);
}

.action-btn.link-btn {
  background-color: var(--high-color);
}

.action-btn.case-btn {
  background-color: var(--success-color);
}

/* Call details panel */
.call-details-panel {
  position: fixed;
  top: 0;
  right: 0;
  width: 400px;
  height: 100vh;
  background-color: var(--content-bg);
  border-left: 1px solid var(--border-color);
  z-index: 1000;
  transition: transform 0.3s ease;
  box-shadow: -5px 0 15px rgba(0, 0, 0, 0.1);
  border-radius: 30px 0 0 30px;
  transform: translateX(100%);
  overflow-y: auto;
  overflow-x: hidden;
  display: flex;
  flex-direction: column;
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.3) transparent;
}

.call-details-panel::-webkit-scrollbar {
  width: 8px;
}

.call-details-panel::-webkit-scrollbar-track {
  background: transparent;
}

.call-details-panel::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: 4px;
}

.call-details-panel::-webkit-scrollbar-thumb:hover {
  background-color: rgba(255, 255, 255, 0.5);
}

.call-details-panel.active {
  transform: translateX(0);
}

.call-details-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 25px;
  border-bottom: 1px solid var(--border-color);
  background-color: var(--content-bg);
  flex-shrink: 0;
}

.call-details-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--highlight-color);
  line-height: 1.4;
}

.close-details {
  background: none;
  border: none;
  color: var(--text-color);
  cursor: pointer;
  font-size: 24px;
  font-weight: 700;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.close-details:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.call-details-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 25px;
  display: flex;
  flex-direction: column;
  gap: 18px;
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.3) transparent;
}

.call-details-content::-webkit-scrollbar {
  width: 8px;
}

.call-details-content::-webkit-scrollbar-track {
  background: transparent;
}

.call-details-content::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: 4px;
}

.call-details-content::-webkit-scrollbar-thumb:hover {
  background-color: rgba(255, 255, 255, 0.5);
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  background-color: var(--background-color);
  padding: 18px;
  border-radius: 15px;
  transition: all 0.3s ease;
}

.detail-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.detail-label {
  font-size: 12px;
  font-weight: 700;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.detail-value {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-color);
  line-height: 1.4;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal-content {
  background-color: var(--content-bg);
  border-radius: 20px;
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 25px;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-color);
}

.call-timer-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 700;
  color: var(--success-color);
}

.modal-close {
  background: none;
  border: none;
  color: var(--text-color);
  cursor: pointer;
  font-size: 24px;
  font-weight: 700;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.modal-close:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.modal-body {
  padding: 25px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 8px;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  background-color: var(--input-bg);
  color: var(--text-color);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 12px 16px;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--accent-color);
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 25px;
}

.btn-primary {
  background-color: var(--accent-color);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 12px 24px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-primary:hover {
  background-color: var(--accent-hover);
  transform: translateY(-1px);
}

.btn-secondary {
  background-color: var(--border-color);
  color: var(--text-color);
  border: none;
  border-radius: 12px;
  padding: 12px 24px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-secondary:hover {
  background-color: var(--text-secondary);
  transform: translateY(-1px);
}

/* Case Options Modal Styles */
.case-options-modal {
  background-color: var(--content-bg);
  border-radius: 20px;
  width: 90%;
  max-width: 700px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.case-options-grid {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.case-option-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 25px;
  background-color: var(--background-color);
  border-radius: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid var(--border-color);
}

.case-option-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  border-color: var(--accent-color);
}

.option-icon {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.option-icon.new-case {
  background-color: var(--success-color);
}

.option-icon.existing-case {
  background-color: var(--accent-color);
}

.option-icon.disposition-call {
  background-color: var(--medium-color);
}

.option-content {
  flex: 1;
}

.option-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-color);
  margin-bottom: 8px;
}

.option-description {
  font-size: 16px;
  font-weight: 500;
  color: var(--text-secondary);
  line-height: 1.5;
}

.option-arrow {
  color: var(--text-secondary);
  transition: all 0.3s ease;
}

.case-option-card:hover .option-arrow {
  color: var(--accent-color);
  transform: translateX(5px);
}

/* Existing Case Search Modal */
.existing-case-modal {
  background-color: var(--content-bg);
  border-radius: 20px;
  width: 90%;
  max-width: 800px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease-out;
}

.case-search {
  margin-bottom: 20px;
}

.search-input {
  width: 100%;
  background-color: var(--input-bg);
  color: var(--text-color);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 15px 20px;
  font-size: 16px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: var(--accent-color);
  box-shadow: 0 0 0 3px rgba(150, 75, 0, 0.1);
}

.existing-cases-list {
  max-height: 400px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.existing-case-item {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
  background-color: var(--background-color);
  border-radius: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid var(--border-color);
}

.existing-case-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
  border-color: var(--accent-color);
}

.case-info {
  flex: 1;
}

.case-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.case-id {
  font-size: 16px;
  font-weight: 700;
  color: var(--accent-color);
}

.case-priority {
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  padding: 4px 8px;
  border-radius: 8px;
  color: white;
}

.case-priority.critical {
  background-color: var(--critical-color);
}

.case-priority.high {
  background-color: var(--high-color);
}

.case-priority.medium {
  background-color: var(--medium-color);
}

.case-priority.low {
  background-color: var(--low-color);
}

.case-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 8px;
  line-height: 1.3;
}

.case-meta {
  display: flex;
  gap: 15px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.case-client {
  color: var(--text-color);
}

.case-status {
  display: flex;
  align-items: center;
}

.case-select-arrow {
  color: var(--text-secondary);
  transition: all 0.3s ease;
}

.existing-case-item:hover .case-select-arrow {
  color: var(--accent-color);
  transform: translateX(5px);
}

/* Queue Popup Modal */
.queue-popup {
  background-color: var(--content-bg);
  border-radius: 20px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease-out;
}

.queue-popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 25px;
  border-bottom: 1px solid var(--border-color);
}

.queue-popup-header h3 {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-color);
}

.queue-members {
  padding: 25px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
}

.queue-member-card {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background-color: var(--background-color);
  border-radius: 15px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.queue-member-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.member-avatar {
  position: relative;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
}

.member-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.status-indicator {
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid var(--background-color);
}

.status-indicator.available {
  background-color: var(--success-color);
}

.status-indicator.busy {
  background-color: var(--danger-color);
}

.status-indicator.away {
  background-color: var(--pending-color);
}

.member-info {
  flex: 1;
}

.member-name {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-color);
  margin-bottom: 2px;
}

.member-role {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 2px;
}

.member-status {
  font-size: 11px;
  font-weight: 600;
  color: var(--accent-color);
}

.queue-popup-footer {
  padding: 20px 25px;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
}

/* Ringing Call Interface Styles */
.ringing-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 3000;
}

.ringing-container {
  background-color: var(--content-bg);
  border-radius: 30px;
  width: 90%;
  max-width: 450px;
  padding: 30px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
  text-align: center;
}

.ringing-header {
  margin-bottom: 20px;
}

.call-type-badge {
  font-size: 14px;
  font-weight: 700;
  text-transform: uppercase;
  padding: 8px 16px;
  border-radius: 30px;
  color: white;
  display: inline-block;
}

.call-type-badge.critical {
  background-color: var(--critical-color);
}

.call-type-badge.high {
  background-color: var(--high-color);
}

.call-type-badge.medium {
  background-color: var(--medium-color);
}

.call-type-badge.low {
  background-color: var(--low-color);
}

.caller-info {
  margin-bottom: 30px;
}

.caller-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background-color: var(--background-color);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 15px;
}

.caller-avatar svg {
  width: 40px;
  height: 40px;
  stroke: var(--text-color);
}

.caller-name {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-color);
  margin-bottom: 8px;
}

.caller-number {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.call-duration {
  font-size: 15px;
  font-weight: 600;
  color: var(--success-color);
}

.ringing-animation {
  position: relative;
  width: 120px;
  height: 120px;
  margin: 0 auto 30px;
}

.pulse-ring {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 3px solid var(--medium-color);
  position: absolute;
  top: 0;
  left: 0;
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  opacity: 0;
}

.pulse-ring.delay-1 {
  animation-delay: 0.5s;
}

.pulse-ring.delay-2 {
  animation-delay: 1s;
}

@keyframes pulse {
  0% {
    transform: scale(0);
    opacity: 0;
  }
  50% {
    opacity: 1;
  }
  100% {
    transform: scale(1.2);
    opacity: 0;
  }
}

.call-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.call-btn {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.call-btn svg {
  width: 28px;
  height: 28px;
  stroke: white;
}

.call-btn.decline {
  background-color: var(--danger-color);
}

.call-btn.decline:hover {
  background-color: #d32f2f;
  transform: scale(1.1);
}

.call-btn.answer {
  background-color: var(--success-color);
}

.call-btn.answer:hover {
  background-color: #43a047;
  transform: scale(1.1);
}

/* Case Form Styles */
.case-form-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 4000;
}

.case-form-container {
  background-color: var(--content-bg);
  border-radius: 30px;
  width: 95%;
  max-width: 900px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
  display: flex;
  flex-direction: column;
}

.case-form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 25px 30px;
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
}

.form-title {
  flex: 1;
  text-align: left;
}

.form-title h3 {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-color);
  margin-bottom: 5px;
}

.case-id {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
}

.call-timer {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 700;
  color: var(--success-color);
  flex-shrink: 0;
}

.minimize-btn {
  background: none;
  border: none;
  color: var(--text-color);
  cursor: pointer;
  font-size: 20px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.minimize-btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.case-form-content {
  flex: 1;
  overflow-y: auto;
  padding: 30px;
}

.form-section {
  margin-bottom: 30px;
}

.section-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-color);
  margin-bottom: 20px;
}

.form-row {
  display: flex;
  gap: 20px;
}

.form-row .form-group {
  flex: 1;
}

.form-control {
  width: 100%;
  background-color: var(--input-bg);
  color: var(--text-color);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 12px 16px;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.form-control:focus {
  outline: none;
  border-color: var(--accent-color);
}

.form-actions {
  display: flex;
  gap: 15px;
  justify-content: flex-end;
  margin-top: 30px;
}

/* Minimized Case Form Styles */
.minimized-case-form {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background-color: var(--content-bg);
  border-radius: 15px;
  padding: 12px 20px;
  cursor: pointer;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  transition: all 0.3s ease;
  z-index: 4000;
}

.minimized-case-form:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}

.minimized-content {
  display: flex;
  align-items: center;
  gap: 10px;
}

.minimized-content svg {
  width: 18px;
  height: 18px;
  stroke: var(--text-color);
}

.minimized-content span {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-color);
}

.minimized-content .timer {
  font-size: 14px;
  font-weight: 600;
  color: var(--success-color);
}

/* Enhanced Disposition Modal Styles */
.disposition-modal {
  background-color: var(--content-bg);
  border-radius: 20px;
  width: 95%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease-out;
}

.disposition-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 25px;
}

.duration-display {
  background-color: var(--background-color) !important;
  color: var(--success-color) !important;
  font-weight: 700 !important;
  text-align: center;
}

.disposition-summary {
  background-color: var(--background-color);
  border-radius: 15px;
  padding: 20px;
  margin-top: 25px;
  border: 2px solid var(--border-color);
}

.disposition-summary h4 {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-color);
  margin-bottom: 15px;
  text-align: center;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
  text-align: center;
}

.summary-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
}

.summary-value {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-color);
}

.summary-value.priority-indicator {
  padding: 4px 8px;
  border-radius: 8px;
  color: white;
  text-transform: uppercase;
}

/* Call Options Modal Styles */
.call-options-modal {
  max-width: 400px;
}

.call-options {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.call-option {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 20px;
  background-color: var(--background-color);
  border-radius: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid var(--border-color);
}

.call-option:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
  border-color: var(--accent-color);
}

.contacts-modal {
  max-width: 600px;
}

.contacts-search {
  margin-bottom: 20px;
}

.contacts-list {
  max-height: 300px;
  overflow-y: auto;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background-color: var(--background-color);
  border-radius: 12px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.contact-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.contact-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: var(--content-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.contact-avatar svg {
  width: 20px;
  height: 20px;
  stroke: var(--text-color);
}

.contact-info {
  flex: 1;
}

.contact-name {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-color);
  margin-bottom: 4px;
}

.contact-phone {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 6px;
}

.contact-meta {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  display: flex;
  gap: 10px;
}

.contact-priority {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  flex-shrink: 0;
}

.priority-indicator {
  display: block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.priority-indicator.critical {
  background-color: var(--critical-color);
}

.priority-indicator.high {
  background-color: var(--high-color);
}

.priority-indicator.medium {
  background-color: var(--medium-color);
}

.priority-indicator.low {
  background-color: var(--low-color);
}

.new-call-modal {
  max-width: 450px;
}

.phone-input {
  width: 100%;
  background-color: var(--input-bg);
  color: var(--text-color);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 15px 20px;
  font-size: 16px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.call-info {
  margin-top: 20px;
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
}

.info-item svg {
  width: 18px;
  height: 18px;
  stroke: var(--text-secondary);
}

/* Notification Styles */
.notification-overlay {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 5000;
  animation: slideInRight 0.3s ease-out;
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.notification-container {
  display: flex;
  align-items: center;
  gap: 12px;
  background-color: var(--content-bg);
  border-radius: 12px;
  padding: 16px 20px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  border-left: 4px solid;
  min-width: 300px;
  max-width: 400px;
}

.notification-container.success {
  border-left-color: var(--success-color);
}

.notification-container.info {
  border-left-color: var(--medium-color);
}

.notification-container.error {
  border-left-color: var(--danger-color);
}

.notification-icon {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  color: var(--text-color);
}

.notification-container.success .notification-icon {
  color: var(--success-color);
}

.notification-container.info .notification-icon {
  color: var(--medium-color);
}

.notification-container.error .notification-icon {
  color: var(--danger-color);
}

.notification-content {
  flex: 1;
}

.notification-message {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-color);
  line-height: 1.4;
}

.notification-close {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.notification-close:hover {
  background-color: rgba(255, 255, 255, 0.1);
  color: var(--text-color);
}

/* Responsive Styles */
@media (max-width: 768px) {
  .header-actions {
    gap: 12px;
  }
  
  .theme-toggle {
    padding: 6px 12px;
    font-size: 13px;
    min-width: 100px;
  }
}
@media (max-width: 1200px) {
  .calls-container {
    padding: 10px 2vw;
  }
}
@media (max-width: 1024px) {
  .main-content {
    margin-left: 0;
    width: 100vw;
  }
  .calls-container {
    padding: 10px 2vw;
  }
}
@media (max-width: 900px) {
  .calls-container {
    padding: 8px 1vw;
  }
}
@media (max-width: 768px) {
  .main-content {
    margin-left: 0;
    width: 100vw;
    padding: 10px 2vw;
  }
  .calls-container {
    padding: 6px 1vw;
  }
  .view-tabs {
    flex-direction: column;
    gap: 8px;
  }
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}
@media (max-width: 480px) {
  .main-content {
    margin-left: 0;
    width: 100vw;
    padding: 4px 1vw;
  }
  .calls-container {
    padding: 2px 0.5vw;
  }
  .view-tabs {
    flex-direction: column;
    gap: 6px;
  }
}
.fab-new-call {
  position: fixed;
  bottom: 32px;
  right: 32px;
  background: var(--success-color);
  color: #fff;
  border-radius: 50px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.18);
  padding: 16px 24px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 700;
  font-size: 16px;
  cursor: pointer;
  z-index: 1001;
  transition: background 0.2s, box-shadow 0.2s;
}
.fab-new-call:hover {
  background: #45a049;
  box-shadow: 0 8px 32px rgba(0,0,0,0.22);
}
@media (max-width: 768px) {
  .fab-new-call {
    bottom: 16px;
    right: 16px;
    padding: 12px 18px;
    font-size: 14px;
  }
}

.calls-container, .calls-container * {
  color: #222 !important;
}
.status-card-label, .status-card-count, .status-card-progress, .queue-title, .queue-stat, .queue-subtitle, .queue-call-type, .queue-call-details, .queue-call-info, .queue-call-actions, .call-type, .call-time, .call-meta, .case-link, .call-id, .status-badge, .table-actions, .view-tab, .page-title, .header, .header-actions, .main-content, .call-details-title, .call-details-header, .call-details-panel {
  color: #222 !important;
}

/* Dark mode overrides */
:root.dark .calls-container, :root.dark .calls-container *,
body.dark .calls-container, body.dark .calls-container * {
  color: #fff !important;
}
:root.dark .call-type, :root.dark .call-time, :root.dark .call-meta, :root.dark .case-link, :root.dark .status-card-label, :root.dark .status-card-count, :root.dark .queue-title, :root.dark .queue-stat, :root.dark .queue-subtitle, :root.dark .queue-call-type, :root.dark .queue-call-details, :root.dark .queue-call-info, :root.dark .queue-call-actions, :root.dark .status-badge, :root.dark .table-actions, :root.dark .view-tab, :root.dark .page-title, :root.dark .header, :root.dark .header-actions, :root.dark .main-content, :root.dark .call-details-title, :root.dark .call-details-header, :root.dark .call-details-panel {
  color: #fff !important;
  opacity: 1 !important;
}
body.dark .call-type, body.dark .call-time, body.dark .call-meta, body.dark .case-link, body.dark .status-card-label, body.dark .status-card-count, body.dark .queue-title, body.dark .queue-stat, body.dark .queue-subtitle, body.dark .queue-call-type, body.dark .queue-call-details, body.dark .queue-call-info, body.dark .queue-call-actions, body.dark .status-badge, body.dark .table-actions, body.dark .view-tab, body.dark .page-title, body.dark .header, body.dark .header-actions, body.dark .main-content, body.dark .call-details-title, body.dark .call-details-header, body.dark .call-details-panel {
  color: #fff !important;
  opacity: 1 !important;
}
[data-theme="dark"] .call-type, [data-theme="dark"] .call-time, [data-theme="dark"] .call-meta, [data-theme="dark"] .case-link, [data-theme="dark"] .status-card-label, [data-theme="dark"] .status-card-count, [data-theme="dark"] .queue-title, [data-theme="dark"] .queue-stat, [data-theme="dark"] .queue-subtitle, [data-theme="dark"] .queue-call-type, [data-theme="dark"] .queue-call-details, [data-theme="dark"] .queue-call-info, [data-theme="dark"] .queue-call-actions, [data-theme="dark"] .status-badge, [data-theme="dark"] .table-actions, [data-theme="dark"] .view-tab, [data-theme="dark"] .page-title, [data-theme="dark"] .header, [data-theme="dark"] .header-actions, [data-theme="dark"] .main-content, [data-theme="dark"] .call-details-title, [data-theme="dark"] .call-details-header, [data-theme="dark"] .call-details-panel {
  color: #fff !important;
  opacity: 1 !important;
}

/* Dark mode overrides */
:root.dark .calls-container, :root.dark .calls-container *,
body.dark .calls-container, body.dark .calls-container *,
[data-theme="dark"] .calls-container, [data-theme="dark"] .calls-container * {
  color: #fff !important;
}
:root.dark .calls-table th, :root.dark .calls-table td,
body.dark .calls-table th, body.dark .calls-table td,
[data-theme="dark"] .calls-table th, [data-theme="dark"] .calls-table td {
  color: #fff !important;
}
:root.dark .queue-section, :root.dark .queue-section *,
body.dark .queue-section, body.dark .queue-section *,
[data-theme="dark"] .queue-section, [data-theme="dark"] .queue-section * {
  color: #fff !important;
}
</style>
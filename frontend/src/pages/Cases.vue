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
      <div class="cases-container">
        <!-- Cleaned up header section with better structure and spacing -->
        <header class="page-header">
          <div class="header-top">
            <div class="header-left">
              <h1 class="page-title">Cases</h1>
              <router-link to="/case-creation" class="btn btn--primary btn--sm">Add New Case</router-link>
            </div>
            
          </div>
          
          <!-- Combined search and view toggle into single horizontal row -->
          <div class="search-and-controls-section">
            <div class="search-container">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Search case by title, assignee, or filter..."
                class="input"
              />
            </div>
            
            <div class="view-toggle">
              <button 
                class="btn btn--secondary btn--sm" 
                :class="{ active: currentView === 'table' }" 
                @click="setCurrentView('table')"
              >
                Table View
              </button>
              <button 
                class="btn btn--secondary btn--sm" 
                :class="{ active: currentView === 'timeline' }" 
                @click="setCurrentView('timeline')"
              >
                Timeline
              </button>
            </div>
          </div>

          <!-- Moved filter tabs to separate section -->
          <div class="filter-section">
            <button
              v-for="filter in filters"
              :key="filter.id"
              class="btn btn--secondary btn--sm"
              :class="{ active: activeFilter === filter.id }"
              @click="setActiveFilter(filter.id)"
            >
              {{ filter.name }}
            </button>
            <router-link to="/reports-category" class="btn btn--secondary btn--sm">Advanced Filters</router-link>
          </div>
        </header>

        <!-- Added conditional rendering for table view and timeline view -->
        <!-- Table View -->
        <div v-if="currentView === 'table'" class="cases-table-container">
          <div class="cases-table-wrapper card" style="padding:0;">
            <table class="cases-table">
              <thead>
                <tr>
                  <!-- Improved table headers with better labels and spacing -->
                  <th class="case-id-header">Case ID</th>
                  <th class="created-by-header">Created By</th>
                  <th class="created-on-header">Created On</th>
                  <th class="source-header">Source</th>
                  <th class="priority-header">Priority</th>
                  <th class="status-header">Status</th>
                  <th class="actions-header">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="caseItem in filteredCases"
                  :key="casesStore.cases_k?.id ? caseItem[casesStore.cases_k.id[0]] : caseItem.id"
                  :class="['table-row', {
                    selected: selectedCaseId === (casesStore.cases_k?.id ? caseItem[casesStore.cases_k.id[0]] : caseItem.id)
                  }]"
                  @click="selectCase(casesStore.cases_k?.id ? caseItem[casesStore.cases_k.id[0]] : caseItem.id)"
                >
                  <td class="case-id-cell">
                    {{ casesStore.cases_k?.id ? caseItem[casesStore.cases_k.id[0]] : caseItem.id || 'N/A' }}
                  </td>
                  <td class="created-by-cell">
                    {{ casesStore.cases_k?.created_by ? caseItem[casesStore.cases_k.created_by[0]] || 'N/A' : 'N/A' }}
                  </td>
                  <td class="created-on-cell">
                    {{ casesStore.cases_k?.dt ? new Date(
                      caseItem[casesStore.cases_k.dt[0]] < 10000000000
                        ? caseItem[casesStore.cases_k.dt[0]] * 1000
                        : caseItem[casesStore.cases_k.dt[0]] * 3600 * 1000
                    ).toLocaleDateString() : 'N/A' }}
                  </td>
                  <td class="source-cell">
                    {{ casesStore.cases_k?.source ? caseItem[casesStore.cases_k.source[0]] || 'N/A' : 'N/A' }}
                  </td>
                  <td class="priority-cell">
                    <span class="priority-badge" :class="(casesStore.cases_k?.priority ? caseItem[casesStore.cases_k.priority[0]] || 'normal' : 'normal').toLowerCase()">
                      <span
                        :class="['priority-dot', (casesStore.cases_k?.priority ? caseItem[casesStore.cases_k.priority[0]] || '' : '').toLowerCase()]"
                      />
                      {{ casesStore.cases_k?.priority ? caseItem[casesStore.cases_k.priority[0]] || 'Normal' : 'Normal' }}
                    </span>
                  </td>
                  <td class="status-cell">
                    <span class="status-badge" :class="(casesStore.cases_k?.status ? caseItem[casesStore.cases_k.status[0]] || 'open' : 'open').toLowerCase()">
                      {{ casesStore.cases_k?.status ? caseItem[casesStore.cases_k.status[0]] || 'Open' : 'Open' }}
                    </span>
                  </td>
                  <td class="actions-cell">
                    <button class="btn btn--secondary btn--sm" @click.stop="selectCase(casesStore.cases_k?.id ? caseItem[casesStore.cases_k.id[0]] : caseItem.id)">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                        <circle cx="12" cy="12" r="3"/>
                      </svg>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <!-- Edit Case Modal -->
          <div v-if="editModalOpen" class="case-detail-drawer">
            <div class="case-detail-drawer-header">
              <div class="case-detail-title">Edit Case</div>
              <button class="close-details" @click="closeEdit">×</button>
            </div>
            <div class="case-detail-content">
              <div class="detail-item">
                <div class="detail-label">Priority</div>
                <div><select v-model="editForm.priority" class="input"><option>Low</option><option>Medium</option><option>High</option></select></div>
              </div>
              <div class="detail-item">
                <div class="detail-label">Status</div>
                <div><select v-model="editForm.status" class="input"><option>Open</option><option>Pending</option><option>Closed</option></select></div>
              </div>
              <div class="detail-item">
                <div class="detail-label">Assigned To</div>
                <div><input v-model="editForm.assignedTo" class="input" /></div>
              </div>
              <div class="detail-item">
                <div class="detail-label">Case Plan</div>
                <div><textarea v-model="editForm.casePlan" class="input" rows="3"/></div>
              </div>
              <div style="display:flex; gap:8px; justify-content:flex-end;">
                <button class="btn btn--secondary btn--sm" @click="closeEdit">Cancel</button>
                <button class="btn btn--primary btn--sm" @click="saveEdit">Save</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Timeline View (Original Card Layout) -->
        <div v-else class="cases-container-inner">
          <div class="cases-list">
            <h2 class="cases-title">Cases</h2>

            <div
              v-for="caseItem in filteredCases"
              :key="casesStore.cases_k?.id ? caseItem[casesStore.cases_k.id[0]] : caseItem.id"
              :class="[
                'case-item card',
                {
                  selected: selectedCaseId === (casesStore.cases_k?.id ? caseItem[casesStore.cases_k.id[0]] : caseItem.id),
                },
              ]"
              @click="selectCase(casesStore.cases_k?.id ? caseItem[casesStore.cases_k.id[0]] : caseItem.id)"
            >
              <div class="case-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                  <path
                    d="M12 22C12 22 20 18 20 12V5L12 2L4 5V12C4 18 12 22 12 22Z"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                  <path
                    d="M9 12L11 14L15 10"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                </svg>
              </div>
              <div class="case-details">
                <div class="case-title">
                  {{ casesStore.cases_k?.cat_1 ? caseItem[casesStore.cases_k.cat_1[0]] : "Untitled Case" }}
                </div>
                <div class="case-meta">
                  <span class="case-priority">
                    <span
                      :class="['priority-dot', (casesStore.cases_k?.priority ? caseItem[casesStore.cases_k.priority[0]] || '' : '').toLowerCase()]"
                    />
                    {{ casesStore.cases_k?.priority ? caseItem[casesStore.cases_k.priority[0]] || "Normal" : "Normal" }}
                    priority
                  </span>
                  <span class="case-date">
                    {{ casesStore.cases_k?.dt ? new Date(
                      caseItem[casesStore.cases_k.dt[0]] < 10000000000
                        ? caseItem[casesStore.cases_k.dt[0]] * 1000
                        : caseItem[casesStore.cases_k.dt[0]] * 3600 * 1000
                    ).toLocaleString() : "No Date" }}
                  </span>
                  <span class="case-assigned">
                    {{ casesStore.cases_k?.assigned_to && caseItem[casesStore.cases_k.assigned_to[0]]
                      ? `Assigned: ${caseItem[casesStore.cases_k.assigned_to[0]]}`
                      : "Unassigned" }}
                  </span>
                  <button class="btn btn--secondary btn--sm" @click.stop="openEdit(caseItem)">Edit</button>
                </div>
              </div>
              <div v-if="caseItem.activity && caseItem.activity.length" class="case-activity" style="margin-top:8px; font-size:12px; color:var(--color-muted);">
                <div v-for="(log, idx) in caseItem.activity.slice(0,3)" :key="idx">
                  <strong>{{ log.type }}</strong> • {{ new Date(log.at).toLocaleString() }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Enhanced Case Detail Drawer -->
        <div class="case-detail-drawer" v-if="selectedCaseDetails">
          <div class="case-detail-drawer-header">
            <div class="case-detail-title">
              <button class="back-button" @click="closeCaseDetails">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                  <path d="M19 12H5" stroke="currentColor" stroke-width="2"/>
                  <path d="M12 19L5 12L12 5" stroke="currentColor" stroke-width="2"/>
                </svg>
              </button>
              {{ getCaseTitle(selectedCaseDetails) }}
            </div>
            <div class="case-detail-id">
              Case ID: {{ getCaseId(selectedCaseDetails) }}
            </div>
            <button class="close-details" @click="closeCaseDetails">×</button>
          </div>

          <!-- Case Navigation Tabs -->
          <div class="case-tabs">
            <button 
              class="case-tab" 
              :class="{ active: currentTab === 'details' }"
              @click="currentTab = 'details'"
            >
              Case Details
            </button>
            <button 
              class="case-tab" 
              :class="{ active: currentTab === 'history' }"
              @click="currentTab = 'history'"
            >
              Case History
            </button>
            <button 
              class="case-tab" 
              :class="{ active: currentTab === 'update' }"
              @click="handleUpdateTabClick"
            >
              Update
            </button>
            <button 
              class="case-tab" 
              :class="{ active: currentTab === 'print' }"
              @click="printCase"
            >
              Print
            </button>
            <button class="edit-case-btn" @click="handleEditButtonClick">Edit</button>
          </div>

          <div class="case-detail-content">
            <!-- Case Details Tab Content -->
            <div v-if="currentTab === 'details'">
              <!-- Reporter Information -->
              <div class="detail-section">
                <h3 class="section-title">Reported By</h3>
                <div class="reporter-info">
                  <div class="reporter-details">
                    <div class="reporter-name">{{ getReporterName(selectedCaseDetails) }}</div>
                    <div class="reporter-demographics">{{ getReporterDemographics(selectedCaseDetails) }}</div>
                    <div class="reporter-location">{{ getReporterLocation(selectedCaseDetails) }}</div>
                    <div class="reporter-contacts">
                      <button class="contact-btn" @click="callReporter(selectedCaseDetails)">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                          <path d="M22 16.92V19C22 20.1046 21.1046 21 20 21C10.6112 21 3 13.3888 3 4C3 2.89543 3.89543 2 5 2H7.08C7.5561 2 7.9582 2.3372 8.0251 2.8075L8.7 7.5C8.7669 7.9704 8.5368 8.4299 8.12 8.67L6.5 9.5C7.84 12.16 11.84 16.16 14.5 17.5L15.33 15.88C15.5701 15.4632 16.0296 15.2331 16.5 15.3L21.1925 16.0249C21.6628 16.0918 22 16.4939 22 16.97V16.92Z" stroke="currentColor" stroke-width="2"/>
                        </svg>
                      </button>
                      <button class="contact-btn" @click="emailReporter(selectedCaseDetails)">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                          <path d="M4 4H20C21.1 4 22 4.9 22 6V18C22 19.1 21.1 20 20 20H4C2.9 20 2 19.1 2 18V6C2 4.9 2.9 4 4 4Z" stroke="currentColor" stroke-width="2"/>
                          <polyline points="22,6 12,13 2,6" stroke="currentColor" stroke-width="2"/>
                        </svg>
                      </button>
              </div>
            </div>
              </div>
            </div>

              <!-- Followup By -->
              <div class="detail-section">
                <h3 class="section-title">Followup By</h3>
                <div class="followup-info">
                  <div class="followup-contacts">
                    <button class="contact-btn">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                        <path d="M22 16.92V19C22 20.1046 21.1046 21 20 21C10.6112 21 3 13.3888 3 4C3 2.89543 3.89543 2 5 2H7.08C7.5561 2 7.9582 2.3372 8.0251 2.8075L8.7 7.5C8.7669 7.9704 8.5368 8.4299 8.12 8.67L6.5 9.5C7.84 12.16 11.84 16.16 14.5 17.5L15.33 15.88C15.5701 15.4632 16.0296 15.2331 16.5 15.3L21.1925 16.0249C21.6628 16.0918 22 16.4939 22 16.97V16.92Z" stroke="currentColor" stroke-width="2"/>
                      </svg>
                    </button>
                    <button class="contact-btn">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                        <path d="M4 4H20C21.1 4 22 4.9 22 6V18C22 19.1 21.1 20 20 20H4C2.9 20 2 19.1 2 18V6C2 4.9 2.9 4 4 4Z" stroke="currentColor" stroke-width="2"/>
                        <polyline points="22,6 12,13 2,6" stroke="currentColor" stroke-width="2"/>
                      </svg>
                    </button>
                  </div>
                </div>
              </div>

              <!-- Clients -->
              <div class="detail-section">
                <h3 class="section-title">Clients</h3>
                <div class="clients-info">
                  <div class="empty-state">No clients added</div>
                </div>
              </div>

              <!-- Perpetrators -->
              <div class="detail-section">
                <h3 class="section-title">Perpetrators</h3>
                <div class="perpetrators-info">
                  <div v-if="!getCasePerpetrators(selectedCaseDetails).length" class="empty-state">No perpetrators added</div>
                  <div v-else class="perpetrators-list">
                    <div v-for="perpetrator in getCasePerpetrators(selectedCaseDetails)" :key="perpetrator.id" class="perpetrator-item">
                      <div class="perpetrator-name">{{ perpetrator.name }}</div>
                      <div class="perpetrator-details">{{ perpetrator.age }} {{ perpetrator.sex }} - {{ perpetrator.location }}</div>
                    </div>
                  </div>
                  <button class="btn btn--primary btn--sm" @click="openPerpetratorModal">+ Add a Perpetrator</button>
                </div>
              </div>

              <!-- Related Files -->
              <div class="detail-section">
                <h3 class="section-title">Related Files</h3>
                <div class="files-list">
                  <div class="file-item" v-for="file in getCaseFiles(selectedCaseDetails)" :key="file.name">
                    <div class="file-name">{{ file.name }}</div>
                    <div class="file-size">{{ file.size }}</div>
                    <button class="file-remove" @click="removeFile(file)">×</button>
                  </div>
                  <div v-if="!getCaseFiles(selectedCaseDetails).length" class="empty-state">No files attached</div>
                </div>
              </div>

              <!-- Services Offered -->
              <div class="detail-section">
                <h3 class="section-title">Services Offered</h3>
                <div class="services-info">
                  <div class="service-item">Know About 116</div>
                </div>
              </div>

              <!-- Case Information -->
              <div class="detail-section">
                <h3 class="section-title">Case Information</h3>
                <div class="case-info-grid">
                  <div class="info-item">
                    <div class="info-label">Department</div>
                    <div class="info-value">{{ getCaseDepartment(selectedCaseDetails) }}</div>
                  </div>
                  <div class="info-item">
                    <div class="info-label">Case Category</div>
                    <div class="info-value">
                      <div class="category-tags">
                        <span class="category-tag">Abuse</span>
                        <span class="category-tag">Child Exploitation</span>
                      </div>
                    </div>
                  </div>
                  <div class="info-item">
                    <div class="info-label">Is Case GBV Related?</div>
                    <div class="info-value">
                      <span class="status-badge status-yes">Yes</span>
                    </div>
                  </div>
                  <div class="info-item">
                    <div class="info-label">Case Narrative</div>
                    <div class="info-value">{{ getCaseNarrative(selectedCaseDetails) }}</div>
                  </div>
                  <div class="info-item">
                    <div class="info-label">Case Plan</div>
                    <div class="info-value">{{ getCasePlan(selectedCaseDetails) }}</div>
                  </div>
                  <div class="info-item">
                    <div class="info-label">State of the Case in the Justice System</div>
                    <div class="info-value">{{ getJusticeSystemState(selectedCaseDetails) }}</div>
                  </div>
                  <div class="info-item">
                    <div class="info-label">General Case Assessment</div>
                    <div class="info-value">{{ getGeneralAssessment(selectedCaseDetails) }}</div>
                  </div>
                  <div class="info-item">
                    <div class="info-label">Priority</div>
                    <div class="info-value">
                      <span class="priority-badge high">High</span>
                    </div>
                  </div>
                  <div class="info-item">
                    <div class="info-label">Status</div>
                    <div class="info-value">
                      <span class="status-badge status-ongoing">Ongoing</span>
                    </div>
                  </div>
                  <div class="info-item">
                    <div class="info-label">Escalated To</div>
                    <div class="info-value">{{ getEscalatedTo(selectedCaseDetails) }}</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Case History Tab Content -->
            <div v-if="currentTab === 'history'" class="case-history-content">
              <div class="history-header">
                <h3 class="section-title">Case Activity Timeline</h3>
                <p class="history-subtitle">All changes and updates made to this case</p>
              </div>
              
              <div class="timeline">
                <div v-if="!getCaseActivity(selectedCaseDetails).length" class="empty-state">
                  <p>No activity recorded for this case yet.</p>
                </div>
                <div v-else>
                  <div v-for="activity in getCaseActivity(selectedCaseDetails)" :key="activity.id" class="timeline-item">
                    <div class="timeline-marker">
                      <div class="timeline-icon" :class="getActivityIconClass(activity.type)">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                          <path :d="getActivityIcon(activity.type)" stroke="currentColor" stroke-width="2"/>
                        </svg>
                      </div>
                    </div>
                    <div class="timeline-content">
                      <div class="timeline-header">
                        <h4 class="timeline-title">{{ activity.type }}</h4>
                        <span class="timeline-time">{{ formatActivityTime(activity.at) }}</span>
                      </div>
                      <div class="timeline-body">
                        <p class="timeline-user">By: {{ activity.by }}</p>
                        <div v-if="activity.changes" class="timeline-changes">
                          <h5>Changes Made:</h5>
                          <ul>
                            <li v-for="(value, key) in activity.changes" :key="key">
                              <strong>{{ formatFieldName(key) }}:</strong> {{ value }}
                            </li>
                          </ul>
                        </div>
                        <div v-if="activity.details" class="timeline-details">
                          <p>{{ activity.details.perpetratorName ? `Perpetrator: ${activity.details.perpetratorName}` : '' }}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Case Update Modal -->
        <div v-if="updateModalOpen" class="case-update-modal" @click="closeUpdateModal">
          <div class="modal-content" @click.stop>
            <div class="modal-header">
              <h2 class="modal-title">{{ getCaseTitle(selectedCaseDetails) }}</h2>
              <button class="modal-close" @click="closeUpdateModal">×</button>
            </div>
            
            <div class="modal-body">
              <form @submit.prevent="saveCaseUpdate">
                <div class="form-group">
                  <label for="case-plan-update">Case Plan Update *</label>
                  <textarea
                    v-model="updateForm.casePlan"
                    id="case-plan-update"
                    class="form-control"
                    rows="4"
                    placeholder="Enter case plan update..."
                    required
                  ></textarea>
                </div>

                <div class="form-group">
                  <label for="justice-system-state-update">State of the Case in the Justice System</label>
                  <select
                    v-model="updateForm.justiceSystemState"
                    id="justice-system-state-update"
                    class="form-control"
                  >
                    <option value="">Select state...</option>
                    <option value="Social Worker">Social Worker</option>
                    <option value="Police Investigation">Police Investigation</option>
                    <option value="Court Proceedings">Court Proceedings</option>
                    <option value="Prosecution">Prosecution</option>
                    <option value="Sentencing">Sentencing</option>
                    <option value="Closed">Closed</option>
                  </select>
              </div>

                <div class="form-group">
                  <label for="general-assessment-update">General Case Assessment</label>
                  <select
                    v-model="updateForm.generalAssessment"
                    id="general-assessment-update"
                    class="form-control"
                  >
                    <option value="">Select assessment...</option>
                    <option value="Progressing">Progressing</option>
                    <option value="Stalled">Stalled</option>
                    <option value="Resolved">Resolved</option>
                    <option value="Escalated">Escalated</option>
                    <option value="Under Review">Under Review</option>
                  </select>
            </div>

                <div class="form-group">
                  <label for="priority-update">Priority *</label>
                  <select
                    v-model="updateForm.priority"
                    id="priority-update"
                    class="form-control"
                    required
                  >
                    <option value="">Select priority...</option>
                    <option value="Low">Low</option>
                    <option value="Medium">Medium</option>
                    <option value="High">High</option>
                    <option value="Critical">Critical</option>
                  </select>
              </div>

                <div class="form-group">
                  <label for="status-update">Status *</label>
                  <select
                    v-model="updateForm.status"
                    id="status-update"
                    class="form-control"
                    required
                  >
                    <option value="">Select status...</option>
                    <option value="New">New</option>
                    <option value="In Progress">In Progress</option>
                    <option value="Pending">Pending</option>
                    <option value="Ongoing">Ongoing</option>
                    <option value="Resolved">Resolved</option>
                    <option value="Closed">Closed</option>
                  </select>
            </div>

                <div class="form-group">
                  <label for="escalated-to-update">Escalated To</label>
                  <select
                    v-model="updateForm.escalatedTo"
                    id="escalated-to-update"
                    class="form-control"
                  >
                    <option value="">Select escalation level...</option>
                    <option value="Supervisor">Supervisor</option>
                    <option value="Manager">Manager</option>
                    <option value="Director">Director</option>
                    <option value="External Agency">External Agency</option>
                    <option value="Law Enforcement">Law Enforcement</option>
                  </select>
              </div>

                <!-- File Management Section -->
                <div class="form-group">
                  <label>File Management</label>
                  <div class="file-management">
                    <div class="current-files">
                      <h5>Current Files:</h5>
                      <div v-if="getCaseFiles(selectedCaseDetails).length" class="files-list">
                        <div v-for="file in getCaseFiles(selectedCaseDetails)" :key="file.name" class="file-item">
                          <div class="file-info">
                            <div class="file-name">{{ file.name }}</div>
                            <div class="file-size">{{ formatFileSize(file.size) }}</div>
            </div>
                          <button class="file-remove" @click="removeFileFromUpdate(file)">×</button>
              </div>
            </div>
                      <div v-else class="empty-state">No files attached</div>
              </div>
                    
                    <div class="add-files">
                      <h5>Add New Files:</h5>
                      <div class="file-upload-area" 
                           @dragover.prevent 
                           @dragleave.prevent 
                           @drop.prevent="handleFileDrop"
                           :class="{ 'drag-over': isDragOver }">
                        <input 
                          ref="fileInput"
                          type="file" 
                          multiple 
                          @change="handleFileSelect"
                          style="display: none;"
                        />
                        <div class="upload-content">
                          <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
                            <path d="M14 2H6C4.9 2 4 2.9 4 4V20C4 21.1 4.89 22 5.99 22H18C19.1 22 20 21.1 20 20V8L14 2Z" stroke="currentColor" stroke-width="2"/>
                            <polyline points="14,2 14,8 20,8" stroke="currentColor" stroke-width="2"/>
                            <line x1="16" y1="13" x2="8" y2="13" stroke="currentColor" stroke-width="2"/>
                            <line x1="16" y1="17" x2="8" y2="17" stroke="currentColor" stroke-width="2"/>
                            <polyline points="10,9 9,9 8,9" stroke="currentColor" stroke-width="2"/>
                          </svg>
                          <p>Drag and drop files here or <button type="button" @click="$refs.fileInput.click()" class="upload-btn">browse</button></p>
                          <small>Supported formats: PDF, DOC, DOCX, JPG, PNG, MP3, WAV</small>
            </div>
              </div>
                      
                      <div v-if="newFiles.length" class="new-files-preview">
                        <h6>Files to be added:</h6>
                        <div v-for="file in newFiles" :key="file.name" class="new-file-item">
                          <span class="file-name">{{ file.name }}</span>
                          <span class="file-size">{{ formatFileSize(file.size) }}</span>
                          <button type="button" @click="removeNewFile(file)" class="remove-new-file">×</button>
            </div>
          </div>
                    </div>
                  </div>
                </div>

                <div class="modal-actions">
                  <button type="button" class="btn btn--secondary" @click="closeUpdateModal">Cancel</button>
                  <button type="submit" class="btn btn--primary">Update</button>
            </div>
              </form>

              <!-- Current Values Display -->
              <div class="current-values">
                <h4>Current Values</h4>
                <div class="current-values-grid">
                  <div class="current-value-item">
                    <span class="current-label">Justice System State:</span>
                    <span class="current-value">{{ updateForm.justiceSystemState || "Not set" }}</span>
              </div>
                  <div class="current-value-item">
                    <span class="current-label">General Assessment:</span>
                    <span class="current-value">{{ updateForm.generalAssessment || "Not set" }}</span>
            </div>
                  <div class="current-value-item">
                    <span class="current-label">Priority:</span>
                    <span class="current-value">{{ updateForm.priority || "Not set" }}</span>
              </div>
                  <div class="current-value-item">
                    <span class="current-label">Status:</span>
                    <span class="current-value">{{ updateForm.status || "Not set" }}</span>
            </div>
                  <div class="current-value-item">
                    <span class="current-label">Escalated To:</span>
                    <span class="current-value">{{ updateForm.escalatedTo || "Not set" }}</span>
              </div>
            </div>
          </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- New Perpetrator Modal -->
    <div v-if="perpetratorModalOpen" class="perpetrator-modal">
      <div class="modal-overlay" @click="closePerpetratorModal"></div>
      <div class="modal-content perpetrator-modal-content">
        <div class="modal-header">
          <h2 class="modal-title">New Perpetrator</h2>
          <button class="modal-close" @click="closePerpetratorModal">×</button>
        </div>
        
        <div class="modal-body">
          <form @submit.prevent="savePerpetrator">
            <div class="form-row">
              <div class="form-column">
                <div class="form-group">
                  <label for="perpetrator-name">Perpetrator's Name *</label>
                  <input
                    v-model="perpetratorForm.name"
                    type="text"
                    id="perpetrator-name"
                    class="form-control"
                    required
                  />
                </div>

                <div class="form-group">
                  <label for="perpetrator-location">Location</label>
                  <select
                    v-model="perpetratorForm.location"
                    id="perpetrator-location"
                    class="form-control"
                  >
                    <option value="">Select location...</option>
                    <option value="Nairobi">Nairobi</option>
                    <option value="Mombasa">Mombasa</option>
                    <option value="Kisumu">Kisumu</option>
                    <option value="Nakuru">Nakuru</option>
                    <option value="Eldoret">Eldoret</option>
                  </select>
                </div>

                <div class="form-group">
                  <label for="perpetrator-landmark">Nearest Landmark</label>
                  <input
                    v-model="perpetratorForm.landmark"
                    type="text"
                    id="perpetrator-landmark"
                    class="form-control"
                  />
                </div>

                <div class="form-group">
                  <label for="perpetrator-id-type">ID Type</label>
                  <select
                    v-model="perpetratorForm.idType"
                    id="perpetrator-id-type"
                    class="form-control"
                  >
                    <option value="">Select ID type...</option>
                    <option value="National ID">National ID</option>
                    <option value="Passport">Passport</option>
                    <option value="Birth Certificate">Birth Certificate</option>
                    <option value="Alien Card">Alien Card</option>
                  </select>
                </div>

                <div class="form-group">
                  <label>Is the Perpetrator a Refugee?</label>
                  <div class="radio-group">
                    <label class="radio-label">
                      <input type="radio" v-model="perpetratorForm.isRefugee" value="Yes" />
                      Yes
                    </label>
                    <label class="radio-label">
                      <input type="radio" v-model="perpetratorForm.isRefugee" value="No" />
                      No
                    </label>
                    <label class="radio-label">
                      <input type="radio" v-model="perpetratorForm.isRefugee" value="Unknown" />
                      Unknown
                    </label>
                  </div>
                </div>

                <div class="form-group">
                  <label for="perpetrator-phone">Phone Number</label>
                  <input
                    v-model="perpetratorForm.phone"
                    type="tel"
                    id="perpetrator-phone"
                    class="form-control"
                  />
                </div>

                <div class="form-group">
                  <label for="perpetrator-relationship">Relationship with Client?</label>
                  <select
                    v-model="perpetratorForm.relationship"
                    id="perpetrator-relationship"
                    class="form-control"
                  >
                    <option value="">Select relationship...</option>
                    <option value="Parent">Parent</option>
                    <option value="Sibling">Sibling</option>
                    <option value="Relative">Relative</option>
                    <option value="Friend">Friend</option>
                    <option value="Stranger">Stranger</option>
                    <option value="Teacher">Teacher</option>
                    <option value="Neighbor">Neighbor</option>
                  </select>
                </div>

                <div class="form-group">
                  <label for="perpetrator-health">Health Status</label>
                  <select
                    v-model="perpetratorForm.healthStatus"
                    id="perpetrator-health"
                    class="form-control"
                  >
                    <option value="">Select Health Status</option>
                    <option value="Good">Good</option>
                    <option value="Fair">Fair</option>
                    <option value="Poor">Poor</option>
                    <option value="Unknown">Unknown</option>
                  </select>
                </div>

                <div class="form-group">
                  <label for="perpetrator-guardian">Perpetrator's Guardian's Name</label>
                  <input
                    v-model="perpetratorForm.guardianName"
                    type="text"
                    id="perpetrator-guardian"
                    class="form-control"
                  />
                </div>
              </div>

              <div class="form-column">
                <div class="form-group">
                  <label for="perpetrator-age">Age</label>
                  <input
                    v-model="perpetratorForm.age"
                    type="number"
                    id="perpetrator-age"
                    class="form-control"
                  />
                </div>

                <div class="form-group">
                  <label for="perpetrator-dob">DOB</label>
                  <input
                    v-model="perpetratorForm.dob"
                    type="date"
                    id="perpetrator-dob"
                    class="form-control"
                  />
                </div>

                <div class="form-group">
                  <label for="perpetrator-age-group">Age Group</label>
                  <input
                    v-model="perpetratorForm.ageGroup"
                    type="text"
                    id="perpetrator-age-group"
                    class="form-control"
                  />
                </div>

                <div class="form-group">
                  <label for="perpetrator-sex">Sex</label>
                  <select
                    v-model="perpetratorForm.sex"
                    id="perpetrator-sex"
                    class="form-control"
                  >
                    <option value="">Select sex...</option>
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                  </select>
                </div>

                <div class="form-group">
                  <label for="perpetrator-nationality">Nationality</label>
                  <select
                    v-model="perpetratorForm.nationality"
                    id="perpetrator-nationality"
                    class="form-control"
                  >
                    <option value="">Select nationality...</option>
                    <option value="Kenyan">Kenyan</option>
                    <option value="Ugandan">Ugandan</option>
                    <option value="Tanzanian">Tanzanian</option>
                    <option value="Somali">Somali</option>
                    <option value="Ethiopian">Ethiopian</option>
                    <option value="Other">Other</option>
                  </select>
                </div>

                <div class="form-group">
                  <label for="perpetrator-id-number">ID Number</label>
                  <input
                    v-model="perpetratorForm.idNumber"
                    type="text"
                    id="perpetrator-id-number"
                    class="form-control"
                  />
                </div>

                <div class="form-group">
                  <label for="perpetrator-language">Language</label>
                  <select
                    v-model="perpetratorForm.language"
                    id="perpetrator-language"
                    class="form-control"
                  >
                    <option value="">Select language...</option>
                    <option value="English">English</option>
                    <option value="Kiswahili">Kiswahili</option>
                    <option value="Luo">Luo</option>
                    <option value="Kikuyu">Kikuyu</option>
                    <option value="Kalenjin">Kalenjin</option>
                    <option value="Luhya">Luhya</option>
                    <option value="Kamba">Kamba</option>
                    <option value="Other">Other</option>
                  </select>
                </div>

                <div class="form-group">
                  <label for="perpetrator-tribe">Tribe</label>
                  <select
                    v-model="perpetratorForm.tribe"
                    id="perpetrator-tribe"
                    class="form-control"
                  >
                    <option value="">Select tribe...</option>
                    <option value="Kikuyu">Kikuyu</option>
                    <option value="Luo">Luo</option>
                    <option value="Kalenjin">Kalenjin</option>
                    <option value="Luhya">Luhya</option>
                    <option value="Kamba">Kamba</option>
                    <option value="Kisii">Kisii</option>
                    <option value="Meru">Meru</option>
                    <option value="Other">Other</option>
                  </select>
                </div>

                <div class="form-group">
                  <label for="perpetrator-alt-phone">Alternative Phone</label>
                  <input
                    v-model="perpetratorForm.alternativePhone"
                    type="tel"
                    id="perpetrator-alt-phone"
                    class="form-control"
                  />
                </div>

                <div class="form-group">
                  <label for="perpetrator-email">Email</label>
                  <input
                    v-model="perpetratorForm.email"
                    type="email"
                    id="perpetrator-email"
                    class="form-control"
                  />
                </div>

                <div class="form-group">
                  <label for="perpetrator-shares-home">Shares Home with Client?</label>
                  <select
                    v-model="perpetratorForm.sharesHome"
                    id="perpetrator-shares-home"
                    class="form-control"
                  >
                    <option value="">Select...</option>
                    <option value="Yes">Yes</option>
                    <option value="No">No</option>
                    <option value="Unknown">Unknown</option>
                  </select>
                </div>

                <div class="form-group">
                  <label for="perpetrator-profession">Perpetrator's Profession</label>
                  <select
                    v-model="perpetratorForm.profession"
                    id="perpetrator-profession"
                    class="form-control"
                  >
                    <option value="">Select profession...</option>
                    <option value="Teacher">Teacher</option>
                    <option value="Doctor">Doctor</option>
                    <option value="Driver">Driver</option>
                    <option value="Farmer">Farmer</option>
                    <option value="Business Owner">Business Owner</option>
                    <option value="Unemployed">Unemployed</option>
                    <option value="Student">Student</option>
                    <option value="Other">Other</option>
                  </select>
                </div>

                <div class="form-group">
                  <label for="perpetrator-marital-status">Perpetrator's Marital Status</label>
                  <select
                    v-model="perpetratorForm.maritalStatus"
                    id="perpetrator-marital-status"
                    class="form-control"
                  >
                    <option value="">Select marital status...</option>
                    <option value="Single">Single</option>
                    <option value="Married">Married</option>
                    <option value="Divorced">Divorced</option>
                    <option value="Widowed">Widowed</option>
                    <option value="Separated">Separated</option>
                  </select>
                </div>
              </div>
            </div>

            <div class="form-group">
              <label for="perpetrator-additional-details">Additional Details</label>
              <textarea
                v-model="perpetratorForm.additionalDetails"
                id="perpetrator-additional-details"
                class="form-control"
                rows="4"
                placeholder="Enter any additional information about the perpetrator..."
              ></textarea>
            </div>

            <div class="modal-actions">
              <button type="button" class="btn btn--secondary" @click="closePerpetratorModal">Cancel</button>
              <button type="submit" class="btn btn--primary">Create</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import SidePanel from "@/components/SidePanel.vue";
import { useCaseStore } from "@/stores/cases";

const casesStore = useCaseStore();
const router = useRouter();

// Reactive state
const searchQuery = ref("");
const activeFilter = ref("all");
const selectedCaseId = ref(null);
const currentTheme = ref("light");
const currentView = ref("table"); // Default to table view
const updateModalOpen = ref(false);
const currentTab = ref('details');
const perpetratorModalOpen = ref(false);
const isDragOver = ref(false);
const newFiles = ref([]);
const filesToRemove = ref([]);

// Update form data
const updateForm = ref({
  casePlan: '',
  justiceSystemState: '',
  generalAssessment: '',
  priority: '',
  status: '',
  escalatedTo: ''
});

// Perpetrator form data
const perpetratorForm = ref({
  name: '',
  location: '',
  landmark: '',
  idType: '',
  isRefugee: '',
  phone: '',
  relationship: '',
  healthStatus: '',
  guardianName: '',
  age: '',
  dob: '',
  ageGroup: '',
  sex: '',
  nationality: '',
  idNumber: '',
  language: '',
  tribe: '',
  alternativePhone: '',
  email: '',
  sharesHome: '',
  profession: '',
  maritalStatus: '',
  additionalDetails: ''
});

// SidePanel related state
const userRole = ref("super-admin");
const isInQueue = ref(false);
const isProcessingQueue = ref(false);
const currentCall = ref(null);

// Filter options
const filters = ref([
  { id: "all", name: "All" },
  { id: "open", name: "Open", status: "open" },
  { id: "pending", name: "Pending", status: "pending" },
  { id: "assigned", name: "Assigned" },
  { id: "closed", name: "Closed", status: "closed" },
  { id: "today", name: "Today" },
  { id: "priority", name: "Priority" },
]);

// Computed properties
const filteredCases = computed(() => {
  let filtered = casesStore.cases || [];
 
  const normalizeStatus = (value) => {
    if (!value && value !== 0) return '';
    const v = String(value).toLowerCase();
    if (v === '1') return 'open';
    if (v === '2') return 'closed';
    if (v === '0') return 'pending';
    return v; // already a label like 'open', 'closed', 'pending'
  };

  const normalizePriority = (value) => {
    if (!value && value !== 0) return '';
    const v = String(value).toLowerCase();
    if (v === '3') return 'high';
    if (v === '2') return 'medium';
    if (v === '1') return 'low';
    return v; // already a label
  };

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    filtered = filtered.filter((c) => {
      // Search in case title/category
      const title = casesStore.cases_k?.cat_1 ? c[casesStore.cases_k.cat_1[0]] : '';
      // Search in assigned to
      const assignedTo = casesStore.cases_k?.assigned_to ? c[casesStore.cases_k.assigned_to[0]] : '';
      // Search in created by
      const createdBy = casesStore.cases_k?.created_by ? c[casesStore.cases_k.created_by[0]] : '';
      // Search in source
      const source = casesStore.cases_k?.source ? c[casesStore.cases_k.source[0]] : '';
      
      return (
        (title && title.toString().toLowerCase().includes(query)) ||
        (assignedTo && assignedTo.toString().toLowerCase().includes(query)) ||
        (createdBy && createdBy.toString().toLowerCase().includes(query)) ||
        (source && source.toString().toLowerCase().includes(query))
      );
    });
  }

  if (activeFilter.value !== "all") {
    const filterStatus = filters.value.find(
      (f) => f.id === activeFilter.value
    )?.status;
    if (filterStatus) {
      filtered = filtered.filter((c) => {
        const raw = casesStore.cases_k?.status ? c[casesStore.cases_k.status[0]] : '';
        const status = normalizeStatus(raw);
        return status && status === filterStatus.toLowerCase();
      });
    } else if (activeFilter.value === "assigned") {
      filtered = filtered.filter((c) => {
        const assignedTo = casesStore.cases_k?.assigned_to ? c[casesStore.cases_k.assigned_to[0]] : '';
        return assignedTo && assignedTo.trim() !== '';
      });
    } else if (activeFilter.value === "priority") {
      filtered = filtered.filter((c) => {
        const raw = casesStore.cases_k?.priority ? c[casesStore.cases_k.priority[0]] : '';
        const priority = normalizePriority(raw);
        return priority === 'high';
      });
    } else if (activeFilter.value === "today") {
      // Filter for today's cases
      const today = new Date().toDateString();
      filtered = filtered.filter((c) => {
        if (casesStore.cases_k?.dt && c[casesStore.cases_k.dt[0]]) {
          const caseDate = new Date(
            c[casesStore.cases_k.dt[0]] < 10000000000
              ? c[casesStore.cases_k.dt[0]] * 1000
              : c[casesStore.cases_k.dt[0]] * 3600 * 1000
          );
          return caseDate.toDateString() === today;
        }
        return false;
      });
    }
  }

  return filtered;
});

// Edit modal state and helpers
const editModalOpen = ref(false);
const editForm = ref({ priority: 'Medium', status: 'Open', assignedTo: '', casePlan: '' });
let editingCaseRef = null;

const openEdit = (caseItem) => {
  editingCaseRef = caseItem;
  editForm.value = {
    priority: (casesStore.cases_k?.priority ? caseItem[casesStore.cases_k.priority[0]] : '') || 'Medium',
    status: (casesStore.cases_k?.status ? caseItem[casesStore.cases_k.status[0]] : '') || 'Open',
    assignedTo: (casesStore.cases_k?.assigned_to ? caseItem[casesStore.cases_k.assigned_to[0]] : '') || '',
    casePlan: caseItem.casePlan || ''
  };
  editModalOpen.value = true;
};

const closeEdit = () => { editModalOpen.value = false; editingCaseRef = null; };

const saveEdit = () => {
  if (!editingCaseRef) return;
  if (casesStore.cases_k?.priority) editingCaseRef[casesStore.cases_k.priority[0]] = editForm.value.priority;
  if (casesStore.cases_k?.status) editingCaseRef[casesStore.cases_k.status[0]] = editForm.value.status;
  if (casesStore.cases_k?.assigned_to) editingCaseRef[casesStore.cases_k.assigned_to[0]] = editForm.value.assignedTo;
  editingCaseRef.casePlan = editForm.value.casePlan;
  // Log to a simple activity timeline array on the case
  const now = new Date();
  editingCaseRef.activity = editingCaseRef.activity || [];
  editingCaseRef.activity.unshift({
    type: 'Case Updated',
    by: 'current user',
    at: now.toISOString(),
    changes: { ...editForm.value }
  });
  editModalOpen.value = false;
};

const selectedCaseDetails = computed(() => {
  if (!casesStore.cases_k?.id) return null;
  return casesStore.cases.find(
    (caseItem) => caseItem[casesStore.cases_k.id[0]] === selectedCaseId.value
  );
});

const setCurrentView = (view) => {
  currentView.value = view;
};

const setActiveFilter = (filterId) => {
  activeFilter.value = filterId;
};

// SidePanel event handlers
const handleQueueToggle = () => {
  isInQueue.value = !isInQueue.value;
  console.log("Queue toggled:", isInQueue.value);
};

const handleLogout = () => {
  router.push("/");
};

const handleSidebarToggle = (collapsed) => {
  console.log("Sidebar toggled:", collapsed);
};

// Theme methods (unchanged)
const applyTheme = (theme) => {
  const root = document.documentElement;

  if (theme === "light") {
    root.style.setProperty("--background-color", "#f5f5f5");
    root.style.setProperty("--sidebar-bg", "#ffffff");
    root.style.setProperty("--content-bg", "#ffffff");
    root.style.setProperty("--text-color", "#333");
    root.style.setProperty("--text-secondary", "#666");
    root.style.setProperty("--border-color", "#ddd");
    root.style.setProperty("--card-bg", "#ffffff");
    root.style.setProperty("--header-bg", "#ffffff");
    root.style.setProperty("--input-bg", "#f0f0f0");
    root.setAttribute("data-theme", "light");
  } else {
    root.style.setProperty("--background-color", "#0a0a0a");
    root.style.setProperty("--sidebar-bg", "#111");
    root.style.setProperty("--content-bg", "#222");
    root.style.setProperty("--text-color", "#fff");
    root.style.setProperty("--text-secondary", "#aaa");
    root.style.setProperty("--border-color", "#333");
    root.style.setProperty("--card-bg", "#222");
    root.style.setProperty("--header-bg", "#333");
    root.style.setProperty("--input-bg", "#1a1a1a");
    root.setAttribute("data-theme", "dark");
  }

  // Common variables
      root.style.setProperty("--accent-color", "#8B4513");
    root.style.setProperty("--accent-hover", "#A0522D");
  root.style.setProperty("--danger-color", "#ff3b30");
  root.style.setProperty("--success-color", "#4CAF50");
  root.style.setProperty("--pending-color", "#FFA500");
  root.style.setProperty("--unassigned-color", "#808080");
  root.style.setProperty("--highlight-color", "#ff3b30");
  root.style.setProperty("--high-priority", "#ff3b30");
  root.style.setProperty("--medium-priority", "#FFA500");
  root.style.setProperty("--low-priority", "#4CAF50");
};

const toggleTheme = () => {
  const newTheme = currentTheme.value === "dark" ? "light" : "dark";
  localStorage.setItem("theme", newTheme);
  currentTheme.value = newTheme;
  applyTheme(newTheme);
};

const selectCase = (caseId) => {
  selectedCaseId.value = caseId;
};

const openUpdateModal = () => {
  console.log('openUpdateModal called');
  console.log('selectedCaseDetails:', selectedCaseDetails.value);
  console.log('updateModalOpen before:', updateModalOpen.value);
  
  if (!selectedCaseDetails.value) {
    console.error('No case selected for update');
    alert('No case selected for update');
    return;
  }
  
  // Initialize form with current case data
  updateForm.value = {
    casePlan: selectedCaseDetails.value.casePlan || '',
    justiceSystemState: selectedCaseDetails.value.justiceSystemState || '',
    generalAssessment: selectedCaseDetails.value.generalAssessment || '',
    priority: selectedCaseDetails.value.priority || '',
    status: selectedCaseDetails.value.status || '',
    escalatedTo: selectedCaseDetails.value.escalatedTo || ''
  };
  
  console.log('updateForm initialized:', updateForm.value);
  
  updateModalOpen.value = true;
  currentTab.value = 'update';
  
  console.log('Modal opened, updateModalOpen after:', updateModalOpen.value);
  console.log('currentTab:', currentTab.value);
};

const handleUpdateTabClick = () => {
  console.log('Update tab clicked');
  openUpdateModal();
};

const closeUpdateModal = () => {
  updateModalOpen.value = false;
  updateForm.value = {
    casePlan: '',
    justiceSystemState: '',
    generalAssessment: '',
    priority: '',
    status: '',
    escalatedTo: ''
  };
  resetFileManagement();
};

const saveCaseUpdate = () => {
  console.log('saveCaseUpdate called');
  console.log('selectedCaseDetails:', selectedCaseDetails.value);
  console.log('updateForm:', updateForm.value);
  
  if (!selectedCaseDetails.value) {
    console.error('No case selected for update');
    return;
  }

  // Basic validation
  if (!updateForm.value.casePlan.trim()) {
    alert('Please enter a case plan update');
    return;
  }
  
  if (!updateForm.value.priority) {
    alert('Please select a priority');
    return;
  }
  
  if (!updateForm.value.status) {
    alert('Please select a status');
    return;
  }

  // Update the case with new values
  const caseItem = selectedCaseDetails.value;
  caseItem.casePlan = updateForm.value.casePlan;
  caseItem.justiceSystemState = updateForm.value.justiceSystemState;
  caseItem.generalAssessment = updateForm.value.generalAssessment;
  caseItem.priority = updateForm.value.priority;
  caseItem.status = updateForm.value.status;
  caseItem.escalatedTo = updateForm.value.escalatedTo;

  // Handle file management
  if (filesToRemove.value.length > 0) {
    caseItem.files = caseItem.files.filter(file => 
      !filesToRemove.value.find(removedFile => removedFile.name === file.name)
    );
  }

  if (newFiles.value.length > 0) {
    caseItem.files = caseItem.files || [];
    newFiles.value.forEach(newFile => {
      caseItem.files.push({
        name: newFile.name,
        size: newFile.size
      });
    });
  }

  // Log the update to activity timeline
  const now = new Date();
  caseItem.activity = caseItem.activity || [];
  
  // Create activity log for case update
  const activityLog = {
    id: Date.now(),
    type: 'Case Updated',
    by: 'current user',
    at: now.toISOString(),
    changes: { ...updateForm.value }
  };
  
  // Add file activity logs
  if (filesToRemove.value.length > 0) {
    filesToRemove.value.forEach(file => {
      caseItem.activity.unshift({
        id: Date.now() + Math.random(),
        type: 'File Removed',
        by: 'current user',
        at: now.toISOString(),
        details: { fileName: file.name }
      });
    });
  }
  
  if (newFiles.value.length > 0) {
    newFiles.value.forEach(file => {
      caseItem.activity.unshift({
        id: Date.now() + Math.random(),
        type: 'File Added',
        by: 'current user',
        at: now.toISOString(),
        details: { fileName: file.name }
      });
    });
  }
  
  caseItem.activity.unshift(activityLog);

  closeUpdateModal();
  console.log('Case updated successfully:', caseItem);
  
  // Show success message
  alert('Case updated successfully!');
};

const openEditModal = () => {
  console.log('Opening edit modal for case:', selectedCaseId.value);
  console.log('selectedCaseDetails:', selectedCaseDetails.value);
  
  if (!selectedCaseDetails.value) {
    console.error('No case selected for edit');
    alert('No case selected for editing');
    return;
  }
  
  // For now, open the update modal as edit functionality
  // In a real application, this would open a different edit modal
  openUpdateModal();
};

const handleEditButtonClick = () => {
  console.log('Edit button clicked');
  openEditModal();
};

const printCase = () => {
  console.log('Printing case:', selectedCaseDetails.value);
  // In a real application, this would open a print dialog
  window.print();
};

// Perpetrator modal methods
const openPerpetratorModal = () => {
  console.log('Opening perpetrator modal');
  perpetratorModalOpen.value = true;
};

const closePerpetratorModal = () => {
  perpetratorModalOpen.value = false;
  // Reset form
  perpetratorForm.value = {
    name: '',
    location: '',
    landmark: '',
    idType: '',
    isRefugee: '',
    phone: '',
    relationship: '',
    healthStatus: '',
    guardianName: '',
    age: '',
    dob: '',
    ageGroup: '',
    sex: '',
    nationality: '',
    idNumber: '',
    language: '',
    tribe: '',
    alternativePhone: '',
    email: '',
    sharesHome: '',
    profession: '',
    maritalStatus: '',
    additionalDetails: ''
  };
};

const savePerpetrator = () => {
  console.log('Saving perpetrator:', perpetratorForm.value);
  
  if (!perpetratorForm.value.name.trim()) {
    alert('Please enter the perpetrator\'s name');
    return;
  }

  // Add perpetrator to case
  if (selectedCaseDetails.value) {
    const perpetrator = {
      id: Date.now(), // Simple ID generation
      ...perpetratorForm.value
    };
    
    selectedCaseDetails.value.perpetrators = selectedCaseDetails.value.perpetrators || [];
    selectedCaseDetails.value.perpetrators.push(perpetrator);
    
    // Log activity
    const now = new Date();
    selectedCaseDetails.value.activity = selectedCaseDetails.value.activity || [];
    selectedCaseDetails.value.activity.unshift({
      type: 'Perpetrator Added',
      by: 'current user',
      at: now.toISOString(),
      details: { perpetratorName: perpetrator.name }
    });
    
    closePerpetratorModal();
    alert('Perpetrator added successfully!');
    console.log('Perpetrator added to case:', selectedCaseDetails.value);
  }
};

const getCasePerpetrators = (caseItem) => {
  return caseItem?.perpetrators || [];
};

// Case History Methods
const getCaseActivity = (caseItem) => {
  return caseItem?.activity || [];
};

const getActivityIcon = (type) => {
  const icons = {
    'Case Updated': 'M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z',
    'Perpetrator Added': 'M16 21V19C16 17.9391 15.5786 16.9217 14.8284 16.1716C14.0783 15.4214 13.0609 15 12 15H5C3.93913 15 2.92172 15.4214 2.17157 16.1716C1.42143 16.9217 1 17.9391 1 19V21M13 7C13 9.20914 11.2091 11 9 11C6.79086 11 5 9.20914 5 7C5 4.79086 6.79086 3 9 3C11.2091 3 13 4.79086 13 7ZM23 21V19C22.9993 18.1137 22.7044 17.2528 22.1614 16.5523C21.6184 15.8519 20.8581 15.3516 20 15.13M16 3.13C16.8604 3.35031 17.623 3.85071 18.1676 4.55232C18.7122 5.25392 19.0078 6.11683 19.0078 7.005C19.0078 7.89317 18.7122 8.75608 18.1676 9.45768C17.623 10.1593 16.8604 10.6597 16 10.88',
    'File Added': 'M14 2H6C4.9 2 4 2.9 4 4V20C4 21.1 4.89 22 5.99 22H18C19.1 22 20 21.1 20 20V8L14 2ZM16 18H8V16H16V18ZM16 14H8V12H16V14ZM13 9V3.5L18.5 9H13Z',
    'File Removed': 'M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12ZM10 10L14 14M14 10L10 14'
  };
  return icons[type] || icons['Case Updated'];
};

const getActivityIconClass = (type) => {
  const classes = {
    'Case Updated': 'icon-update',
    'Perpetrator Added': 'icon-add',
    'File Added': 'icon-file-add',
    'File Removed': 'icon-file-remove'
  };
  return classes[type] || 'icon-update';
};

const formatActivityTime = (timestamp) => {
  const date = new Date(timestamp);
  return date.toLocaleString();
};

const formatFieldName = (fieldName) => {
  const fieldMap = {
    casePlan: 'Case Plan',
    justiceSystemState: 'Justice System State',
    generalAssessment: 'General Assessment',
    priority: 'Priority',
    status: 'Status',
    escalatedTo: 'Escalated To'
  };
  return fieldMap[fieldName] || fieldName;
};

// File Management Methods
const formatFileSize = (bytes) => {
  if (!bytes) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const handleFileDrop = (event) => {
  isDragOver.value = false;
  const files = Array.from(event.dataTransfer.files);
  addFiles(files);
};

const handleFileSelect = (event) => {
  const files = Array.from(event.target.files);
  addFiles(files);
};

const addFiles = (files) => {
  files.forEach(file => {
    if (!newFiles.value.find(f => f.name === file.name)) {
      newFiles.value.push({
        name: file.name,
        size: file.size,
        file: file
      });
    }
  });
};

const removeNewFile = (file) => {
  const index = newFiles.value.findIndex(f => f.name === file.name);
  if (index > -1) {
    newFiles.value.splice(index, 1);
  }
};

const removeFileFromUpdate = (file) => {
  filesToRemove.value.push(file);
};

const resetFileManagement = () => {
  newFiles.value = [];
  filesToRemove.value = [];
  isDragOver.value = false;
};

// Helper methods for case details
const getCaseTitle = (caseItem) => {
  if (casesStore.cases_k?.cat_1 && caseItem[casesStore.cases_k.cat_1[0]]) {
    return caseItem[casesStore.cases_k.cat_1[0]];
  }
  return caseItem.title || caseItem.caseTitle || "Case Details";
};

const getCaseId = (caseItem) => {
  if (casesStore.cases_k?.id && caseItem[casesStore.cases_k.id[0]]) {
    return caseItem[casesStore.cases_k.id[0]];
  }
  return caseItem.id || "N/A";
};

const getReporterName = (caseItem) => {
  if (casesStore.cases_k?.created_by && caseItem[casesStore.cases_k.created_by[0]]) {
    return caseItem[casesStore.cases_k.created_by[0]];
  }
  return caseItem.reporterName || caseItem.reporter_name || "mark";
};

const getReporterDemographics = (caseItem) => {
  const age = caseItem.reporterAge || caseItem.reporter_age || "18-24";
  const gender = caseItem.reporterGender || caseItem.reporter_gender || "Female";
  return `${age} ${gender}`;
};

const getReporterLocation = (caseItem) => {
  if (casesStore.cases_k?.reporter_location && caseItem[casesStore.cases_k.reporter_location[0]]) {
    return caseItem[casesStore.cases_k.reporter_location[0]];
  }
  return caseItem.reporterLocation || caseItem.reporter_location || "EASTERN > AMURIA > AMURIA";
};

const getCaseFiles = (caseItem) => {
  if (caseItem.files && Array.isArray(caseItem.files)) {
    return caseItem.files;
  }
  // Return mock files for demonstration
  return [
    { name: "1756073575.0.wav16", size: "1535404" },
    { name: "WhatsApp Image 2025-09-02 at 8.20.14 AM.jpeg", size: "144935" },
    { name: "aa.flac", size: "679546" }
  ];
};

const closeCaseDetails = () => {
  selectedCaseId.value = null;
};

const callReporter = (caseItem) => {
  const phone = caseItem.reporterPhone || caseItem.reporter_phone;
  if (phone) {
    window.open(`tel:${phone}`, '_self');
  } else {
    console.log('No phone number available for reporter');
  }
};

const emailReporter = (caseItem) => {
  const email = caseItem.reporterEmail || caseItem.reporter_email;
  if (email) {
    window.open(`mailto:${email}`, '_self');
  } else {
    console.log('No email address available for reporter');
  }
};

const removeFile = (file) => {
  console.log('Removing file:', file.name);
  // In a real application, this would remove the file from the case
};

const getCaseDepartment = (caseItem) => {
  return caseItem.department || "116";
};

const getCaseNarrative = (caseItem) => {
  return caseItem.narrative || caseItem.caseNarrative || "yes";
};

const getCasePlan = (caseItem) => {
  return caseItem.casePlan || "yes";
};

const getJusticeSystemState = (caseItem) => {
  return caseItem.justiceSystemState || "Social Worker";
};

const getGeneralAssessment = (caseItem) => {
  return caseItem.generalAssessment || "Progressing";
};

const getEscalatedTo = (caseItem) => {
  return caseItem.escalatedTo || "N/A";
};

const handleSearch = () => {
  // Filtering handled by 'filteredCases'
};

// Lifecycle hooks
onMounted(() => {
  casesStore.listCases();
  console.log("Cases loaded:", casesStore.raw);
  const savedTheme = localStorage.getItem("theme") || "light";
  currentTheme.value = savedTheme;
  applyTheme(savedTheme);
});
</script>

<style scoped>
/* Ensure priority label is readable even when no variant class matches */
.priority-badge {
  color: var(--text-color);
  background: var(--content-bg);
  border: 1px solid var(--border-color);
  text-transform: capitalize;
}

/* Map numeric values coming from API (1/2/3) to visual styles */
.priority-badge.\31 { /* 1 → low */
  background: rgba(21, 128, 61, 0.1);
  color: var(--success-color);
}
.priority-badge.\32 { /* 2 → medium */
  background: rgba(255, 149, 0, 0.1);
  color: #ff9500;
}
.priority-badge.\33 { /* 3 → high */
  background: rgba(204, 47, 47, 0.1);
  color: var(--danger-color);
}

/* Support textual variants as well */
.priority-badge.low {
  background: rgba(21, 128, 61, 0.1);
  color: var(--success-color);
}
.priority-badge.medium {
  background: rgba(255, 149, 0, 0.1);
  color: #ff9500;
}
.priority-badge.high {
  background: rgba(204, 47, 47, 0.1);
  color: var(--danger-color);
}
.priority-badge.normal {
  background: rgba(0, 0, 0, 0.04);
  color: var(--text-color);
}

/* Priority indicator dot uses current text color by default */
.priority-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
  background: currentColor;
  border: none;
}

.priority-dot.low, .priority-dot.\31 { background: var(--success-color); }
.priority-dot.medium, .priority-dot.\32 { background: #ff9500; }
.priority-dot.high, .priority-dot.\33 { background: var(--danger-color); }
.priority-dot.normal { background: var(--text-color); }

/* Enhanced Case Detail Drawer Styles */
.case-detail-drawer {
  position: fixed;
  top: 0;
  right: 0;
  width: 100%;
  max-width: 800px;
  height: 100vh;
  background: var(--color-surface);
  border-left: 1px solid var(--color-border);
  box-shadow: -4px 0 20px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  overflow-y: auto;
}

.case-detail-drawer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface);
  position: sticky;
  top: 0;
  z-index: 10;
}

.case-detail-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 18px;
  font-weight: 700;
  color: var(--text-color);
}

.back-button {
  background: none;
  border: none;
  color: var(--color-muted);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.back-button:hover {
  background: var(--color-surface-muted);
  color: var(--text-color);
}

.case-detail-id {
  font-size: 14px;
  color: var(--color-muted);
}

.close-details {
  background: none;
  border: none;
  font-size: 24px;
  color: var(--color-muted);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.close-details:hover {
  background: var(--color-surface-muted);
  color: var(--text-color);
}

/* Case Navigation Tabs */
.case-tabs {
  display: flex;
  align-items: center;
  padding: 0 20px;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface);
  position: sticky;
  top: 73px;
  z-index: 9;
}

.case-tab {
  background: none;
  border: none;
  padding: 12px 16px;
  font-size: 14px;
  font-weight: 600;
  color: var(--color-muted);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.2s ease;
}

.case-tab:hover {
  color: var(--text-color);
}

.case-tab.active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}

.edit-case-btn {
  margin-left: auto;
  background: var(--color-primary);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.edit-case-btn:hover {
  background: color-mix(in oklab, var(--color-primary) 80%, black);
}

/* Case Detail Content */
.case-detail-content {
  padding: 20px;
}

.detail-section {
  margin-bottom: 24px;
}

.section-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-color);
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--color-border);
}

/* Reporter Information */
.reporter-info {
  background: var(--color-surface-muted);
  border-radius: 8px;
  padding: 16px;
}

.reporter-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.reporter-name {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-color);
}

.reporter-demographics {
  font-size: 14px;
  color: var(--color-muted);
}

.reporter-location {
  font-size: 14px;
  color: var(--color-muted);
}

.reporter-contacts {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.contact-btn {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  padding: 8px;
  color: var(--color-muted);
  cursor: pointer;
  transition: all 0.2s ease;
}

.contact-btn:hover {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

/* Followup Info */
.followup-info {
  background: var(--color-surface-muted);
  border-radius: 8px;
  padding: 16px;
}

.followup-contacts {
  display: flex;
  gap: 8px;
}

/* Empty States */
.empty-state {
  background: var(--color-surface-muted);
  border-radius: 8px;
  padding: 16px;
  text-align: center;
  color: var(--color-muted);
  font-style: italic;
}

/* Files List */
.files-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.file-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--color-surface-muted);
  border-radius: 8px;
  padding: 12px 16px;
}

.file-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-color);
  flex: 1;
}

.file-size {
  font-size: 12px;
  color: var(--color-muted);
  margin-right: 12px;
}

.file-remove {
  background: none;
  border: none;
  color: var(--color-muted);
  cursor: pointer;
  font-size: 16px;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.file-remove:hover {
  background: var(--color-danger);
  color: white;
}

/* Services Info */
.services-info {
  background: var(--color-surface-muted);
  border-radius: 8px;
  padding: 16px;
}

.service-item {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-color);
}

/* Case Info Grid */
.case-info-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}

@media (min-width: 768px) {
  .case-info-grid {
    grid-template-columns: 1fr 1fr;
  }
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-value {
  font-size: 14px;
  color: var(--text-color);
}

/* Category Tags */
.category-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.category-tag {
  display: inline-block;
  padding: 4px 8px;
  background: var(--color-primary);
  color: white;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

/* Status Badges */
.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.status-yes {
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
}

.status-ongoing {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

/* Priority Badge */
.priority-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.priority-badge.high {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

/* Case Update Modal */
.case-update-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 3000;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.2);
}

/* Perpetrator Modal */
.perpetrator-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 3000;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.2);
}

.perpetrator-modal-content {
  width: 95%;
  max-width: 1000px;
  max-height: 95vh;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

.form-column {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.radio-group {
  display: flex;
  gap: 16px;
  margin-top: 8px;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  cursor: pointer;
}

.radio-label input[type="radio"] {
  margin: 0;
}

.perpetrators-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}

.perpetrator-item {
  padding: 12px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 8px;
}

.perpetrator-name {
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 4px;
}

.perpetrator-details {
  font-size: 14px;
  color: var(--text-secondary);
}

/* Case History Styles */
.case-history-content {
  padding: 20px;
}

.history-header {
  margin-bottom: 24px;
}

.history-subtitle {
  color: var(--text-secondary);
  margin-top: 8px;
}

.timeline {
  position: relative;
  padding-left: 30px;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 15px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: var(--color-border);
}

.timeline-item {
  position: relative;
  margin-bottom: 24px;
}

.timeline-marker {
  position: absolute;
  left: -22px;
  top: 0;
}

.timeline-icon {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid var(--color-border);
  background: white;
}

.timeline-icon.icon-update {
  color: var(--color-primary);
  border-color: var(--color-primary);
}

.timeline-icon.icon-add {
  color: #22c55e;
  border-color: #22c55e;
}

.timeline-icon.icon-file-add {
  color: #3b82f6;
  border-color: #3b82f6;
}

.timeline-icon.icon-file-remove {
  color: #ef4444;
  border-color: #ef4444;
}

.timeline-content {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 16px;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.timeline-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
  color: var(--text-color);
}

.timeline-time {
  font-size: 12px;
  color: var(--text-secondary);
}

.timeline-body {
  color: var(--text-secondary);
}

.timeline-user {
  margin: 0 0 8px 0;
  font-size: 14px;
}

.timeline-changes {
  margin-top: 12px;
}

.timeline-changes h5 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: var(--text-color);
}

.timeline-changes ul {
  margin: 0;
  padding-left: 16px;
}

.timeline-changes li {
  margin-bottom: 4px;
  font-size: 14px;
}

.timeline-details {
  margin-top: 8px;
  font-size: 14px;
}

/* File Management Styles */
.file-management {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-top: 16px;
}

.current-files h5,
.add-files h5 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-color);
}

.file-upload-area {
  border: 2px dashed var(--color-border);
  border-radius: 8px;
  padding: 24px;
  text-align: center;
  transition: all 0.2s ease;
  cursor: pointer;
}

.file-upload-area:hover,
.file-upload-area.drag-over {
  border-color: var(--color-primary);
  background: rgba(0, 0, 0, 0.02);
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.upload-content svg {
  color: var(--text-secondary);
}

.upload-content p {
  margin: 0;
  color: var(--text-color);
}

.upload-btn {
  background: none;
  border: none;
  color: var(--color-primary);
  text-decoration: underline;
  cursor: pointer;
  font-size: inherit;
}

.upload-content small {
  color: var(--text-secondary);
  font-size: 12px;
}

.new-files-preview {
  margin-top: 16px;
}

.new-files-preview h6 {
  margin: 0 0 8px 0;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-color);
}

.new-file-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  margin-bottom: 8px;
}

.new-file-item .file-name {
  font-weight: 500;
  color: var(--text-color);
}

.new-file-item .file-size {
  font-size: 12px;
  color: var(--text-secondary);
}

.remove-new-file {
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 12px;
}

.file-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.modal-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.2);
}

.modal-content {
  position: relative;
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  z-index: 3001;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--color-border);
}

.modal-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-color);
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  color: var(--color-muted);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.modal-close:hover {
  background: var(--color-surface-muted);
  color: var(--text-color);
}

.modal-body {
  padding: 24px;
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

.form-control {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background: var(--color-surface);
  color: var(--text-color);
  font-size: 14px;
  transition: all 0.2s ease;
}

.form-control:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(var(--color-primary-rgb), 0.1);
}

.form-control::placeholder {
  color: var(--color-muted);
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--color-border);
}

/* Current Values Display */
.current-values {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--color-border);
}

.current-values h4 {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-color);
  margin-bottom: 12px;
}

.current-values-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 8px;
}

.current-value-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: var(--color-surface-muted);
  border-radius: 6px;
}

.current-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.current-value {
  font-size: 14px;
  color: var(--text-color);
  font-weight: 600;
}
</style>

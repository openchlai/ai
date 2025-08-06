<template>
  <div class="case-creation-page">
    <router-link class="back-button" to="/cases">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M19 12H5" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" />
        <path d="M12 19L5 12L12 5" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" />
      </svg>
      Back to Cases
    </router-link>

    <button class="theme-toggle" @click="toggleTheme">
      <svg v-if="currentTheme === 'dark'" width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 16C14.2091 16 16 14.2091 16 12C16 9.79086 14.2091 8 12 8C9.79086 8 8 9.79086 8 12C8 14.2091 9.79086 16 12 16Z" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" />
        <path d="M12 2V4M12 20V22M4.93 4.93L6.34 6.34M17.66 17.66L19.07 19.07M2 12H4M20 12H22M4.93 19.07L6.34 17.66M17.66 6.34L19.07 4.93" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" />
      </svg>
      <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <span>{{ currentTheme === 'dark' ? 'Light Mode' : 'Dark Mode' }}</span>
    </button>

    <div class="case-container">
      <div class="main-form-container">
        <div class="case-header">
          <div>
            <h1>Create New Case</h1>
            <p>{{ stepDescriptions[currentStep - 1] }}</p>
          </div>
          <div class="toggle-container">
            <span class="toggle-label">
              <span class="ai-icon">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" />
                  <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" />
                  <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" />
                </svg>
              </span>
              AI Enabled
            </span>
            <label class="toggle-switch">
              <input v-model="isAIEnabled" type="checkbox" />
              <span class="toggle-slider"></span>
            </label>
          </div>
        </div>

        <div class="progress-container">
          <div class="progress-steps">
            <div 
              v-for="step in totalSteps" 
              :key="step"
              class="progress-step"
              :class="{ active: currentStep >= step }"
            >
              <div class="step-circle" :class="{ active: currentStep >= step, completed: currentStep > step }">
                {{ currentStep > step ? '✓' : step }}
              </div>
              <div class="step-label" :class="{ active: currentStep >= step }">{{ stepLabels[step - 1] }}</div>
            </div>
          </div>
        </div>

        <!-- Step 1: Reporter Selection -->
        <div v-show="currentStep === 1" class="step-content">
          <form class="case-form" @submit.prevent="validateAndProceed(1)">
            <div class="form-section">
              <div class="section-title">Select Reporter</div>
              <p class="section-description">Choose an existing contact or create a new reporter for this case.</p>
              
              <div class="search-section">
                <div class="search-box">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="11" cy="11" r="8" stroke="currentColor" stroke-width="2"/>
                    <path d="m21 21-4.35-4.35" stroke="currentColor" stroke-width="2"/>
                  </svg>
                  <input 
                    v-model="searchQuery" 
                    type="text" 
                    placeholder="Search existing contacts..." 
                    class="search-input"
                  />
                </div>
              </div>

              <div class="contacts-grid">
                <div 
                  v-for="contact in filteredContacts" 
                  :key="contact.id"
                  class="contact-card"
                  :class="{ selected: selectedReporter?.id === contact.id }"
                  @click="selectExistingReporter(contact)"
                >
                  <div class="contact-avatar">
                    <span>{{ getInitials(contact.name) }}</span>
                  </div>
                  <div class="contact-info">
                    <div class="contact-name">{{ contact.name }}</div>
                    <div class="contact-details">
                      <span class="contact-tag">{{ contact.age }}y</span>
                      <span class="contact-tag">{{ contact.gender }}</span>
                    </div>
                    <div class="contact-meta">
                      <div class="contact-location">📍 {{ contact.location }}</div>
                      <div class="contact-phone">📞 {{ contact.phone }}</div>
                    </div>
                    <div class="contact-timestamp">{{ contact.lastContact }}</div>
                  </div>
                  <div class="contact-select-indicator">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <polyline points="9,18 15,12 9,6" stroke="currentColor" stroke-width="2"/>
                    </svg>
                  </div>
                </div>
              </div>

              <div class="action-buttons">
                <button 
                  v-if="selectedReporter" 
                  type="submit"
                  class="btn btn-primary btn-large" 
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M5 12l5 5L20 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  Continue with {{ selectedReporter.name }}
                </button>
                <button type="button" class="btn btn-secondary btn-large" @click="createNewReporter">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                  </svg>
                  Create New Reporter
                </button>
              </div>
            </div>
            <div class="form-actions">
              <button type="button" class="btn btn-cancel" @click="cancelForm">Cancel</button>
              <div>
                <button type="button" class="btn btn-skip" @click="skipStep(1)">Skip</button>
                <button type="submit" class="btn btn-next" :disabled="!selectedReporter">Next</button>
              </div>
            </div>
          </form>
        </div>

        <!-- Step 2: Reporter Details -->
        <div v-show="currentStep === 2" class="step-content">
          <form class="case-form" @submit.prevent="saveAndProceed(2)">
            <div class="form-section">
              <div class="section-title">
                {{ selectedReporter ? 'Reporter Details' : 'New Reporter Information' }}
              </div>
              <p class="section-description">Enter the reporter's contact information and details.</p>
              
              <div class="form-row">
                <div class="form-group">
                  <label for="reporter-name">Full Name*</label>
                  <input 
                    v-model="formData.step2.name"
                    type="text" 
                    id="reporter-name" 
                    class="form-control" 
                    placeholder="Enter full name"
                    required
                    :readonly="!!selectedReporter"
                  />
                </div>
                <div class="form-group">
                  <label for="reporter-age">Age</label>
                  <input 
                    v-model="formData.step2.age"
                    type="number" 
                    id="reporter-age" 
                    class="form-control" 
                    placeholder="Enter age"
                    min="1"
                    max="120"
                  />
                </div>
              </div>
              
              <div class="form-row">
                <div class="form-group">
                  <label for="reporter-gender">Gender</label>
                  <select v-model="formData.step2.gender" id="reporter-gender" class="form-control">
                    <option value="">Select gender</option>
                    <option value="female">Female</option>
                    <option value="male">Male</option>
                    <option value="non-binary">Non-binary</option>
                    <option value="transgender">Transgender</option>
                    <option value="other">Other</option>
                    <option value="prefer-not-to-say">Prefer not to say</option>
                  </select>
                </div>
                <div class="form-group">
                  <label for="reporter-location">Location</label>
                  <input 
                    v-model="formData.step2.location"
                    type="text" 
                    id="reporter-location" 
                    class="form-control" 
                    placeholder="Enter location"
                  />
                </div>
              </div>
              
              <div class="form-row">
                <div class="form-group">
                  <label for="reporter-phone">Phone Number*</label>
                  <input 
                    v-model="formData.step2.phone"
                    type="tel" 
                    id="reporter-phone" 
                    class="form-control" 
                    placeholder="Enter phone number"
                    required
                  />
                </div>
                <div class="form-group">
                  <label for="reporter-alt-phone">Alternative Phone</label>
                  <input 
                    v-model="formData.step2.altPhone"
                    type="tel" 
                    id="reporter-alt-phone" 
                    class="form-control" 
                    placeholder="Enter alternative phone"
                  />
                </div>
              </div>
              
              <div class="form-group">
                <label for="reporter-email">Email Address</label>
                <input 
                  v-model="formData.step2.email"
                  type="email" 
                  id="reporter-email" 
                  class="form-control" 
                  placeholder="Enter email address"
                />
              </div>
              
              <div class="form-row">
                <div class="form-group">
                  <label for="reporter-id-type">ID Type</label>
                  <select v-model="formData.step2.idType" id="reporter-id-type" class="form-control">
                    <option value="">Select ID type</option>
                    <option value="national-id">National ID</option>
                    <option value="passport">Passport</option>
                    <option value="drivers-license">Driver's License</option>
                    <option value="other">Other</option>
                  </select>
                </div>
                <div class="form-group">
                  <label for="reporter-id-number">ID Number</label>
                  <input 
                    v-model="formData.step2.idNumber"
                    type="text" 
                    id="reporter-id-number" 
                    class="form-control" 
                    placeholder="Enter ID number"
                  />
                </div>
              </div>

              <div class="form-group">
                <label>Is Reporter also a Client?</label>
                <div class="radio-group">
                  <label class="radio-option">
                    <input 
                      v-model="formData.step2.isClient" 
                      type="radio" 
                      :value="true"
                    />
                    <span class="radio-indicator"></span>
                    <span class="radio-label">Yes</span>
                  </label>
                  <label class="radio-option">
                    <input 
                      v-model="formData.step2.isClient" 
                      type="radio" 
                      :value="false"
                    />
                    <span class="radio-indicator"></span>
                    <span class="radio-label">No</span>
                  </label>
                </div>
              </div>
            </div>
            <div class="form-actions">
              <button type="button" class="btn btn-back" @click="goToStep(1)">Back</button>
              <div>
                <button type="button" class="btn btn-skip" @click="skipStep(2)">Skip</button>
                <button type="submit" class="btn btn-next">Next</button>
              </div>
            </div>
          </form>
        </div>

        <!-- Step 3: Case Details -->
        <div v-show="currentStep === 3" class="step-content">
          <form class="case-form" @submit.prevent="saveAndProceed(3)">
            <div class="form-section">
              <div class="section-title">Case Information</div>
              <p class="section-description">Provide detailed information about the case and incident.</p>
              
              <div class="form-group">
                <label for="case-narrative">Case Narrative*</label>
                <textarea 
                  v-model="formData.step3.narrative"
                  id="case-narrative" 
                  class="form-control" 
                  placeholder="Describe the case details, incident, and circumstances in detail..."
                  required
                  rows="6"
                ></textarea>
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label for="incident-date">Date of Incident</label>
                  <input 
                    v-model="formData.step3.incidentDate"
                    type="date" 
                    id="incident-date" 
                    class="form-control"
                  />
                </div>
                <div class="form-group">
                  <label for="incident-time">Time of Incident</label>
                  <input 
                    v-model="formData.step3.incidentTime"
                    type="time" 
                    id="incident-time" 
                    class="form-control"
                  />
                </div>
              </div>

              <div class="form-group">
                <label for="incident-location">Location of Incident</label>
                <input 
                  v-model="formData.step3.location"
                  type="text" 
                  id="incident-location" 
                  class="form-control" 
                  placeholder="Enter location where incident occurred"
                />
              </div>

              <div class="form-group">
                <label>Is this Case GBV Related?*</label>
                <div class="radio-group">
                  <label class="radio-option">
                    <input 
                      v-model="formData.step3.isGBVRelated" 
                      type="radio" 
                      :value="true"
                      required
                    />
                    <span class="radio-indicator"></span>
                    <span class="radio-label">Yes</span>
                  </label>
                  <label class="radio-option">
                    <input 
                      v-model="formData.step3.isGBVRelated" 
                      type="radio" 
                      :value="false"
                      required
                    />
                    <span class="radio-indicator"></span>
                    <span class="radio-label">No</span>
                  </label>
                </div>
              </div>

              <div class="form-group">
                <label for="case-plan">Case Plan</label>
                <textarea 
                  v-model="formData.step3.casePlan"
                  id="case-plan" 
                  class="form-control" 
                  placeholder="Outline the planned interventions and support services..."
                  rows="4"
                ></textarea>
              </div>
            </div>
            <div class="form-actions">
              <button type="button" class="btn btn-back" @click="goToStep(2)">Back</button>
              <div>
                <button type="button" class="btn btn-skip" @click="skipStep(3)">Skip</button>
                <button type="submit" class="btn btn-next">Next</button>
              </div>
            </div>
          </form>
        </div>

        <!-- Step 4: Case Classification -->
        <div v-show="currentStep === 4" class="step-content">
          <form class="case-form" @submit.prevent="saveAndProceed(4)">
            <div class="form-section">
              <div class="section-title">Case Classification & Assignment</div>
              <p class="section-description">Classify the case and set priority levels for proper handling.</p>
              
              <div class="form-row">
                <div class="form-group">
                  <label>Department*</label>
                  <div class="radio-group">
                    <label class="radio-option">
                      <input 
                        v-model="formData.step4.department" 
                        type="radio" 
                        value="116"
                        required
                      />
                      <span class="radio-indicator"></span>
                      <span class="radio-label">116 (Emergency Helpline)</span>
                    </label>
                    <label class="radio-option">
                      <input 
                        v-model="formData.step4.department" 
                        type="radio" 
                        value="labor"
                        required
                      />
                      <span class="radio-indicator"></span>
                      <span class="radio-label">Labor Department</span>
                    </label>
                  </div>
                </div>
                <div class="form-group">
                  <label for="case-category">Case Category*</label>
                  <select 
                    v-model="formData.step4.category"
                    id="case-category" 
                    class="form-control"
                    required
                  >
                    <option value="">Select category</option>
                    <option value="domestic-violence">Domestic Violence</option>
                    <option value="sexual-assault">Sexual Assault</option>
                    <option value="child-abuse">Child Abuse</option>
                    <option value="human-trafficking">Human Trafficking</option>
                    <option value="labor-exploitation">Labor Exploitation</option>
                    <option value="elder-abuse">Elder Abuse</option>
                    <option value="stalking">Stalking</option>
                    <option value="substance-abuse">Substance Abuse</option>
                    <option value="other">Other</option>
                  </select>
                </div>
              </div>
              
              <div class="form-row">
                <div class="form-group">
                  <label for="priority">Priority*</label>
                  <select 
                    v-model="formData.step4.priority"
                    id="priority" 
                    class="form-control"
                    required
                  >
                    <option value="">Select priority</option>
                    <option value="critical">🔴 Critical</option>
                    <option value="high">🟠 High</option>
                    <option value="medium">🟡 Medium</option>
                    <option value="low">🟢 Low</option>
                  </select>
                </div>
                <div class="form-group">
                  <label for="status">Status*</label>
                  <select 
                    v-model="formData.step4.status"
                    id="status" 
                    class="form-control"
                    required
                  >
                    <option value="">Select status</option>
                    <option value="new">New</option>
                    <option value="in-progress">In Progress</option>
                    <option value="pending">Pending</option>
                    <option value="resolved">Resolved</option>
                  </select>
                </div>
              </div>

              <div class="form-group">
                <label for="escalated-to">Escalated To</label>
                <select 
                  v-model="formData.step4.escalatedTo"
                  id="escalated-to" 
                  class="form-control"
                >
                  <option value="">Select escalation level</option>
                  <option value="supervisor">Supervisor</option>
                  <option value="manager">Manager</option>
                  <option value="director">Director</option>
                  <option value="external-agency">External Agency</option>
                  <option value="law-enforcement">Law Enforcement</option>
                </select>
              </div>

              <div class="form-group">
                <label>Services Offered</label>
                <div class="checkbox-grid">
                  <label class="checkbox-option">
                    <input 
                      v-model="formData.step4.servicesOffered" 
                      type="checkbox" 
                      value="counseling"
                    />
                    <span class="checkbox-indicator"></span>
                    <span class="checkbox-label">Counseling</span>
                  </label>
                  <label class="checkbox-option">
                    <input 
                      v-model="formData.step4.servicesOffered" 
                      type="checkbox" 
                      value="legal-aid"
                    />
                    <span class="checkbox-indicator"></span>
                    <span class="checkbox-label">Legal Aid</span>
                  </label>
                  <label class="checkbox-option">
                    <input 
                      v-model="formData.step4.servicesOffered" 
                      type="checkbox" 
                      value="shelter"
                    />
                    <span class="checkbox-indicator"></span>
                    <span class="checkbox-label">Shelter</span>
                  </label>
                  <label class="checkbox-option">
                    <input 
                      v-model="formData.step4.servicesOffered" 
                      type="checkbox" 
                      value="medical-assistance"
                    />
                    <span class="checkbox-indicator"></span>
                    <span class="checkbox-label">Medical Assistance</span>
                  </label>
                  <label class="checkbox-option">
                    <input 
                      v-model="formData.step4.servicesOffered" 
                      type="checkbox" 
                      value="financial-support"
                    />
                    <span class="checkbox-indicator"></span>
                    <span class="checkbox-label">Financial Support</span>
                  </label>
                  <label class="checkbox-option">
                    <input 
                      v-model="formData.step4.servicesOffered" 
                      type="checkbox" 
                      value="referral"
                    />
                    <span class="checkbox-indicator"></span>
                    <span class="checkbox-label">Referral Services</span>
                  </label>
                </div>
              </div>
            </div>
            <div class="form-actions">
              <button type="button" class="btn btn-back" @click="goToStep(3)">Back</button>
              <div>
                <button type="button" class="btn btn-skip" @click="skipStep(4)">Skip</button>
                <button type="submit" class="btn btn-next">Next</button>
              </div>
            </div>
          </form>
        </div>

        <!-- Step 5: Review -->
        <div v-show="currentStep === 5" class="step-content">
          <div class="review-sections">
            <div class="review-section">
              <div class="section-header">
                <div class="section-title">Reporter Information</div>
                <button class="edit-btn" @click="goToStep(2)">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  Edit
                </button>
              </div>
              <div class="review-content">
                <div class="review-item">
                  <div class="review-label">Name</div>
                  <div class="review-value">{{ formData.step2.name || 'N/A' }}</div>
                </div>
                <div class="review-item">
                  <div class="review-label">Phone</div>
                  <div class="review-value">{{ formData.step2.phone || 'N/A' }}</div>
                </div>
                <div class="review-item">
                  <div class="review-label">Location</div>
                  <div class="review-value">{{ formData.step2.location || 'N/A' }}</div>
                </div>
                <div class="review-item">
                  <div class="review-label">Is Client</div>
                  <div class="review-value">
                    <span class="status-badge" :class="formData.step2.isClient ? 'status-yes' : 'status-no'">
                      {{ formData.step2.isClient ? 'Yes' : 'No' }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="review-section">
              <div class="section-header">
                <div class="section-title">Case Details</div>
                <button class="edit-btn" @click="goToStep(3)">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  Edit
                </button>
              </div>
              <div class="review-content">
                <div class="review-item review-item-full">
                  <div class="review-label">Case Narrative</div>
                  <div class="review-value">{{ formData.step3.narrative || 'N/A' }}</div>
                </div>
                <div class="review-item">
                  <div class="review-label">GBV Related</div>
                  <div class="review-value">
                    <span class="status-badge" :class="formData.step3.isGBVRelated ? 'status-warning' : 'status-info'">
                      {{ formData.step3.isGBVRelated ? 'Yes' : 'No' }}
                    </span>
                  </div>
                </div>
                <div class="review-item">
                  <div class="review-label">Incident Date</div>
                  <div class="review-value">{{ formData.step3.incidentDate || 'N/A' }}</div>
                </div>
                <div class="review-item">
                  <div class="review-label">Location</div>
                  <div class="review-value">{{ formData.step3.location || 'N/A' }}</div>
                </div>
              </div>
            </div>
            
            <div class="review-section">
              <div class="section-header">
                <div class="section-title">Classification</div>
                <button class="edit-btn" @click="goToStep(4)">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  Edit
                </button>
              </div>
              <div class="review-content">
                <div class="review-item">
                  <div class="review-label">Department</div>
                  <div class="review-value">{{ formatDepartment(formData.step4.department) || 'N/A' }}</div>
                </div>
                <div class="review-item">
                  <div class="review-label">Category</div>
                  <div class="review-value">{{ formatCategory(formData.step4.category) || 'N/A' }}</div>
                </div>
                <div class="review-item">
                  <div class="review-label">Priority</div>
                  <div class="review-value">
                    <span v-if="formData.step4.priority" class="priority-badge" :class="`priority-${formData.step4.priority}`">
                      {{ formatPriority(formData.step4.priority) }}
                    </span>
                    <span v-else>N/A</span>
                  </div>
                </div>
                <div class="review-item">
                  <div class="review-label">Status</div>
                  <div class="review-value">
                    <span v-if="formData.step4.status" class="status-badge status-info">
                      {{ formatStatus(formData.step4.status) }}
                    </span>
                    <span v-else>N/A</span>
                  </div>
                </div>
                <div class="review-item review-item-full">
                  <div class="review-label">Services Offered</div>
                  <div class="review-value">
                    <div v-if="formData.step4.servicesOffered.length > 0" class="services-tags">
                      <span 
                        v-for="service in formData.step4.servicesOffered" 
                        :key="service" 
                        class="service-tag"
                      >
                        {{ formatService(service) }}
                      </span>
                    </div>
                    <span v-else>None selected</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="form-actions">
            <button type="button" class="btn btn-back" @click="goToStep(4)">Back</button>
            <button type="button" class="glass-btn filled">Create Case</button>
          </div>
        </div>
      </div>
      
      <!-- Enhanced AI Insights Panel -->
      <div v-if="isAIEnabled" class="ai-preview-container">
        <div class="ai-preview">
          <div class="ai-preview-header">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <div class="ai-preview-title">AI Insights <span class="ai-badge">LIVE</span></div>
          </div>
          <div class="ai-preview-content">
            <!-- Audio Transcription Results -->
            <div v-if="transcriptionData" class="ai-preview-section">
              <div class="ai-preview-section-title">Audio Analysis Results</div>
              <!-- Transcription -->
              <div v-if="transcriptionData.transcript" class="transcription-section">
                <h4 class="subsection-title">Transcription</h4>
                <div class="transcription-text">{{ transcriptionData.transcript }}</div>
                <button class="btn btn-tiny btn-outline" @click="useTranscription">Use in Case Narrative</button>
              </div>
              <!-- Summary -->
              <div v-if="transcriptionData.summary" class="summary-section">
                <h4 class="subsection-title">Summary</h4>
                <div class="summary-text">{{ transcriptionData.summary }}</div>
              </div>
              <!-- Named Entities -->
              <div v-if="transcriptionData.summary_entities && transcriptionData.summary_entities.length" class="entities-section">
                <h4 class="subsection-title">Detected Entities</h4>
                <div class="entity-suggestions">
                  <div v-for="entity in transcriptionData.summary_entities" :key="entity.text" class="entity-suggestion">
                    <span class="entity-text">{{ entity.text }}</span>
                    <span class="entity-label">{{ entity.label }}</span>
                    <button class="btn btn-tiny btn-outline" @click="useEntity(entity)">Use</button>
                  </div>
                </div>
              </div>
              <!-- Classification Suggestions -->
              <div v-if="transcriptionData.summary_classification" class="classification-section">
                <h4 class="subsection-title">AI Classification Suggestions</h4>
                <div class="classification-suggestions">
                  <div class="suggestion-item">
                    <span class="suggestion-label">Category:</span>
                    <span class="suggestion-value">{{ transcriptionData.summary_classification.sub_category }}</span>
                    <button class="btn btn-tiny btn-primary" @click="useClassification('category', transcriptionData.summary_classification.sub_category)">Use This Category</button>
                  </div>
                  <div class="suggestion-item">
                    <span class="suggestion-label">Priority:</span>
                    <span class="suggestion-value">{{ getPriorityText(transcriptionData.summary_classification.priority) }}</span>
                    <button class="btn btn-tiny btn-primary" @click="useClassification('priority', getPriorityValue(transcriptionData.summary_classification.priority))">Use This Priority</button>
                  </div>
                  <div class="suggestion-item">
                    <span class="suggestion-label">Intervention:</span>
                    <span class="suggestion-value">{{ transcriptionData.summary_classification.intervention }}</span>
                    <button class="btn btn-tiny btn-primary" @click="useClassification('intervention', transcriptionData.summary_classification.intervention)">Add to Services</button>
                  </div>
                </div>
              </div>
            </div>
            <!-- AI Insights from Audio -->
            <div v-if="aiInsights" class="ai-preview-section">
              <div class="ai-preview-section-title">Detailed AI Insights</div>
              <!-- Case Summary -->
              <div v-if="aiInsights.case_summary" class="insight-section">
                <h4 class="subsection-title">Case Summary</h4>
                <p class="insight-text">{{ aiInsights.case_summary }}</p>
                <button class="btn btn-tiny btn-outline" @click="useCaseSummary">Use in Case Plan</button>
              </div>
              <!-- Named Entities -->
              <div v-if="aiInsights.named_entities" class="insight-section">
                <h4 class="subsection-title">Key Information</h4>
                <div v-if="aiInsights.named_entities.persons && aiInsights.named_entities.persons.length" class="entity-group">
                  <h5 class="entity-type">Persons Involved</h5>
                  <div class="entity-tags">
                    <span v-for="person in aiInsights.named_entities.persons" :key="person" class="entity-tag">{{ person }}<button class="entity-use-btn" @click="usePerson(person)">+</button></span>
                  </div>
                </div>
                <div v-if="aiInsights.named_entities.locations && aiInsights.named_entities.locations.length" class="entity-group">
                  <h5 class="entity-type">Locations</h5>
                  <div class="entity-tags">
                    <span v-for="location in aiInsights.named_entities.locations" :key="location" class="entity-tag">{{ location }}<button class="entity-use-btn" @click="useLocation(location)">+</button></span>
                  </div>
                </div>
                <div v-if="aiInsights.named_entities.organizations && aiInsights.named_entities.organizations.length" class="entity-group">
                  <h5 class="entity-type">Organizations</h5>
                  <div class="entity-tags">
                    <span v-for="org in aiInsights.named_entities.organizations" :key="org" class="entity-tag">{{ org }}<button class="entity-use-btn" @click="useOrganization(org)">+</button></span>
                  </div>
                </div>
              </div>
              <!-- Risk Assessment -->
              <div v-if="aiInsights.risk_assessment" class="insight-section">
                <h4 class="subsection-title">Risk Assessment</h4>
                <div v-if="aiInsights.risk_assessment.red_flags && aiInsights.risk_assessment.red_flags.length" class="risk-group">
                  <h5 class="risk-type">🚩 Red Flags</h5>
                  <ul class="risk-list">
                    <li v-for="flag in aiInsights.risk_assessment.red_flags" :key="flag">{{ flag }}</li>
                  </ul>
                </div>
                <div v-if="aiInsights.risk_assessment.protective_factors && aiInsights.risk_assessment.protective_factors.length" class="risk-group">
                  <h5 class="risk-type">🛡️ Protective Factors</h5>
                  <ul class="risk-list">
                    <li v-for="factor in aiInsights.risk_assessment.protective_factors" :key="factor">{{ factor }}</li>
                  </ul>
                </div>
              </div>
              <!-- Recommended Services -->
              <div v-if="aiInsights.case_management && aiInsights.case_management.psychosocial_support" class="insight-section">
                <h4 class="subsection-title">Recommended Services</h4>
                <div v-if="aiInsights.case_management.psychosocial_support.short_term && aiInsights.case_management.psychosocial_support.short_term.length" class="service-group">
                  <h5 class="service-type">Immediate Support</h5>
                  <div class="service-suggestions">
                    <button v-for="service in aiInsights.case_management.psychosocial_support.short_term" :key="service" class="service-suggestion-btn" @click="addRecommendedService(service)">{{ service }}<span class="add-icon">+</span></button>
                  </div>
                </div>
                <div v-if="aiInsights.case_management.psychosocial_support.long_term && aiInsights.case_management.psychosocial_support.long_term.length" class="service-group">
                  <h5 class="service-type">Long-term Support</h5>
                  <div class="service-suggestions">
                    <button v-for="service in aiInsights.case_management.psychosocial_support.long_term" :key="service" class="service-suggestion-btn" @click="addRecommendedService(service)">{{ service }}<span class="add-icon">+</span></button>
                  </div>
                </div>
              </div>
            </div>
            <!-- Original AI Auto-Fill Section -->
            <div class="ai-preview-section">
              <div class="ai-preview-section-title">AI Auto-Fill</div>
              <div class="ai-autofill-section">
                <p class="ai-autofill-description">Let AI automatically populate form fields with sample data based on common case patterns.</p>
                <button class="btn btn-primary btn-small ai-autofill-btn" @click="showAutoFillModal = true">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  Auto-Fill Current Step
                </button>
              </div>
            </div>
            <!-- Smart Suggestions -->
            <div class="ai-preview-section">
              <div class="ai-preview-section-title">Smart Suggestions</div>
              <div class="ai-suggestions">
                <div v-for="suggestion in getActiveSuggestions()" :key="suggestion.id" class="ai-suggestion" :class="`suggestion-${suggestion.type}`">
                  <div class="suggestion-icon">{{ suggestion.icon }}</div>
                  <div class="suggestion-content">
                    <div class="suggestion-text">{{ suggestion.text }}</div>
                    <div v-if="suggestion.action" class="suggestion-action">
                      <button class="btn btn-tiny btn-outline" @click="applySuggestion(suggestion)">Apply</button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <!-- Case Summary -->
            <div class="ai-preview-section">
              <div class="ai-preview-section-title">Case Summary</div>
              <div class="ai-summary">
                <div class="summary-item">
                  <div class="summary-label">Reporter</div>
                  <div class="summary-value">{{ formData.step2.name || 'Not selected' }}</div>
                </div>
                <div class="summary-item">
                  <div class="summary-label">Case Type</div>
                  <div class="summary-value">{{ formatCategory(formData.step4.category) || 'Not classified' }}</div>
                </div>
                <div class="summary-item">
                  <div class="summary-label">Priority</div>
                  <div class="summary-value">
                    <span v-if="formData.step4.priority" class="priority-badge" :class="`priority-${formData.step4.priority}`">{{ formatPriority(formData.step4.priority) }}</span>
                    <span v-else class="text-muted">Not set</span>
                  </div>
                </div>
                <div class="summary-item">
                  <div class="summary-label">GBV Related</div>
                  <div class="summary-value">
                    <span v-if="formData.step3.isGBVRelated !== null" class="status-badge" :class="formData.step3.isGBVRelated ? 'status-warning' : 'status-info'">{{ formData.step3.isGBVRelated ? 'Yes' : 'No' }}</span>
                    <span v-else class="text-muted">Not specified</span>
                  </div>
                </div>
              </div>
            </div>
            <!-- Progress Insights -->
            <div v-if="getCompletedSteps().length > 0" class="ai-preview-section">
              <div class="ai-preview-section-title">Progress Insights</div>
              <div class="progress-insights">
                <div class="insight-item">
                  <div class="insight-icon">📊</div>
                  <div class="insight-text">{{ getCompletedSteps().length }} of {{ totalSteps }} steps completed</div>
                </div>
                <div v-if="getEstimatedTime()" class="insight-item">
                  <div class="insight-icon">⏱️</div>
                  <div class="insight-text">Estimated time remaining: {{ getEstimatedTime() }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- AI Auto-Fill Warning Modal -->
    <div class="modal-overlay" :class="{ active: showAutoFillModal }">
      <div class="modal-content">
        <div class="modal-header">
          <div class="modal-title">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            AI Auto-Fill Warning
          </div>
        </div>
        <div class="modal-body">
          <p><strong>⚠️ This action will replace all existing data in the current step.</strong></p>
          <p>AI will automatically populate the form fields with sample data. Any information you've already entered will be overwritten.</p>
          <p>Are you sure you want to continue?</p>
        </div>
        <div class="modal-footer">
          <button class="modal-btn modal-btn-cancel" @click="cancelAutoFill">Cancel</button>
          <button class="modal-btn modal-btn-confirm" @click="confirmAutoFill">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Yes, Auto-Fill Data
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

export default {
  setup() {
    const router = useRouter()

    // State
    const currentStep = ref(1)
    const totalSteps = 5
    const currentTheme = ref(localStorage.getItem('theme') || 'dark')
    const isAIEnabled = ref(true) // Changed to true to show AI panel by default
    const showAutoFillModal = ref(false)
    const searchQuery = ref('')
    const selectedReporter = ref(null)
    
    // AI Data from audio transcription
    const transcriptionData = ref(null)
    const aiInsights = ref(null)

    // Mock contacts data - updated with sample data
    const contacts = [
      {
        id: 1,
        name: 'Ivan Somondi',
        age: 16,
        gender: 'Male',
        location: 'Narok County',
        phone: '254700112233',
        lastContact: '23 May 2025 3:30 PM'
      },
      {
        id: 2,
        name: 'Susan Kirigwa',
        age: 45,
        gender: 'Female',
        location: 'Narok',
        phone: '254700445566',
        lastContact: '20 May 2025 1:42 PM'
      },
      {
        id: 3,
        name: 'Amira',
        age: 28,
        gender: 'Female',
        location: 'Nairobi',
        phone: '254700778899',
        lastContact: '1 Jun 2025 9:34 AM'
      }
    ]

    // AI Suggestions data
    const aiSuggestions = reactive({
      1: [
        {
          id: 'duplicate-check',
          type: 'info',
          icon: '💡',
          text: 'Consider checking for duplicate contacts before creating new reporters',
          action: null
        }
      ],
      2: [
        {
          id: 'contact-validation',
          type: 'warning',
          icon: '⚠️',
          text: 'Ensure phone number is valid and reachable for follow-ups',
          action: null
        }
      ],
      3: [
        {
          id: 'narrative-analysis',
          type: 'success',
          icon: '🎯',
          text: 'Case narrative indicates potential high priority - consider urgent classification',
          action: { type: 'set-priority', value: 'high' }
        },
        {
          id: 'gbv-detection',
          type: 'warning',
          icon: '🚨',
          text: 'Keywords suggest this may be GBV-related. Ensure proper protocols are followed',
          action: null
        }
      ],
      4: [
        {
          id: 'priority-recommendation',
          type: 'success',
          icon: '🎯',
          text: 'Based on case details, recommended priority: Medium',
          action: { type: 'set-priority', value: 'medium' }
        },
        {
          id: 'service-suggestion',
          type: 'info',
          icon: '💼',
          text: 'Consider adding counseling and legal aid services for this case type',
          action: { type: 'add-services', value: ['counseling', 'legal-aid'] }
        }
      ],
      5: [
        {
          id: 'completeness-check',
          type: 'success',
          icon: '✅',
          text: 'All required fields completed. Case is ready for submission',
          action: null
        }
      ]
    })

    // Form data
    const formData = reactive({
      step2: {
        name: '',
        age: '',
        gender: '',
        location: '',
        phone: '',
        altPhone: '',
        email: '',
        idType: '',
        idNumber: '',
        isClient: null
      },
      step3: {
        narrative: '',
        incidentDate: '',
        incidentTime: '',
        location: '',
        isGBVRelated: null,
        casePlan: ''
      },
      step4: {
        department: '',
        category: '',
        priority: '',
        status: '',
        escalatedTo: '',
        servicesOffered: []
      }
    })

    // Step information
    const stepLabels = [
      'Select Reporter',
      'Reporter Details',
      'Case Information',
      'Classification',
      'Review'
    ]

    const stepDescriptions = [
      'Step 1: Select an existing contact or create a new reporter',
      'Step 2: Enter reporter details and contact information',
      'Step 3: Provide case narrative and incident details',
      'Step 4: Classify case and assign priority',
      'Step 5: Review all information before creating the case'
    ]

    // Computed
    const filteredContacts = computed(() => {
      if (!searchQuery.value) return contacts
      return contacts.filter(contact =>
        contact.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
        contact.phone.includes(searchQuery.value)
      )
    })

    // Methods
    const toggleTheme = () => {
      currentTheme.value = currentTheme.value === 'dark' ? 'light' : 'dark'
      localStorage.setItem('theme', currentTheme.value)
      applyTheme()
    }

    const applyTheme = () => {
      const root = document.documentElement
      
      if (currentTheme.value === 'light') {
        root.style.setProperty('--background-color', '#f5f5f5')
        root.style.setProperty('--sidebar-bg', '#ffffff')
        root.style.setProperty('--content-bg', '#ffffff')
        root.style.setProperty('--text-color', '#333')
        root.style.setProperty('--text-secondary', '#666')
        root.style.setProperty('--border-color', '#ddd')
        root.style.setProperty('--card-bg', '#ffffff')
        root.style.setProperty('--header-bg', '#f0f0f0')
        root.style.setProperty('--input-bg', '#f0f0f0')
        root.setAttribute('data-theme', 'light')
      } else {
        root.style.setProperty('--background-color', '#0a0a0a')
        root.style.setProperty('--sidebar-bg', '#111')
        root.style.setProperty('--content-bg', '#222')
        root.style.setProperty('--text-color', '#fff')
        root.style.setProperty('--text-secondary', '#aaa')
        root.style.setProperty('--border-color', '#333')
        root.style.setProperty('--card-bg', '#222')
        root.style.setProperty('--header-bg', '#333')
        root.style.setProperty('--input-bg', '#1a1a1a')
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
      root.style.setProperty('--high-priority', '#ff3b30')
      root.style.setProperty('--medium-priority', '#FFA500')
      root.style.setProperty('--low-priority', '#4CAF50')
    }

    const getInitials = (name) => {
      return name.split(' ').map(n => n[0]).join('').toUpperCase()
    }

    const selectExistingReporter = (contact) => {
      selectedReporter.value = contact
    }

    const createNewReporter = () => {
      selectedReporter.value = null
      // Clear reporter data
      Object.keys(formData.step2).forEach(key => {
        formData.step2[key] = key === 'isClient' ? null : ''
      })
      currentStep.value = 2
    }

    const goToStep = (step) => {
      currentStep.value = step
    }

    const validateAndProceed = (step) => {
      if (step === 1 && selectedReporter.value) {
        // Pre-fill reporter data with selected contact
        formData.step2.name = selectedReporter.value.name
        formData.step2.age = selectedReporter.value.age
        formData.step2.gender = selectedReporter.value.gender.toLowerCase()
        formData.step2.location = selectedReporter.value.location
        formData.step2.phone = selectedReporter.value.phone
        currentStep.value = 2
      }
    }

    const skipStep = (step) => {
      currentStep.value = step + 1
    }

    const saveAndProceed = (step) => {
      currentStep.value = step + 1
    }

    // AI methods
    const cancelAutoFill = () => {
      showAutoFillModal.value = false
    }

    const confirmAutoFill = () => {
      showAutoFillModal.value = false
      applyAISuggestions()
    }

    const applyAISuggestions = () => {
      // Auto-fill based on current step
      switch (currentStep.value) {
        case 2:
          if (!selectedReporter.value) {
            formData.step2.name = 'John Doe'
            formData.step2.age = '35'
            formData.step2.gender = 'male'
            formData.step2.location = 'Downtown'
            formData.step2.phone = '+1234567890'
            formData.step2.email = 'john.doe@example.com'
            formData.step2.idType = 'national-id'
            formData.step2.idNumber = 'ID123456789'
            formData.step2.isClient = false
          }
          break
          
        case 3:
          formData.step3.narrative = 'Incident reported involving domestic dispute. Caller requested immediate assistance and support services. Situation appears to require urgent intervention and follow-up care.'
          formData.step3.incidentDate = new Date().toISOString().split('T')[0]
          formData.step3.incidentTime = '14:30'
          formData.step3.location = 'Residential area, Main Street'
          formData.step3.isGBVRelated = true
          formData.step3.casePlan = 'Provide immediate safety assessment, connect with counseling services, and follow up within 24 hours. Coordinate with local support agencies for ongoing assistance.'
          break
          
        case 4:
          formData.step4.department = '116'
          formData.step4.category = 'domestic-violence'
          formData.step4.priority = 'high'
          formData.step4.status = 'new'
          formData.step4.escalatedTo = 'supervisor'
          formData.step4.servicesOffered = ['counseling', 'legal-aid', 'shelter']
          break
      }
    }

    const getActiveSuggestions = () => {
      const currentSuggestions = aiSuggestions[currentStep.value] || []
      const previousSteps = Array.from({length: currentStep.value - 1}, (_, i) => i + 1)

      let allSuggestions = [...currentSuggestions]

      // Add suggestions from completed steps
      previousSteps.forEach(step => {
        const stepSuggestions = aiSuggestions[step] || []
        allSuggestions = [...allSuggestions, ...stepSuggestions]
      })

      return allSuggestions
    }

    const applySuggestion = (suggestion) => {
      if (!suggestion.action) return

      switch (suggestion.action.type) {
        case 'set-priority':
          formData.step4.priority = suggestion.action.value
          break
        case 'add-services':
          formData.step4.servicesOffered = [...new Set([...formData.step4.servicesOffered, ...suggestion.action.value])]
          break
      }
    }

    const getCompletedSteps = () => {
      return Array.from({length: currentStep.value - 1}, (_, i) => i + 1)
    }

    const getEstimatedTime = () => {
      const remaining = totalSteps - currentStep.value
      if (remaining <= 0) return null
      return `${remaining * 2} minutes`
    }

    // Load sample transcription data
    const loadSampleTranscriptionData = () => {
      // Sample data based on the provided transcription
      transcriptionData.value = {
        transcript: "Hello. Hello. Good evening. Good evening. You are speaking to Amira from Child Health Line. How may I assist? I was asking, like this Child Health Line, like in Asahidia, what to do? Thank you so much for the question. Who am I speaking to? You are speaking to Eva and Sumu. Are you speaking to Ivan Somondi? You're calling us from which county, Ivan Somondi? Um, in, um, Narok. Which ward in Narok County? I don't know exactly, but I'm in Narok County...",
        summary: "Child Health Counseling Line deals with all child protection cases. Case involves a 16-year-old named Ivan Somondi from Narok County seeking help for substance abuse (alcohol and cannabis). The caller admits to daily substance use and wants to quit.",
        summary_entities: [
          { text: "Ivan Somondi", label: "PERSON" },
          { text: "Narok County", label: "LOCATION" },
          { text: "Child Health Line", label: "ORG" },
          { text: "Susan Kirigwa", label: "PERSON" },
          { text: "Nyarach Secondary School", label: "ORG" }
        ],
        summary_classification: {
          main_category: "Child Protection",
          sub_category: "Substance Abuse",
          intervention: "Professional counseling",
          priority: 2
        }
      }

      aiInsights.value = {
        case_summary: "Case involving a 16-year-old minor from Narok County seeking help for substance abuse. The child reports daily use of alcohol and cannabis, started with peer influence, and expresses desire to change. Parents are unaware of the substance use.",
        named_entities: {
          persons: ["Ivan Somondi", "Susan Kirigwa", "Amira"],
          organizations: ["Child Health Line", "Nyarach Secondary School"],
          locations: ["Narok County", "Nairobi"],
          contact_information: ["Child Health Line"]
        },
        classification: {
          category: ["Child Protection", "Substance Abuse"],
          interventions_needed: ["Professional counseling", "Rehabilitation services"],
          priority_level: "High"
        },
        case_management: {
          psychosocial_support: {
            short_term: ["Professional counseling", "Peer support groups", "Family counseling"],
            long_term: ["Rehabilitation program", "Educational support", "Life skills training"]
          },
          safety_planning: {
            immediate_actions: ["Assess immediate safety", "Contact parents/guardians"],
            long_term_measures: ["Regular follow-up", "School coordination"]
          }
        },
        risk_assessment: {
          red_flags: ["Daily substance use", "Hiding behavior from parents", "Peer influence"],
          protective_factors: ["Expressed desire to change", "Access to education", "Family support available"],
          potential_barriers: ["Peer pressure", "Lack of parental awareness", "Geographic distance from services"]
        }
      }
    }

    // AI Suggestion Usage Methods
    const useTranscription = () => {
      if (transcriptionData.value?.transcript) {
        formData.step3.narrative = transcriptionData.value.transcript
        goToStep(3)
      }
    }

    const useEntity = (entity) => {
      if (entity.label === 'PERSON') {
        formData.step2.name = entity.text
        goToStep(2)
      } else if (entity.label === 'LOCATION') {
        formData.step3.location = entity.text
        goToStep(3)
      }
    }

    const useClassification = (type, value) => {
      if (type === 'category') {
        const categoryMap = {
          'Child Abuse': 'child-abuse',
          'Substance Abuse': 'substance-abuse',
          'Domestic Violence': 'domestic-violence'
        }
        formData.step4.category = categoryMap[value] || value.toLowerCase().replace(' ', '-')
      } else if (type === 'priority') {
        formData.step4.priority = value
      } else if (type === 'intervention') {
        const serviceMap = {
          'Professional counseling': 'counseling',
          'Legal assistance': 'legal-aid',
          'Medical assistance': 'medical-assistance'
        }
        const service = serviceMap[value] || value.toLowerCase().replace(' ', '-')
        if (!formData.step4.servicesOffered.includes(service)) {
          formData.step4.servicesOffered.push(service)
        }
      }
      goToStep(4)
    }

    const useCaseSummary = () => {
      if (aiInsights.value?.case_summary) {
        formData.step3.casePlan = aiInsights.value.case_summary
        goToStep(3)
      }
    }

    const usePerson = (person) => {
      formData.step2.name = person
      goToStep(2)
    }

    const useLocation = (location) => {
      formData.step3.location = location
      goToStep(3)
    }

    const useOrganization = (org) => {
      // Could be used in case narrative or other relevant fields
      const currentNarrative = formData.step3.narrative || ''
      formData.step3.narrative = currentNarrative + (currentNarrative ? '\n\n' : '') + `Organization involved: ${org}`
      goToStep(3)
    }

    const addRecommendedService = (service) => {
      const serviceMap = {
        'Professional counseling': 'counseling',
        'Peer support groups': 'counseling',
        'Family counseling': 'counseling',
        'Rehabilitation program': 'medical-assistance',
        'Educational support': 'referral',
        'Life skills training': 'counseling'
      }
      const mappedService = serviceMap[service] || 'counseling'
      if (!formData.step4.servicesOffered.includes(mappedService)) {
        formData.step4.servicesOffered.push(mappedService)
      }
      goToStep(4)
    }

    const getPriorityText = (priority) => {
      const priorityMap = { 1: 'Critical', 2: 'High', 3: 'Medium', 4: 'Low' }
      return priorityMap[priority] || 'Medium'
    }

    const getPriorityValue = (priority) => {
      const priorityMap = { 1: 'critical', 2: 'high', 3: 'medium', 4: 'low' }
      return priorityMap[priority] || 'medium'
    }

    // Formatting methods
    const formatDepartment = (dept) => {
      const deptMap = {
        '116': '116 (Emergency Helpline)',
        'labor': 'Labor Department'
      }
      return deptMap[dept] || dept
    }

    const formatCategory = (category) => {
      const categoryMap = {
        'domestic-violence': 'Domestic Violence',
        'sexual-assault': 'Sexual Assault',
        'child-abuse': 'Child Abuse',
        'human-trafficking': 'Human Trafficking',
        'labor-exploitation': 'Labor Exploitation',
        'elder-abuse': 'Elder Abuse',
        'stalking': 'Stalking',
        'substance-abuse': 'Substance Abuse',
        'other': 'Other'
      }
      return categoryMap[category] || category
    }

    const formatPriority = (priority) => {
      const priorityMap = {
        'critical': 'Critical',
        'high': 'High',
        'medium': 'Medium',
        'low': 'Low'
      }
      return priorityMap[priority] || priority
    }

    const formatStatus = (status) => {
      const statusMap = {
        'new': 'New',
        'in-progress': 'In Progress',
        'pending': 'Pending',
        'resolved': 'Resolved'
      }
      return statusMap[status] || status
    }

    const formatService = (service) => {
      const serviceMap = {
        'counseling': 'Counseling',
        'legal-aid': 'Legal Aid',
        'shelter': 'Shelter',
        'medical-assistance': 'Medical Assistance',
        'financial-support': 'Financial Support',
        'referral': 'Referral Services'
      }
      return serviceMap[service] || service
    }

    const cancelForm = () => {
      router.push('/cases')
    }

    const submitCase = () => {
      const casePayload = {
        reporter: formData.step2,
        caseDetails: formData.step3,
        classification: formData.step4,
        aiInsights: aiInsights.value,
        transcriptionData: transcriptionData.value,
        createdAt: new Date().toISOString()
      }

      console.log('Creating case:', casePayload)
      alert('Case created successfully!')
      router.push('/cases')
    }

    // Lifecycle hooks
    onMounted(() => {
      applyTheme()
      // Load sample data for demonstration
      setTimeout(() => {
        loadSampleTranscriptionData()
      }, 2000)
    })

    return {
      currentStep,
      totalSteps,
      currentTheme,
      isAIEnabled,
      showAutoFillModal,
      searchQuery,
      selectedReporter,
      contacts,
      aiSuggestions,
      formData,
      stepLabels,
      stepDescriptions,
      transcriptionData,
      aiInsights,
      filteredContacts,
      toggleTheme,
      getInitials,
      selectExistingReporter,
      createNewReporter,
      goToStep,
      validateAndProceed,
      skipStep,
      saveAndProceed,
      cancelAutoFill,
      confirmAutoFill,
      getActiveSuggestions,
      applySuggestion,
      getCompletedSteps,
      getEstimatedTime,
      useTranscription,
      useEntity,
      useClassification,
      useCaseSummary,
      usePerson,
      useLocation,
      useOrganization,
      addRecommendedService,
      getPriorityText,
      getPriorityValue,
      formatDepartment,
      formatCategory,
      formatPriority,
      formatStatus,
      formatService,
      cancelForm,
      submitCase,
    }
  }
}
</script>

<style>
/* All original styles remain exactly the same, adding new AI insights styles */

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
  transition: background-color 0.3s, color 0.3s;
}

.case-creation-page {
  min-height: 100vh;
  background-color: var(--background-color);
  color: var(--text-color);
  padding: 20px;
  position: relative;
}

.back-button {
  position: absolute;
  top: 20px;
  left: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-color);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  padding: 8px 16px;
  border-radius: 8px;
  background-color: var(--content-bg);
  border: 1px solid var(--border-color);
  transition: background-color 0.3s, border-color 0.3s;
  z-index: 10;
}

.back-button:hover {
  background-color: var(--border-color);
}

.theme-toggle {
  position: absolute;
  top: 20px;
  right: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
  background-color: var(--content-bg);
  color: var(--text-color);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 8px 16px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.3s, border-color 0.3s;
  z-index: 10;
}

.theme-toggle:hover {
  background-color: var(--border-color);
}

.case-container {
  display: flex;
  gap: 20px;
  max-width: 1400px;
  margin: 80px auto 0;
  min-height: calc(100vh - 120px);
}

.main-form-container {
  flex: 1;
  background-color: var(--content-bg);
  border-radius: 15px;
  padding: 30px;
  border: 1px solid var(--border-color);
  overflow-y: auto;
  max-height: calc(100vh - 120px);
}

.case-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--border-color);
}

.case-header h1 {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 8px;
}

.case-header p {
  color: var(--text-secondary);
  font-size: 16px;
}

.toggle-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toggle-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-color);
}

.ai-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  background-color: var(--accent-color);
  border-radius: 4px;
}

.ai-icon svg {
  stroke: white;
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 24px;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--border-color);
  transition: 0.3s;
  border-radius: 24px;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: 0.3s;
  border-radius: 50%;
}

input:checked + .toggle-slider {
  background-color: var(--accent-color);
}

input:checked + .toggle-slider:before {
  transform: translateX(26px);
}

.progress-container {
  margin-bottom: 40px;
}

.progress-steps {
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  margin-bottom: 20px;
}

.progress-steps::before {
  content: '';
  position: absolute;
  top: 20px;
  left: 20px;
  right: 20px;
  height: 2px;
  background-color: var(--border-color);
  z-index: 1;
}

.progress-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  position: relative;
  z-index: 2;
}

.step-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: var(--content-bg);
  border: 2px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
  transition: all 0.3s;
}

.step-circle.active {
  background-color: var(--accent-color);
  border-color: var(--accent-color);
  color: white;
}

.step-circle.completed {
  background-color: var(--success-color);
  border-color: var(--success-color);
  color: white;
}

.step-label {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  text-align: center;
  transition: color 0.3s;
}

.step-label.active {
  color: var(--text-color);
  font-weight: 600;
}

.step-content {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.case-form {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 10px;
}

.section-description {
  color: var(--text-secondary);
  font-size: 14px;
  margin-bottom: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-color);
}

.form-control {
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background-color: var(--input-bg);
  color: var(--text-color);
  font-size: 14px;
  transition: border-color 0.3s, box-shadow 0.3s;
}

.form-control:focus {
  outline: none;
  border-color: var(--accent-color);
  box-shadow: 0 0 0 3px rgba(150, 75, 0, 0.1);
}

.form-control::placeholder {
  color: var(--text-secondary);
}

.form-control:read-only {
  background-color: var(--border-color);
  cursor: not-allowed;
}

textarea.form-control {
  min-height: 100px;
  resize: vertical;
}

.search-section {
  margin-bottom: 20px;
}

.search-box {
  position: relative;
  max-width: 400px;
}

.search-box svg {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  stroke: var(--text-secondary);
}

.search-input {
  width: 100%;
  padding: 12px 16px 12px 40px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background-color: var(--input-bg);
  color: var(--text-color);
  font-size: 14px;
  transition: border-color 0.3s;
}

.search-input:focus {
  outline: none;
  border-color: var(--accent-color);
}

.contacts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.contact-card {
  background-color: var(--input-bg);
  border: 2px solid var(--border-color);
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  gap: 12px;
  position: relative;
}

.contact-card:hover {
  border-color: var(--accent-color);
  transform: translateY(-2px);
}

.contact-card.selected {
  border-color: var(--accent-color);
  background-color: rgba(150, 75, 0, 0.1);
}

.contact-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: var(--accent-color);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
  flex-shrink: 0;
}

.contact-info {
  flex: 1;
}

.contact-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 4px;
}

.contact-details {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.contact-tag {
  font-size: 12px;
  background-color: var(--border-color);
  color: var(--text-secondary);
  padding: 2px 6px;
  border-radius: 4px;
}

.contact-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 12px;
  color: var(--text-secondary);
}

.contact-timestamp {
  font-size: 11px;
  color: var(--text-secondary);
  margin-top: 8px;
}

.contact-select-indicator {
  position: absolute;
  top: 50%;
  right: 16px;
  transform: translateY(-50%);
  color: var(--accent-color);
  opacity: 0;
  transition: opacity 0.3s;
}

.contact-card.selected .contact-select-indicator {
  opacity: 1;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.radio-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.radio-option {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  position: relative;
  padding-left: 28px;
}

.radio-option input[type="radio"] {
  opacity: 0;
  position: absolute;
  width: 0;
  height: 0;
}

.radio-indicator {
  position: absolute;
  left: 0;
  top: 2px;
  height: 20px;
  width: 20px;
  background-color: var(--input-bg);
  border: 2px solid var(--border-color);
  border-radius: 50%;
  transition: all 0.3s;
}

.radio-option:hover .radio-indicator {
  border-color: var(--accent-color);
}

.radio-option input[type="radio"]:checked ~ .radio-indicator {
  background-color: var(--accent-color);
  border-color: var(--accent-color);
}

.radio-indicator::after {
  content: "";
  position: absolute;
  display: none;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: white;
}

.radio-option input[type="radio"]:checked ~ .radio-indicator::after {
  display: block;
}

.radio-label {
  font-size: 14px;
  color: var(--text-color);
}

.checkbox-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.checkbox-option {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  position: relative;
  padding-left: 28px;
}

.checkbox-option input[type="checkbox"] {
  opacity: 0;
  position: absolute;
  width: 0;
  height: 0;
}

.checkbox-indicator {
  position: absolute;
  left: 0;
  top: 2px;
  height: 20px;
  width: 20px;
  background-color: var(--input-bg);
  border: 2px solid var(--border-color);
  border-radius: 4px;
  transition: all 0.3s;
}

.checkbox-option:hover .checkbox-indicator {
  border-color: var(--accent-color);
}

.checkbox-option input[type="checkbox"]:checked ~ .checkbox-indicator {
  background-color: var(--accent-color);
  border-color: var(--accent-color);
}

.checkbox-indicator::after {
  content: "";
  position: absolute;
  display: none;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%) rotate(45deg);
  width: 6px;
  height: 10px;
  border: solid white;
  border-width: 0 2px 2px 0;
}

.checkbox-option input[type="checkbox"]:checked ~ .checkbox-indicator::after {
  display: block;
}

.checkbox-label {
  font-size: 14px;
  color: var(--text-color);
}

.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}

.form-actions > div {
  display: flex;
  gap: 12px;
}

.btn {
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  border: none;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-cancel {
  background-color: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

.btn-cancel:hover {
  background-color: var(--border-color);
  color: var(--text-color);
}

.btn-back {
  background-color: transparent;
  color: var(--text-color);
  border: 1px solid var(--border-color);
}

.btn-back:hover {
  background-color: var(--border-color);
}

.btn-skip {
  background-color: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

.btn-skip:hover {
  background-color: var(--border-color);
  color: var(--text-color);
}

.btn-next {
  background-color: var(--accent-color);
  color: white;
}

.btn-next:hover:not(:disabled) {
  background-color: var(--accent-hover);
}

.btn-primary {
  background-color: var(--accent-color);
  color: white;
}

.btn-primary:hover {
  background-color: var(--accent-hover);
}

.btn-secondary {
  background-color: transparent;
  color: var(--text-color);
  border: 1px solid var(--border-color);
}

.btn-secondary:hover {
  background-color: var(--border-color);
}

.btn-submit {
  background-color: var(--success-color);
  color: white;
}

.btn-submit:hover {
  background-color: #45a049;
}

.btn-large {
  padding: 16px 24px;
  font-size: 16px;
}

.btn-small {
  padding: 8px 12px;
  font-size: 12px;
}

.btn-tiny {
  padding: 6px 10px;
  font-size: 11px;
}

.review-sections {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.review-section {
  background-color: var(--input-bg);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid var(--border-color);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-color);
}

.edit-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background-color: transparent;
  color: var(--accent-color);
  border: 1px solid var(--accent-color);
  border-radius: 6px;
  padding: 6px 12px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.edit-btn:hover {
  background-color: var(--accent-color);
  color: white;
}

.review-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.review-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.review-item-full {
  grid-column: 1 / -1;
}

.review-label {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.review-value {
  font-size: 14px;
  color: var(--text-color);
  word-wrap: break-word;
}

.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  color: white;
}

.status-yes {
  background-color: var(--success-color);
}

.status-no {
  background-color: var(--danger-color);
}

.status-info {
  background-color: #3b82f6;
}

.status-warning {
  background-color: var(--pending-color);
}

.priority-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  color: white;
}

.priority-critical {
  background-color: var(--danger-color);
}

.priority-high {
  background-color: var(--pending-color);
}

.priority-medium {
  background-color: #ffc857;
  color: #333;
}

.priority-low {
  background-color: var(--success-color);
}

.services-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.service-tag {
  font-size: 12px;
  background-color: var(--border-color);
  color: var(--text-color);
  padding: 4px 8px;
  border-radius: 4px;
}

.ai-preview-container {
  width: 400px;
  flex-shrink: 0;
}

.ai-preview {
  background-color: var(--content-bg);
  border-radius: 15px;
  border: 1px solid var(--border-color);
  height: calc(100vh - 120px);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.ai-preview-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px;
  border-bottom: 1px solid var(--border-color);
  background-color: var(--input-bg);
}

.ai-preview-header svg {
  stroke: var(--accent-color);
}

.ai-preview-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-color);
  display: flex;
  align-items: center;
  gap: 8px;
}

.ai-badge {
  background-color: var(--accent-color);
  color: white;
  font-size: 10px;
  font-weight: 500;
  padding: 2px 6px;
  border-radius: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.ai-preview-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.ai-preview-section {
  margin-bottom: 24px;
}

.ai-preview-section:last-child {
  margin-bottom: 0;
}

.ai-preview-section-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 12px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--border-color);
}

.ai-autofill-section {
  background-color: var(--input-bg);
  border-radius: 8px;
  padding: 16px;
  border: 1px solid var(--border-color);
}

.ai-autofill-description {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.4;
  margin-bottom: 12px;
}

.ai-autofill-btn {
  width: 100%;
  justify-content: center;
}

.ai-suggestions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.ai-suggestion {
  display: flex;
  gap: 12px;
  padding: 12px;
  background-color: var(--input-bg);
  border-radius: 8px;
  border-left: 3px solid var(--border-color);
}

.suggestion-info {
  border-left-color: #3b82f6;
}

.suggestion-warning {
  border-left-color: var(--pending-color);
}

.suggestion-success {
  border-left-color: var(--success-color);
}

.suggestion-icon {
  font-size: 16px;
  line-height: 1;
  flex-shrink: 0;
}

.suggestion-content {
  flex: 1;
}

.suggestion-text {
  font-size: 13px;
  color: var(--text-color);
  line-height: 1.4;
  margin-bottom: 8px;
}

.suggestion-action {
  display: flex;
  justify-content: flex-end;
}

.btn-outline {
  background-color: transparent;
  color: var(--accent-color);
  border: 1px solid var(--accent-color);
}

.btn-outline:hover {
  background-color: var(--accent-color);
  color: white;
}

.ai-summary {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
}

.summary-label {
  font-weight: 500;
  color: var(--text-secondary);
}

.summary-value {
  text-align: right;
  color: var(--text-color);
}

.text-muted {
  color: var(--text-secondary);
}

.progress-insights {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.insight-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--text-color);
}

.insight-icon {
  font-size: 16px;
  line-height: 1;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s;
}

.modal-overlay.active {
  opacity: 1;
  visibility: visible;
}

.modal-content {
  background-color: var(--content-bg);
  border-radius: 12px;
  padding: 0;
  max-width: 500px;
  width: 90%;
  border: 1px solid var(--border-color);
  animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
  from {
    transform: translateY(-20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.modal-header {
  padding: 20px;
  border-bottom: 1px solid var(--border-color);
}

.modal-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-color);
}

.modal-title svg {
  stroke: var(--accent-color);
}

.modal-body {
  padding: 20px;
}

.modal-body p {
  color: var(--text-color);
  line-height: 1.5;
  margin: 0 0 12px 0;
}

.modal-body p:last-child {
  margin-bottom: 0;
}

.modal-footer {
  padding: 20px;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.modal-btn {
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  border: none;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.modal-btn-cancel {
  background-color: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

.modal-btn-cancel:hover {
  background-color: var(--border-color);
  color: var(--text-color);
}

.modal-btn-confirm {
  background-color: var(--accent-color);
  color: white;
}

.modal-btn-confirm:hover {
  background-color: var(--accent-hover);
}

/* New AI Insights Specific Styles */
.transcription-section,
.summary-section,
.entities-section,
.classification-section {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background-color: var(--input-bg);
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.transcription-text,
.summary-text {
  font-size: 0.875rem;
  line-height: 1.5;
  color: var(--text-color);
  margin-bottom: 0.75rem;
  max-height: 150px;
  overflow-y: auto;
  background-color: var(--content-bg);
  padding: 0.75rem;
  border-radius: 6px;
  border: 1px solid var(--border-color);
}

.entity-suggestions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.entity-suggestion {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem;
  background-color: var(--content-bg);
  border-radius: 6px;
  border: 1px solid var(--border-color);
}

.entity-text {
  font-weight: 500;
  color: var(--text-color);
}

.entity-label {
  font-size: 0.75rem;
  background-color: var(--accent-color);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  text-transform: uppercase;
}

.classification-suggestions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.suggestion-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem;
  background-color: var(--content-bg);
  border-radius: 6px;
  border: 1px solid var(--border-color);
  flex-wrap: wrap;
  gap: 0.5rem;
}

.suggestion-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.suggestion-value {
  font-size: 0.875rem;
  color: var(--text-color);
  font-weight: 500;
}

.insight-section {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background-color: var(--input-bg);
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.insight-text {
  font-size: 0.875rem;
  line-height: 1.5;
  color: var(--text-color);
  margin-bottom: 0.75rem;
}

.entity-group,
.risk-group,
.service-group {
  margin-bottom: 1rem;
}

.entity-type,
.risk-type,
.service-type {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 0.5rem;
}

.entity-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.entity-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  background-color: var(--accent-color);
  color: white;
  border-radius: 1rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.entity-use-btn {
  background-color: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  font-size: 0.75rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
}

.entity-use-btn:hover {
  background-color: rgba(255, 255, 255, 0.3);
}

.risk-list {
  list-style-type: disc;
  padding-left: 1.5rem;
  color: var(--text-color);
  font-size: 0.875rem;
}

.service-suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.service-suggestion-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background-color: var(--content-bg);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-color);
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.service-suggestion-btn:hover {
  background-color: var(--accent-color);
  color: white;
  border-color: var(--accent-color);
}

.add-icon {
  background-color: var(--accent-color);
  color: white;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  font-size: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.service-suggestion-btn:hover .add-icon {
  background-color: white;
  color: var(--accent-color);
}

.subsection-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 0.5rem;
  margin-top: 0.75rem;
}

/* Responsive styles */
@media (max-width: 1200px) {
  .case-container {
    flex-direction: column;
  }
  
  .ai-preview-container {
    width: 100%;
  }
  
  .ai-preview {
    height: 400px;
  }
  
  .entity-tags {
    flex-direction: column;
  }
  
  .service-suggestions {
    flex-direction: column;
  }
  
  .classification-suggestions {
    gap: 0.5rem;
  }
  
  .suggestion-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}

@media (max-width: 768px) {
  .case-creation-page {
    padding: 10px;
  }
  
  .case-container {
    margin-top: 60px;
  }
  
  .main-form-container {
    padding: 20px;
  }
  
  .case-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .case-header h1 {
    font-size: 24px;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .contacts-grid {
    grid-template-columns: 1fr;
  }
  
  .review-content {
    grid-template-columns: 1fr;
  }
  
  .form-actions {
    flex-direction: column;
    gap: 15px;
  }
  
  .form-actions > div {
    width: 100%;
    justify-content: center;
  }
  
  .progress-steps {
    flex-wrap: wrap;
    gap: 10px;
  }
  
  .step-circle {
    width: 35px;
    height: 35px;
    font-size: 12px;
  }
  
  .step-label {
    font-size: 11px;
  }
  
  .checkbox-grid {
    grid-template-columns: 1fr;
  }
  
  .transcription-text,
  .summary-text {
    max-height: 100px;
  }
  
  .entity-suggestion {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}

@media (max-width: 480px) {
  .back-button,
  .theme-toggle {
    position: relative;
    top: 0;
    left: 0;
    right: 0;
    margin-bottom: 10px;
    width: 100%;
    justify-content: center;
  }
  
  .case-container {
    margin-top: 20px;
  }
  
  .main-form-container {
    padding: 15px;
  }
  
  .case-header h1 {
    font-size: 20px;
  }
  
  .btn {
    padding: 10px 16px;
    font-size: 13px;
  }
  
  .contacts-grid {
    padding: 0;
  }
  
  .contact-card {
    flex-direction: column;
    text-align: center;
  }
  
  .contact-select-indicator {
    position: static;
    transform: none;
    align-self: center;
    margin-top: 10px;
  }
  
  .modal-content {
    width: 95%;
    margin: 10px;
  }
  
  .modal-header,
  .modal-body,
  .modal-footer {
    padding: 15px;
  }
  
  .ai-preview {
    height: 300px;
  }
  
  .ai-preview-content {
    padding: 15px;
  }
}

.glass-card {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.fine-border {
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.glass-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 8px;
  padding: 10px 20px;
  color: white;
  cursor: pointer;
  transition: background 0.3s;
}

.glass-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.glass-btn.filled {
  background: var(--accent-color);
}

.glass-btn.filled:hover {
  background: var(--accent-hover);
}
</style>

<template>
  <div class="case-creation-page">
    <router-link class="back-button" to="/cases">
      <svg
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M19 12H5"
          stroke="currentColor"
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
        />
        <path
          d="M12 19L5 12L12 5"
          stroke="currentColor"
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
        />
      </svg>
      Back to Cases
    </router-link>

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
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M12 2L2 7L12 12L22 7L12 2Z"
                    stroke="currentColor"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                  />
                  <path
                    d="M2 17L12 22L22 17"
                    stroke="currentColor"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                  />
                  <path
                    d="M2 12L12 17L22 12"
                    stroke="currentColor"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                  />
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
              class="progress-step clickable-step"
              :class="{ active: currentStep >= step }"
              @click="navigateToStep(step)"
            >
              <div
                class="step-circle"
                :class="{
                  active: currentStep >= step,
                  completed: currentStep > step,
                }"
              >
                {{ currentStep > step ? "✓" : step }}
              </div>
              <div class="step-label" :class="{ active: currentStep >= step }">
                {{ stepLabels[step - 1] }}
              </div>
            </div>
          </div>
        </div>

        <!-- Step 1: Reporter Selection -->
        <div v-show="currentStep === 1" class="step-content">
          <form class="case-form" @submit.prevent="validateAndProceed(1)">
            <div class="form-section">
              <div class="section-title">Select Reporter</div>
              <p class="section-description">
                Choose an existing contact or create a new reporter for this case.
              </p>

              <div class="search-section">
                <div class="search-row">
                  <div class="search-box">
                    <svg
                      width="18"
                      height="18"
                      viewBox="0 0 24 24"
                      fill="none"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <circle
                        cx="11"
                        cy="11"
                        r="8"
                        stroke="currentColor"
                        stroke-width="2"
                      />
                      <path
                        d="m21 21-4.35-4.35"
                        stroke="currentColor"
                        stroke-width="2"
                      />
                    </svg>
                    <input
                      v-model="searchQuery"
                      type="text"
                      placeholder="Search by name or phone..."
                      class="search-input"
                    />
                    <!-- Live suggestions -->
                    <ul
                      class="search-suggestions"
                      v-if="debouncedQuery && filteredContacts.length"
                      :style="{ width: suggestionWidth }"
                    >
                      <li
                        v-for="contact in filteredContacts.slice(0, 8)"
                        :key="contact[casesStore.cases_k.id[0]]"
                        class="suggestion-item"
                        @click="selectExistingReporter(contact)"
                      >
                        <span class="suggestion-name">{{ contact[casesStore.cases_k.reporter_fullname[0]] || 'Unnamed' }}</span>
                        <span class="suggestion-phone">{{ contact[casesStore.cases_k.reporter_phone[0]] || '' }}</span>
                      </li>
                    </ul>
                    <div
                      class="search-empty"
                      v-else-if="debouncedQuery && !filteredContacts.length"
                      :style="{ width: suggestionWidth }"
                    >
                      No matches found
                    </div>
                  </div>
                  <button type="button" class="create-reporter-btn" @click="createNewReporter">
                    + New Reporter
                  </button>
                </div>
              </div>

              <!-- Updated contacts list format -->
              <div class="contacts-list" v-if="searchQuery && filteredContacts.length">
                <div
                  v-for="contact in filteredContacts"
                  :key="contact[casesStore.cases_k.id[0]]"
                  class="contact-item"
                  :class="{ selected: selectedReporter && selectedReporter[casesStore.cases_k.id[0]] === contact[casesStore.cases_k.id[0]] }"
                  @click="selectExistingReporter(contact)"
                >
                  <div class="contact-avatar">
                    <span>{{
                      getInitials(
                        contact[casesStore.cases_k.reporter_fullname[0]] ||
                          "NA"
                      )
                        .slice(0, 2)
                        .toUpperCase()
                    }}</span>
                  </div>
                  <div class="contact-details">
                    <div class="contact-main-info">
                      <div class="contact-name">
                        {{
                          contact[casesStore.cases_k.reporter_fullname[0]] ||
                          "Untitled Case"
                        }}
                      </div>
                      <div class="contact-phone">{{ contact[casesStore.cases_k.reporter_phone[0]] }}</div>
                    </div>
                    <div class="contact-meta-info">
                      <div class="contact-tags">
                        <span class="contact-tag">{{ contact[casesStore.cases_k.reporter_age[0]] }}y</span>
                        <span class="contact-tag">{{ contact[casesStore.cases_k.reporter_sex[0]]}}</span>
                        <span class="contact-tag location">📍 {{ contact[casesStore.cases_k.reporter_location[0]]}}</span>
                      </div>
                      <div class="contact-timestamp">{{ new Date(contact[casesStore.cases_k.dt[0]] * 1000).toLocaleString('en-US') }}</div>
                    </div>
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
                  <svg
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      d="M5 12l5 5L20 7"
                      stroke="currentColor"
                      stroke-width="2"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                  </svg>
                  Continue with {{ selectedReporter?.[casesStore.cases_k.reporter_fullname[0]] }}
                </button>
              </div>
            </div>
            <div class="form-actions">
              <button type="button" class="btn btn-cancel" @click="cancelForm">
                Cancel
              </button>
              <div>
                <button type="button" class="btn btn-skip" @click="skipStep(1)">
                  Skip
                </button>
                <button
                  type="submit"
                  class="btn btn-next"
                  :disabled="!selectedReporter"
                >
                  Next
                </button>
              </div>
            </div>
          </form>
        </div>

        <!-- Step 2: Reporter Details -->
        <div v-show="currentStep === 2" class="step-content">
          <form class="case-form" @submit.prevent="saveAndProceed(2)">
            <div class="form-section">
              <div class="section-title">
                {{
                  selectedReporter
                    ? "Reporter Details"
                    : "New Reporter Information"
                }}
              </div>
              <p class="section-description">
                Enter the reporter's contact information and details.
              </p>

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
                  <select
                    v-model="formData.step2.gender"
                    id="reporter-gender"
                    class="form-control"
                  >
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
                  <select
                    v-model="formData.step2.idType"
                    id="reporter-id-type"
                    class="form-control"
                  >
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
              <button type="button" class="btn btn-back" @click="goToStep(1)">
                Back
              </button>
              <div>
                <button type="button" class="btn btn-skip" @click="skipStep(2)">
                  Skip
                </button>
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
              <p class="section-description">
                Provide detailed information about the case and incident.
              </p>

              

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
              <button type="button" class="btn btn-back" @click="goToStep(2)">
                Back
              </button>
              <div>
                <button type="button" class="btn btn-skip" @click="skipStep(3)">
                  Skip
                </button>
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
              <p class="section-description">
                Classify the case and set priority levels for proper handling.
              </p>

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
                    <option value="labor-exploitation">
                      Labor Exploitation
                    </option>
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
              <button type="button" class="btn btn-back" @click="goToStep(3)">
                Back
              </button>
              <div>
                <button type="button" class="btn btn-skip" @click="skipStep(4)">
                  Skip
                </button>
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
                  <svg
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"
                      stroke="currentColor"
                      stroke-width="2"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                    <path
                      d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"
                      stroke="currentColor"
                      stroke-width="2"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                  </svg>
                  Edit
                </button>
              </div>
              <div class="review-content">
                <div class="review-item">
                  <div class="review-label">Name</div>
                  <div class="review-value">
                    {{ formData.step2.name || "N/A" }}
                  </div>
                </div>
                <div class="review-item">
                  <div class="review-label">Phone</div>
                  <div class="review-value">
                    {{ formData.step2.phone || "N/A" }}
                  </div>
                </div>
                <div class="review-item">
                  <div class="review-label">Location</div>
                  <div class="review-value">
                    {{ formData.step2.location || "N/A" }}
                  </div>
                </div>
                <div class="review-item">
                  <div class="review-label">Is Client</div>
                  <div class="review-value">
                    <span
                      class="status-badge"
                      :class="
                        formData.step2.isClient ? 'status-yes' : 'status-no'
                      "
                    >
                      {{ formData.step2.isClient ? "Yes" : "No" }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <div class="review-section">
              <div class="section-header">
                <div class="section-title">Case Details</div>
                <button class="edit-btn" @click="goToStep(3)">
                  <svg
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"
                      stroke="currentColor"
                      stroke-width="2"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                    <path
                      d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"
                      stroke="currentColor"
                      stroke-width="2"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                  </svg>
                  Edit
                </button>
              </div>
              <div class="review-content">
                <div class="review-item review-item-full">
                  <div class="review-label">Case Narrative</div>
                  <div class="review-value">
                    {{ formData.step3.narrative || "N/A" }}
                  </div>
                </div>
                <div class="review-item">
                  <div class="review-label">GBV Related</div>
                  <div class="review-value">
                    <span
                      class="status-badge"
                      :class="
                        formData.step3.isGBVRelated
                          ? 'status-warning'
                          : 'status-info'
                      "
                    >
                      {{ formData.step3.isGBVRelated ? "Yes" : "No" }}
                    </span>
                  </div>
                </div>
                <div class="review-item">
                  <div class="review-label">Incident Date</div>
                  <div class="review-value">
                    {{ formData.step3.incidentDate || "N/A" }}
                  </div>
                </div>
                <div class="review-item">
                  <div class="review-label">Location</div>
                  <div class="review-value">
                    {{ formData.step3.location || "N/A" }}
                  </div>
                </div>
              </div>
            </div>

            <div class="review-section">
              <div class="section-header">
                <div class="section-title">Classification</div>
                <button class="edit-btn" @click="goToStep(4)">
                  <svg
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"
                      stroke="currentColor"
                      stroke-width="2"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                    <path
                      d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"
                      stroke="currentColor"
                      stroke-width="2"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                  </svg>
                  Edit
                </button>
              </div>
              <div class="review-content">
                <div class="review-item">
                  <div class="review-label">Department</div>
                  <div class="review-value">
                    {{ formatDepartment(formData.step4.department) || "N/A" }}
                  </div>
                </div>
                <div class="review-item">
                  <div class="review-label">Category</div>
                  <div class="review-value">
                    {{ formatCategory(formData.step4.category) || "N/A" }}
                  </div>
                </div>
                <div class="review-item">
                  <div class="review-label">Priority</div>
                  <div class="review-value">
                    <span
                      v-if="formData.step4.priority"
                      class="priority-badge"
                      :class="`priority-${formData.step4.priority}`"
                    >
                      {{ formatPriority(formData.step4.priority) }}
                    </span>
                    <span v-else>N/A</span>
                  </div>
                </div>
                <div class="review-item">
                  <div class="review-label">Status</div>
                  <div class="review-value">
                    <span
                      v-if="formData.step4.status"
                      class="status-badge status-info"
                    >
                      {{ formatStatus(formData.step4.status) }}
                    </span>
                    <span v-else>N/A</span>
                  </div>
                </div>
                <div class="review-item review-item-full">
                  <div class="review-label">Services Offered</div>
                  <div class="review-value">
                    <div
                      v-if="formData.step4.servicesOffered.length > 0"
                      class="services-tags"
                    >
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
            <button type="button" class="btn btn-back" @click="goToStep(4)">
              Back
            </button>
            <button type="button" class="glass-btn filled" @click="submitCase">Create Case</button>
          </div>
        </div>
      </div>

      <!-- Enhanced AI Insights Panel -->
      <div v-if="isAIEnabled" class="ai-preview-container">
        <div class="ai-preview" style="border:1px solid var(--border-color, rgba(0,0,0,0.08)); border-radius:12px; overflow:hidden; background: var(--card-bg, #fff);">
          <div class="ai-preview-header">
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M12 2L2 7L12 12L22 7L12 2Z"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
              <path
                d="M2 17L12 22L22 17"
                stroke="currentColor"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
              <path
                d="M2 12L12 17L22 12"
                stroke="currentColor"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
            <div class="ai-preview-title">
              AI Insights <span class="ai-badge">LIVE</span>
            </div>
          </div>
          <div class="ai-preview-content">
            <!-- Audio Upload (AI Panel) -->
            <div class="ai-preview-section">
              <div class="ai-preview-section-title">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" stroke="currentColor" stroke-width="2"/>
                  <path d="M19 10v2a7 7 0 0 1-14 0v-2" stroke="currentColor" stroke-width="2"/>
                </svg>
                Upload Audio
              </div>
              <div class="ai-audio-upload">
                <input type="file" accept="audio/*" @change="onAudioUpload" />
                <div v-if="audioFile" class="ai-audio-meta">
                  <div class="audio-name">{{ audioFile.name || 'Audio file' }}</div>
                  <div class="audio-meta">{{ formatFileSize(audioFile.size) }} • {{ audioDuration }}s</div>
                </div>
              </div>
            </div>

            <!-- Transcription Section (AI Panel) -->
            <div v-if="audioTranscription" class="ai-preview-section">
              <div class="ai-preview-section-title">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" stroke="currentColor" stroke-width="2"/>
                  <polyline points="14,2 14,8 20,8" stroke="currentColor" stroke-width="2"/>
                </svg>
                Case Transcription
                <button type="button" class="btn-copy" @click="copyTranscription" style="margin-left:auto;">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2" stroke="currentColor" stroke-width="2"/>
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" stroke="currentColor" stroke-width="2"/>
                  </svg>
                  Copy
                </button>
              </div>
              <div class="transcription-text">{{ audioTranscription }}</div>
              <div class="transcription-verify" style="margin-top:10px; display:flex; flex-direction:column; gap:8px;">
                <div class="question" style="font-weight:600;">Is the transcription correct?</div>
                <div class="options" style="display:flex; gap:16px; align-items:center;">
                  <label style="display:flex; align-items:center; gap:6px; cursor:pointer;">
                    <input
                      type="radio"
                      name="transcription-correct"
                      v-model="isTranscriptionCorrect"
                      :value="true"
                    />
                    <span>Yes</span>
                  </label>
                  <label style="display:flex; align-items:center; gap:6px; cursor:pointer;">
                    <input
                      type="radio"
                      name="transcription-correct"
                      v-model="isTranscriptionCorrect"
                      :value="false"
                      @change="enqueueForTranscriptionReview"
                    />
                    <span>No</span>
                  </label>
                </div>
              </div>
            </div>
            
            <!-- Case Summary Section -->
            <div v-if="caseSummary" class="ai-preview-section">
              <div class="ai-preview-section-title">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" stroke="currentColor" stroke-width="2"/>
                  <polyline points="14,2 14,8 20,8" stroke="currentColor" stroke-width="2"/>
                  <line x1="16" y1="13" x2="8" y2="13" stroke="currentColor" stroke-width="2"/>
                  <line x1="16" y1="17" x2="8" y2="17" stroke="currentColor" stroke-width="2"/>
                </svg>
                Case Summary
              </div>
              <div class="case-summary">
                <div class="summary-item">
                  <div class="summary-label">Risk Level</div>
                  <div class="summary-value">
                    <span class="risk-badge" :class="`risk-${caseSummary.riskLevel}`">
                      {{ caseSummary.riskLevel.toUpperCase() }}
                    </span>
                  </div>
                </div>
                <div class="summary-item">
                  <div class="summary-label">Urgency</div>
                  <div class="summary-value">{{ caseSummary.urgency }}</div>
                </div>
                <div class="summary-item">
                  <div class="summary-label">Key Concerns</div>
                  <div class="summary-value">
                    <div class="concern-tags">
                      <span v-for="concern in caseSummary.keyConcerns" :key="concern" class="concern-tag">
                        {{ concern }}
                      </span>
                    </div>
                  </div>
                </div>
                <div class="summary-item full-width">
                  <div class="summary-label">AI Analysis</div>
                  <div class="summary-value summary-text">{{ caseSummary.analysis }}</div>
                </div>
              </div>
            </div>

            <!-- Smart Insights Section -->
            <div class="ai-preview-section">
              <div class="ai-preview-section-title">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/>
                  <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" stroke="currentColor" stroke-width="2"/>
                </svg>
                Smart Insights
              </div>
              <div class="ai-suggestions">
                <div v-for="insight in aiInsights" :key="insight.id" class="ai-suggestion" :class="`suggestion-${insight.type}`">
                  <div class="suggestion-icon">{{ insight.icon }}</div>
                  <div class="suggestion-content">
                    <div class="suggestion-title">{{ insight.title }}</div>
                    <div class="suggestion-text">{{ insight.message }}</div>
                    <div v-if="insight.action" class="suggestion-action">
                      <button class="btn-suggestion" @click="applyInsight(insight)">
                        {{ insight.action }}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Recommendations Section -->
            <div v-if="recommendations.length > 0" class="ai-preview-section">
              <div class="ai-preview-section-title">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M9 11H5a2 2 0 0 0-2 2v7a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7a2 2 0 0 0-2-2h-4" stroke="currentColor" stroke-width="2"/>
                  <polyline points="9,11 12,14 15,11" stroke="currentColor" stroke-width="2"/>
                  <line x1="12" y1="2" x2="12" y2="14" stroke="currentColor" stroke-width="2"/>
                </svg>
                Recommendations
              </div>
              <div class="recommendations-list">
                <div v-for="rec in recommendations" :key="rec.id" class="recommendation-item">
                  <div class="rec-priority" :class="`priority-${rec.priority}`"></div>
                  <div class="rec-content">
                    <div class="rec-title">{{ rec.title }}</div>
                    <div class="rec-description">{{ rec.description }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useTranscriptionsStore } from '@/stores/transcriptionsStore'

const router = useRouter()
const transcriptionsStore = useTranscriptionsStore()

// State
const currentStep = ref(1)
const totalSteps = 5
const isAIEnabled = ref(true)
const searchQuery = ref('')
const selectedReporter = ref(null)

// Audio recording state
const isRecording = ref(false)
const recordingTime = ref(0)
const audioFile = ref(null)
const audioDuration = ref(0)
const isPlaying = ref(false)
const audioTranscription = ref('')
const isTranscriptionCorrect = ref(false)
let mediaRecorder = null
let recordingInterval = null

// AI state
const caseSummary = ref(null)
const aiInsights = ref([])
const recommendations = ref([])

// Mock store for demonstration
const casesStore = {
  cases_k: {
    id: [0],
    reporter_fullname: [1],
    reporter_phone: [2],
    reporter_age: [3],
    reporter_sex: [4],
    reporter_location: [5],
    dt: [6]
  },
  cases: [
    [1, 'Ivan Somondi', '254700112233', 16, 'Male', 'Narok County', 1640995200],
    [2, 'Susan Kirigwa', '254700445566', 45, 'Female', 'Narok', 1640908800],
    [3, 'Amira', '254700778899', 28, 'Female', 'Nairobi', 1641081600]
  ]
}

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
const debouncedQuery = ref('')
const suggestionWidth = '100%'
let debounceTimer = null

watch(searchQuery, (val) => {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => { 
    debouncedQuery.value = val.trim() 
  }, 200)
})

const filteredContacts = computed(() => {
  if (!debouncedQuery.value) return []
  const q = debouncedQuery.value.toLowerCase()
  const nameIdx = casesStore.cases_k.reporter_fullname[0]
  const phoneIdx = casesStore.cases_k.reporter_phone[0]
  
  return casesStore.cases.filter((contact) => {
    const name = (contact[nameIdx] || '').toString().toLowerCase()
    const phone = (contact[phoneIdx] || '').toString()
    return name.includes(q) || phone.includes(debouncedQuery.value)
  })
})

// Watch for form changes to generate AI insights
watch([formData, currentStep], () => {
  if (isAIEnabled.value) {
    generateAIInsights()
    generateCaseSummary()
  }
}, { deep: true })

// Methods
const getInitials = (name) => {
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
}

const navigateToStep = (step) => {
  if (step <= currentStep.value + 1) {
    currentStep.value = step
  }
}

const selectExistingReporter = (contact) => {
  selectedReporter.value = contact
}

const createNewReporter = () => {
  selectedReporter.value = null
  Object.keys(formData.step2).forEach((key) => {
    formData.step2[key] = key === 'isClient' ? null : ''
  })
  currentStep.value = 2
}

const goToStep = (step) => {
  currentStep.value = step
}

const validateAndProceed = (step) => {
  if (step === 1 && selectedReporter.value) {
    const reporter = selectedReporter.value
    const nameIdx = casesStore.cases_k.reporter_fullname[0]
    const ageIdx = casesStore.cases_k.reporter_age[0]
    const genderIdx = casesStore.cases_k.reporter_sex[0]
    const locationIdx = casesStore.cases_k.reporter_location[0]
    const phoneIdx = casesStore.cases_k.reporter_phone[0]

    formData.step2.name = reporter[nameIdx]
    formData.step2.age = reporter[ageIdx]
    formData.step2.gender = reporter[genderIdx]?.toLowerCase() || ''
    formData.step2.location = reporter[locationIdx]
    formData.step2.phone = reporter[phoneIdx]

    currentStep.value = 2
  }
}

const skipStep = (step) => {
  currentStep.value = step + 1
}

const saveAndProceed = (step) => {
  currentStep.value = step + 1
}

// Audio recording methods
const startRecording = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    mediaRecorder = new MediaRecorder(stream)
    const chunks = []

    mediaRecorder.ondataavailable = (event) => {
      chunks.push(event.data)
    }

    mediaRecorder.onstop = () => {
      const blob = new Blob(chunks, { type: 'audio/wav' })
      audioFile.value = new File([blob], 'recording.wav', { type: 'audio/wav' })
      audioDuration.value = recordingTime.value
      transcribeAudio()
    }

    mediaRecorder.start()
    isRecording.value = true
    recordingTime.value = 0
    
    recordingInterval = setInterval(() => {
      recordingTime.value++
    }, 1000)
  } catch (error) {
    console.error('Error starting recording:', error)
  }
}

const stopRecording = () => {
  if (mediaRecorder && isRecording.value) {
    mediaRecorder.stop()
    mediaRecorder.stream.getTracks().forEach(track => track.stop())
    isRecording.value = false
    clearInterval(recordingInterval)
  }
}

const togglePlayback = () => {
  // Mock playback toggle
  isPlaying.value = !isPlaying.value
  if (isPlaying.value) {
    setTimeout(() => {
      isPlaying.value = false
    }, audioDuration.value * 1000)
  }
}

const removeAudio = () => {
  audioFile.value = null
  audioTranscription.value = ''
  isTranscriptionCorrect.value = false
  audioDuration.value = 0
  isPlaying.value = false
}

// Handle uploaded audio file
const onAudioUpload = async (event) => {
  const file = event.target?.files?.[0]
  if (!file) return
  audioFile.value = file
  isTranscriptionCorrect.value = false
  // Compute duration via HTMLAudioElement
  try {
    const url = URL.createObjectURL(file)
    const audioEl = new Audio()
    audioEl.src = url
    await new Promise((resolve, reject) => {
      audioEl.addEventListener('loadedmetadata', () => resolve())
      audioEl.addEventListener('error', (e) => reject(e))
    })
    audioDuration.value = Math.round(audioEl.duration || 0)
    URL.revokeObjectURL(url)
  } catch (e) {
    audioDuration.value = 0
  }
  // Trigger transcription (mock)
  transcribeAudio()
}

const transcribeAudio = async () => {
  // Mock transcription - in real app, this would call an AI service
  setTimeout(() => {
    audioTranscription.value = "This is a mock transcription of the audio recording. The reporter described an incident that occurred on the evening of the 15th involving domestic violence. The victim is seeking immediate assistance and shelter services."
    
    // Auto-fill narrative if empty
    if (!formData.step3.narrative) {
      formData.step3.narrative = audioTranscription.value
    }
  }, 2000)
}

const copyTranscription = () => {
  navigator.clipboard.writeText(audioTranscription.value)
}

const enqueueForTranscriptionReview = () => {
  if (isTranscriptionCorrect.value === false && audioTranscription.value) {
    let audioUrl = null
    if (audioFile.value instanceof File) {
      audioUrl = URL.createObjectURL(audioFile.value)
    }
    transcriptionsStore.addItem({
      audioFile: audioFile.value || null,
      audioUrl,
      transcription: audioTranscription.value,
      counsellor: 'Current User',
      uploadedAt: Date.now()
    })
  }
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// AI Methods
const generateCaseSummary = () => {
  if (!formData.step3.narrative && !audioTranscription.value) return

  // Mock AI analysis
  const narrative = formData.step3.narrative || audioTranscription.value
  const isGBV = formData.step3.isGBVRelated
  
  caseSummary.value = {
    riskLevel: isGBV ? 'high' : 'medium',
    urgency: isGBV ? 'Immediate attention required' : 'Standard processing',
    keyConcerns: isGBV ? ['Safety Risk', 'Trauma Support', 'Legal Protection'] : ['Support Services', 'Documentation'],
    analysis: `Based on the case narrative, this appears to be a ${isGBV ? 'high-priority GBV case requiring immediate intervention' : 'standard case requiring appropriate support services'}. Key indicators suggest the need for ${isGBV ? 'emergency shelter, counseling, and legal aid' : 'counseling and referral services'}.`
  }
}

const generateAIInsights = () => {
  const insights = []
  
  // Step-specific insights
  if (currentStep.value === 2 && formData.step2.age && formData.step2.age < 18) {
    insights.push({
      id: 'minor-alert',
      type: 'warning',
      icon: '⚠️',
      title: 'Minor Detected',
      message: 'Reporter is under 18. Additional child protection protocols may apply.',
      action: 'Review Child Protection Guidelines'
    })
  }

  if (currentStep.value === 3 && formData.step3.isGBVRelated === true) {
    insights.push({
      id: 'gbv-protocol',
      type: 'critical',
      icon: '🚨',
      title: 'GBV Case Detected',
      message: 'This case requires immediate attention and specialized handling protocols.',
      action: 'Apply GBV Protocol'
    })
  }

  if (currentStep.value === 4 && !formData.step4.priority && formData.step3.isGBVRelated) {
    insights.push({
      id: 'priority-suggestion',
      type: 'info',
      icon: '💡',
      title: 'Priority Recommendation',
      message: 'Based on case details, we recommend setting priority to "High" or "Critical".',
      action: 'Set High Priority'
    })
  }

  if (audioTranscription.value) {
    insights.push({
      id: 'transcription-ready',
      type: 'success',
      icon: '✅',
      title: 'Audio Transcribed',
      message: 'Audio has been successfully transcribed and can be used to populate case narrative.',
      action: 'Use Transcription'
    })
  }

  aiInsights.value = insights

  // Generate recommendations
  generateRecommendations()
}

const generateRecommendations = () => {
  const recs = []
  
  if (formData.step3.isGBVRelated === true) {
    recs.push({
      id: 'shelter-rec',
      priority: 'high',
      title: 'Emergency Shelter',
      description: 'Consider immediate shelter placement for victim safety'
    })
    
    recs.push({
      id: 'legal-rec',
      priority: 'high',
      title: 'Legal Protection',
      description: 'Initiate legal protection order proceedings'
    })
  }

  if (formData.step2.age && formData.step2.age < 18) {
    recs.push({
      id: 'child-services',
      priority: 'critical',
      title: 'Child Protection Services',
      description: 'Notify child protection services immediately'
    })
  }

  recs.push({
    id: 'counseling-rec',
    priority: 'medium',
    title: 'Counseling Services',
    description: 'Schedule trauma-informed counseling session'
  })

  recommendations.value = recs
}

const applyInsight = (insight) => {
  switch (insight.id) {
    case 'priority-suggestion':
      formData.step4.priority = 'high'
      break
    case 'transcription-ready':
      if (!formData.step3.narrative) {
        formData.step3.narrative = audioTranscription.value
      }
      break
    case 'gbv-protocol':
      formData.step4.servicesOffered = ['counseling', 'legal-aid', 'shelter']
      break
  }
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

const submitCase = async () => {
  console.log('Submitting case:', formData)
  alert('Case created successfully!')
  router.push('/cases')
}

// Initialize AI insights on mount
onMounted(() => {
  if (isAIEnabled.value) {
    generateAIInsights()
  }
})
</script>

<style scoped>
/* Ensure consistent typography and polished AI panel UI */
.case-creation-page {
  min-height: 0;
  overflow: auto;
}

.ai-preview-container {
  font-family: inherit;
  position: sticky;
  top: 16px;
  align-self: start;
  min-height: 0; /* allow inner scroll in flex/grid parents */
}

.ai-preview {
  backdrop-filter: saturate(140%) blur(4px);
  height: calc(100vh - 140px);
  overflow-y: auto;
  overflow-x: hidden;
  -webkit-overflow-scrolling: touch;
  overscroll-behavior: contain;
  display: flex;
  flex-direction: column;
  touch-action: pan-y;
}

.ai-preview-header {
  padding: 12px 14px;
  border-bottom: 1px solid var(--border-color, rgba(0,0,0,0.06));
  position: sticky;
  top: 0;
  background: var(--card-bg, #fff);
  z-index: 2;
}

.ai-preview-title {
  font-weight: 600;
  font-size: 14px;
}

.ai-preview-section {
  padding: 14px;
  border-bottom: 1px dashed var(--border-color, rgba(0,0,0,0.06));
}

.ai-preview-section:last-child {
  border-bottom: none;
}

.ai-preview-section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  margin-bottom: 10px;
}

.ai-audio-upload input[type="file"] {
  width: 100%;
}

.ai-audio-meta {
  margin-top: 8px;
  font-size: 12px;
  color: var(--text-muted, #666);
}

.transcription-text {
  white-space: pre-wrap;
  line-height: 1.5;
  font-size: 14px;
  background: var(--surface-muted, rgba(0,0,0,0.02));
  padding: 10px;
  border-radius: 8px;
}

.btn-suggestion {
  font-family: inherit;
}

/* Ensure ancestors don't block child overflow scrolling */
.case-container {
  min-height: 0;
}

.main-form-container {
  min-height: 0;
  overflow: visible;
}
</style>

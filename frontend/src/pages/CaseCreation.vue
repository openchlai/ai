<template>
  <div class="case-creation-page">
    <router-link class="btn btn--primary back-button" to="/cases">
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
              :class="{
                active: currentStep === step,
                completed: stepStatus(step) === 'completed',
                error: stepStatus(step) === 'error'
              }"
              @click="navigateToStep(step)"
            >
              <div
                class="step-circle"
                :class="{
                  active: currentStep === step,
                  completed: stepStatus(step) === 'completed',
                  error: stepStatus(step) === 'error'
                }"
              >
                {{ stepStatus(step) === 'completed' ? '✓' : step }}
              </div>
              <div class="step-label" :class="{ active: currentStep === step }">
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
                    <!-- Suggestions will render inline below using contacts-list -->
                  </div>
                  <button type="button" class="btn btn--primary new-reporter-btn" @click="createNewReporter">
                    + New Reporter
                  </button>
                </div>
              </div>

              <!-- Inline results under search -->
              <div class="contacts-list" v-if="debouncedQuery && filteredContacts.length">
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
              <div class="search-empty" v-else-if="debouncedQuery && !filteredContacts.length">No matches found</div>

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
                <BaseButton variant="secondary" @click="skipStep(1)">Skip</BaseButton>
                <BaseButton type="submit" :disabled="!selectedReporter">Next</BaseButton>
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
                <BaseInput id="reporter-name" label="Full Name*" v-model="formData.step2.name" placeholder="Enter full name" :readonly="!!selectedReporter" />
                <BaseInput id="reporter-age" label="Age" type="number" v-model="formData.step2.age" placeholder="Enter age" />
              </div>

              <div class="form-row">
                <BaseInput id="reporter-dob" label="DOB" type="date" v-model="formData.step2.dob" />
                <BaseSelect id="reporter-age-group" label="Age Group" v-model="formData.step2.ageGroup" placeholder="Select age group">
                  <option value="">Select age group</option>
                  <option>0-5</option>
                  <option>6-12</option>
                  <option>13-17</option>
                  <option>18-24</option>
                  <option>25-34</option>
                  <option>35-49</option>
                  <option>50+</option>
                </BaseSelect>
              </div>

              <div class="form-row">
                <BaseSelect id="reporter-gender" label="Sex" v-model="formData.step2.gender" placeholder="Select sex">
                  <option value="female">Female</option>
                  <option value="male">Male</option>
                  <option value="non-binary">Non-binary</option>
                  <option value="other">Other</option>
                </BaseSelect>
                <BaseInput id="reporter-location" label="Location" v-model="formData.step2.location" placeholder="Enter location" />
              </div>

              <div class="form-row">
                <BaseInput id="reporter-landmark" label="Nearest Landmark" v-model="formData.step2.nearestLandmark" placeholder="Enter nearest landmark" />
                <BaseSelect id="reporter-nationality" label="Nationality" v-model="formData.step2.nationality" placeholder="Select nationality">
                  <option value="">Select nationality</option>
                  <option>Kenyan</option>
                  <option>Ugandan</option>
                  <option>Tanzanian</option>
                  <option>Somali</option>
                  <option>South Sudanese</option>
                  <option>Other</option>
                </BaseSelect>
              </div>

              <div class="form-row">
                <BaseSelect id="reporter-language" label="Language" v-model="formData.step2.language" placeholder="Select language">
                  <option value="">Select language</option>
                  <option>English</option>
                  <option>Kiswahili</option>
                  <option>Somali</option>
                  <option>Arabic</option>
                  <option>Other</option>
                </BaseSelect>
                <BaseSelect id="reporter-tribe" label="Tribe" v-model="formData.step2.tribe" placeholder="Select tribe">
                  <option value="">Select tribe</option>
                  <option>Kikuyu</option>
                  <option>Luhya</option>
                  <option>Luo</option>
                  <option>Kalenjin</option>
                  <option>Kamba</option>
                  <option>Somali</option>
                  <option>Other</option>
                </BaseSelect>
              </div>

              <div class="form-row">
                <BaseInput id="reporter-phone" label="Phone Number*" type="tel" v-model="formData.step2.phone" placeholder="Enter phone number" />
                <BaseInput id="reporter-alt-phone" label="Alternative Phone" type="tel" v-model="formData.step2.altPhone" placeholder="Enter alternative phone" />
              </div>

              <BaseInput id="reporter-email" label="Email Address" type="email" v-model="formData.step2.email" placeholder="Enter email address" />

              <div class="form-row">
                <BaseSelect id="reporter-id-type" label="ID Type" v-model="formData.step2.idType" placeholder="Select ID type">
                  <option value="national-id">National ID</option>
                  <option value="passport">Passport</option>
                  <option value="drivers-license">Driver's License</option>
                  <option value="other">Other</option>
                </BaseSelect>
                <BaseInput id="reporter-id-number" label="ID Number" v-model="formData.step2.idNumber" placeholder="Enter ID number" />
              </div>


              <div class="form-row">
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
                        @change="handleClientSelection"
                      />
                      <span class="radio-indicator"></span>
                      <span class="radio-label">No</span>
                    </label>
                  </div>
                </div>

                <!-- Perpetrators Section -->
                <div class="form-group">
                  <label>Perpetrators</label>
                  <div class="perpetrators-section">
                    <div v-if="formData.step2.perpetrators.length" class="perpetrators-list">
                      <div v-for="(perpetrator, index) in formData.step2.perpetrators" :key="index" class="perpetrator-item">
                        <div class="perpetrator-info">
                          <div class="perpetrator-name">{{ perpetrator.name }}</div>
                          <div class="perpetrator-details">{{ perpetrator.age }} {{ perpetrator.sex }} - {{ perpetrator.location }}</div>
                        </div>
                        <button type="button" class="remove-perpetrator" @click="removePerpetrator(index)">×</button>
                      </div>
                    </div>
                    <button type="button" class="btn btn--primary btn--sm add-perpetrator-btn" @click="openPerpetratorModal">
                      + Add Perpetrator
                    </button>
                  </div>
                </div>

                <!-- Clients Section - Only show if "Is Reporter a Client?" is "No" -->
                <div v-if="formData.step2.isClient === false" class="form-group">
                  <label>Clients</label>
                  <div class="clients-section">
                    <div v-if="formData.step2.clients.length" class="clients-list">
                      <div v-for="(client, index) in formData.step2.clients" :key="index" class="client-item">
                        <div class="client-info">
                          <div class="client-name">{{ client.name }}</div>
                          <div class="client-details">{{ client.age }} {{ client.sex }} - {{ client.phone || 'No phone' }}</div>
                        </div>
                        <button type="button" class="remove-client" @click="removeClient(index)">×</button>
                      </div>
                    </div>
                    <div v-else class="empty-state">
                      <p>No clients added yet</p>
                    </div>
                    <button type="button" class="btn btn--primary btn--sm add-client-btn" @click="openClientModal">
                      + Add Client
                    </button>
                  </div>
                </div>
              </div>
            </div>
            <div class="form-actions">
              <BaseButton variant="secondary" @click="goToStep(1)">Back</BaseButton>
              <div>
                <BaseButton variant="secondary" @click="skipStep(2)">Skip</BaseButton>
                <BaseButton type="submit">Next</BaseButton>
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

              

              <BaseTextarea
                id="case-narrative"
                label="Case Narrative*"
                v-model="formData.step3.narrative"
                placeholder="Describe the case details, incident, and circumstances in detail..."
                :rows="6"
              />

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
              <BaseButton variant="secondary" @click="goToStep(2)">Back</BaseButton>
              <div>
                <BaseButton variant="secondary" @click="skipStep(3)">Skip</BaseButton>
                <BaseButton type="submit">Next</BaseButton>
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
                      <span class="radio-label">116</span>
                    </label>
                    <label class="radio-option">
                      <input
                        v-model="formData.step4.department"
                        type="radio"
                        value="labor"
                        required
                      />
                      <span class="radio-indicator"></span>
                      <span class="radio-label">Labor</span>
                    </label>
                  </div>
                </div>
                
                <!-- Labor Department - Client Passport Search -->
                <div v-if="formData.step4.department === 'labor'" class="form-group labor-search-section">
                  <label>Client's Passport Number</label>
                  <div class="passport-search-container">
                    <input 
                      v-model="formData.step4.clientPassportNumber" 
                      type="text" 
                      placeholder="Enter passport number"
                      class="passport-input"
                    />
                    <button type="button" @click="searchClientByPassport" class="search-btn">
                      Search
                    </button>
                  </div>
                  
                  <!-- Search Results -->
                  <div v-if="clientSearchResults.length > 0" class="search-results">
                    <h4>Search Results:</h4>
                    <div v-for="client in clientSearchResults" :key="client.id" class="client-result">
                      <div class="client-info">
                        <strong>{{ client.name }}</strong>
                        <span class="client-details">{{ client.passportNumber }} • {{ client.nationality }}</span>
                      </div>
                      <button @click="selectClient(client)" class="select-client-btn">Select</button>
                    </div>
                  </div>
                  
                  <!-- No Results -->
                  <div v-if="clientSearchResults.length === 0 && hasSearched" class="no-results">
                    <p>No client found with this passport number.</p>
                    <button @click="createNewClient" class="create-client-btn">Create New Client</button>
                  </div>
                </div>
                <div class="form-group">
                  <label for="case-category">Case Category*</label>
                  <div class="hierarchical-dropdown">
                    <div class="dropdown-trigger" @click="toggleCategoryDropdown">
                      <div class="selected-categories">
                        <span 
                          v-for="category in formData.step4.categories" 
                          :key="category" 
                          class="category-tag"
                        >
                          {{ category }}
                          <button type="button" @click.stop="removeCategory(category)" class="tag-remove">×</button>
                        </span>
                        <span v-if="formData.step4.categories.length === 0" class="placeholder">Select Category</span>
                      </div>
                      <svg class="dropdown-arrow" :class="{ 'open': showCategoryDropdown }" width="12" height="12" viewBox="0 0 12 12">
                        <path d="M6 8L2 4h8L6 8z" fill="currentColor"/>
                      </svg>
                    </div>
                    
                    <div v-if="showCategoryDropdown" class="category-dropdown-panel">
                      <div class="panel-header">
                        <span class="panel-title">Case Category</span>
                        <button @click="expandCategoryPanel" class="expand-btn">
                          <svg width="16" height="16" viewBox="0 0 16 16">
                            <path d="M2 2h12v12H2V2zm1 1v10h10V3H3z" fill="currentColor"/>
                            <path d="M5 5h6v6H5V5zm1 1v4h4V6H6z" fill="currentColor"/>
                          </svg>
                        </button>
                      </div>
                      
                      <div class="category-tree">
                        <div 
                          v-for="category in caseCategories" 
                          :key="category.value"
                          class="category-item"
                          :class="{ 'expanded': category.expanded }"
                        >
                          <div 
                            class="category-row"
                            @click="toggleCategory(category)"
                          >
                            <span class="category-icon" v-if="category.children && category.children.length > 0">
                              <svg width="12" height="12" viewBox="0 0 12 12">
                                <path d="M4 2l4 4-4 4V2z" fill="currentColor"/>
                              </svg>
                            </span>
                            <span class="category-name">{{ category.label }}</span>
                            <input 
                              type="checkbox" 
                              :value="category.value"
                              v-model="formData.step4.categories"
                              @click.stop
                              class="category-checkbox"
                            />
                          </div>
                          
                          <div v-if="category.expanded && category.children" class="subcategories">
                            <div 
                              v-for="subcategory in category.children" 
                              :key="subcategory.value"
                              class="subcategory-item"
                            >
                              <div class="subcategory-row">
                                <span class="subcategory-name">{{ subcategory.label }}</span>
                                <input 
                                  type="checkbox" 
                                  :value="subcategory.value"
                                  v-model="formData.step4.categories"
                                  @click.stop
                                  class="category-checkbox"
                                />
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                      
                      <div class="pagination-info">
                        <span>{{ caseCategories.length }} categories available</span>
                      </div>
                    </div>
                  </div>
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

              <div class="form-row">
                <div class="form-group">
                  <label for="justice-system-state">State of the Case in the Justice System</label>
                  <select
                    v-model="formData.step4.justiceSystemState"
                    id="justice-system-state"
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
                  <label for="general-assessment">General Case Assessment</label>
                  <select
                    v-model="formData.step4.generalAssessment"
                    id="general-assessment"
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
              </div>

              <div class="form-group">
                <label for="services-offered">Services Offered</label>
                <select
                  v-model="formData.step4.servicesOffered"
                  id="services-offered"
                  class="form-control"
                >
                  <option value="">Select service...</option>
                  <option value="Know About 116">Know About 116</option>
                  <option value="Counseling">Counseling</option>
                  <option value="Legal Aid">Legal Aid</option>
                  <option value="Shelter">Shelter</option>
                  <option value="Medical Assistance">Medical Assistance</option>
                  <option value="Financial Support">Financial Support</option>
                  <option value="Referral Services">Referral Services</option>
                  <option value="Emergency Response">Emergency Response</option>
                  <option value="Crisis Intervention">Crisis Intervention</option>
                  <option value="Support Groups">Support Groups</option>
                  <option value="Education Programs">Education Programs</option>
                  <option value="Community Outreach">Community Outreach</option>
                </select>
              </div>

              <div class="form-group">
                <label for="referral-source">How did you know about 116?</label>
                <select
                  v-model="formData.step4.referralSource"
                  id="referral-source"
                  class="form-control"
                >
                  <option value="">Select source...</option>
                  <option value="Community Sensitizations">Community Sensitizations</option>
                  <option value="Facebook">Facebook</option>
                  <option value="Friend">Friend</option>
                  <option value="IEC Material">IEC Material</option>
                  <option value="Instagram">Instagram</option>
                  <option value="News Papers">News Papers</option>
                  <option value="NGO/CSO/Partners">NGO/CSO/Partners</option>
                  <option value="Radio">Radio</option>
                  <option value="Relative/Family Member">Relative/Family Member</option>
                  <option value="School">School</option>
                  <option value="Television">Television</option>
                  <option value="WhatsApp">WhatsApp</option>
                  <option value="Word of Mouth">Word of Mouth</option>
                  <option value="Other">Other</option>
                </select>
              </div>
            </div>
            <div class="form-actions">
              <BaseButton variant="secondary" @click="goToStep(3)">Back</BaseButton>
              <div>
                <BaseButton variant="secondary" @click="skipStep(4)">Skip</BaseButton>
                <BaseButton type="submit">Next</BaseButton>
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
                <div class="review-item review-item-full">
                  <div class="review-label">Categories</div>
                  <div class="review-value">
                    <div v-if="formData.step4.categories.length > 0" class="category-tags">
                      <span v-for="category in formData.step4.categories" :key="category" class="category-tag">
                        {{ category }}
                      </span>
                    </div>
                    <span v-else>N/A</span>
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
                <div class="review-item">
                  <div class="review-label">Justice System State</div>
                  <div class="review-value">
                    {{ formData.step4.justiceSystemState || "N/A" }}
                  </div>
                </div>
                <div class="review-item">
                  <div class="review-label">General Assessment</div>
                  <div class="review-value">
                    {{ formData.step4.generalAssessment || "N/A" }}
                  </div>
                </div>
                <div class="review-item">
                  <div class="review-label">Services Offered</div>
                  <div class="review-value">
                    {{ formData.step4.servicesOffered || "N/A" }}
                  </div>
                </div>
                <div class="review-item">
                  <div class="review-label">Referral Source</div>
                  <div class="review-value">
                    {{ formData.step4.referralSource || "N/A" }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="form-actions">
            <BaseButton variant="secondary" @click="goToStep(4)">Back</BaseButton>
            <BaseButton @click="submitCase">Create Case</BaseButton>
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
            <!-- AI Mode Selector -->
            <div class="ai-mode-row">
              <label class="ai-mode-label">Mode</label>
              <select v-model="aiMode" class="ai-mode-select ai-mode-select--elevated">
                <option value="transcription">Transcription</option>
                <option value="translation">Translation</option>
                <option value="ner">NER</option>
                <option value="summary">Case Summary</option>
                <option value="qa">QA Analysis</option>
              </select>
            </div>
            <!-- Audio Upload (AI Panel) -->
            <div v-if="aiMode === 'transcription'" class="ai-preview-section">
              <div class="ai-preview-section-title">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" stroke="currentColor" stroke-width="2"/>
                  <path d="M19 10v2a7 7 0 0 1-14 0v-2" stroke="currentColor" stroke-width="2"/>
                </svg>
                Upload Audio
              </div>
              <div 
                class="ai-audio-upload"
                :class="{ 'has-file': audioFile, 'drag-over': isDragOver }"
                @drop="onAudioDrop"
                @dragover.prevent="isDragOver = true"
                @dragleave.prevent="isDragOver = false"
                @dragenter.prevent
              >
                <input 
                  ref="audioFileInput"
                  type="file" 
                  accept="audio/*" 
                  @change="onAudioUpload" 
                  style="display: none;"
                />
                
                <div v-if="!audioFile" class="upload-placeholder">
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" stroke="currentColor" stroke-width="2"/>
                    <path d="M19 10v2a7 7 0 0 1-14 0v-2" stroke="currentColor" stroke-width="2"/>
                  </svg>
                  <div class="upload-text">
                    <span class="upload-title">Drop audio file here</span>
                    <span class="upload-subtitle">or click to browse</span>
                  </div>
                  <button type="button" class="upload-btn" @click="$refs.audioFileInput.click()">
                    Choose File
                  </button>
                </div>
                
                <div v-else class="audio-file-info">
                  <div class="audio-icon">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M9 18V5l12-2v13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                      <circle cx="6" cy="18" r="3" stroke="currentColor" stroke-width="2"/>
                      <circle cx="18" cy="16" r="3" stroke="currentColor" stroke-width="2"/>
                    </svg>
                  </div>
                  <div class="audio-details">
                    <div class="audio-name">{{ audioFile.name || 'Audio file' }}</div>
                    <div class="audio-meta">{{ formatFileSize(audioFile.size) }} • {{ audioDuration }}s</div>
                  </div>
                  <button type="button" class="remove-audio-btn" @click="removeAudio" title="Remove audio">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M18 6L6 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                      <path d="M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                  </button>
                </div>
              </div>
            </div>

            <!-- Transcription Output -->
            <div v-if="aiMode === 'transcription' && audioTranscription" class="ai-preview-section">
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
            
            <!-- Translation Input/Output -->
            <div v-if="aiMode === 'translation'" class="ai-preview-section">
              <div class="ai-preview-section-title">Translate Text</div>
              <textarea v-model="translationInput" class="form-control" rows="4" placeholder="Enter text to translate..."></textarea>
              <div class="ai-action-row">
                <button class="btn btn--primary btn--sm" @click="runTranslation">Translate</button>
              </div>
              <div v-if="translationOutput" class="ai-io-output">{{ translationOutput }}</div>
            </div>

            <!-- NER Input/Output -->
            <div v-if="aiMode === 'ner'" class="ai-preview-section">
              <div class="ai-preview-section-title">Named Entity Recognition</div>
              <textarea v-model="nerInput" class="form-control" rows="4" placeholder="Enter text for entity extraction..."></textarea>
              <div class="ai-action-row">
                <button class="btn btn--primary btn--sm" @click="runNER">Extract Entities</button>
              </div>
              <div v-if="nerOutput && nerOutput.length" class="ner-output">
                <div v-for="(ent, idx) in nerOutput" :key="idx" class="ner-chip">
                  <span class="ent-text">{{ ent.text }}</span>
                  <span class="ent-label">{{ ent.label }}</span>
                </div>
              </div>
            </div>

            <!-- Case Summary Section -->
            <div v-if="aiMode === 'summary'" class="ai-preview-section">
              <div class="ai-preview-section-title">Case Summary</div>
              <div class="summary-textarea">
                <textarea class="form-control" rows="6" v-model="caseSummaryText" placeholder="Summary will appear here..."></textarea>
              </div>
            </div>

            <!-- QA Analysis -->
            <div v-if="aiMode === 'qa'" class="ai-preview-section">
              <div class="ai-preview-section-title">QA Analysis</div>
              <div class="qa-grid">
                <div class="qa-card">
                  <div class="qa-card-title">Call Quality</div>
                  <div class="qa-score">—</div>
                </div>
                <div class="qa-card">
                  <div class="qa-card-title">Compliance</div>
                  <div class="qa-score">—</div>
                </div>
                <div class="qa-card">
                  <div class="qa-card-title">Empathy</div>
                  <div class="qa-score">—</div>
                </div>
                <div class="qa-card qa-card-full">
                  <div class="qa-card-title">Notes</div>
                  <div class="qa-notes">QA insights will appear here when available.</div>
                </div>
              </div>
            </div>
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

    <!-- Client Modal -->
    <div v-if="clientModalOpen" class="simple-modal">
      <div class="simple-modal-content client-modal-large">
        <div class="simple-modal-header">
          <h3>New Client</h3>
          <span class="simple-modal-close" @click="closeClientModal">×</span>
        </div>
        
        <div class="simple-modal-body">
          <!-- Show existing clients -->
          <div v-if="formData.step2.clients.length > 0" class="existing-clients">
            <h4>Added Clients:</h4>
            <div v-for="(client, index) in formData.step2.clients" :key="index" class="client-display">
              <span>{{ client.name }} ({{ client.age }} {{ client.sex }})</span>
              <button @click="removeClient(index)" class="remove-btn">Remove</button>
            </div>
          </div>
          
          <!-- Multi-step Client Form -->
          <div class="add-client-form">
            <h4>Add New Client:</h4>
            
            <!-- Progress Steps -->
            <div class="form-steps">
              <div class="step-indicator">
                <div v-for="(step, index) in clientSteps" :key="index" 
                     :class="['step', { 
                       active: currentClientStep === index, 
                       completed: currentClientStep > index,
                       future: currentClientStep < index
                     }]">
                  <span class="step-number">
                    <span>{{ index + 1 }}</span>
                  </span>
                  <span class="step-title">{{ step.title }}</span>
                </div>
              </div>
            </div>
            
            <!-- Step Content -->
            <div class="step-content">
              <!-- Step 1: Basic Information -->
              <div v-if="currentClientStep === 0" class="form-step">
                <div class="form-fields">
                  <div class="field-group">
                    <label>Client's Name *</label>
                    <input v-model="clientForm.name" type="text" placeholder="Enter Client's Names" />
                  </div>
                  
                  <div class="field-group">
                    <label>Age</label>
                    <input v-model="clientForm.age" type="number" placeholder="Enter age" />
                  </div>
                  
                  <div class="field-group">
                    <label>DOB</label>
                    <input v-model="clientForm.dob" type="date" />
                  </div>
                  
                  <div class="field-group">
                    <label>Age Group</label>
                    <select v-model="clientForm.ageGroup">
                      <option value="">Select Age Group</option>
                      <option value="0-5">0-5 years</option>
                      <option value="6-12">6-12 years</option>
                      <option value="13-17">13-17 years</option>
                      <option value="18-25">18-25 years</option>
                      <option value="26-35">26-35 years</option>
                      <option value="36-50">36-50 years</option>
                      <option value="51+">51+ years</option>
                    </select>
                  </div>
                  
                  <div class="field-group">
                    <label>Location</label>
                    <select v-model="clientForm.location">
                      <option value="">Select Location</option>
                      <option value="Nairobi">Nairobi</option>
                      <option value="Mombasa">Mombasa</option>
                      <option value="Kisumu">Kisumu</option>
                      <option value="Nakuru">Nakuru</option>
                      <option value="Eldoret">Eldoret</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>
                  
                  <div class="field-group">
                    <label>Sex</label>
                    <select v-model="clientForm.sex">
                      <option value="">Select Gender</option>
                      <option value="female">Female</option>
                      <option value="male">Male</option>
                      <option value="non-binary">Non-binary</option>
                      <option value="other">Other</option>
                    </select>
                  </div>
                </div>
              </div>
              
              <!-- Step 2: Contact & Identity -->
              <div v-if="currentClientStep === 1" class="form-step">
                <div class="form-fields">
                  <div class="field-group">
                    <label>Nearest Landmark</label>
                    <input v-model="clientForm.landmark" type="text" placeholder="Enter Nearest Landmark" />
                  </div>
                  
                  <div class="field-group">
                    <label>Nationality</label>
                    <select v-model="clientForm.nationality">
                      <option value="">Select Nationality</option>
                      <option value="Kenyan">Kenyan</option>
                      <option value="Ugandan">Ugandan</option>
                      <option value="Tanzanian">Tanzanian</option>
                      <option value="Somali">Somali</option>
                      <option value="South Sudanese">South Sudanese</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>
                  
                  <div class="field-group">
                    <label>ID Type</label>
                    <select v-model="clientForm.idType">
                      <option value="">Select ID Type</option>
                      <option value="National ID">National ID</option>
                      <option value="Passport">Passport</option>
                      <option value="Birth Certificate">Birth Certificate</option>
                      <option value="Refugee ID">Refugee ID</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>
                  
                  <div class="field-group">
                    <label>ID Number</label>
                    <input v-model="clientForm.idNumber" type="text" placeholder="Enter Reporter's ID Number" />
                  </div>
                  
                  <div class="field-group">
                    <label>Language</label>
                    <select v-model="clientForm.language">
                      <option value="">Select Language</option>
                      <option value="English">English</option>
                      <option value="Kiswahili">Kiswahili</option>
                      <option value="Luo">Luo</option>
                      <option value="Kikuyu">Kikuyu</option>
                      <option value="Luhya">Luhya</option>
                      <option value="Kalenjin">Kalenjin</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>
                  
                  <div class="field-group">
                    <label>Is the Client a Refugee?</label>
                    <div class="radio-group">
                      <label class="radio-option">
                        <input type="radio" v-model="clientForm.isRefugee" value="yes" />
                        <span class="radio-indicator"></span>
                        <span class="radio-label">Yes</span>
                      </label>
                      <label class="radio-option">
                        <input type="radio" v-model="clientForm.isRefugee" value="no" />
                        <span class="radio-indicator"></span>
                        <span class="radio-label">No</span>
                      </label>
                      <label class="radio-option">
                        <input type="radio" v-model="clientForm.isRefugee" value="unknown" />
                        <span class="radio-indicator"></span>
                        <span class="radio-label">Unknown</span>
                      </label>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Step 3: Contact Information -->
              <div v-if="currentClientStep === 2" class="form-step">
                <div class="form-fields">
                  <div class="field-group">
                    <label>Tribe</label>
                    <select v-model="clientForm.tribe">
                      <option value="">Select Tribe</option>
                      <option value="Kikuyu">Kikuyu</option>
                      <option value="Luhya">Luhya</option>
                      <option value="Kalenjin">Kalenjin</option>
                      <option value="Luo">Luo</option>
                      <option value="Kamba">Kamba</option>
                      <option value="Kisii">Kisii</option>
                      <option value="Meru">Meru</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>
                  
                  <div class="field-group">
                    <label>Phone Number</label>
                    <input v-model="clientForm.phone" type="tel" placeholder="Enter Reporter's Phone Number" />
                  </div>
                  
                  <div class="field-group">
                    <label>Alternative Phone</label>
                    <input v-model="clientForm.alternativePhone" type="tel" placeholder="Enter Alternate Phone Number" />
                  </div>
                  
                  <div class="field-group">
                    <label>Email</label>
                    <input v-model="clientForm.email" type="email" placeholder="Enter Reporter's Email Address" />
                  </div>
                  
                  <div class="field-group">
                    <label>Reporter's Relationship with Client</label>
                    <select v-model="clientForm.relationship">
                      <option value="">Select Relationship</option>
                      <option value="Parent">Parent</option>
                      <option value="Guardian">Guardian</option>
                      <option value="Sibling">Sibling</option>
                      <option value="Relative">Relative</option>
                      <option value="Friend">Friend</option>
                      <option value="Neighbor">Neighbor</option>
                      <option value="Teacher">Teacher</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>
                  
                  <div class="field-group">
                    <label>Relationship Comment</label>
                    <textarea v-model="clientForm.relationshipComment" placeholder="Enter Comments about the relationship" rows="3"></textarea>
                  </div>
                </div>
              </div>
              
              <!-- Step 4: Household & Background -->
              <div v-if="currentClientStep === 3" class="form-step">
                <div class="form-fields">
                  <div class="field-group">
                    <label>Number of Adults in Household</label>
                    <input v-model="clientForm.adultsInHousehold" type="number" placeholder="Enter number" />
                  </div>
                  
                  <div class="field-group">
                    <label>Household Type</label>
                    <select v-model="clientForm.householdType">
                      <option value="">Select Household Type</option>
                      <option value="Nuclear">Nuclear Family</option>
                      <option value="Extended">Extended Family</option>
                      <option value="Single Parent">Single Parent</option>
                      <option value="Child Headed">Child Headed</option>
                      <option value="Institutional">Institutional</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>
                  
                  <div class="field-group">
                    <label>Head of Household Occupation</label>
                    <select v-model="clientForm.headOccupation">
                      <option value="">Select Employment Status</option>
                      <option value="Employed">Employed</option>
                      <option value="Self-employed">Self-employed</option>
                      <option value="Unemployed">Unemployed</option>
                      <option value="Student">Student</option>
                      <option value="Retired">Retired</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>
                  
                  <div class="field-group">
                    <label>Parent/Guardian's Name</label>
                    <input v-model="clientForm.parentGuardianName" type="text" placeholder="Enter name" />
                  </div>
                  
                  <div class="field-group">
                    <label>Parent/Guardian's Marital Status</label>
                    <select v-model="clientForm.parentMaritalStatus">
                      <option value="">Select Marital Status</option>
                      <option value="Single">Single</option>
                      <option value="Married">Married</option>
                      <option value="Divorced">Divorced</option>
                      <option value="Widowed">Widowed</option>
                      <option value="Separated">Separated</option>
                    </select>
                  </div>
                  
                  <div class="field-group">
                    <label>Parent/Guardian's Identification Number</label>
                    <input v-model="clientForm.parentIdNumber" type="text" placeholder="Enter ID number" />
                  </div>
                </div>
              </div>
              
              <!-- Step 5: Health & Status -->
              <div v-if="currentClientStep === 4" class="form-step">
                <div class="form-fields">
                  <div class="field-group">
                    <label>Client's Health Status</label>
                    <select v-model="clientForm.healthStatus">
                      <option value="">Select Health Status</option>
                      <option value="Good">Good</option>
                      <option value="Fair">Fair</option>
                      <option value="Poor">Poor</option>
                      <option value="Unknown">Unknown</option>
                    </select>
                  </div>
                  
                  <div class="field-group">
                    <label>Client's HIV Status</label>
                    <select v-model="clientForm.hivStatus">
                      <option value="">Select HIV Status</option>
                      <option value="Positive">Positive</option>
                      <option value="Negative">Negative</option>
                      <option value="Unknown">Unknown</option>
                      <option value="Not Tested">Not Tested</option>
                    </select>
                  </div>
                  
                  <div class="field-group">
                    <label>Client's Marital Status</label>
                    <select v-model="clientForm.maritalStatus">
                      <option value="">Select Marital Status</option>
                      <option value="Single">Single</option>
                      <option value="Married">Married</option>
                      <option value="Divorced">Divorced</option>
                      <option value="Widowed">Widowed</option>
                      <option value="Separated">Separated</option>
                    </select>
                  </div>
                  
                  <div class="field-group">
                    <label>Is the Client Attending School?</label>
                    <div class="radio-group">
                      <label class="radio-option">
                        <input type="radio" v-model="clientForm.attendingSchool" value="yes" />
                        <span class="radio-indicator"></span>
                        <span class="radio-label">Yes</span>
                      </label>
                      <label class="radio-option">
                        <input type="radio" v-model="clientForm.attendingSchool" value="no" />
                        <span class="radio-indicator"></span>
                        <span class="radio-label">No</span>
                      </label>
                      <label class="radio-option">
                        <input type="radio" v-model="clientForm.attendingSchool" value="unknown" />
                        <span class="radio-indicator"></span>
                        <span class="radio-label">Unknown</span>
                      </label>
                    </div>
                    
                    <!-- Conditional field for school name when "Yes" is selected -->
                    <div v-if="clientForm.attendingSchool === 'yes'" class="conditional-field">
                      <label>School Name</label>
                      <input 
                        v-model="clientForm.schoolName" 
                        type="text" 
                        placeholder="Enter school name"
                        class="school-input"
                      />
                      
                      <label>School Level</label>
                      <select v-model="clientForm.schoolLevel">
                        <option value="">Select School Level</option>
                        <option value="nursery">Nursery</option>
                        <option value="primary">Primary</option>
                        <option value="secondary">Secondary</option>
                        <option value="tertiary">Tertiary</option>
                      </select>
                      
                      <label>School Address</label>
                      <input 
                        v-model="clientForm.schoolAddress" 
                        type="text" 
                        placeholder="Enter school address"
                      />
                      
                      <label>School Type</label>
                      <select v-model="clientForm.schoolType">
                        <option value="">Select School Type</option>
                        <option value="government-boarding">Government Boarding</option>
                        <option value="government-day">Government Day</option>
                        <option value="government-day-boarding">Government Day and Boarding</option>
                        <option value="none">None</option>
                        <option value="private-boarding">Private Boarding</option>
                        <option value="private-day">Private Day</option>
                        <option value="private-day-boarding">Private Day and Boarding</option>
                      </select>
                      
                      <label>School Attendance</label>
                      <select v-model="clientForm.schoolAttendance">
                        <option value="">Select Attendance Status</option>
                        <option value="regular">Regular</option>
                        <option value="irregular">Irregular</option>
                        <option value="absent">Frequently Absent</option>
                        <option value="dropped">Dropped Out</option>
                        <option value="unknown">Unknown</option>
                      </select>
                    </div>
                  </div>
                  
                  <div class="field-group">
                    <label>Is the Client Disabled?</label>
                    <div class="radio-group">
                      <label class="radio-option">
                        <input type="radio" v-model="clientForm.isDisabled" value="yes" />
                        <span class="radio-indicator"></span>
                        <span class="radio-label">Yes</span>
                      </label>
                      <label class="radio-option">
                        <input type="radio" v-model="clientForm.isDisabled" value="no" />
                        <span class="radio-indicator"></span>
                        <span class="radio-label">No</span>
                      </label>
                      <label class="radio-option">
                        <input type="radio" v-model="clientForm.isDisabled" value="unknown" />
                        <span class="radio-indicator"></span>
                        <span class="radio-label">Unknown</span>
                      </label>
                    </div>
                    
                    <!-- Conditional field for disability details when "Yes" is selected -->
                    <div v-if="clientForm.isDisabled === 'yes'" class="conditional-field">
                      <label>Disability</label>
                      <select v-model="clientForm.disability">
                        <option value="">Select Type of Disability</option>
                        <option value="physical">Physical Disability</option>
                        <option value="visual">Visual Impairment</option>
                        <option value="hearing">Hearing Impairment</option>
                        <option value="speech">Speech Impairment</option>
                        <option value="intellectual">Intellectual Disability</option>
                        <option value="developmental">Developmental Disability</option>
                        <option value="mental-health">Mental Health Condition</option>
                        <option value="multiple">Multiple Disabilities</option>
                        <option value="other">Other</option>
                      </select>
                    </div>
                  </div>
                  
                  <div class="field-group">
                    <label>Is the Client Referred for Special Services?</label>
                    <div class="radio-group">
                      <label class="radio-option">
                        <input type="radio" v-model="clientForm.specialServicesReferred" value="yes" />
                        <span class="radio-indicator"></span>
                        <span class="radio-label">Yes</span>
                      </label>
                      <label class="radio-option">
                        <input type="radio" v-model="clientForm.specialServicesReferred" value="no" />
                        <span class="radio-indicator"></span>
                        <span class="radio-label">No</span>
                      </label>
                      <label class="radio-option">
                        <input type="radio" v-model="clientForm.specialServicesReferred" value="unknown" />
                        <span class="radio-indicator"></span>
                        <span class="radio-label">Unknown</span>
                      </label>
                    </div>
                    
                    <!-- Conditional field for special services referral when "Yes" is selected -->
                    <div v-if="clientForm.specialServicesReferred === 'yes'" class="conditional-field">
                      <label>Special Services Referral</label>
                      <div class="multi-select-dropdown">
                        <div class="dropdown-trigger" @click="toggleSpecialServicesDropdown">
                          <span class="selected-text">
                            {{ getSelectedSpecialServicesText() || 'Select Special Services Referral' }}
                          </span>
                          <svg class="dropdown-arrow" :class="{ 'open': showSpecialServicesDropdown }" width="12" height="12" viewBox="0 0 12 12">
                            <path d="M6 8L2 4h8L6 8z" fill="currentColor"/>
                          </svg>
                        </div>
                        
                        <div v-if="showSpecialServicesDropdown" class="dropdown-options">
                          <div class="search-box">
                            <input 
                              v-model="specialServicesSearch" 
                              type="text" 
                              placeholder="Search services..."
                              @click.stop
                            />
                          </div>
                          
                          <div class="options-list">
                            <label 
                              v-for="service in filteredSpecialServices" 
                              :key="service.value"
                              class="checkbox-option"
                            >
                              <input 
                                type="checkbox" 
                                :value="service.value"
                                v-model="clientForm.specialServicesReferral"
                                @click.stop
                              />
                              <span class="checkbox-label">{{ service.label }}</span>
                            </label>
                          </div>
                          
                          <div class="pagination-info">
                            <span>{{ filteredSpecialServices.length }} of {{ specialServicesOptions.length }}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Step Navigation -->
            <div class="step-navigation">
              <button v-if="currentClientStep > 0" @click="prevClientStep" type="button" class="btn btn--secondary">Previous</button>
              <button v-if="currentClientStep < clientSteps.length - 1" @click="nextClientStep" type="button" class="btn btn--primary">Next</button>
              <button v-if="currentClientStep === clientSteps.length - 1" @click="addClient" type="button" class="btn btn--primary">Create</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Perpetrator Modal -->
    <div v-if="perpetratorModalOpen" class="simple-modal">
      <div class="simple-modal-content perpetrator-modal-large">
        <div class="simple-modal-header">
          <h3>New Perpetrator</h3>
          <span class="simple-modal-close" @click="closePerpetratorModal">×</span>
        </div>
        
        <div class="simple-modal-body">
          <!-- Show existing perpetrators -->
          <div v-if="formData.step2.perpetrators.length > 0" class="existing-perpetrators">
            <h4>Added Perpetrators:</h4>
            <div v-for="(perpetrator, index) in formData.step2.perpetrators" :key="index" class="perpetrator-display">
              <span>{{ perpetrator.name }} ({{ perpetrator.age }} {{ perpetrator.sex }})</span>
              <button @click="removePerpetrator(index)" class="remove-btn">Remove</button>
            </div>
          </div>
          
          <!-- Multi-step Perpetrator Form -->
          <div class="add-perpetrator-form">
            <h4>Add New Perpetrator:</h4>
            
            <!-- Progress Steps -->
            <div class="form-steps">
              <div class="step-indicator">
                <div v-for="(step, index) in perpetratorSteps" :key="index" 
                     :class="['step', { 
                       active: currentPerpetratorStep === index, 
                       completed: currentPerpetratorStep > index,
                       future: currentPerpetratorStep < index
                     }]">
                  <span class="step-number">
                    <span>{{ index + 1 }}</span>
                  </span>
                  <span class="step-title">{{ step.title }}</span>
                </div>
              </div>
            </div>
            
            <!-- Step Content -->
            <div class="step-content">
              <!-- Step 1: Basic Information -->
              <div v-if="currentPerpetratorStep === 0" class="form-step">
                <div class="form-fields">
                  <div class="field-group">
                    <label>Perpetrator's Name *</label>
                    <input v-model="perpetratorForm.name" type="text" placeholder="Enter Perpetrator's Names" />
                  </div>
                  
                  <div class="field-group">
                    <label>Age</label>
                    <input v-model="perpetratorForm.age" type="number" placeholder="Enter age" />
                  </div>
                  
                  <div class="field-group">
                    <label>DOB</label>
                    <input v-model="perpetratorForm.dob" type="date" />
                  </div>
                  
                  <div class="field-group">
                    <label>Age Group</label>
                    <select v-model="perpetratorForm.ageGroup">
                      <option value="">Select Age Group</option>
                      <option value="0-5">0-5 years</option>
                      <option value="6-12">6-12 years</option>
                      <option value="13-17">13-17 years</option>
                      <option value="18-25">18-25 years</option>
                      <option value="26-35">26-35 years</option>
                      <option value="36-50">36-50 years</option>
                      <option value="51+">51+ years</option>
                    </select>
                  </div>
                  
                  <div class="field-group">
                    <label>Location</label>
                    <select v-model="perpetratorForm.location">
                      <option value="">Select Location</option>
                      <option value="Nairobi">Nairobi</option>
                      <option value="Mombasa">Mombasa</option>
                      <option value="Kisumu">Kisumu</option>
                      <option value="Nakuru">Nakuru</option>
                      <option value="Eldoret">Eldoret</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>
                  
                  <div class="field-group">
                    <label>Sex</label>
                    <select v-model="perpetratorForm.sex">
                      <option value="">Select Gender</option>
                      <option value="female">Female</option>
                      <option value="male">Male</option>
                      <option value="non-binary">Non-binary</option>
                      <option value="other">Other</option>
                    </select>
                  </div>
                </div>
              </div>
              
              <!-- Step 2: Identity & Contact -->
              <div v-if="currentPerpetratorStep === 1" class="form-step">
                <div class="form-fields">
                  <div class="field-group">
                    <label>Nearest Landmark</label>
                    <input v-model="perpetratorForm.landmark" type="text" placeholder="Enter Nearest Landmark" />
                  </div>
                  
                  <div class="field-group">
                    <label>Nationality</label>
                    <select v-model="perpetratorForm.nationality">
                      <option value="">Select Nationality</option>
                      <option value="Kenyan">Kenyan</option>
                      <option value="Ugandan">Ugandan</option>
                      <option value="Tanzanian">Tanzanian</option>
                      <option value="Somali">Somali</option>
                      <option value="South Sudanese">South Sudanese</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>
                  
                  <div class="field-group">
                    <label>ID Type</label>
                    <select v-model="perpetratorForm.idType">
                      <option value="">Select ID Type</option>
                      <option value="National ID">National ID</option>
                      <option value="Passport">Passport</option>
                      <option value="Birth Certificate">Birth Certificate</option>
                      <option value="Refugee ID">Refugee ID</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>
                  
                  <div class="field-group">
                    <label>ID Number</label>
                    <input v-model="perpetratorForm.idNumber" type="text" placeholder="Enter Reporter's ID Number" />
                  </div>
                  
                  <div class="field-group">
                    <label>Language</label>
                    <select v-model="perpetratorForm.language">
                      <option value="">Select Language</option>
                      <option value="English">English</option>
                      <option value="Kiswahili">Kiswahili</option>
                      <option value="Luo">Luo</option>
                      <option value="Kikuyu">Kikuyu</option>
                      <option value="Luhya">Luhya</option>
                      <option value="Kalenjin">Kalenjin</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>
                  
                  <div class="field-group">
                    <label>Is the Perpetrator a Refugee?</label>
                    <div class="radio-group">
                      <label class="radio-option">
                        <input type="radio" v-model="perpetratorForm.isRefugee" value="yes" />
                        <span class="radio-indicator"></span>
                        <span class="radio-label">Yes</span>
                      </label>
                      <label class="radio-option">
                        <input type="radio" v-model="perpetratorForm.isRefugee" value="no" />
                        <span class="radio-indicator"></span>
                        <span class="radio-label">No</span>
                      </label>
                      <label class="radio-option">
                        <input type="radio" v-model="perpetratorForm.isRefugee" value="unknown" />
                        <span class="radio-indicator"></span>
                        <span class="radio-label">Unknown</span>
                      </label>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Step 3: Contact & Background -->
              <div v-if="currentPerpetratorStep === 2" class="form-step">
                <div class="form-fields">
                  <div class="field-group">
                    <label>Tribe</label>
                    <select v-model="perpetratorForm.tribe">
                      <option value="">Select Tribe</option>
                      <option value="Kikuyu">Kikuyu</option>
                      <option value="Luhya">Luhya</option>
                      <option value="Kalenjin">Kalenjin</option>
                      <option value="Luo">Luo</option>
                      <option value="Kamba">Kamba</option>
                      <option value="Kisii">Kisii</option>
                      <option value="Meru">Meru</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>
                  
                  <div class="field-group">
                    <label>Phone Number</label>
                    <input v-model="perpetratorForm.phone" type="tel" placeholder="Enter Reporter's Phone Number" />
                  </div>
                  
                  <div class="field-group">
                    <label>Alternative Phone</label>
                    <input v-model="perpetratorForm.alternativePhone" type="tel" placeholder="Enter Alternate Phone Number" />
                  </div>
                  
                  <div class="field-group">
                    <label>Email</label>
                    <input v-model="perpetratorForm.email" type="email" placeholder="Enter Reporter's Email Address" />
                  </div>
                  
                  <div class="field-group">
                    <label>Relationship with Client?</label>
                    <select v-model="perpetratorForm.relationship">
                      <option value="">Select Relationship</option>
                      <option value="Parent">Parent</option>
                      <option value="Guardian">Guardian</option>
                      <option value="Sibling">Sibling</option>
                      <option value="Relative">Relative</option>
                      <option value="Friend">Friend</option>
                      <option value="Neighbor">Neighbor</option>
                      <option value="Teacher">Teacher</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>
                  
                  <div class="field-group">
                    <label>Shares Home with Client?</label>
                    <div class="radio-group">
                      <label class="radio-option">
                        <input type="radio" v-model="perpetratorForm.sharesHome" value="yes" />
                        <span class="radio-indicator"></span>
                        <span class="radio-label">Yes</span>
                      </label>
                      <label class="radio-option">
                        <input type="radio" v-model="perpetratorForm.sharesHome" value="no" />
                        <span class="radio-indicator"></span>
                        <span class="radio-label">No</span>
                      </label>
                      <label class="radio-option">
                        <input type="radio" v-model="perpetratorForm.sharesHome" value="unknown" />
                        <span class="radio-indicator"></span>
                        <span class="radio-label">Unknown</span>
                      </label>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Step 4: Status & Details -->
              <div v-if="currentPerpetratorStep === 3" class="form-step">
                <div class="form-fields">
                  <div class="field-group">
                    <label>Health Status</label>
                    <select v-model="perpetratorForm.healthStatus">
                      <option value="">Select Health Status</option>
                      <option value="Good">Good</option>
                      <option value="Fair">Fair</option>
                      <option value="Poor">Poor</option>
                      <option value="Unknown">Unknown</option>
                    </select>
                  </div>
                  
                  <div class="field-group">
                    <label>Perpetrator's Profession</label>
                    <select v-model="perpetratorForm.profession">
                      <option value="">Select Work Status</option>
                      <option value="Employed">Employed</option>
                      <option value="Self-employed">Self-employed</option>
                      <option value="Unemployed">Unemployed</option>
                      <option value="Student">Student</option>
                      <option value="Retired">Retired</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>
                  
                  <div class="field-group">
                    <label>Perpetrator's Marital Status</label>
                    <select v-model="perpetratorForm.maritalStatus">
                      <option value="">Select Marital Status</option>
                      <option value="Single">Single</option>
                      <option value="Married">Married</option>
                      <option value="Divorced">Divorced</option>
                      <option value="Widowed">Widowed</option>
                      <option value="Separated">Separated</option>
                    </select>
                  </div>
                  
                  <div class="field-group">
                    <label>Perpetrator's Guardian's Name</label>
                    <input v-model="perpetratorForm.guardianName" type="text" placeholder="Enter Perpetrator's Guardian Name" />
                  </div>
                  
                  <div class="field-group">
                    <label>Additional Details</label>
                    <textarea v-model="perpetratorForm.additionalDetails" placeholder="Enter Additional Details" rows="4"></textarea>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Step Navigation -->
            <div class="step-navigation">
              <button v-if="currentPerpetratorStep > 0" @click="prevPerpetratorStep" type="button" class="btn btn--secondary">Previous</button>
              <button v-if="currentPerpetratorStep < perpetratorSteps.length - 1" @click="nextPerpetratorStep" type="button" class="btn btn--primary">Next</button>
              <button v-if="currentPerpetratorStep === perpetratorSteps.length - 1" @click="addPerpetrator" type="button" class="btn btn--primary">Create</button>
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
import BaseButton from '@/components/base/BaseButton.vue'
import BaseInput from '@/components/base/BaseInput.vue'
import BaseTextarea from '@/components/base/BaseTextarea.vue'
import BaseSelect from '@/components/base/BaseSelect.vue'
import { useTranscriptionsStore } from '@/stores/transcriptionsStore'
import { useCaseStore } from '@/stores/cases'

const router = useRouter()
const transcriptionsStore = useTranscriptionsStore()
const casesStore = useCaseStore()

// State
const currentStep = ref(1)
const totalSteps = 5
const isAIEnabled = ref(true)
const searchQuery = ref('')
const debouncedQuery = ref('')
let debounceTimer = null
const selectedReporter = ref(null)
const selectedCategory = ref('')
const clientModalOpen = ref(false)
const perpetratorModalOpen = ref(false)

// Special Services dropdown state
const showSpecialServicesDropdown = ref(false)
const specialServicesSearch = ref('')

// Case Category dropdown state
const showCategoryDropdown = ref(false)
const isCategoryPanelExpanded = ref(false)

// Case Categories with hierarchical structure
const caseCategories = ref([
  {
    value: 'abuse',
    label: 'Abuse',
    expanded: false,
    children: [
      { value: 'child-exploitation', label: 'Child Exploitation' },
      { value: 'child-neglect', label: 'Child Neglect' },
      { value: 'economic-violence', label: 'Economic Violence' },
      { value: 'emotional-psychological-abuse', label: 'Emotional & Psychological Abuse' },
      { value: 'harmful-traditional-practices', label: 'Harmful Traditional Practices' },
      { value: 'murder', label: 'Murder' },
      { value: 'online-sexual-abuse-violence', label: 'Online Sexual Abuse & Violence' },
      { value: 'others', label: 'Others' },
      { value: 'physical-violence', label: 'Physical Violence' },
      { value: 'sexual-violence', label: 'Sexual Violence' }
    ]
  },
  {
    value: 'counseling',
    label: 'Counseling',
    expanded: false,
    children: [
      { value: 'family-counseling', label: 'Family Counseling' },
      { value: 'individual-counseling', label: 'Individual Counseling' },
      { value: 'group-counseling', label: 'Group Counseling' },
      { value: 'crisis-counseling', label: 'Crisis Counseling' }
    ]
  },
  {
    value: 'distress',
    label: 'Distress',
    expanded: false,
    children: [
      { value: 'emotional-distress', label: 'Emotional Distress' },
      { value: 'mental-health-crisis', label: 'Mental Health Crisis' },
      { value: 'suicidal-ideation', label: 'Suicidal Ideation' },
      { value: 'panic-attacks', label: 'Panic Attacks' }
    ]
  },
  {
    value: 'fraud-theft',
    label: 'Fraud/Theft',
    expanded: false,
    children: [
      { value: 'identity-theft', label: 'Identity Theft' },
      { value: 'financial-fraud', label: 'Financial Fraud' },
      { value: 'cyber-crime', label: 'Cyber Crime' },
      { value: 'property-theft', label: 'Property Theft' }
    ]
  },
  {
    value: 'health',
    label: 'Health',
    expanded: false,
    children: [
      { value: 'medical-emergency', label: 'Medical Emergency' },
      { value: 'mental-health', label: 'Mental Health' },
      { value: 'substance-abuse', label: 'Substance Abuse' },
      { value: 'healthcare-access', label: 'Healthcare Access' }
    ]
  },
  {
    value: 'information-inquiry',
    label: 'Information Inquiry',
    expanded: false,
    children: [
      { value: 'general-information', label: 'General Information' },
      { value: 'service-inquiry', label: 'Service Inquiry' },
      { value: 'resource-request', label: 'Resource Request' },
      { value: 'referral-inquiry', label: 'Referral Inquiry' }
    ]
  }
])

// Special Services options
const specialServicesOptions = ref([
  { value: 'assistant-commissioner-ees', label: 'Assistant Commissioner EES' },
  { value: 'childrens-home', label: 'Children\'s Home' },
  { value: 'commissioner-ees', label: 'Commissioner EES' },
  { value: 'foreign-affairs', label: 'Foreign Affairs' },
  { value: 'gbv-shelters', label: 'GBV Shelters' },
  { value: 'head-eeu', label: 'Head EEU' },
  { value: 'head-ieu', label: 'Head IEU' },
  { value: 'health-facility', label: 'Health Facility' },
  { value: 'labour-officer', label: 'Labour Officer (LO)' },
  { value: 'labour-support-officer', label: 'Labour Support Officer (LSO)' },
  { value: 'lcs-lcs', label: 'LCs LCs' },
  { value: 'legal-aid', label: 'Legal Aid' },
  { value: 'local-recruitment-agency', label: 'Local Recruitment Agency/Associations' },
  { value: 'mia-uganda-police', label: 'MIA (Uganda Police Force)' },
  { value: 'ngos-csos-cbos', label: 'NGOs/CSOs/CBOs' },
  { value: 'other', label: 'Other' },
  { value: 'police', label: 'Police' },
  { value: 'probation-office', label: 'Probation Office' },
  { value: 'special-needs-facility', label: 'Special Needs Facility' }
])

// Audio recording state
const isRecording = ref(false)
const recordingTime = ref(0)
const audioFile = ref(null)
const audioDuration = ref(0)
const isPlaying = ref(false)
const audioTranscription = ref('')
const isTranscriptionCorrect = ref(false)
const isDragOver = ref(false)
let mediaRecorder = null
let recordingInterval = null

// AI panel mode and IO state
const aiMode = ref('transcription')
const translationInput = ref('')
const translationOutput = ref('')
const nerInput = ref('')
const nerOutput = ref([])
const caseSummaryText = ref('')

// AI state
const caseSummary = ref({
  riskLevel: 'low',
  urgency: 'Normal',
  keyConcerns: [],
  analysis: ''
})
const aiInsights = ref([])
const recommendations = ref([])

// Client and Perpetrator forms
const currentClientStep = ref(0)

// Client form steps
const clientSteps = ref([
  { title: 'Basic Info' },
  { title: 'Identity' },
  { title: 'Contact' },
  { title: 'Household' },
  { title: 'Health & Status' }
])

const clientForm = reactive({
  name: '',
  age: '',
  dob: '',
  ageGroup: '',
  location: '',
  sex: '',
  landmark: '',
  nationality: '',
  idType: '',
  idNumber: '',
  language: '',
  isRefugee: '',
  tribe: '',
  phone: '',
  alternativePhone: '',
  email: '',
  relationship: '',
  relationshipComment: '',
  adultsInHousehold: '',
  householdType: '',
  headOccupation: '',
  parentGuardianName: '',
  parentMaritalStatus: '',
  parentIdNumber: '',
  healthStatus: '',
  hivStatus: '',
  maritalStatus: '',
  attendingSchool: '',
  previousSchool: '',
  schoolName: '',
  schoolLevel: '',
  schoolAddress: '',
  schoolType: '',
  schoolAttendance: '',
  isDisabled: '',
  disability: '',
  specialServicesReferred: '',
  specialServicesReferral: []
})

// Perpetrator form steps
const perpetratorSteps = ref([
  { title: 'Basic Info' },
  { title: 'Identity' },
  { title: 'Contact' },
  { title: 'Status & Details' }
])

const currentPerpetratorStep = ref(0)

const perpetratorForm = reactive({
  name: '',
  age: '',
  dob: '',
  ageGroup: '',
  location: '',
  sex: '',
  landmark: '',
  nationality: '',
  idType: '',
  idNumber: '',
  language: '',
  isRefugee: '',
  tribe: '',
  phone: '',
  alternativePhone: '',
  email: '',
  relationship: '',
  sharesHome: '',
  healthStatus: '',
  profession: '',
  maritalStatus: '',
  guardianName: '',
  additionalDetails: ''
})

// Using real Pinia cases store (mock removed)

// Form data
const formData = reactive({
  step2: {
    name: '',
    age: '',
    dob: '',
    ageGroup: '',
    gender: '',
    location: '',
    nearestLandmark: '',
    nationality: '',
    language: '',
    tribe: '',
    phone: '',
    altPhone: '',
    email: '',
    idType: '',
    idNumber: '',
    isRefugee: '',
    isClient: null,
    clients: [],
    perpetrators: []
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
    clientPassportNumber: '',
    selectedClient: null,
    categories: [],
    priority: '',
    status: '',
    escalatedTo: '',
    justiceSystemState: '',
    generalAssessment: '',
    servicesOffered: '',
    referralSource: ''
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

// Labor Department - Client Search
const clientSearchResults = ref([])
const hasSearched = ref(false)

// Mock client database for demonstration
const mockClients = [
  { id: 1, name: 'John Doe', passportNumber: 'A1234567', nationality: 'Kenyan', phone: '254700123456' },
  { id: 2, name: 'Jane Smith', passportNumber: 'B2345678', nationality: 'Ugandan', phone: '254700234567' },
  { id: 3, name: 'Ahmed Hassan', passportNumber: 'C3456789', nationality: 'Somali', phone: '254700345678' },
  { id: 4, name: 'Maria Garcia', passportNumber: 'D4567890', nationality: 'Spanish', phone: '254700456789' }
]

const searchClientByPassport = () => {
  if (!formData.step4.clientPassportNumber.trim()) {
    alert('Please enter a passport number')
    return
  }
  
  hasSearched.value = true
  
  // Search in mock database
  const results = mockClients.filter(client => 
    client.passportNumber.toLowerCase().includes(formData.step4.clientPassportNumber.toLowerCase())
  )
  
  clientSearchResults.value = results
  
  if (results.length === 0) {
    console.log('No client found with passport:', formData.step4.clientPassportNumber)
  }
}

const selectClient = (client) => {
  formData.step4.selectedClient = client
  console.log('Selected client:', client)
  
  // Clear search results
  clientSearchResults.value = []
  hasSearched.value = false
  
  // You could also populate some form fields with client data
  // formData.step2.name = client.name
  // formData.step2.phone = client.phone
}

const createNewClient = () => {
  // Open the client modal for creating a new client
  clientModalOpen.value = true
}

watch(searchQuery, (val) => {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => { 
    debouncedQuery.value = val.trim() 
  }, 200)
})

const filteredContacts = computed(() => {
  if (!debouncedQuery.value) return []

  const text = debouncedQuery.value.toString().trim().toLowerCase()
  const digits = text.replace(/\D+/g, '')

  const getField = (row, keyDef, fallbacks = []) => {
    // Attempt by mapping
    if (keyDef && Array.isArray(keyDef) && keyDef.length > 0) {
      const k = keyDef[0]
      const v = row?.[k]
      if (v != null) return v
    }
    // Attempt by common keys
    for (const k of fallbacks) {
      const v = row?.[k]
      if (v != null) return v
    }
    return ''
  }

  const k = casesStore.cases_k || {}
  const nameMap = k.reporter_fullname || k.created_by || k.name
  const phoneMap = k.reporter_phone || k.phone

  const nameFallbacks = ['reporter_fullname', 'reporter_name', 'created_by', 'name', 'full_name']
  const phoneFallbacks = ['reporter_phone', 'phone', 'contact_phone', 'reporterPhone']

  const list = Array.isArray(casesStore.cases) ? casesStore.cases : []

  return list.filter((row) => {
    const rawName = getField(row, nameMap, nameFallbacks)
    const rawPhone = getField(row, phoneMap, phoneFallbacks)

    const name = rawName == null ? '' : String(rawName).toLowerCase()
    const phone = rawPhone == null ? '' : String(rawPhone)
    const phoneDigits = phone.replace(/\D+/g, '')

    const byName = text ? name.includes(text) : false
    const byPhone = digits ? phoneDigits.includes(digits) : false
    return byName || byPhone
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

// Client and Perpetrator Methods
const handleClientSelection = () => {
  if (formData.step2.isClient === true) {
    // If reporter is a client, clear any existing clients
    formData.step2.clients = []
  } else if (formData.step2.isClient === false) {
    // If reporter is not a client, open the client modal
    clientModalOpen.value = true
  }
}

const openClientModal = () => {
  clientModalOpen.value = true
}

const closeClientModal = () => {
  clientModalOpen.value = false
  resetClientForm()
}

const resetClientForm = () => {
  Object.keys(clientForm).forEach(key => {
    clientForm[key] = ''
  })
  currentClientStep.value = 0
}

const nextClientStep = () => {
  if (currentClientStep.value < clientSteps.value.length - 1) {
    currentClientStep.value++
  }
}

const prevClientStep = () => {
  if (currentClientStep.value > 0) {
    currentClientStep.value--
  }
}

const addClient = () => {
  console.log('addClient called', clientForm)
  
  if (!clientForm.name.trim()) {
    alert('Please enter client name')
    return
  }
  
  console.log('Adding client:', clientForm)
  formData.step2.clients.push({ ...clientForm })
  console.log('Clients after add:', formData.step2.clients)
  
  resetClientForm()
  closeClientModal()
  
  console.log('Client added successfully')
}

const removeClient = (index) => {
  formData.step2.clients.splice(index, 1)
}

// Special Services Dropdown Methods
const toggleSpecialServicesDropdown = () => {
  showSpecialServicesDropdown.value = !showSpecialServicesDropdown.value
}

const filteredSpecialServices = computed(() => {
  if (!specialServicesSearch.value) return specialServicesOptions.value
  
  return specialServicesOptions.value.filter(service =>
    service.label.toLowerCase().includes(specialServicesSearch.value.toLowerCase())
  )
})

const getSelectedSpecialServicesText = () => {
  if (!clientForm.specialServicesReferral || clientForm.specialServicesReferral.length === 0) {
    return ''
  }
  
  if (clientForm.specialServicesReferral.length === 1) {
    const selected = specialServicesOptions.value.find(opt => opt.value === clientForm.specialServicesReferral[0])
    return selected ? selected.label : ''
  }
  
  return `${clientForm.specialServicesReferral.length} services selected`
}

// Case Category Dropdown Methods
const toggleCategoryDropdown = () => {
  showCategoryDropdown.value = !showCategoryDropdown.value
}

const toggleCategory = (category) => {
  category.expanded = !category.expanded
}

const expandCategoryPanel = () => {
  isCategoryPanelExpanded.value = !isCategoryPanelExpanded.value
  // This could open a modal or expand the panel further
  console.log('Expand category panel:', isCategoryPanelExpanded.value)
}

const openPerpetratorModal = () => {
  perpetratorModalOpen.value = true
}

const closePerpetratorModal = () => {
  perpetratorModalOpen.value = false
  resetPerpetratorForm()
}

const resetPerpetratorForm = () => {
  Object.keys(perpetratorForm).forEach(key => {
    perpetratorForm[key] = ''
  })
  currentPerpetratorStep.value = 0
}

const nextPerpetratorStep = () => {
  if (currentPerpetratorStep.value < perpetratorSteps.value.length - 1) {
    currentPerpetratorStep.value++
  }
}

const prevPerpetratorStep = () => {
  if (currentPerpetratorStep.value > 0) {
    currentPerpetratorStep.value--
  }
}

const addPerpetrator = () => {
  if (!perpetratorForm.name.trim()) {
    alert('Please enter perpetrator name')
    return
  }
  
  formData.step2.perpetrators.push({ ...perpetratorForm })
  resetPerpetratorForm()
}

const removePerpetrator = (index) => {
  formData.step2.perpetrators.splice(index, 1)
}

const addCategory = () => {
  if (selectedCategory.value && !formData.step4.categories.includes(selectedCategory.value)) {
    formData.step4.categories.push(selectedCategory.value)
    selectedCategory.value = ''
  }
}

const removeCategory = (category) => {
  const index = formData.step4.categories.indexOf(category)
  if (index > -1) {
    formData.step4.categories.splice(index, 1)
  }
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

// Handle drag and drop
const onAudioDrop = async (event) => {
  event.preventDefault()
  isDragOver.value = false
  
  const files = event.dataTransfer.files
  if (files.length > 0) {
    const file = files[0]
    if (file.type.startsWith('audio/')) {
      await onAudioUpload({ target: { files: [file] } })
    }
  }
}

// Simple mocked AI runners (replace with backend calls later)
const runTranslation = () => {
  translationOutput.value = translationInput.value
    ? `Translated: ${translationInput.value}`
    : ''
}

const runNER = () => {
  if (!nerInput.value) { nerOutput.value = []; return }
  nerOutput.value = nerInput.value
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 12)
    .map(t => ({ text: t.replace(/[^\w-]/g,''), label: t[0] === t[0]?.toUpperCase() ? 'PERSON' : 'MISC' }))
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

const progressWidth = computed(() => {
  const completeCount = [1,2,3,4].filter(s => stepStatus(s) === 'completed' || currentStep.value > s).length
  const totalSegments = totalSteps - 1
  const percent = Math.min(100, Math.round((completeCount / totalSegments) * 100))
  return percent + '%'
})

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

// Determine step completion/error status for timeline colors
const stepStatus = (step) => {
  switch (step) {
    case 1:
      return selectedReporter.value ? 'completed' : 'idle'
    case 2:
      // basic validation: name and phone
      if (!formData.step2.name || !formData.step2.phone) return 'error'
      return 'completed'
    case 3:
      if (!formData.step3.narrative) return 'error'
      return 'completed'
    case 4:
      if (!formData.step4.priority || !formData.step4.status || formData.step4.categories.length === 0) return 'error'
      return 'completed'
    default:
      return 'idle'
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
onMounted(async () => {
  if (isAIEnabled.value) {
    generateAIInsights()
  }
  // Ensure cases are available for search suggestions
  try { await casesStore.listCases({ src: 'call' }) } catch (e) {}

  // Dev fallback: if no data loaded, seed a few demo contacts so filtering can be verified live
  if (import.meta.env.DEV && (!Array.isArray(casesStore.cases) || casesStore.cases.length === 0)) {
    // Use object rows with friendly keys; computed uses fallbacks so this works
    casesStore.cases = [
      { id: 1, reporter_fullname: 'Amira Karim', reporter_phone: '254700112233', reporter_age: 28, reporter_sex: 'Female', reporter_location: 'Nairobi', dt: 1641081600 },
      { id: 2, reporter_fullname: 'Brian Newton', reporter_phone: '254711223344', reporter_age: 34, reporter_sex: 'Male', reporter_location: 'Nakuru', dt: 1640908800 },
      { id: 3, reporter_fullname: 'Susan Kirigwa', reporter_phone: '254722334455', reporter_age: 45, reporter_sex: 'Female', reporter_location: 'Narok', dt: 1640995200 },
      { id: 4, reporter_fullname: 'Ivan Somondi', reporter_phone: '254733445566', reporter_age: 16, reporter_sex: 'Male', reporter_location: 'Narok County', dt: 1640995200 }
    ]
    casesStore.cases_k = {
      id: ['id'],
      reporter_fullname: ['reporter_fullname'],
      reporter_phone: ['reporter_phone'],
      reporter_age: ['reporter_age'],
      reporter_sex: ['reporter_sex'],
      reporter_location: ['reporter_location'],
      dt: ['dt']
    }
  }
  // update CSS var for vertical progress fill
  updateStepCSSVar()
})

watch(currentStep, () => updateStepCSSVar())

const updateStepCSSVar = () => {
  // compute progress ratio 0..1 based on current step index
  const ratio = (currentStep.value - 1) / (totalSteps - 1)
  const root = document.querySelector('.progress-steps')
  if (root) {
    root.style.setProperty('--progress-ratio', String(ratio))
  }
}
</script>

<style scoped>
/* Ensure consistent typography and polished AI panel UI */
.case-creation-page {
  min-height: 0;
  overflow: auto;
}

/* Layout: main form + AI panel */
.case-container {
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
}
@media (min-width: 1100px) {
  .case-container { grid-template-columns: 1fr 360px; }
}

.main-form-container {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 20px;
  box-shadow: var(--shadow-sm);
  padding: 16px;
}

.case-header { display:flex; align-items:center; justify-content:space-between; gap: 12px; }
.case-header h1 { margin:0; font-size: 26px; font-weight: 900; letter-spacing: -0.2px; color: var(--text-color); }
.case-header h1::after { content: ""; display:block; width: 48px; height: 3px; border-radius: 2px; background: var(--color-primary); margin-top: 6px; }
.case-header p { margin:6px 0 0; color: var(--color-muted); font-size: 13px; }

/* Stepper */
.progress-container { padding: 6px 0 12px; }
.progress-steps { position:relative; display:flex; justify-content:space-between; align-items:flex-start; gap: 24px; padding-top: 28px; }
.progress-step { display:flex; flex-direction:column; align-items:center; gap:6px; cursor:pointer; flex:1; }
.progress-step .step-circle { font-weight:800; font-size:14px; color: var(--color-muted); line-height:1; }
.progress-step .step-label { font-weight:700; color: var(--color-muted); font-size:12px; text-align:center; }
.progress-step.active .step-circle { color: var(--text-color); }
.progress-step.active .step-label { color: var(--text-color); }
.progress-step.completed .step-circle { color: #fff; background: var(--success-color); width:24px; height:24px; border-radius:999px; display:flex; align-items:center; justify-content:center; }
.progress-step.completed .step-label { color: var(--success-color); }
.progress-step.error .step-circle { color: var(--color-primary); background: transparent; }
.progress-step.error .step-label { color: var(--color-primary); }
.progress-steps::before { content: none; }
.progress-steps::after { content: none; }

/* Search / contacts */
.search-row { display:flex; gap: 8px; align-items:center; }
.search-box { position:relative; display:flex; align-items:center; gap:8px; border:1px solid var(--color-border); border-radius: 12px; padding: 8px 10px; background: var(--color-surface); color: var(--text-color); width: 180px; }
.new-reporter-btn { height: 36px; }
.search-input { border:0; outline:0; width:100%; background: transparent; font-size:13px; color: var(--text-color); }
.search-empty { margin-top: 8px; background: var(--color-surface); border:1px solid var(--color-border); border-radius: 12px; padding:10px; color: var(--color-muted); }

.create-reporter-btn { border:1px solid var(--color-border); background: var(--color-surface); padding: 8px 12px; border-radius: 12px; font-weight:600; cursor:pointer; }
.create-reporter-btn:hover { transform: translateY(-1px); }

.contacts-list { display:flex; flex-direction:column; gap:8px; margin-top: 8px; }
.contact-item { display:flex; align-items:center; gap:12px; border:1px solid var(--color-border); border-radius: 14px; padding: 12px; background: var(--color-surface); cursor:pointer; transition: background .15s ease, border-color .15s ease; }
.contact-item:hover { background: var(--color-surface-muted); }
.contact-item.selected { outline: 2px solid color-mix(in oklab, var(--color-primary) 28%, transparent); }
.contact-avatar { width:40px; height:40px; border-radius:999px; display:flex; align-items:center; justify-content:center; background: var(--color-surface-muted); font-weight:700; }
.contact-details { flex:1; display:grid; grid-template-columns: 1fr auto; align-items:center; column-gap: 12px; min-width: 0; }
.contact-main-info { display:flex; align-items:center; gap:10px; min-width:0; }
.contact-name { font-weight:700; font-size: 16px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.contact-phone { color: var(--color-muted); font-size: 12px; white-space: nowrap; }
.contact-meta-info { display:flex; align-items:center; gap:10px; flex-wrap: wrap; justify-content:flex-end; }
.contact-tags { display:flex; gap:6px; flex-wrap:wrap; max-width: 420px; }
.contact-tag { border:1px solid var(--color-border); border-radius:999px; padding:2px 8px; font-size: 12px; }
.contact-tag.location { background: var(--color-surface-muted); }
.contact-select-indicator { color: var(--color-muted); }

/* Forms */
.case-form { display:flex; flex-direction:column; gap: 14px; }
.form-row { display:grid; grid-template-columns: 1fr; gap: 12px; }
@media (min-width: 780px) { .form-row { grid-template-columns: 1fr 1fr; } }
.form-actions { display:flex; justify-content:space-between; align-items:center; gap:10px; margin-top: 10px; }

/* AI upload dropzone */
.ai-audio-upload { 
  border: 2px dashed var(--color-border); 
  border-radius: 12px; 
  padding: 20px; 
  background: var(--color-surface); 
  text-align: center; 
  position: relative;
  transition: all 0.2s ease;
  cursor: pointer;
}

.ai-audio-upload:hover {
  border-color: var(--color-primary);
  background: color-mix(in oklab, var(--color-primary) 2%, transparent);
}

.ai-audio-upload.drag-over {
  border-color: var(--color-primary);
  background: color-mix(in oklab, var(--color-primary) 8%, transparent);
  transform: scale(1.02);
}

.ai-audio-upload.has-file {
  border-style: solid;
  border-color: var(--success-color);
  background: color-mix(in oklab, var(--success-color) 4%, transparent);
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.upload-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.upload-title {
  font-weight: 600;
  color: var(--text-color);
  font-size: 14px;
}

.upload-subtitle {
  color: var(--color-muted);
  font-size: 12px;
}

.upload-btn {
  background: var(--color-primary);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.upload-btn:hover {
  background: color-mix(in oklab, var(--color-primary) 80%, black);
  transform: translateY(-1px);
}

/* AI mode controls and IO */
.ai-mode-row { display:flex; align-items:center; gap:12px; }
.ai-mode-label { font-weight:700; color: var(--text-color); }
.ai-mode-select { padding:10px 14px; border:1px solid var(--color-border); border-radius:14px; background:#fff; color:#111; font-weight:600; font-family: 'Inter', system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, 'Helvetica Neue', Arial, 'Noto Sans', 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol'; }
.ai-mode-select--elevated { box-shadow: 0 1px 2px rgba(0,0,0,0.06), 0 4px 10px rgba(0,0,0,0.04); }
.ai-mode-select:focus { outline: none; box-shadow: 0 0 0 3px color-mix(in oklab, var(--color-primary) 20%, white); }
.ai-mode-select option { font-weight:600; }
.ai-action-row { margin-top:8px; }
.ai-io-output { margin-top:10px; padding:12px; border:1px solid var(--color-border); border-radius:12px; background: var(--color-surface); color: var(--text-color); }
.ner-output { display:flex; flex-wrap:wrap; gap:8px; margin-top:10px; }
.ner-chip { display:inline-flex; gap:6px; padding:6px 10px; border:1px solid var(--color-border); border-radius:999px; background: var(--color-surface); }
.ner-chip .ent-text { font-weight:600; }
.ner-chip .ent-label { text-transform:uppercase; font-size:12px; color: var(--color-muted); }
.summary-textarea .form-control { width:100%; }

/* QA cards */
.qa-grid { display:grid; grid-template-columns: repeat(3, 1fr); gap:12px; }
.qa-card { border:1px solid var(--color-border); border-radius:14px; background: var(--color-surface); padding:12px; }
.qa-card-title { font-weight:700; color: var(--text-color); margin-bottom:6px; }
.qa-score { font-size:22px; font-weight:800; color: var(--text-color); }
.qa-card-full { grid-column: 1 / -1; }
.qa-notes { color: var(--color-muted); }

.audio-file-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px;
  background: var(--color-surface);
  border-radius: 8px;
  border: 1px solid var(--color-border);
}

.audio-icon {
  color: var(--color-primary);
  flex-shrink: 0;
}

.audio-details {
  flex: 1;
  text-align: left;
}

.audio-name {
  font-weight: 600;
  color: var(--text-color);
  font-size: 14px;
  margin-bottom: 2px;
}

.audio-meta {
  color: var(--color-muted);
  font-size: 12px;
}

.remove-audio-btn {
  background: none;
  border: none;
  color: var(--color-muted);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.remove-audio-btn:hover {
  background: var(--color-surface-muted);
  color: var(--color-danger, #dc2626);
}

/* Review styles */
.review-sections { display:flex; flex-direction:column; gap:12px; }
.review-section { border:1px solid var(--color-border); border-radius: 14px; background: var(--color-surface); }
.section-header { display:flex; align-items:center; justify-content:space-between; padding: 10px 12px; border-bottom:1px solid var(--color-border); }
.review-content { padding: 10px 12px; display:grid; grid-template-columns: 1fr 1fr; gap:10px; }
.review-item-full { grid-column: 1 / -1; }
.review-label { font-weight:600; color: var(--color-muted); }
.review-value { color: var(--text-color); }

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
  font-weight: 800;
  font-size: 16px;
  color: var(--text-color);
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
  font-weight: 700;
  margin-bottom: 12px;
  color: var(--text-color);
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

.ai-suggestion { display:flex; gap:10px; padding:12px; border:1px solid var(--color-border); border-radius:12px; background: var(--color-surface); margin-bottom:8px; }
.suggestion-icon { font-size:16px; }
.suggestion-content { flex:1; }
.suggestion-title { font-weight:700; color: var(--text-color); margin-bottom:4px; }
.suggestion-text { color: var(--color-muted); font-size:13px; margin-bottom:8px; }
.btn-suggestion { background: var(--color-primary); color:#fff; border:0; padding:6px 12px; border-radius:8px; font-size:12px; font-weight:600; cursor:pointer; }

/* Ensure ancestors don't block child overflow scrolling */
.case-container {
  min-height: 0;
}

.main-form-container {
  min-height: 0;
  overflow: visible;
}

.back-button { margin-bottom: 12px; }

/* Category tags */
.category-tags-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.category-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  min-height: 32px;
  padding: 4px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background: var(--color-surface);
}

.category-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  background: var(--color-primary);
  color: white;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 600;
}

.tag-remove {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 14px;
  line-height: 1;
  padding: 0;
  margin-left: 4px;
}

.tag-remove:hover {
  color: rgba(255, 255, 255, 0.8);
}

/* Main Form Display Sections */
.clients-section,
.perpetrators-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.clients-list,
.perpetrators-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.client-item,
.perpetrator-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  background: var(--color-surface-muted);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
}

.client-info,
.perpetrator-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.client-name,
.perpetrator-name {
  font-weight: 600;
  color: var(--color-fg);
  font-size: 14px;
}

.client-details,
.perpetrator-details {
  font-size: 12px;
  color: var(--color-muted);
}

.remove-client,
.remove-perpetrator {
  background: var(--color-danger);
  color: white;
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.remove-client:hover,
.remove-perpetrator:hover {
  background: color-mix(in oklab, var(--color-danger) 80%, black);
  transform: scale(1.1);
}

.empty-state {
  padding: 20px;
  text-align: center;
  color: var(--color-muted);
  font-style: italic;
  background: var(--color-surface-muted);
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-md);
}

.empty-state p {
  margin: 0;
  font-size: 14px;
}

.add-client-btn,
.add-perpetrator-btn {
  align-self: flex-start;
  margin-top: 8px;
}

/* Simple Modal Styles - Using Application Theme */
.simple-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.simple-modal-content {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  max-width: 90%;
  max-height: 90%;
  overflow-y: auto;
  width: 600px;
}

.client-modal-large,
.perpetrator-modal-large {
  width: 800px;
  max-width: 95vw;
}

/* Multi-step Form Styles */
.form-steps {
  margin-bottom: 24px;
  padding: 20px 0;
  border-top: 1px solid #e5e5e5;
  border-bottom: 1px solid #e5e5e5;
}

.step-indicator {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  flex: 1;
  position: relative;
}

.step:not(:last-child)::after {
  content: '';
  position: absolute;
  top: 16px;
  left: 50%;
  right: -50%;
  height: 2px;
  background: #e5e5e5;
  z-index: 1;
}

.step.completed:not(:last-child)::after {
  background: #28a745;
}

.step.active:not(:last-child)::after {
  background: #28a745;
}

.step-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
  position: relative;
  z-index: 2;
}

/* Completed steps - Green background with white numbers */
.step.completed .step-number {
  background: #28a745;
  color: white;
}

/* Active steps - Green */
.step.active .step-number {
  background: #28a745;
  color: white;
}

/* Future steps - Grey */
.step.future .step-number {
  background: #e5e5e5;
  color: #666666;
}

.step-title {
  font-size: 12px;
  font-weight: 500;
  text-align: center;
  margin-top: 4px;
}

/* Completed step titles - Green */
.step.completed .step-title {
  color: #28a745;
  font-weight: 600;
}

/* Active step titles - Green */
.step.active .step-title {
  color: #28a745;
  font-weight: 600;
}

/* Future step titles - Grey */
.step.future .step-title {
  color: #666666;
}

.step-content {
  min-height: 400px;
}

.form-step {
  padding: 20px 0;
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateX(20px); }
  to { opacity: 1; transform: translateX(0); }
}

.step-navigation {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--color-border);
}

.simple-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid var(--color-border);
}

.simple-modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: var(--color-fg);
}

.simple-modal-close {
  font-size: 24px;
  cursor: pointer;
  color: var(--color-muted);
  padding: 5px;
  border-radius: var(--radius-sm);
  transition: all 0.2s;
}

.simple-modal-close:hover {
  background: var(--color-surface-muted);
  color: var(--color-fg);
}

.simple-modal-body {
  padding: 20px;
}

/* Form Styles */
.form-fields {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

.field-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.field-group label {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text);
  margin-bottom: 4px;
}

.field-group input,
.field-group select,
.field-group textarea {
  padding: 12px 16px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 14px;
  background: var(--color-background);
  color: var(--color-text);
  transition: all 0.2s ease;
}

.field-group input:focus,
.field-group select:focus,
.field-group textarea:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(var(--color-primary-rgb), 0.1);
}

.field-group textarea {
  resize: vertical;
  min-height: 80px;
}

.radio-options {
  display: flex;
  gap: 16px;
  margin-top: 4px;
}

.radio-options label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 400;
  cursor: pointer;
}

.radio-options input[type="radio"] {
  width: 16px;
  height: 16px;
  margin: 0;
}


.field-group label {
  font-weight: 600;
  color: var(--color-fg);
  font-size: 14px;
}

.field-group input,
.field-group select,
.field-group textarea {
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 14px;
  background: var(--color-surface);
  color: var(--color-fg);
  transition: border-color 0.2s ease;
}

.field-group input:focus,
.field-group select:focus,
.field-group textarea:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px color-mix(in oklab, var(--color-primary) 20%, transparent);
}

.field-group textarea {
  resize: vertical;
  min-height: 60px;
}

/* Radio Options */
.radio-options {
  display: flex;
  gap: 16px;
  margin-top: 8px;
}

.radio-options label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-weight: 500;
}

.radio-options input[type="radio"] {
  margin: 0;
  cursor: pointer;
}

/* Existing Items Display */
.existing-clients,
.existing-perpetrators {
  margin-bottom: 20px;
  padding: 16px;
  background: var(--color-surface-muted);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
}

.existing-clients h4,
.existing-perpetrators h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--color-fg);
}

.client-display,
.perpetrator-display {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  margin-bottom: 8px;
}

.client-display span,
.perpetrator-display span {
  font-size: 14px;
  color: var(--color-fg);
  font-weight: 500;
}

.remove-btn {
  background: var(--color-danger);
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: var(--radius-sm);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.remove-btn:hover {
  background: color-mix(in oklab, var(--color-danger) 80%, black);
  transform: translateY(-1px);
}

/* Form Actions */
.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--color-border);
}

.add-btn {
  background: var(--color-primary);
  color: white;
  border: 1px solid var(--color-primary);
  padding: 10px 20px;
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.add-btn:hover {
  background: var(--color-primary-hover);
  border-color: var(--color-primary-hover);
  transform: translateY(-1px);
}

.cancel-btn {
  background: var(--color-surface);
  color: var(--color-fg);
  border: 1px solid var(--color-border);
  padding: 10px 20px;
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cancel-btn:hover {
  background: var(--color-surface-muted);
  transform: translateY(-1px);
}

/* Responsive */
@media (max-width: 768px) {
  .form-fields {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .simple-modal-content {
    width: 95%;
    margin: 10px;
  }
  
  .client-modal-large,
  .perpetrator-modal-large {
    width: 95%;
    max-width: 95vw;
  }
  
  .radio-options {
    flex-direction: column;
    gap: 8px;
  }
}

/* Labor Department - Passport Search Styles */
.labor-search-section {
  margin-top: 20px;
  padding: 20px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
}

.passport-search-container {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.passport-input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid var(--color-border, #d1d5db);
  border-radius: var(--radius-md, 6px);
  font-size: 14px;
  background: var(--color-background, #ffffff);
  color: var(--color-text, #1f2937);
  transition: all 0.2s ease;
}

.passport-input:hover {
  border-color: var(--color-primary, #8b4513);
  background: var(--color-background, #ffffff);
  color: var(--color-text, #1f2937);
}

.passport-input:focus {
  outline: none;
  border-color: var(--color-primary, #8b4513);
  background: var(--color-background, #ffffff);
  color: var(--color-text, #1f2937);
  box-shadow: 0 0 0 2px rgba(139, 69, 19, 0.1);
}

.passport-input::placeholder {
  color: var(--color-text-secondary, #6b7280);
  opacity: 1;
}

.search-btn {
  background: var(--color-primary);
  color: white;
  border: 1px solid var(--color-primary);
  padding: 12px 24px;
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.search-btn:hover {
  background: var(--color-primary-hover, #7a3a0f);
  border-color: var(--color-primary-hover, #7a3a0f);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(139, 69, 19, 0.2);
}

.search-results {
  margin-top: 16px;
}

.search-results h4 {
  margin-bottom: 12px;
  color: var(--color-text);
  font-size: 16px;
  font-weight: 600;
}

.client-result {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  margin-bottom: 8px;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  transition: all 0.2s ease;
}

.client-result:hover {
  border-color: var(--color-primary);
  box-shadow: 0 2px 8px rgba(var(--color-primary-rgb), 0.1);
}

.client-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.client-info strong {
  color: var(--color-text);
  font-size: 14px;
  font-weight: 600;
}

.client-details {
  color: var(--color-text-secondary);
  font-size: 12px;
}

.select-client-btn {
  padding: 8px 16px;
  background: var(--color-success);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.select-client-btn:hover {
  background: var(--color-success-dark);
}

.no-results {
  margin-top: 16px;
  padding: 16px;
  text-align: center;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
}

.no-results p {
  margin-bottom: 12px;
  color: var(--color-text-secondary);
  font-size: 14px;
}

.create-client-btn {
  background: var(--color-primary);
  color: white;
  border: 1px solid var(--color-primary);
  padding: 10px 20px;
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.create-client-btn:hover {
  background: var(--color-primary-hover, #7a3a0f);
  border-color: var(--color-primary-hover, #7a3a0f);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(139, 69, 19, 0.2);
}

/* Conditional Field Styling */
.conditional-field {
  margin-top: 16px;
  padding: 16px;
  background: var(--color-surface-muted, #f8f9fa);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: var(--radius-md, 6px);
  animation: slideDown 0.3s ease-out;
}

.conditional-field label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text, #1f2937);
}

.school-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--color-border, #d1d5db);
  border-radius: var(--radius-md, 6px);
  font-size: 14px;
  background: var(--color-background, #ffffff);
  color: var(--color-text, #1f2937);
  transition: all 0.2s ease;
}

.school-input:focus {
  outline: none;
  border-color: var(--color-primary, #8b4513);
  box-shadow: 0 0 0 2px rgba(139, 69, 19, 0.1);
}

.school-input::placeholder {
  color: var(--color-text-secondary, #6b7280);
  opacity: 1;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
    max-height: 0;
  }
  to {
    opacity: 1;
    transform: translateY(0);
    max-height: 100px;
  }
}

/* Custom Radio Button Styling */
.radio-options input[type="radio"] {
  width: 16px;
  height: 16px;
  margin: 0;
  cursor: pointer;
  accent-color: var(--color-primary, #8b4513);
}

.radio-options input[type="radio"]:checked {
  accent-color: var(--color-primary, #8b4513);
}

/* Custom radio button styling for better control */
.radio-options label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-weight: 500;
  position: relative;
}

.radio-options label input[type="radio"] {
  appearance: none;
  width: 16px;
  height: 16px;
  border: 2px solid var(--color-border, #d1d5db);
  border-radius: 50%;
  background: var(--color-background, #ffffff);
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.radio-options label input[type="radio"]:checked {
  border-color: var(--color-primary, #8b4513);
  background: var(--color-primary, #8b4513);
}

.radio-options label input[type="radio"]:checked::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: white;
}

/* Button Styles */
.btn {
  padding: 10px 20px;
  border: none;
  border-radius: var(--radius-md, 6px);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn--primary {
  background: var(--color-primary, #8b4513);
  color: white;
  border: 1px solid var(--color-primary, #8b4513);
}

.btn--primary:hover {
  background: var(--color-primary-hover, #7a3a0f);
  border-color: var(--color-primary-hover, #7a3a0f);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(139, 69, 19, 0.2);
}

.btn--secondary {
  background: var(--color-surface, #ffffff);
  color: var(--color-text, #1f2937);
  border: 1px solid var(--color-border, #d1d5db);
}

.btn--secondary:hover {
  background: var(--color-surface-muted, #f8f9fa);
  transform: translateY(-1px);
}

.btn--sm {
  padding: 8px 16px;
  font-size: 12px;
}

/* Multi-Select Dropdown Styles */
.multi-select-dropdown {
  position: relative;
  width: 100%;
}

.dropdown-trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border: 1px solid var(--color-border, #d1d5db);
  border-radius: var(--radius-md, 6px);
  background: var(--color-surface, #ffffff);
  cursor: pointer;
  transition: all 0.2s ease;
}

.dropdown-trigger:hover {
  border-color: var(--color-primary, #8b4513);
}

.selected-text {
  color: var(--color-text, #1f2937);
  flex: 1;
  text-align: left;
}

.dropdown-arrow {
  transition: transform 0.2s ease;
  color: var(--color-text-secondary, #6b7280);
}

.dropdown-arrow.open {
  transform: rotate(180deg);
}

.dropdown-options {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  z-index: 1000;
  background: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #d1d5db);
  border-radius: var(--radius-md, 6px);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  max-height: 300px;
  overflow: hidden;
  margin-top: 4px;
}

.search-box {
  padding: 12px;
  border-bottom: 1px solid var(--color-border, #d1d5db);
}

.search-box input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--color-border, #d1d5db);
  border-radius: var(--radius-sm, 4px);
  font-size: 14px;
  outline: none;
}

.search-box input:focus {
  border-color: var(--color-primary, #8b4513);
  box-shadow: 0 0 0 1px var(--color-primary, #8b4513);
}

.options-list {
  max-height: 200px;
  overflow-y: auto;
}

.checkbox-option {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.checkbox-option:hover {
  background-color: var(--color-surface-hover, #f9fafb);
}

.checkbox-option input[type="checkbox"] {
  margin-right: 12px;
  width: 16px;
  height: 16px;
  accent-color: var(--color-primary, #8b4513);
}

.checkbox-label {
  flex: 1;
  color: var(--color-text, #1f2937);
  font-size: 14px;
  user-select: none;
}

.pagination-info {
  padding: 6px 12px;
  background-color: var(--color-surface-muted, #f3f4f6);
  border-top: 1px solid var(--color-border, #d1d5db);
  font-size: 11px;
  color: var(--color-text-secondary, #6b7280);
  text-align: center;
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

/* Scrollbar styles for options list */
.options-list::-webkit-scrollbar {
  width: 6px;
}

.options-list::-webkit-scrollbar-track {
  background: var(--color-surface-muted, #f3f4f6);
}

.options-list::-webkit-scrollbar-thumb {
  background: var(--color-border, #d1d5db);
  border-radius: 3px;
}

.options-list::-webkit-scrollbar-thumb:hover {
  background: var(--color-text-secondary, #6b7280);
}

/* Hierarchical Category Dropdown Styles */
.hierarchical-dropdown {
  position: relative;
  width: 100%;
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

.hierarchical-dropdown .dropdown-trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  border: 1px solid var(--color-border, #d1d5db);
  border-radius: var(--radius-md, 6px);
  background: var(--color-surface, #ffffff);
  cursor: pointer;
  transition: all 0.2s ease;
  min-height: 36px;
  font-size: 13px;
}

.hierarchical-dropdown .dropdown-trigger:hover {
  border-color: var(--color-primary, #8b4513);
}

.selected-categories {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  flex: 1;
  align-items: center;
}

.category-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 6px;
  background-color: var(--color-primary, #8b4513);
  color: white;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

.tag-remove {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 12px;
  font-weight: bold;
  padding: 0;
  width: 14px;
  height: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.2s ease;
}

.tag-remove:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

.placeholder {
  color: var(--color-text-secondary, #6b7280);
  font-style: italic;
  font-size: 13px;
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

.category-dropdown-panel {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  z-index: 1000;
  background: var(--color-surface, #ffffff);
  border: 1px solid var(--color-border, #d1d5db);
  border-radius: var(--radius-md, 6px);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  max-height: 300px;
  overflow: hidden;
  margin-top: 4px;
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  border-bottom: 1px solid var(--color-border, #d1d5db);
  background-color: var(--color-surface-muted, #f8f9fa);
}

.panel-title {
  font-weight: 600;
  color: var(--color-text, #1f2937);
  font-size: 13px;
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

.expand-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 2px;
  border-radius: 3px;
  transition: background-color 0.2s ease;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.expand-btn:hover {
  background-color: var(--color-surface-hover, #e5e7eb);
}

.expand-btn svg {
  width: 12px;
  height: 12px;
}

.category-tree {
  max-height: 250px;
  overflow-y: auto;
}

.category-item {
  border-bottom: 1px solid var(--color-border-light, #f3f4f6);
}

.category-item:last-child {
  border-bottom: none;
}

.category-row {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  cursor: pointer;
  transition: background-color 0.2s ease;
  position: relative;
}

.category-row:hover {
  background-color: var(--color-surface-hover, #f9fafb);
}

.category-icon {
  margin-right: 6px;
  transition: transform 0.2s ease;
  color: var(--color-text-secondary, #6b7280);
}

.category-icon svg {
  width: 10px;
  height: 10px;
}

.category-item.expanded .category-icon {
  transform: rotate(90deg);
}

.category-name {
  flex: 1;
  color: var(--color-text, #1f2937);
  font-weight: 500;
  font-size: 13px;
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

.category-checkbox {
  margin-left: 8px;
  width: 14px;
  height: 14px;
  accent-color: var(--color-primary, #8b4513);
}

.subcategories {
  background-color: var(--color-surface-muted, #f8f9fa);
  border-left: 2px solid var(--color-primary, #8b4513);
}

.subcategory-item {
  border-bottom: 1px solid var(--color-border-light, #f3f4f6);
}

.subcategory-item:last-child {
  border-bottom: none;
}

.subcategory-row {
  display: flex;
  align-items: center;
  padding: 6px 12px 6px 24px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.subcategory-row:hover {
  background-color: var(--color-surface-hover, #f0f0f0);
}

.subcategory-name {
  flex: 1;
  color: var(--color-text, #1f2937);
  font-size: 12px;
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

/* Scrollbar styles for category tree */
.category-tree::-webkit-scrollbar {
  width: 6px;
}

.category-tree::-webkit-scrollbar-track {
  background: var(--color-surface-muted, #f3f4f6);
}

.category-tree::-webkit-scrollbar-thumb {
  background: var(--color-border, #d1d5db);
  border-radius: 3px;
}

.category-tree::-webkit-scrollbar-thumb:hover {
  background: var(--color-text-secondary, #6b7280);
}
</style>

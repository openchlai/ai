<template>
   <!-- Client Modal -->
    <div v-if="clientModalOpen" class="simple-modal">
      <div class="simple-modal-content client-modal-large">
        <div class="simple-modal-header">
          <h3>New Client</h3>
          <span class="simple-modal-close" @click="closeClientModal">×</span>
        </div>

        <div class="simple-modal-body">
          <!-- Show existing clients -->
          <div
            v-if="formData.step2.clients.length > 0"
            class="existing-clients"
          >
            <h4>Added Clients:</h4>
            <div
              v-for="(client, index) in formData.step2.clients"
              :key="index"
              class="client-display"
            >
              <span>{{ client.name }} ({{ client.age }} {{ client.sex }})</span>
              <button @click="removeClient(index)" class="remove-btn">
                Remove
              </button>
            </div>
          </div>

          <!-- Multi-step Client Form -->
          <div class="add-client-form">
            <h4>Add New Client:</h4>

            <!-- Progress Steps -->
            <div class="form-steps">
              <div class="step-indicator">
                <div
                  v-for="(step, index) in clientSteps"
                  :key="index"
                  :class="[
                    'step',
                    {
                      active: currentClientStep === index,
                      completed: currentClientStep > index,
                      future: currentClientStep < index,
                    },
                  ]"
                >
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
                    <input
                      v-model="clientForm.name"
                      type="text"
                      placeholder="Enter Client's Names"
                    />
                  </div>

                  <div class="field-group">
                    <label>Age</label>
                    <input
                      v-model="clientForm.age"
                      type="number"
                      placeholder="Enter age"
                    />
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
                    <input
                      v-model="clientForm.landmark"
                      type="text"
                      placeholder="Enter Nearest Landmark"
                    />
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
                      <option value="Birth Certificate">
                        Birth Certificate
                      </option>
                      <option value="Refugee ID">Refugee ID</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>

                  <div class="field-group">
                    <label>ID Number</label>
                    <input
                      v-model="clientForm.idNumber"
                      type="text"
                      placeholder="Enter Reporter's ID Number"
                    />
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
                        <input
                          type="radio"
                          v-model="clientForm.isRefugee"
                          value="yes"
                        />
                        <span class="radio-indicator"></span>
                        <span class="radio-label">Yes</span>
                      </label>
                      <label class="radio-option">
                        <input
                          type="radio"
                          v-model="clientForm.isRefugee"
                          value="no"
                        />
                        <span class="radio-indicator"></span>
                        <span class="radio-label">No</span>
                      </label>
                      <label class="radio-option">
                        <input
                          type="radio"
                          v-model="clientForm.isRefugee"
                          value="unknown"
                        />
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
                    <input
                      v-model="clientForm.phone"
                      type="tel"
                      placeholder="Enter Reporter's Phone Number"
                    />
                  </div>

                  <div class="field-group">
                    <label>Alternative Phone</label>
                    <input
                      v-model="clientForm.alternativePhone"
                      type="tel"
                      placeholder="Enter Alternate Phone Number"
                    />
                  </div>

                  <div class="field-group">
                    <label>Email</label>
                    <input
                      v-model="clientForm.email"
                      type="email"
                      placeholder="Enter Reporter's Email Address"
                    />
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
                    <textarea
                      v-model="clientForm.relationshipComment"
                      placeholder="Enter Comments about the relationship"
                      rows="3"
                    ></textarea>
                  </div>
                </div>
              </div>

              <!-- Step 4: Household & Background -->
              <div v-if="currentClientStep === 3" class="form-step">
                <div class="form-fields">
                  <div class="field-group">
                    <label>Number of Adults in Household</label>
                    <input
                      v-model="clientForm.adultsInHousehold"
                      type="number"
                      placeholder="Enter number"
                    />
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
                    <input
                      v-model="clientForm.parentGuardianName"
                      type="text"
                      placeholder="Enter name"
                    />
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
                    <input
                      v-model="clientForm.parentIdNumber"
                      type="text"
                      placeholder="Enter ID number"
                    />
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
                        <input
                          type="radio"
                          v-model="clientForm.attendingSchool"
                          value="yes"
                        />
                        <span class="radio-indicator"></span>
                        <span class="radio-label">Yes</span>
                      </label>
                      <label class="radio-option">
                        <input
                          type="radio"
                          v-model="clientForm.attendingSchool"
                          value="no"
                        />
                        <span class="radio-indicator"></span>
                        <span class="radio-label">No</span>
                      </label>
                      <label class="radio-option">
                        <input
                          type="radio"
                          v-model="clientForm.attendingSchool"
                          value="unknown"
                        />
                        <span class="radio-indicator"></span>
                        <span class="radio-label">Unknown</span>
                      </label>
                    </div>

                    <!-- Conditional field for school name when "Yes" is selected -->
                    <div
                      v-if="clientForm.attendingSchool === 'yes'"
                      class="conditional-field"
                    >
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
                        <option value="government-boarding">
                          Government Boarding
                        </option>
                        <option value="government-day">Government Day</option>
                        <option value="government-day-boarding">
                          Government Day and Boarding
                        </option>
                        <option value="none">None</option>
                        <option value="private-boarding">
                          Private Boarding
                        </option>
                        <option value="private-day">Private Day</option>
                        <option value="private-day-boarding">
                          Private Day and Boarding
                        </option>
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
                        <input
                          type="radio"
                          v-model="clientForm.isDisabled"
                          value="yes"
                        />
                        <span class="radio-indicator"></span>
                        <span class="radio-label">Yes</span>
                      </label>
                      <label class="radio-option">
                        <input
                          type="radio"
                          v-model="clientForm.isDisabled"
                          value="no"
                        />
                        <span class="radio-indicator"></span>
                        <span class="radio-label">No</span>
                      </label>
                      <label class="radio-option">
                        <input
                          type="radio"
                          v-model="clientForm.isDisabled"
                          value="unknown"
                        />
                        <span class="radio-indicator"></span>
                        <span class="radio-label">Unknown</span>
                      </label>
                    </div>

                    <!-- Conditional field for disability details when "Yes" is selected -->
                    <div
                      v-if="clientForm.isDisabled === 'yes'"
                      class="conditional-field"
                    >
                      <label>Disability</label>
                      <select v-model="clientForm.disability">
                        <option value="">Select Type of Disability</option>
                        <option value="physical">Physical Disability</option>
                        <option value="visual">Visual Impairment</option>
                        <option value="hearing">Hearing Impairment</option>
                        <option value="speech">Speech Impairment</option>
                        <option value="intellectual">
                          Intellectual Disability
                        </option>
                        <option value="developmental">
                          Developmental Disability
                        </option>
                        <option value="mental-health">
                          Mental Health Condition
                        </option>
                        <option value="multiple">Multiple Disabilities</option>
                        <option value="other">Other</option>
                      </select>
                    </div>
                  </div>

                  <div class="field-group">
                    <label>Is the Client Referred for Special Services?</label>
                    <div class="radio-group">
                      <label class="radio-option">
                        <input
                          type="radio"
                          v-model="clientForm.specialServicesReferred"
                          value="yes"
                        />
                        <span class="radio-indicator"></span>
                        <span class="radio-label">Yes</span>
                      </label>
                      <label class="radio-option">
                        <input
                          type="radio"
                          v-model="clientForm.specialServicesReferred"
                          value="no"
                        />
                        <span class="radio-indicator"></span>
                        <span class="radio-label">No</span>
                      </label>
                      <label class="radio-option">
                        <input
                          type="radio"
                          v-model="clientForm.specialServicesReferred"
                          value="unknown"
                        />
                        <span class="radio-indicator"></span>
                        <span class="radio-label">Unknown</span>
                      </label>
                    </div>

                    <!-- Conditional field for special services referral when "Yes" is selected -->
                    <div
                      v-if="clientForm.specialServicesReferred === 'yes'"
                      class="conditional-field"
                    >
                      <label>Special Services Referral</label>
                      <div class="multi-select-dropdown">
                        <div
                          class="dropdown-trigger"
                          @click="toggleSpecialServicesDropdown"
                        >
                          <span class="selected-text">
                            {{
                              getSelectedSpecialServicesText() ||
                              "Select Special Services Referral"
                            }}
                          </span>
                          <svg
                            class="dropdown-arrow"
                            :class="{ open: showSpecialServicesDropdown }"
                            width="12"
                            height="12"
                            viewBox="0 0 12 12"
                          >
                            <path d="M6 8L2 4h8L6 8z" fill="currentColor" />
                          </svg>
                        </div>

                        <div
                          v-if="showSpecialServicesDropdown"
                          class="dropdown-options"
                        >
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
                              <span class="checkbox-label">{{
                                service.label
                              }}</span>
                            </label>
                          </div>

                          <div class="pagination-info">
                            <span
                              >{{ filteredSpecialServices.length }} of
                              {{ specialServicesOptions.length }}</span
                            >
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
              <button
                v-if="currentClientStep > 0"
                @click="prevClientStep"
                type="button"
                class="btn btn--secondary"
              >
                Previous
              </button>
              <button
                v-if="currentClientStep < clientSteps.length - 1"
                @click="nextClientStep"
                type="button"
                class="btn btn--primary"
              >
                Next
              </button>
              <button
                v-if="currentClientStep === clientSteps.length - 1"
                @click="addClient"
                type="button"
                class="btn btn--primary"
              >
                Create
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
</template>

<script setup>
import { ref, reactive, computed } from "vue";

// Modal state
const clientModalOpen = ref(false);
function closeClientModal() {
  clientModalOpen.value = false;
}

// Stepper state
const currentClientStep = ref(0);
const clientSteps = [
  { title: "Basic Information" },
  { title: "Contact & Identity" },
  { title: "Contact Information" },
  { title: "Household & Background" },
  { title: "Health & Status" },
];
function nextClientStep() {
  if (currentClientStep.value < clientSteps.length - 1) {
    currentClientStep.value++;
  }
}
function prevClientStep() {
  if (currentClientStep.value > 0) {
    currentClientStep.value--;
  }
}

// Form data
const clientForm = reactive({
  name: "",
  age: "",
  dob: "",
  ageGroup: "",
  location: "",
  sex: "",
  landmark: "",
  nationality: "",
  idType: "",
  idNumber: "",
  language: "",
  isRefugee: "",
  tribe: "",
  phone: "",
  alternativePhone: "",
  email: "",
  relationship: "",
  relationshipComment: "",
  adultsInHousehold: "",
  householdType: "",
  headOccupation: "",
  parentGuardianName: "",
  parentMaritalStatus: "",
  parentIdNumber: "",
  healthStatus: "",
  hivStatus: "",
  maritalStatus: "",
  attendingSchool: "",
  schoolName: "",
  schoolLevel: "",
  schoolAddress: "",
  schoolType: "",
  schoolAttendance: "",
  isDisabled: "",
  disability: "",
  specialServicesReferred: "",
  specialServicesReferral: [],
});

// Added clients (inside parent formData.step2.clients)
const formData = reactive({
  step2: {
    clients: [],
  },
});

// Add/remove clients
function addClient() {
  formData.step2.clients.push({ ...clientForm });
  resetClientForm();
  currentClientStep.value = 0;
  clientModalOpen.value = false;
}
function removeClient(index) {
  formData.step2.clients.splice(index, 1);
}
function resetClientForm() {
  Object.keys(clientForm).forEach((key) => {
    if (Array.isArray(clientForm[key])) {
      clientForm[key] = [];
    } else {
      clientForm[key] = "";
    }
  });
}

// Special services dropdown
const showSpecialServicesDropdown = ref(false);
const specialServicesSearch = ref("");
const specialServicesOptions = [
  { value: "counseling", label: "Counseling" },
  { value: "medical", label: "Medical Care" },
  { value: "legal", label: "Legal Aid" },
  { value: "shelter", label: "Shelter" },
  { value: "education", label: "Education Support" },
  { value: "food", label: "Food Support" },
  { value: "rehabilitation", label: "Rehabilitation" },
  { value: "livelihood", label: "Livelihood Support" },
  { value: "psychosocial", label: "Psychosocial Support" },
];

const filteredSpecialServices = computed(() =>
  specialServicesOptions.filter((s) =>
    s.label.toLowerCase().includes(specialServicesSearch.value.toLowerCase())
  )
);

function toggleSpecialServicesDropdown() {
  showSpecialServicesDropdown.value = !showSpecialServicesDropdown.value;
}

function getSelectedSpecialServicesText() {
  if (!clientForm.specialServicesReferral.length) return "";
  return clientForm.specialServicesReferral
    .map(
      (val) =>
        specialServicesOptions.find((s) => s.value === val)?.label || val
    )
    .join(", ");
}
</script>

<style>
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
.client-modal-large,
  .perpetrator-modal-large {
    width: 95%;
    max-width: 95vw;
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
  content: "";
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
.step-content {
  min-height: 400px;
}

.form-step {
  padding: 20px 0;
  animation: fadeIn 0.3s ease-in-out;
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
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1),
    0 2px 4px -1px rgba(0, 0, 0, 0.06);
  max-height: 300px;
  overflow: hidden;
  margin-top: 4px;
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 8px 10px;
  background: var(--color-surface);
  color: var(--text-color);
  width: 180px;
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
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial,
    sans-serif;
}
.step-navigation {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--color-border);
}
</style>
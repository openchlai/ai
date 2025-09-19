<template>
  <div v-if="perpetratorModalOpen" class="simple-modal">
    <div class="simple-modal-content perpetrator-modal-large">
      <div class="simple-modal-header">
        <h3>New Perpetrator</h3>
        <span class="simple-modal-close" @click="closeModal">×</span>
      </div>

      <div class="simple-modal-body">
        <!-- Show existing perpetrators -->
        <div v-if="perpetrators.length > 0" class="existing-perpetrators">
          <h4>Added Perpetrators:</h4>
          <div
            v-for="(perpetrator, index) in perpetrators"
            :key="index"
            class="perpetrator-display"
          >
            <span>{{ perpetrator.name }} ({{ perpetrator.age }} {{ perpetrator.sex }})</span>
            <button @click="removePerpetrator(index)" class="remove-btn">
              Remove
            </button>
          </div>
        </div>

        <!-- Multi-step Perpetrator Form -->
        <div class="add-perpetrator-form">
          <h4>Add New Perpetrator:</h4>

          <!-- Progress Steps -->
          <div class="form-steps">
            <div class="step-indicator">
              <div
                v-for="(step, index) in perpetratorSteps"
                :key="index"
                :class="[
                  'step',
                  {
                    active: currentPerpetratorStep === index,
                    completed: currentPerpetratorStep > index,
                    future: currentPerpetratorStep < index,
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

          <!-- ✅ Step Content (what you gave me) -->
          <div class="step-content">
            <!-- Step 1: Basic Information -->
            <div v-if="currentPerpetratorStep === 0" class="form-step">
              <div class="form-fields">
                <!-- Name -->
                <div class="field-group">
                  <label>Perpetrator's Name *</label>
                  <input
                    v-model="perpetratorForm.name"
                    type="text"
                    placeholder="Enter Perpetrator's Names"
                  />
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
                  <input
                    v-model="perpetratorForm.landmark"
                    type="text"
                    placeholder="Enter Nearest Landmark"
                  />
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
                  <input
                    v-model="perpetratorForm.idNumber"
                    type="text"
                    placeholder="Enter Reporter's ID Number"
                  />
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
                      <span class="radio-label">Yes</span>
                    </label>
                    <label class="radio-option">
                      <input type="radio" v-model="perpetratorForm.isRefugee" value="no" />
                      <span class="radio-label">No</span>
                    </label>
                    <label class="radio-option">
                      <input
                        type="radio"
                        v-model="perpetratorForm.isRefugee"
                        value="unknown"
                      />
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
                  <input
                    v-model="perpetratorForm.phone"
                    type="tel"
                    placeholder="Enter Reporter's Phone Number"
                  />
                </div>

                <div class="field-group">
                  <label>Alternative Phone</label>
                  <input
                    v-model="perpetratorForm.alternativePhone"
                    type="tel"
                    placeholder="Enter Alternate Phone Number"
                  />
                </div>

                <div class="field-group">
                  <label>Email</label>
                  <input
                    v-model="perpetratorForm.email"
                    type="email"
                    placeholder="Enter Reporter's Email Address"
                  />
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
                      <span class="radio-label">Yes</span>
                    </label>
                    <label class="radio-option">
                      <input type="radio" v-model="perpetratorForm.sharesHome" value="no" />
                      <span class="radio-label">No</span>
                    </label>
                    <label class="radio-option">
                      <input
                        type="radio"
                        v-model="perpetratorForm.sharesHome"
                        value="unknown"
                      />
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
                  <input
                    v-model="perpetratorForm.guardianName"
                    type="text"
                    placeholder="Enter Perpetrator's Guardian Name"
                  />
                </div>

                <div class="field-group">
                  <label>Additional Details</label>
                  <textarea
                    v-model="perpetratorForm.additionalDetails"
                    placeholder="Enter Additional Details"
                    rows="4"
                  ></textarea>
                </div>
              </div>
            </div>
          </div>

          <!-- Step Navigation -->
          <div class="step-navigation">
            <button
              v-if="currentPerpetratorStep > 0"
              @click="prevStep"
              type="button"
              class="btn btn--secondary"
            >
              Previous
            </button>
            <button
              v-if="currentPerpetratorStep < perpetratorSteps.length - 1"
              @click="nextStep"
              type="button"
              class="btn btn--primary"
            >
              Next
            </button>
            <button
              v-if="currentPerpetratorStep === perpetratorSteps.length - 1"
              @click="addPerpetrator"
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
// Props from parent
const props = defineProps({
  perpetratorModalOpen: { type: Boolean, required: true },
  perpetrators: { type: Array, required: true },
  perpetratorForm: { type: Object, required: true },
  currentPerpetratorStep: { type: Number, required: true }
});

// Events back to parent
const emit = defineEmits([
  "close-modal",
  "add-perpetrator",
  "remove-perpetrator",
  "next-perpetrator-step",
  "prev-perpetrator-step",
]);

// Steps list
const perpetratorSteps = [
  { title: "Basic Information" },
  { title: "Identity & Contact" },
  { title: "Contact & Background" },
  { title: "Status & Details" },
];

// Emit helpers
const closeModal = () => emit("close-modal");
const addPerpetrator = () => emit("add-perpetrator");
const removePerpetrator = (index) => emit("remove-perpetrator", index);
const nextStep = () => emit("next-perpetrator-step");
const prevStep = () => emit("prev-perpetrator-step");
</script>

<style>
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

.step-navigation {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--color-border);
}
</style>
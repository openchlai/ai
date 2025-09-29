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
            <span>{{ perpetrator.name || 'Unnamed' }} ({{ perpetrator.age || 'Unknown age' }} {{ perpetrator.sex || 'Unknown gender' }})</span>
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

          <!-- Step Content -->
          <div class="step-content">
            <!-- Step 1: Basic Information -->
            <div v-if="currentPerpetratorStep === 0" class="form-step">
              <div class="form-fields">
                <!-- Name -->
                <div class="field-group">
                  <label>Perpetrator's Name *</label>
                  <input
                    v-model="localPerpetratorForm.name"
                    type="text"
                    placeholder="Enter Perpetrator's Names"
                    @input="updatePerpetratorForm"
                  />
                </div>

                <div class="field-group">
                  <label>Age</label>
                  <input 
                    v-model="localPerpetratorForm.age" 
                    type="number" 
                    placeholder="Enter age"
                    @input="updatePerpetratorForm" 
                  />
                </div>

                <div class="field-group">
                  <label>DOB</label>
                  <input 
                    v-model="localPerpetratorForm.dob" 
                    type="date"
                    @change="handleDobChange" 
                  />
                </div>

                <div class="field-group">
                  <BaseSelect
                    id="perpetrator-age-group"
                    label="Age Group"
                    v-model="localPerpetratorForm.ageGroup"
                    placeholder="Select Age Group"
                    :category-id="101"
                    @change="updatePerpetratorForm"
                  />
                </div>

                <div class="field-group">
                  <BaseSelect
                    id="perpetrator-location"
                    label="Location"
                    v-model="localPerpetratorForm.location"
                    placeholder="Select Location"
                    :category-id="88"
                    @change="updatePerpetratorForm"
                  />
                </div>

                <div class="field-group">
                  <BaseSelect
                    id="perpetrator-sex"
                    label="Sex"
                    v-model="localPerpetratorForm.sex"
                    placeholder="Select Gender"
                    :category-id="120"
                    @change="updatePerpetratorForm"
                  />
                </div>
              </div>
            </div>

            <!-- Step 2: Identity & Contact -->
            <div v-if="currentPerpetratorStep === 1" class="form-step">
              <div class="form-fields">
                <div class="field-group">
                  <label>Nearest Landmark</label>
                  <input
                    v-model="localPerpetratorForm.landmark"
                    type="text"
                    placeholder="Enter Nearest Landmark"
                    @input="updatePerpetratorForm"
                  />
                </div>

                <div class="field-group">
                  <BaseSelect
                    id="perpetrator-nationality"
                    label="Nationality"
                    v-model="localPerpetratorForm.nationality"
                    placeholder="Select Nationality"
                    :category-id="126"
                    @change="updatePerpetratorForm"
                  />
                </div>

                <div class="field-group">
                  <BaseSelect
                    id="perpetrator-id-type"
                    label="ID Type"
                    v-model="localPerpetratorForm.idType"
                    placeholder="Select ID Type"
                    :category-id="362409"
                    @change="updatePerpetratorForm"
                  />
                </div>

                <div class="field-group">
                  <label>ID Number</label>
                  <input
                    v-model="localPerpetratorForm.idNumber"
                    type="text"
                    placeholder="Enter ID Number"
                    @input="updatePerpetratorForm"
                  />
                </div>

                <div class="field-group">
                  <BaseSelect
                    id="perpetrator-language"
                    label="Language"
                    v-model="localPerpetratorForm.language"
                    placeholder="Select Language"
                    :category-id="123"
                    @change="updatePerpetratorForm"
                  />
                </div>

                <div class="field-group">
                  <label>Is the Perpetrator a Refugee?</label>
                  <div class="radio-group">
                    <label class="radio-option">
                      <input 
                        type="radio" 
                        v-model="localPerpetratorForm.isRefugee" 
                        value="yes"
                        @change="updatePerpetratorForm" 
                      />
                      <span class="radio-indicator"></span>
                      <span class="radio-label">Yes</span>
                    </label>
                    <label class="radio-option">
                      <input 
                        type="radio" 
                        v-model="localPerpetratorForm.isRefugee" 
                        value="no"
                        @change="updatePerpetratorForm" 
                      />
                      <span class="radio-indicator"></span>
                      <span class="radio-label">No</span>
                    </label>
                    <label class="radio-option">
                      <input
                        type="radio"
                        v-model="localPerpetratorForm.isRefugee"
                        value="unknown"
                        @change="updatePerpetratorForm"
                      />
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
                  <BaseSelect
                    id="perpetrator-tribe"
                    label="Tribe"
                    v-model="localPerpetratorForm.tribe"
                    placeholder="Select Tribe"
                    :category-id="133"
                    @change="updatePerpetratorForm"
                  />
                </div>

                <div class="field-group">
                  <label>Phone Number</label>
                  <input
                    v-model="localPerpetratorForm.phone"
                    type="tel"
                    placeholder="Enter Phone Number"
                    @input="updatePerpetratorForm"
                  />
                </div>

                <div class="field-group">
                  <label>Alternative Phone</label>
                  <input
                    v-model="localPerpetratorForm.alternativePhone"
                    type="tel"
                    placeholder="Enter Alternate Phone Number"
                    @input="updatePerpetratorForm"
                  />
                </div>

                <div class="field-group">
                  <label>Email</label>
                  <input
                    v-model="localPerpetratorForm.email"
                    type="email"
                    placeholder="Enter Email Address"
                    @input="updatePerpetratorForm"
                  />
                </div>

                <div class="field-group">
                  <BaseSelect
                    id="Relationship with Client"
                    label="Relationship with Client?"
                    v-model="localPerpetratorForm.relationship"
                    placeholder="Select relationship"
                    :category-id="236634"
                    @change="updatePerpetratorForm"
                  />
                </div>

                <div class="field-group">
                  <BaseSelect
                    id="Shares Home with Client"
                    label="Shares Home with Client?"
                    v-model="localPerpetratorForm.sharesHome"
                    placeholder="Select option"
                    :category-id="236631"
                    @change="updatePerpetratorForm"
                  />
                </div>
              </div>
            </div>

            <!-- Step 4: Status & Details -->
            <div v-if="currentPerpetratorStep === 3" class="form-step">
              <div class="form-fields">
                <div class="field-group">
                  <BaseSelect
                    id="Health Status"
                    label="Health Status"
                    v-model="localPerpetratorForm.healthStatus"
                    placeholder="Select health status"
                    :category-id="236660"
                    @change="updatePerpetratorForm"
                  />
                </div>

                <div class="field-group">
                  <BaseSelect
                    id="Perpetrator's Profession"
                    label="Perpetrator's Profession"
                    v-model="localPerpetratorForm.profession"
                    placeholder="Select profession"
                    :category-id="236648"
                    @change="updatePerpetratorForm"
                  />
                </div>

                <div class="field-group">
                  <BaseSelect
                    id="Perpetrator's Marital Status"
                    label="Perpetrator's Marital Status"
                    v-model="localPerpetratorForm.maritalStatus"
                    placeholder="Select marital status"
                    :category-id="236654"
                    @change="handleMaritalStatusChange"
                  />

                  <!-- Conditional Fields: Spouse Details -->
                  <div v-if="showSpouseFields" class="conditional-field">
                    <div class="spouse-fields">
                      <div class="field-group">
                        <label>Spouse Name</label>
                        <input
                          v-model="localPerpetratorForm.spouseName"
                          type="text"
                          placeholder="Enter spouse's name"
                          @input="updatePerpetratorForm"
                        />
                      </div>
                      
                      <div class="field-group">
                        <BaseSelect
                          id="spouse-profession"
                          label="Spouse Profession"
                          v-model="localPerpetratorForm.spouseProfession"
                          placeholder="Select spouse's profession"
                          :category-id="236648"
                          @change="updatePerpetratorForm"
                        />
                      </div>
                    </div>
                  </div>
                </div>

                <div class="field-group">
                  <label>Perpetrator's Guardian's Name</label>
                  <input
                    v-model="localPerpetratorForm.guardianName"
                    type="text"
                    placeholder="Enter Perpetrator's Guardian Name"
                    @input="updatePerpetratorForm"
                  />
                </div>

                <div class="field-group">
                  <label>Additional Details</label>
                  <textarea
                    v-model="localPerpetratorForm.additionalDetails"
                    placeholder="Enter Additional Details"
                    rows="4"
                    @input="updatePerpetratorForm"
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
              @click="handleAddPerpetrator"
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
import { computed, reactive, watch } from "vue";
import BaseSelect from "@/components/base/BaseSelect.vue";

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
  "update-perpetrator-form"
]);

// Create local reactive copy of the form
const localPerpetratorForm = reactive({
  ...props.perpetratorForm,
  // Ensure all fields are initialized
  name: props.perpetratorForm.name || '',
  age: props.perpetratorForm.age || '',
  dob: props.perpetratorForm.dob || '',
  ageGroup: props.perpetratorForm.ageGroup || '',
  location: props.perpetratorForm.location || '',
  sex: props.perpetratorForm.sex || '',
  landmark: props.perpetratorForm.landmark || '',
  nationality: props.perpetratorForm.nationality || '',
  idType: props.perpetratorForm.idType || '',
  idNumber: props.perpetratorForm.idNumber || '',
  language: props.perpetratorForm.language || '',
  isRefugee: props.perpetratorForm.isRefugee || '',
  tribe: props.perpetratorForm.tribe || '',
  phone: props.perpetratorForm.phone || '',
  alternativePhone: props.perpetratorForm.alternativePhone || '',
  email: props.perpetratorForm.email || '',
  relationship: props.perpetratorForm.relationship || '',
  sharesHome: props.perpetratorForm.sharesHome || '',
  healthStatus: props.perpetratorForm.healthStatus || '',
  profession: props.perpetratorForm.profession || '',
  maritalStatus: props.perpetratorForm.maritalStatus || '',
  guardianName: props.perpetratorForm.guardianName || '',
  additionalDetails: props.perpetratorForm.additionalDetails || '',
  // Spouse fields
  spouseName: props.perpetratorForm.spouseName || '',
  spouseProfession: props.perpetratorForm.spouseProfession || ''
});

// Watch for changes from parent
watch(() => props.perpetratorForm, (newForm) => {
  Object.assign(localPerpetratorForm, newForm);
}, { deep: true });

// Steps list
const perpetratorSteps = [
  { title: "Basic Information" },
  { title: "Identity & Contact" },
  { title: "Contact & Background" },
  { title: "Status & Details" },
];

// Array of marital status values that should NOT show spouse fields
const singleStatusValues = [
  'single',
  'Single',
  'SINGLE',
  'unknown',
  'Unknown',
  'UNKNOWN',
  'unmarried',
  'Unmarried',
  'never married',
  'Never Married',
];

// Computed property for showing spouse fields
const showSpouseFields = computed(() => {
  const maritalStatus = localPerpetratorForm.maritalStatus;
  
  if (!maritalStatus) {
    return false;
  }
  
  const statusValue = String(maritalStatus);
  const isSingleOrUnknown = singleStatusValues.some(singleStatus => {
    return statusValue.toLowerCase() === String(singleStatus).toLowerCase();
  });
  
  return !isSingleOrUnknown;
});

// Update parent when local form changes
const updatePerpetratorForm = () => {
  emit('update-perpetrator-form', { ...localPerpetratorForm });
};

// Handle marital status change
const handleMaritalStatusChange = () => {
  // Clear spouse fields if marital status is single/unknown
  if (!showSpouseFields.value) {
    localPerpetratorForm.spouseName = '';
    localPerpetratorForm.spouseProfession = '';
  }
  updatePerpetratorForm();
};

// Handle DOB change and auto-calculate age
const handleDobChange = (event) => {
  const dob = event.target ? event.target.value : event;
  
  if (dob) {
    const birthDate = new Date(dob);
    const today = new Date();
    
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    
    if (age >= 0) {
      localPerpetratorForm.age = age.toString();
      
      // Auto-set age group based on calculated age
      if (age < 6) localPerpetratorForm.ageGroup = '0-5';
      else if (age <= 12) localPerpetratorForm.ageGroup = '6-12';
      else if (age <= 17) localPerpetratorForm.ageGroup = '13-17';
      else if (age <= 25) localPerpetratorForm.ageGroup = '18-25';
      else if (age <= 35) localPerpetratorForm.ageGroup = '26-35';
      else if (age <= 50) localPerpetratorForm.ageGroup = '36-50';
      else localPerpetratorForm.ageGroup = '51+';
    }
  }
  
  updatePerpetratorForm();
};

// Validate and add perpetrator
const handleAddPerpetrator = () => {
  // Basic validation
  if (!localPerpetratorForm.name?.trim()) {
    alert('Perpetrator name is required');
    return;
  }
  
  console.log('Adding perpetrator with data:', localPerpetratorForm);
  emit("add-perpetrator");
};

// Navigation helpers
const closeModal = () => emit("close-modal");
const removePerpetrator = (index) => emit("remove-perpetrator", index);
const nextStep = () => {
  // Save current data before moving to next step
  updatePerpetratorForm();
  emit("next-perpetrator-step");
};
const prevStep = () => {
  // Save current data before moving to previous step
  updatePerpetratorForm();
  emit("prev-perpetrator-step");
};
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

  .spouse-fields {
    grid-template-columns: 1fr;
    gap: 12px;
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

.radio-group {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.radio-option {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
}

.conditional-field {
  margin-top: 16px;
  padding: 16px;
  background: var(--color-surface-muted);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
}

.spouse-fields {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.step-navigation {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--color-border);
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn--primary {
  background-color: #007bff;
  color: white;
}

.btn--primary:hover {
  background-color: #0056b3;
}

.btn--secondary {
  background-color: #6c757d;
  color: white;
}

.btn--secondary:hover {
  background-color: #545b62;
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
</style>
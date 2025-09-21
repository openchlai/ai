<template>
   <!-- Client Modal -->
    <div v-if="true" class="simple-modal">
      <div class="simple-modal-content client-modal-large">
        <div class="simple-modal-header">
          <h3>New Client</h3>
          <span class="simple-modal-close" @click="$emit('close-modal')">×</span>
        </div>

        <div class="simple-modal-body">
          <!-- Show existing clients -->
          <div
            v-if="clients && clients.length > 0"
            class="existing-clients"
          >
            <h4>Added Clients:</h4>
            <div
              v-for="(client, index) in clients"
              :key="index"
              class="client-display"
            >
              <span>{{ client.name || 'Unnamed' }} ({{ client.age || 'Unknown age' }} {{ client.sex || 'Unknown gender' }})</span>
              <button @click="$emit('remove-client', index)" class="remove-btn">
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
                      v-model="localClientForm.name"
                      type="text"
                      placeholder="Enter Client's Names"
                      @input="updateClientForm"
                    />
                  </div>

                  <div class="field-group">
                    <label>Age</label>
                    <input
                      v-model="localClientForm.age"
                      type="number"
                      placeholder="Enter age"
                      @input="updateClientForm"
                    />
                  </div>

                  <div class="field-group">
                    <label>DOB</label>
                    <input 
                      v-model="localClientForm.dob" 
                      type="date" 
                      @input="updateClientForm"
                    />
                  </div>

                  <div class="field-group">
                    <BaseSelect
                      id="client-age-group"
                      label="Age Group"
                      v-model="localClientForm.ageGroup"
                      placeholder="Select Age Group"
                      :category-id="101"
                    />
                  </div>

                  <div class="field-group">
                    <BaseSelect
                      id="client-location"
                      label="Location"
                      v-model="localClientForm.location"
                      placeholder="Select Location"
                      :category-id="88"
                    />
                  </div>

                  <div class="field-group">
                    <BaseSelect
                      id="client-sex"
                      label="Sex"
                      v-model="localClientForm.sex"
                      placeholder="Select Gender"
                      :category-id="120"
                    />
                  </div>
                </div>
              </div>

              <!-- Step 2: Contact & Identity -->
              <div v-if="currentClientStep === 1" class="form-step">
                <div class="form-fields">
                  <div class="field-group">
                    <label>Nearest Landmark</label>
                    <input
                      v-model="localClientForm.landmark"
                      type="text"
                      placeholder="Enter Nearest Landmark"
                      @input="updateClientForm"
                    />
                  </div>

                  <div class="field-group">
                    <BaseSelect
                      id="client-nationality"
                      label="Nationality"
                      v-model="localClientForm.nationality"
                      placeholder="Select Nationality"
                      :category-id="126"
                    />
                  </div>

                  <div class="field-group">
                    <BaseSelect
                      id="client-id-type"
                      label="ID Type"
                      v-model="localClientForm.idType"
                      placeholder="Select ID Type"
                      :category-id="362409"
                    />
                  </div>

                  <div class="field-group">
                    <label>ID Number</label>
                    <input
                      v-model="localClientForm.idNumber"
                      type="text"
                      placeholder="Enter ID Number"
                      @input="updateClientForm"
                    />
                  </div>

                  <div class="field-group">
                    <BaseSelect
                      id="client-language"
                      label="Language"
                      v-model="localClientForm.language"
                      placeholder="Select Language"
                      :category-id="123"
                    />
                  </div>

                  <div class="field-group">
                    <label>Is the Client a Refugee?</label>
                    <div class="radio-group">
                      <label class="radio-option">
                        <input
                          type="radio"
                          v-model="localClientForm.isRefugee"
                          value="yes"
                          @change="updateClientForm"
                        />
                        <span class="radio-indicator"></span>
                        <span class="radio-label">Yes</span>
                      </label>
                      <label class="radio-option">
                        <input
                          type="radio"
                          v-model="localClientForm.isRefugee"
                          value="no"
                          @change="updateClientForm"
                        />
                        <span class="radio-indicator"></span>
                        <span class="radio-label">No</span>
                      </label>
                      <label class="radio-option">
                        <input
                          type="radio"
                          v-model="localClientForm.isRefugee"
                          value="unknown"
                          @change="updateClientForm"
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
                    <BaseSelect
                      id="client-tribe"
                      label="Tribe"
                      v-model="localClientForm.tribe"
                      placeholder="Select Tribe"
                      :category-id="133"
                    />
                  </div>

                  <div class="field-group">
                    <label>Phone Number</label>
                    <input
                      v-model="localClientForm.phone"
                      type="tel"
                      placeholder="Enter Phone Number"
                      @input="updateClientForm"
                    />
                  </div>

                  <div class="field-group">
                    <label>Alternative Phone</label>
                    <input
                      v-model="localClientForm.alternativePhone"
                      type="tel"
                      placeholder="Enter Alternate Phone Number"
                      @input="updateClientForm"
                    />
                  </div>

                  <div class="field-group">
                    <label>Email</label>
                    <input
                      v-model="localClientForm.email"
                      type="email"
                      placeholder="Enter Email Address"
                      @input="updateClientForm"
                    />
                  </div>

                  <div class="field-group">
                    
                    <BaseSelect
                    id="Reporter's Relationship with Client"
                    label="Reporter's Relationship with Client"
                    v-model="localClientForm.relationship"
                    placeholder=""
                    :category-id="236634"
                  />
                  </div>

                  <div class="field-group">
                    <label>Relationship Comment</label>
                    <textarea
                      v-model="localClientForm.relationshipComment"
                      placeholder="Enter Comments about the relationship"
                      rows="3"
                      @input="updateClientForm"
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
                      v-model="localClientForm.adultsInHousehold"
                      type="number"
                      placeholder="Enter number"
                      @input="updateClientForm"
                    />
                  </div>

                  <div class="field-group">
                    
                    <BaseSelect
                    id="Household Type"
                    label="Relationship with Client?"
                    v-model="localClientForm.householdType"
                    placeholder=""
                    :category-id="236674"
                  />
                  </div>

                  <div class="field-group">
                    
                     <BaseSelect
                    id="Head of Household Occupation"
                    label="Head of Household Occupation"
                    v-model="localClientForm.headOccupation"
                    placeholder=""
                    :category-id="236648"
                  />
                  </div>

                  <div class="field-group">
                    <label>Parent/Guardian's Name</label>
                    <input
                      v-model="localClientForm.parentGuardianName"
                      type="text"
                      placeholder="Enter name"
                      @input="updateClientForm"
                    />
                  </div>

                  <div class="field-group">
                    <label>Parent/Guardian's Marital Status</label>
                    <select v-model="localClientForm.parentMaritalStatus" @change="updateClientForm">
                      <option value="">Select Marital Status</option>
                      <option value="Single">Single</option>
                      <option value="Married">Married</option>
                      <option value="Divorced">Divorced</option>
                      <option value="Widowed">Widowed</option>
                      <option value="Separated">Separated</option>
                    </select>
                    <BaseSelect
                    id="Parent/Guardian's Marital Status"
                    label="Parent/Guardian's Marital Status"
                    v-model="localClientForm.parentMaritalStatus"
                    placeholder=""
                    :category-id="36654"
                  />
                  </div>

                  <div class="field-group">
                    <label>Parent/Guardian's Identification Number</label>
                    <input
                      v-model="localClientForm.parentIdNumber"
                      type="text"
                      placeholder="Enter ID number"
                      @input="updateClientForm"
                    />
                  </div>
                </div>
              </div>

              <!-- Step 5: Health & Status -->
              <div v-if="currentClientStep === 4" class="form-step">
                <div class="form-fields">
                  <div class="field-group">
                    
                    <BaseSelect
                    id="Client's Health Status"
                    label="Client's Health Status"
                    v-model="localClientForm.healthStatus"
                    placeholder=""
                    :category-id="236660"
                  />
                  </div>

                  <div class="field-group">
                    
                    <BaseSelect
                    id="Client's HIV Status"
                    label="Client's HIV Status"
                    v-model="localClientForm.hivStatus"
                    placeholder=""
                    :category-id="105"
                  />
                  </div>

                  <div class="field-group">
                    <label>Client's Marital Status</label>
                    <select v-model="localClientForm.maritalStatus" @change="updateClientForm">
                      <option value="">Select Marital Status</option>
                      <option value="Single">Single</option>
                      <option value="Married">Married</option>
                      <option value="Divorced">Divorced</option>
                      <option value="Widowed">Widowed</option>
                      <option value="Separated">Separated</option>
                    </select>
                    <BaseSelect
                    id="Client's Marital Status"
                    label="Client's Marital Status"
                    v-model="localClientForm.maritalStatus"
                    placeholder=""
                    :category-id="36654"
                  />
                  </div>

                  <div class="field-group">
                    <label>Is the Client Attending School?</label>
                    <div class="radio-group">
                      <label class="radio-option">
                        <input
                          type="radio"
                          v-model="localClientForm.attendingSchool"
                          value="yes"
                          @change="updateClientForm"
                        />
                        <span class="radio-indicator"></span>
                        <span class="radio-label">Yes</span>
                      </label>
                      <label class="radio-option">
                        <input
                          type="radio"
                          v-model="localClientForm.attendingSchool"
                          value="no"
                          @change="updateClientForm"
                        />
                        <span class="radio-indicator"></span>
                        <span class="radio-label">No</span>
                      </label>
                      <label class="radio-option">
                        <input
                          type="radio"
                          v-model="localClientForm.attendingSchool"
                          value="unknown"
                          @change="updateClientForm"
                        />
                        <span class="radio-indicator"></span>
                        <span class="radio-label">Unknown</span>
                      </label>
                    </div>

                    <!-- School fields when attending -->
                    <div v-if="localClientForm.attendingSchool === 'yes'" class="conditional-field">
                      <label>School Name</label>
                      <input
                        v-model="localClientForm.schoolName"
                        type="text"
                        placeholder="Enter school name"
                        @input="updateClientForm"
                      />

                      <label>School Level</label>
                      <select v-model="localClientForm.schoolLevel" @change="updateClientForm">
                        <option value="">Select School Level</option>
                        <option value="nursery">Nursery</option>
                        <option value="primary">Primary</option>
                        <option value="secondary">Secondary</option>
                        <option value="tertiary">Tertiary</option>
                      </select>
                    </div>
                  </div>

                  <div class="field-group">
                    <label>Is the Client Disabled?</label>
                    <div class="radio-group">
                      <label class="radio-option">
                        <input
                          type="radio"
                          v-model="localClientForm.isDisabled"
                          value="yes"
                          @change="updateClientForm"
                        />
                        <span class="radio-indicator"></span>
                        <span class="radio-label">Yes</span>
                      </label>
                      <label class="radio-option">
                        <input
                          type="radio"
                          v-model="localClientForm.isDisabled"
                          value="no"
                          @change="updateClientForm"
                        />
                        <span class="radio-indicator"></span>
                        <span class="radio-label">No</span>
                      </label>
                      <label class="radio-option">
                        <input
                          type="radio"
                          v-model="localClientForm.isDisabled"
                          value="unknown"
                          @change="updateClientForm"
                        />
                        <span class="radio-indicator"></span>
                        <span class="radio-label">Unknown</span>
                      </label>
                    </div>

                    <!-- Disability details when disabled -->
                    <div v-if="localClientForm.isDisabled === 'yes'" class="conditional-field">
                      <label>Disability</label>
                      <select v-model="localClientForm.disability" @change="updateClientForm">
                        <option value="">Select Type of Disability</option>
                        <option value="physical">Physical Disability</option>
                        <option value="visual">Visual Impairment</option>
                        <option value="hearing">Hearing Impairment</option>
                        <option value="speech">Speech Impairment</option>
                        <option value="intellectual">Intellectual Disability</option>
                        <option value="other">Other</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Step Navigation -->
            <div class="step-navigation">
              <button
                v-if="currentClientStep > 0"
                @click="$emit('prev-client-step')"
                type="button"
                class="btn btn--secondary"
              >
                Previous
              </button>
              <button
                v-if="currentClientStep < clientSteps.length - 1"
                @click="$emit('next-client-step')"
                type="button"
                class="btn btn--primary"
              >
                Next
              </button>
              <button
                v-if="currentClientStep === clientSteps.length - 1"
                @click="handleAddClient"
                type="button"
                class="btn btn--primary"
              >
                Add Client
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
</template>

<script setup>
import { ref, reactive, watch } from "vue";
import BaseSelect from "@/components/base/BaseSelect.vue";

// Props - receive data from parent
const props = defineProps({
  clients: { type: Array, default: () => [] },
  clientForm: { type: Object, required: true },
  currentClientStep: { type: Number, default: 0 },
  showSpecialServicesDropdown: { type: Boolean, default: false },
  specialServicesSearch: { type: String, default: '' },
  filteredSpecialServices: { type: Array, default: () => [] }
});

// Emits - communicate with parent
const emit = defineEmits([
  'close-modal',
  'remove-client',
  'update-client-form',
  'toggle-special-services-dropdown',
  'prev-client-step',
  'next-client-step',
  'add-client'
]);

// Local form data - sync with parent
const localClientForm = reactive({ ...props.clientForm });

// Watch for changes from parent
watch(() => props.clientForm, (newForm) => {
  Object.assign(localClientForm, newForm);
}, { deep: true });

// Update parent when local form changes
const updateClientForm = () => {
  emit('update-client-form', { ...localClientForm });
};

// Handle adding client
const handleAddClient = () => {
  console.log('Adding client:', localClientForm);
  emit('add-client');
};

// Step configuration
const clientSteps = [
  { title: "Basic Information" },
  { title: "Contact & Identity" },
  { title: "Contact Information" },
  { title: "Household & Background" },
  { title: "Health & Status" },
];
</script>

<style>
/* Include all your existing modal styles here */
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

.client-modal-large {
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

/* All your existing styles for steps, forms, etc. */
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

.step.completed:not(:last-child)::after,
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

.step.completed .step-number,
.step.active .step-number {
  background: #28a745;
  color: white;
}

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

.step.completed .step-title,
.step.active .step-title {
  color: #28a745;
  font-weight: 600;
}

.step.future .step-title {
  color: #666666;
}

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

.existing-clients h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--color-fg);
}

.client-display {
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

@media (max-width: 768px) {
  .form-fields {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .simple-modal-content {
    width: 95%;
    margin: 10px;
  }
}
</style>
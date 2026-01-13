<template>
  <!-- Step 2: Reporter Details -->
  <div v-show="currentStep === 2" class="step-content">
    <form class="case-form" @submit.prevent="handleFormSubmit">
      <div class="form-section">
        <div class="section-title">
          {{ selectedReporter ? "Reporter Details" : "New Reporter Information" }}
        </div>
        <p class="section-description">
          Enter the reporter's contact information and details.
        </p>

        <div class="form-row">
          <BaseInput
            id="reporter-name"
            label="Full Name*"
            v-model="formData.name"
            placeholder="Enter full name"
            :readonly="!!selectedReporter"
          />
          <BaseInput
            id="reporter-age"
            label="Age"
            type="number"
            v-model="formData.age"
            placeholder="Enter age"
          />
        </div>

        <div class="form-row">
          <BaseInput
            id="reporter-dob"
            label="DOB"
            type="date"
            v-model="formData.dob"
            @input="handleDobChange"
          />
          <BaseSelect
            id="reporter-age-group"
            label="Age Group"
            v-model="formData.ageGroup"
            placeholder="Select age group"
            :category-id="101"
          />
        </div>

        <div class="form-row">
          <BaseSelect
            id="reporter-gender"
            label="Sex"
            v-model="formData.gender"
            placeholder="Select sex"
            :category-id="120"
          />
          <BaseSelect
            id="reporter-location"
            label="Location"
            v-model="formData.location"
            placeholder="Enter location"
            :category-id="88"
          />
        </div>

        <div class="form-row">
          <BaseInput
            id="reporter-landmark"
            label="Nearest Landmark"
            v-model="formData.nearestLandmark"
            placeholder="Enter nearest landmark"
          />
          <BaseSelect
            id="reporter-nationality"
            label="Nationality"
            v-model="formData.nationality"
            placeholder="Select nationality"
            :category-id="126"
          />
        </div>

        <div class="form-row">
          <BaseSelect
            id="reporter-language"
            label="Language"
            v-model="formData.language"
            placeholder="Select language"
            :category-id="123"
          />
          <BaseSelect
            id="reporter-tribe"
            label="Tribe"
            v-model="formData.tribe"
            placeholder="Select tribe"
            :category-id="133"
          />
        </div>

        <div class="form-row">
          <BaseInput
            id="reporter-phone"
            label="Phone Number*"
            type="tel"
            v-model="formData.phone"
            placeholder="Enter phone number"
          />
          <BaseInput
            id="reporter-alt-phone"
            label="Alternative Phone"
            type="tel"
            v-model="formData.altPhone"
            placeholder="Enter alternative phone"
          />
        </div>

        <BaseInput
          id="reporter-email"
          label="Email Address"
          type="email"
          v-model="formData.email"
          placeholder="Enter email address"
        />

        <div class="form-row">
          <BaseSelect
            id="reporter-id-type"
            label="ID Type"
            v-model="formData.idType"
            placeholder="Select ID type"
            :category-id="362409"
          />
          <BaseInput
            id="reporter-id-number"
            label="ID Number"
            v-model="formData.idNumber"
            placeholder="Enter ID number"
          />
        </div>

        <!-- Is Reporter a Client Section -->
        <div class="form-row">
          <div class="form-group">
            <label>Is Reporter also a Client?</label>
            <div class="radio-group">
              <label class="radio-option">
                <input v-model="formData.isClient" type="radio" :value="true" @change="handleClientSelection" />
                <span class="radio-indicator"></span>
                <span class="radio-label">Yes</span>
              </label>
              <label class="radio-option">
                <input
                  v-model="formData.isClient"
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
              <div v-if="formData.perpetrators && formData.perpetrators.length" class="perpetrators-list">
                <div
                  v-for="(perpetrator, index) in formData.perpetrators"
                  :key="index"
                  class="perpetrator-item"
                >
                  <div class="perpetrator-info">
                    <div class="perpetrator-name">{{ perpetrator.name || 'Unnamed' }}</div>
                    <div class="perpetrator-details">
                      {{ perpetrator.age || 'Unknown age' }} {{ perpetrator.sex || 'Unknown gender' }} - {{ perpetrator.location || 'Unknown location' }}
                    </div>
                  </div>
                  <button
                    type="button"
                    class="remove-perpetrator"
                    @click="removePerpetrator(index)"
                  >
                    ×
                  </button>
                </div>
              </div>
              <div v-else class="empty-state">
                <p>No perpetrators added yet</p>
              </div>
              <button
                type="button"
                class="btn btn--primary btn--sm add-perpetrator-btn"
                @click="openPerpetratorModal"
              >
                + Add Perpetrator
              </button>
            </div>
          </div>
        </div>

        <!-- Clients Section - ALWAYS VISIBLE NOW -->
        <div class="form-group">
          <label class="form-label">Clients</label>
          
          <div class="clients-section">
            <!-- Show existing clients if any -->
            <div v-if="formData.clients && formData.clients.length > 0" class="clients-list">
              <div
                v-for="(client, index) in formData.clients"
                :key="`client-${index}`"
                class="client-item"
                :class="{ 'is-reporter': client.isReporter }"
              >
                <div class="client-info">
                  <div class="client-name">
                    {{ client.name || 'Unnamed Client' }}
                    <span v-if="client.isReporter" class="reporter-badge">Reporter</span>
                  </div>
                  <div class="client-details">
                    {{ client.age ? client.age + ' years' : 'Age unknown' }} • 
                    {{ client.sex || 'Gender unknown' }} • 
                    {{ client.phone || "No phone" }}
                  </div>
                </div>
                <button
                  v-if="!client.isReporter"
                  type="button"
                  class="remove-client btn btn--danger btn--sm"
                  @click="removeClient(index)"
                  title="Remove client"
                >
                  ×
                </button>
                <span v-else class="auto-added-label">Auto-added</span>
              </div>
            </div>

            <!-- Show empty state when no clients -->
            <div v-else class="empty-state">
              <div class="empty-icon">👥</div>
              <p class="empty-text">No clients added yet</p>
              <p class="empty-subtext">
                {{ formData.isClient === true ? 'Reporter will be added as client automatically' : 'Click below to add a client' }}
              </p>
            </div>

            <!-- Add More Clients Button -->
            <button
              type="button"
              class="btn btn--secondary btn--sm add-client-btn"
              @click="handleAddClient"
            >
              <span class="btn-icon">+</span>
              {{ formData.clients.length > 0 ? 'Add Another Client' : 'Add Client' }}
            </button>
          </div>
        </div>

      </div>

      <div class="form-actions">
        <BaseButton type="button" variant="secondary" @click="goToStep(1)">Back</BaseButton>
        <div>
          <BaseButton type="button" variant="secondary" @click="handleSkipStep">Skip</BaseButton>
          <BaseButton type="submit">Next</BaseButton>
        </div>
      </div>
    </form>
  </div>
</template>

<script setup>
import BaseInput from "@/components/base/BaseInput.vue";
import BaseSelect from "@/components/base/BaseSelect.vue";
import BaseButton from "@/components/base/BaseButton.vue";

// Props
const props = defineProps({
  currentStep: { type: Number, required: true },
  selectedReporter: { type: Object, default: null },
  formData: { type: Object, required: true }, // this is step2 data only
});

// Emits
const emit = defineEmits([
  "update:formData",
  "step-change",
  "skip-step",
  "save-step",
  "open-perpetrator-modal",
  "open-client-modal",
  "remove-client",
  "remove-perpetrator"
]);

// Navigation functions
const goToStep = (step) => {
  console.log('Going to step:', step);
  // Update parent formData before navigating
  emit("update:formData", props.formData);
  emit("step-change", step);
};

const handleSkipStep = () => {
  console.log('Skipping step 2');
  emit("skip-step", { step: 2, data: props.formData });
};

// Form submission handler - this handles the Next button
const handleFormSubmit = () => {
  console.log('Form submitted - Next button clicked');
  
  // Basic validation
  if (!validateForm()) {
    return; // Stop if validation fails
  }
  
  // Save the current step data and proceed to next step
  console.log('Emitting save-step with data:', props.formData);
  emit("save-step", { step: 2, data: props.formData });
};

// Form validation - UPDATED to remove isClient requirement
const validateForm = () => {
  const errors = [];
  
  // Check required fields
  if (!props.formData.name?.trim()) {
    errors.push('Full Name is required');
  }
  
  if (!props.formData.phone?.trim()) {
    errors.push('Phone Number is required');
  }
  
  // Removed the isClient validation since it's optional now
  
  // Show validation errors if any
  if (errors.length > 0) {
    alert('Please fix the following errors:\n\n' + errors.join('\n'));
    console.log('Validation errors:', errors);
    return false;
  }
  
  console.log('Form validation passed');
  return true;
};

// Client and perpetrator handlers
const removePerpetrator = (index) => {
  console.log('Removing perpetrator at index:', index);
  emit("remove-perpetrator", index);
};

const removeClient = (index) => {
  console.log('Removing client at index:', index);
  emit("remove-client", index);
};

const openPerpetratorModal = () => {
  console.log('Opening perpetrator modal');
  emit("open-perpetrator-modal");
};

const handleAddClient = () => {
  console.log('Add Client button clicked in Step2');
  console.log('About to emit open-client-modal');
  emit("open-client-modal");
  console.log('open-client-modal event emitted');
};

// Utility function to calculate age from date of birth
const calculateAge = (dob) => {
  if (!dob) return null;
  
  const birthDate = new Date(dob);
  const today = new Date();
  
  let age = today.getFullYear() - birthDate.getFullYear();
  const monthDiff = today.getMonth() - birthDate.getMonth();
  
  // Adjust if birthday hasn't occurred this year yet
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
    age--;
  }
  
  return age >= 0 ? age : null;
};

// Function to determine age group based on age
const getAgeGroup = (age) => {
  if (!age || age < 0) return '';
  
  if (age < 6) return '0-5';
  if (age <= 12) return '6-12';
  if (age <= 17) return '13-17';
  if (age <= 25) return '18-25';
  if (age <= 35) return '26-35';
  if (age <= 50) return '36-50';
  return '51+';
};

// Handle DOB change and auto-calculate age and age group
const handleDobChange = (event) => {
  const dob = event.target ? event.target.value : event;
  console.log('DOB changed:', dob);
  
  if (dob) {
    const calculatedAge = calculateAge(dob);
    const ageGroup = getAgeGroup(calculatedAge);
    
    console.log('Calculated age:', calculatedAge);
    console.log('Calculated age group:', ageGroup);
    
    // Update form data
    props.formData.dob = dob;
    if (calculatedAge !== null) {
      props.formData.age = calculatedAge.toString();
      props.formData.ageGroup = ageGroup;
    }
    
    // Emit update to parent
    emit("update:formData", props.formData);
  } else {
    // Clear age and age group if DOB is cleared
    props.formData.age = '';
    props.formData.ageGroup = '';
    emit("update:formData", props.formData);
  }
};

const handleClientSelection = () => {
  console.log('Client selection changed:', props.formData.isClient);
  
  if (props.formData.isClient === true) {
    // Reporter is a client - add reporter details as the first client
    const reporterAsClient = {
      name: props.formData.name || '',
      age: props.formData.age || '',
      dob: props.formData.dob || '',
      ageGroup: props.formData.ageGroup || '',
      location: props.formData.location || '',
      sex: props.formData.gender || '', // Note: mapping gender to sex
      landmark: props.formData.nearestLandmark || '',
      nationality: props.formData.nationality || '',
      idType: props.formData.idType || '',
      idNumber: props.formData.idNumber || '',
      language: props.formData.language || '',
      tribe: props.formData.tribe || '',
      phone: props.formData.phone || '',
      alternativePhone: props.formData.altPhone || '',
      email: props.formData.email || '',
      isReporter: true, // Special flag to identify this as the reporter
      relationship: 'Self', // Reporter relationship to themselves
      relationshipComment: 'Reporter is also the client'
    };

    // Check if reporter is already in clients list (avoid duplicates)
    const existingReporterIndex = props.formData.clients.findIndex(client => client.isReporter);
    
    if (existingReporterIndex >= 0) {
      // Update existing reporter client with current data
      props.formData.clients[existingReporterIndex] = reporterAsClient;
    } else {
      // Add reporter as first client
      props.formData.clients.unshift(reporterAsClient);
    }
    
    console.log('Added reporter as client:', reporterAsClient);
  } else if (props.formData.isClient === false) {
    // Reporter is NOT a client - remove reporter from clients list if present
    props.formData.clients = props.formData.clients.filter(client => !client.isReporter);
    console.log('Removed reporter from clients list');
  }
  
  // Ensure clients array exists
  props.formData.clients = props.formData.clients || [];
  
  // Emit update to parent
  emit("update:formData", props.formData);
};
</script>

<style>
/* Your existing styles remain the same */
.step-content {
  min-height: 400px;
}

.case-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}
@media (min-width: 780px) {
  .form-row {
    grid-template-columns: 1fr 1fr;
  }
}

.perpetrators-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.perpetrator-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  background: var(--color-surface-muted);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
}

.perpetrator-name {
  font-weight: 600;
  color: var(--color-fg);
  font-size: 14px;
}

.perpetrator-details {
  font-size: 12px;
  color: var(--color-muted);
}

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

.add-client-btn,
.add-perpetrator-btn {
  align-self: flex-start;
  margin-top: 8px;
}

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

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: space-between;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--color-border);
}

.form-actions > div {
  display: flex;
  gap: 12px;
}

.info-message {
  display: flex;
  gap: 12px;
  padding: 16px;
  background-color: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 8px;
  color: #1e40af;
}

.info-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.info-content strong {
  display: block;
  margin-bottom: 4px;
}

.client-item.is-reporter {
  border-color: var(--color-primary);
  background: rgba(var(--color-primary-rgb), 0.05);
}

.reporter-badge {
  display: inline-block;
  background: var(--color-primary);
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
  margin-left: 8px;
  vertical-align: top;
}

.auto-added-label {
  font-size: 12px;
  color: var(--color-muted);
  font-style: italic;
  padding: 4px 8px;
}
</style>
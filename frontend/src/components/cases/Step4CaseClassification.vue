<template>
  <!-- Step 4: Case Classification -->
  <div class="step-content">
    <form class="case-form" @submit.prevent="handleFormSubmit">
      <div class="form-section">
        <div class="section-title">Case Classification & Assignment</div>
        <p class="section-description">
          Classify the case and set priority levels for proper handling.
        </p>

        <div class="form-row">
          <!-- Department -->
          <div class="form-group">
            <label>Department*</label>
            <div class="radio-group">
              <label class="radio-option">
                <input
                  v-model="localForm.department"
                  type="radio"
                  value="116"
                  required
                  @change="handleDepartmentChange"
                />
                <span class="radio-indicator"></span>
                <span class="radio-label">116</span>
              </label>
              <label class="radio-option">
                <input
                  v-model="localForm.department"
                  type="radio"
                  value="labor"
                  required
                  @change="handleDepartmentChange"
                />
                <span class="radio-indicator"></span>
                <span class="radio-label">Labor</span>
              </label>
            </div>
            
            <!-- Conditional Field: Labor Department - Client Passport -->
            <div v-if="showPassportField" class="conditional-field">
              <label for="client-passport">Client's Passport Number</label>
              <input
                id="client-passport"
                v-model="localForm.clientPassportNumber"
                type="text"
                class="form-control"
                placeholder="Enter client's passport number"
                @input="updateForm"
              />
            </div>
          </div>

          <!-- Category -->
          <div class="form-group">
            <BaseSelect
              id="case-category"
              label="case category"
              v-model="localForm.categories"
              placeholder="Select case category"
              :category-id="362557"
              @change="updateForm"
            />
          </div>
        </div>

        <!-- Priority + Status -->
        <div class="form-row">
          <div class="form-group">
            <BaseSelect
              id="priority"
              label="priority"
              v-model="localForm.priority"
              placeholder="Select priority"
              :category-id="236683"
              required
              @change="updateForm"
            />
          </div>
          <div class="form-group">
            <BaseSelect
              id="status"
              label="status"
              v-model="localForm.status"
              placeholder="Select status"
              :category-id="236696"
              required
              @change="updateForm"
            />
          </div>
        </div>

        <!-- Updated Escalated To with numeric values -->
        <div class="form-group">
          <label for="escalated-to">Escalated To</label>
          <select v-model="localForm.escalatedTo" id="escalated-to" class="form-control" @change="updateForm">
            <option value="0">None</option>
            <option value="1">Supervisor</option>
            <option value="2">Manager</option>
            <option value="3">Director</option>
            <option value="4">External Agency</option>
            <option value="5">Law Enforcement</option>
          </select>
        </div>

        <div class="form-row">
          <div class="form-group">
            <BaseSelect
              id="State of the Case in the Justice System"
              label="State of the Case in the Justice System"
              v-model="localForm.justiceSystemState"
              placeholder="Select an option"
              :category-id="236687"
              required
              @change="updateForm"
            />
          </div>
          <div class="form-group">
            <BaseSelect
              id="General Case Assessment"
              label="General Case Assessment"
              v-model="localForm.generalAssessment"
              placeholder="Select an option"
              :category-id="236694"
              required
              @change="updateForm"
            />
          </div>
        </div>

        <!-- Services Offered with Conditional Fields -->
        <div class="form-group">
          <BaseOptions
            id="services-offered"
            label="Services Offered"
            v-model="localForm.servicesOffered"
            placeholder="Select services..."
            :category-id="113"
            @selection-change="handleServicesChange"
          />

          <!-- Conditional Field: Referrals -->
          <div v-if="showReferralsField" class="conditional-field">
            <BaseOptions
              id="referrals-type"
              label="Referral Types"
              v-model="localForm.referralsType"
              placeholder="Select referral types..."
              :category-id="114"
              @selection-change="updateForm"
            />
          </div>

          <!-- Conditional Field: Police Report -->
          <div v-if="showPoliceField" class="conditional-field">
            <label for="police-details">Police Report Details</label>
            <textarea
              id="police-details"
              v-model="localForm.policeDetails"
              class="form-control"
              placeholder="Enter police report details, case number, station, etc."
              rows="3"
              @input="updateForm"
            ></textarea>
          </div>

          <!-- Conditional Field: Others -->
          <div v-if="showOthersField" class="conditional-field">
            <label for="other-services">Other Services Details</label>
            <textarea
              id="other-services"
              v-model="localForm.otherServicesDetails"
              class="form-control"
              placeholder="Please specify the other services provided"
              rows="3"
              @input="updateForm"
            ></textarea>
          </div>
        </div>

        <div class="form-group">
          <BaseSelect
            id="know about 116"
            label="How did you know about 116?"
            v-model="localForm.referralSource"
            placeholder="Select an option"
            :category-id="236700"
            required
            @change="updateForm"
          />
        </div>

        <!-- Attachments Section - Now using the dedicated component -->
        <div class="form-group">
          <AttachmentUpload
            v-model="localForm.attachments"
            label="Case Attachments"
            description="Upload relevant documents, images, or files related to this case."
            :max-size-mb="10"
            @upload-complete="handleAttachmentUploadComplete"
            @upload-error="handleAttachmentUploadError"
          />
        </div>
      </div>

      <!-- Actions -->
      <div class="form-actions">
        <BaseButton type="button" variant="secondary" @click="goToStep(3)">Back</BaseButton>
        <div>
          <BaseButton type="button" variant="secondary" @click="handleSkipStep">Skip</BaseButton>
          <BaseButton type="submit">Next</BaseButton>
        </div>
      </div>
    </form>
  </div>
</template>

<script setup>
import { reactive, watch, computed, ref } from "vue"
import BaseSelect from "@/components/base/BaseSelect.vue"
import BaseButton from "@/components/base/BaseButton.vue"
import BaseOptions from "@/components/base/BaseOptions.vue"
import AttachmentUpload from "@/components/cases/AttachmentUpload.vue"

const props = defineProps({
  currentStep: { type: Number, required: true },
  formData: { type: Object, required: true },
  clientSearchResults: { type: Array, default: () => [] },
  hasSearched: { type: Boolean, default: false },
})

const emit = defineEmits([
  "form-update",
  "search-client-by-passport",
  "select-client",
  "create-new-client",
  "save-and-proceed",
  "step-change",
  "skip-step",
])

// Local copy with conditional fields initialized and new service fields
const localForm = reactive({ 
  ...props.formData,
  // Initialize conditional fields
  clientPassportNumber: props.formData.clientPassportNumber || '',
  referralsType: props.formData.referralsType || [],
  policeDetails: props.formData.policeDetails || '',
  otherServicesDetails: props.formData.otherServicesDetails || '',
  attachments: props.formData.attachments || [],
  // Add service text storage
  servicesOfferedText: props.formData.servicesOfferedText || []
})

// Store selected services options for conditional logic
const selectedServicesOptions = ref([])

// Computed properties for conditional field visibility
const showPassportField = computed(() => {
  return localForm.department === 'labor'
})

const showReferralsField = computed(() => {
  return selectedServicesOptions.value.some(option => 
    option.text?.toLowerCase().includes('referral')
  )
})

const showPoliceField = computed(() => {
  return selectedServicesOptions.value.some(option => 
    option.text?.toLowerCase().includes('police') || 
    option.text?.toLowerCase().includes('report to police')
  )
})

const showOthersField = computed(() => {
  return selectedServicesOptions.value.some(option => 
    option.text?.toLowerCase().includes('other')
  )
})

// Handle department change with conditional field management
const handleDepartmentChange = () => {
  console.log('Department changed:', localForm.department)
  
  // Clear passport field if not labor department
  if (localForm.department !== 'labor') {
    localForm.clientPassportNumber = ''
  }
  
  // Update parent
  updateForm()
}

// Handle services selection change with proper text storage
const handleServicesChange = (selectionData) => {
  console.log('Services selection changed:', selectionData)
  
  // Store both IDs and text values
  localForm.servicesOffered = selectionData.values || []
  localForm.servicesOfferedText = selectionData.options?.map(opt => opt.text) || []
  selectedServicesOptions.value = selectionData.options || []
  
  // Clear conditional fields if their trigger options are no longer selected
  if (!showReferralsField.value) {
    localForm.referralsType = []
  }
  if (!showPoliceField.value) {
    localForm.policeDetails = ''
  }
  if (!showOthersField.value) {
    localForm.otherServicesDetails = ''
  }
  
  // Update parent with both service IDs and text
  updateForm()
}

// Attachment event handlers
const handleAttachmentUploadComplete = (uploadData) => {
  console.log('Attachments uploaded successfully:', uploadData)
  // The component already updates localForm.attachments via v-model
  // Just need to propagate the changes to parent
  updateForm()
}

const handleAttachmentUploadError = (errorData) => {
  console.error('Attachment upload error:', errorData)
  // Could show a toast notification or handle error differently
}

// Watch for changes from parent
watch(() => props.formData, (newData) => {
  Object.assign(localForm, newData);
}, { deep: true });

// Update parent when local form changes with complete data
const updateForm = () => {
  console.log('Step4: Form data updated');
  
  // Create payload with all fields including service text
  const updatePayload = {
    ...localForm,
    servicesOfferedSelection: {
      values: localForm.servicesOffered,
      options: selectedServicesOptions.value
    }
  };
  
  emit("form-update", updatePayload);
};

// Sync changes back up
watch(localForm, (newVal) => {
  // Include service selection data
  const payload = {
    ...newVal,
    servicesOfferedSelection: {
      values: localForm.servicesOffered,
      options: selectedServicesOptions.value
    }
  }
  emit("form-update", payload)
}, { deep: true })

// Navigation functions
const goToStep = (step) => {
  console.log('Step4: Going to step', step);
  // Update parent with current data before navigating
  updateForm();
  emit("step-change", step);
};

const handleSkipStep = () => {
  console.log('Step4: Skipping step');
  emit("skip-step", { step: 4, data: localForm });
};

// Form validation
const validateForm = () => {
  const errors = [];
  
  // Check required fields
  if (!localForm.department) {
    errors.push('Department selection is required');
  }
  
  if (!localForm.priority) {
    errors.push('Priority is required');
  }
  
  if (!localForm.status) {
    errors.push('Status is required');
  }
  
  // Show validation errors if any
  if (errors.length > 0) {
    alert('Please fix the following errors:\n\n' + errors.join('\n'));
    console.log('Step4 validation errors:', errors);
    return false;
  }
  
  console.log('Step4: Form validation passed');
  return true;
};

// Handle form submission with complete data
const handleFormSubmit = () => {
  console.log('Step4: Form submitted - Next button clicked');
  
  // Basic validation
  if (!validateForm()) {
    return;
  }
  
  // Prepare complete data payload
  const completeData = {
    ...localForm,
    servicesOfferedSelection: {
      values: localForm.servicesOffered,
      options: selectedServicesOptions.value
    }
  };
  
  // Save and proceed to next step
  console.log('Step4: Emitting save-and-proceed with data:', completeData);
  emit("save-and-proceed", { step: 4, data: completeData });
};
</script>

<style scoped>
.step-content {
  min-height: 400px;
}

/* Forms */
.case-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--color-fg);
}

.form-control {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 14px;
  background: var(--color-surface);
  color: var(--color-fg);
  transition: all 0.2s ease;
}

.form-control:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(var(--color-primary-rgb), 0.1);
}

.radio-group {
  display: flex;
  gap: 16px;
  margin-top: 8px;
}

.radio-option {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
}

.radio-option input[type="radio"] {
  margin: 0;
  cursor: pointer;
}

.radio-indicator {
  /* Add custom radio styling if needed */
}

.radio-label {
  cursor: pointer;
  font-weight: normal;
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

/* Conditional Fields Styling */
.conditional-field {
  margin-top: 16px;
  padding: 16px;
  background: var(--color-surface-muted);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  animation: fadeIn 0.3s ease-in-out;
}

.conditional-field label {
  display: block;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--color-fg);
}

.conditional-field textarea {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 14px;
  background: var(--color-surface);
  color: var(--color-fg);
  transition: all 0.2s ease;
  resize: vertical;
}

.conditional-field textarea:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(var(--color-primary-rgb), 0.1);
}

@keyframes fadeIn {
  from { 
    opacity: 0; 
    transform: translateY(-10px); 
  }
  to { 
    opacity: 1; 
    transform: translateY(0); 
  }
}
</style>
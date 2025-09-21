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
                  @change="updateForm"
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
                  @change="updateForm"
                />
                <span class="radio-indicator"></span>
                <span class="radio-label">Labor</span>
              </label>
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

        <!-- Other Selects -->
        <div class="form-group">
          <label for="escalated-to">Escalated To</label>
          <select v-model="localForm.escalatedTo" id="escalated-to" class="form-control" @change="updateForm">
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

        <div class="form-group">
            <BaseOptions
  id="services-offered"
  label="Services Offered"
  v-model="localForm.servicesOffered"
  placeholder="Select services..."
  :category-id="113"
  @selection-change="updateForm"
/>
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
import { reactive, watch } from "vue"
import BaseSelect from "@/components/base/BaseSelect.vue"
import BaseButton from "@/components/base/BaseButton.vue"
import BaseOptions from "@/components/base/BaseOptions.vue"

const props = defineProps({
  currentStep: { type: Number, required: true },
  formData: { type: Object, required: true },
  clientSearchResults: { type: Array, default: () => [] },
  hasSearched: { type: Boolean, default: false },
})

// Match parent component event listeners
const emit = defineEmits([
  "form-update",
  "search-client-by-passport",
  "select-client",
  "create-new-client",
  "save-and-proceed",
  "step-change",  // Changed from "go-to-step" to match parent
  "skip-step",
])

// Local copy so edits don't immediately mutate parent
const localForm = reactive({ ...props.formData })

// Watch for changes from parent
watch(() => props.formData, (newData) => {
  Object.assign(localForm, newData);
}, { deep: true });

// Update parent when local form changes
const updateForm = () => {
  console.log('Step4: Form data updated');
  emit("form-update", localForm);
};

// Sync changes back up (keep existing watch for backward compatibility)
watch(localForm, (newVal) => {
  emit("form-update", newVal)
}, { deep: true })

// Navigation functions
const goToStep = (step) => {
  console.log('Step4: Going to step', step);
  // Update parent with current data before navigating
  emit("form-update", localForm);
  emit("step-change", step);  // Changed to match parent listener
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

// Handle form submission (Next button)
const handleFormSubmit = () => {
  console.log('Step4: Form submitted - Next button clicked');
  
  // Basic validation
  if (!validateForm()) {
    return;
  }
  
  // Save and proceed to next step
  console.log('Step4: Emitting save-and-proceed with data:', localForm);
  emit("save-and-proceed", { step: 4, data: localForm });
};
</script>

<style>
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
  padding: 12px 20px;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.search-btn:hover {
  background: var(--color-primary-dark);
  transform: translateY(-1px);
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
</style>
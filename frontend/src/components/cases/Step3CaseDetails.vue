<template>
  <!-- Step 3: Case Details -->
  <div class="step-content">
    <form class="case-form" @submit.prevent="handleFormSubmit">
      <div class="form-section">
        <div class="section-title">Case Information</div>
        <p class="section-description">
          Provide detailed information about the case and incident.
        </p>

        <BaseTextarea
          id="case-narrative"
          label="Case Narrative*"
          v-model="formData.narrative"
          placeholder="Describe the case details, incident, and circumstances in detail..."
          :rows="6"
          @input="updateForm"
        />

        <div class="form-row">
          <div class="form-group">
            <label for="incident-date">Date of Incident</label>
            <input
              v-model="formData.incidentDate"
              type="date"
              id="incident-date"
              class="form-control"
              @input="updateForm"
            />
          </div>
          <div class="form-group">
            <label for="incident-time">Time of Incident</label>
            <input
              v-model="formData.incidentTime"
              type="time"
              id="incident-time"
              class="form-control"
              @input="updateForm"
            />
          </div>
        </div>

        <div class="form-group">
          <label for="incident-location">Location of Incident</label>
          <input
            v-model="formData.location"
            type="text"
            id="incident-location"
            class="form-control"
            placeholder="Enter location where incident occurred"
            @input="updateForm"
          />
        </div>

        <div class="form-group">
          <label>Is this Case GBV Related?*</label>
          <div class="radio-group">
            <BaseSelect
              v-model="formData.isGBVRelated"
              placeholder="Select an option"
              :category-id="118"
              @change="updateForm"
            />
          </div>
        </div>

        <div class="form-group">
          <label for="case-plan">Case Plan</label>
          <textarea
            v-model="formData.casePlan"
            id="case-plan"
            class="form-control"
            placeholder="Outline the planned interventions and support services..."
            rows="4"
            @input="updateForm"
          ></textarea>
        </div>
      </div>

      <div class="form-actions">
        <BaseButton type="button" variant="secondary" @click="goToStep(2)">Back</BaseButton>
        <div>
          <BaseButton type="button" variant="secondary" @click="handleSkipStep">Skip</BaseButton>
          <BaseButton type="submit">Next</BaseButton>
        </div>
      </div>
    </form>
  </div>
</template>

<script setup>
import BaseSelect from "@/components/base/BaseSelect.vue";
import BaseButton from "@/components/base/BaseButton.vue";
import BaseTextarea from "@/components/base/BaseTextarea.vue";

// Props
const props = defineProps({
  currentStep: { type: Number, required: true },
  formData: { type: Object, required: true }
});

// Emits - Match what the parent expects
const emit = defineEmits([
  "form-update",
  "save-and-proceed", 
  "step-change",      // Changed from "go-to-step" to match parent
  "skip-step"
]);

// Methods
function updateForm() {
  console.log('Step3: Form data updated');
  emit("form-update", props.formData);
}

function goToStep(step) {
  console.log('Step3: Going to step', step);
  // Update parent with current data before navigating
  emit("form-update", props.formData);
  emit("step-change", step);  // Changed to match parent listener
}

function handleSkipStep() {
  console.log('Step3: Skipping step');
  emit("skip-step", { step: 3, data: props.formData });
}

// Form validation
function validateForm() {
  const errors = [];
  
  // Check required fields
  if (!props.formData.narrative?.trim()) {
    errors.push('Case Narrative is required');
  }
  
  if (!props.formData.isGBVRelated) {
    errors.push('Please specify if this case is GBV related');
  }
  
  // Show validation errors if any
  if (errors.length > 0) {
    alert('Please fix the following errors:\n\n' + errors.join('\n'));
    console.log('Step3 validation errors:', errors);
    return false;
  }
  
  console.log('Step3: Form validation passed');
  return true;
}

// Handle form submission (Next button)
function handleFormSubmit() {
  console.log('Step3: Form submitted - Next button clicked');
  
  // Basic validation
  if (!validateForm()) {
    return;
  }
  
  // Save and proceed to next step
  console.log('Step3: Emitting save-and-proceed with data:', props.formData);
  emit("save-and-proceed", { step: 3, data: props.formData });
}
</script>

<style>
.step-content {
  min-height: 400px;
}

.form-step {
  padding: 20px 0;
  animation: fadeIn 0.3s ease-in-out;
}

/* Forms */
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
  margin-top: 8px;
}

/* Form Actions */
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
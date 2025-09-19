<template>
  <!-- Step 3: Case Details -->
  <div class="step-content">
    <form class="case-form" @submit.prevent="saveAndProceed(3)">
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
        />

        <div class="form-row">
          <div class="form-group">
            <label for="incident-date">Date of Incident</label>
            <input
              v-model="formData.incidentDate"
              type="date"
              id="incident-date"
              class="form-control"
            />
          </div>
          <div class="form-group">
            <label for="incident-time">Time of Incident</label>
            <input
              v-model="formData.incidentTime"
              type="time"
              id="incident-time"
              class="form-control"
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
          />
        </div>

        <div class="form-group">
          <label>Is this Case GBV Related?*</label>
          <div class="radio-group">
            <BaseSelect
              v-model="formData.isGBVRelated"
              placeholder="Select an option"
              :category-id="118"
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
</template>

<script setup>
import BaseSelect from "@/components/base/BaseSelect.vue";
import BaseButton from "@/components/base/BaseButton.vue";
import BaseTextarea from "@/components/base/BaseTextarea.vue";

// Props
const props = defineProps({
  formData: {
    type: Object,
    required: true
  }
})

// Emits
const emit = defineEmits([
  "form-update",
  "save-and-proceed",
  "go-to-step",
  "skip-step"
])

// Methods
function updateForm() {
  emit("form-update", props.formData)
}

function goToStep(step) {
  emit("go-to-step", step)
}

function skipStep(step) {
  emit("skip-step", { step, data: props.formData })
}

function saveAndProceed(step) {
  emit("save-and-proceed", { step, data: props.formData })
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

/* Form Actions */
.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--color-border);
}
</style>
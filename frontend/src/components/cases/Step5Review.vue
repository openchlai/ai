<template>
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
                    <div
                      v-if="formData.step4.categories.length > 0"
                      class="category-tags"
                    >
                      <span
                        v-for="category in formData.step4.categories"
                        :key="category"
                        class="category-tag"
                      >
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
            <BaseButton variant="secondary" @click="goToStep(4)"
              >Back</BaseButton
            >
            <BaseButton @click="submitCase">Create Case</BaseButton>
          </div>
        </div>
</template>

<script setup>
import BaseButton from "@/components/base/BaseButton.vue";

// Props
const props = defineProps({
  currentStep: { type: Number, required: true },
  formData: { type: Object, required: true }
});

// Emits
const emit = defineEmits(["go-to-step", "submit-case"]);

// Step navigation
function goToStep(step) {
  emit("go-to-step", step);
}

// Submit handler
function submitCase() {
  emit("submit-case", props.formData);
}

// Helpers
function formatDepartment(value) {
  if (!value) return "";
  const map = {
    health: "Health",
    police: "Police",
    legal: "Legal",
    welfare: "Welfare"
  };
  return map[value] || value;
}

function formatPriority(value) {
  if (!value) return "";
  const map = {
    high: "High",
    medium: "Medium",
    low: "Low"
  };
  return map[value] || value;
}

function formatStatus(value) {
  if (!value) return "";
  const map = {
    open: "Open",
    in_progress: "In Progress",
    closed: "Closed"
  };
  return map[value] || value;
}
</script>


<style>
.step-content {
  min-height: 400px;
}
/* Review styles */
.review-sections {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.review-section {
  border: 1px solid var(--color-border);
  border-radius: 14px;
  background: var(--color-surface);
}
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border-bottom: 1px solid var(--color-border);
}
.review-content {
  padding: 10px 12px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
.review-item-full {
  grid-column: 1 / -1;
}
.review-label {
  font-weight: 600;
  color: var(--color-muted);
}
.review-value {
  color: var(--text-color);
}
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
  padding: 2px 6px;
  background-color: var(--color-primary, #8b4513);
  color: white;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial,
    sans-serif;
}
.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--color-border);
}
</style>
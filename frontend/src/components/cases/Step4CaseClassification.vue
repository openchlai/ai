<template>
  <!-- Step 4: Case Classification -->
  <div class="step-content">
    <form class="case-form" @submit.prevent="onSaveAndProceed">
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
                />
                <span class="radio-indicator"></span>
                <span class="radio-label">Labor</span>
              </label>
            </div>
          </div>

          <!-- Labor Department - Client Passport Search -->
          <div
            v-if="localForm.department === 'labor'"
            class="form-group labor-search-section"
          >
            <label>Client's Passport Number</label>
            <div class="passport-search-container">
              <input
                v-model="localForm.clientPassportNumber"
                type="text"
                placeholder="Enter passport number"
                class="passport-input"
              />
              <button
                type="button"
                @click="$emit('search-client-by-passport', localForm.clientPassportNumber)"
                class="search-btn"
              >
                Search
              </button>
            </div>

            <!-- Search Results -->
            <div v-if="clientSearchResults.length > 0" class="search-results">
              <h4>Search Results:</h4>
              <div
                v-for="client in clientSearchResults"
                :key="client.id"
                class="client-result"
              >
                <div class="client-info">
                  <strong>{{ client.name }}</strong>
                  <span class="client-details">
                    {{ client.passportNumber }} • {{ client.nationality }}
                  </span>
                </div>
                <button
                  type="button"
                  @click="$emit('select-client', client)"
                  class="select-client-btn"
                >
                  Select
                </button>
              </div>
            </div>

            <!-- No Results -->
            <div v-if="clientSearchResults.length === 0 && hasSearched" class="no-results">
              <p>No client found with this passport number.</p>
              <button
                type="button"
                @click="$emit('create-new-client')"
                class="create-client-btn"
              >
                Create New Client
              </button>
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
            />
          </div>
        </div>

        <!-- Other Selects -->
        <div class="form-group">
          <label for="escalated-to">Escalated To</label>
          <select v-model="localForm.escalatedTo" id="escalated-to" class="form-control">
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
            <label for="justice-system-state">State of the Case in the Justice System</label>
            <select
              v-model="localForm.justiceSystemState"
              id="justice-system-state"
              class="form-control"
            >
              <option value="">Select state...</option>
              <option value="Social Worker">Social Worker</option>
              <option value="Police Investigation">Police Investigation</option>
              <option value="Court Proceedings">Court Proceedings</option>
              <option value="Prosecution">Prosecution</option>
              <option value="Sentencing">Sentencing</option>
              <option value="Closed">Closed</option>
            </select>
          </div>
          <div class="form-group">
            <label for="general-assessment">General Case Assessment</label>
            <select
              v-model="localForm.generalAssessment"
              id="general-assessment"
              class="form-control"
            >
              <option value="">Select assessment...</option>
              <option value="Progressing">Progressing</option>
              <option value="Stalled">Stalled</option>
              <option value="Resolved">Resolved</option>
              <option value="Escalated">Escalated</option>
              <option value="Under Review">Under Review</option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label for="services-offered">Services Offered</label>
          <select
            v-model="localForm.servicesOffered"
            id="services-offered"
            class="form-control"
          >
            <option value="">Select service...</option>
            <option value="Know About 116">Know About 116</option>
            <option value="Counseling">Counseling</option>
            <option value="Legal Aid">Legal Aid</option>
            <option value="Shelter">Shelter</option>
            <option value="Medical Assistance">Medical Assistance</option>
            <option value="Financial Support">Financial Support</option>
            <option value="Referral Services">Referral Services</option>
            <option value="Emergency Response">Emergency Response</option>
            <option value="Crisis Intervention">Crisis Intervention</option>
            <option value="Support Groups">Support Groups</option>
            <option value="Education Programs">Education Programs</option>
            <option value="Community Outreach">Community Outreach</option>
          </select>
        </div>

        <div class="form-group">
          <label for="referral-source">How did you know about 116?</label>
          <select
            v-model="localForm.referralSource"
            id="referral-source"
            class="form-control"
          >
            <option value="">Select source...</option>
            <option value="Community Sensitizations">Community Sensitizations</option>
            <option value="Facebook">Facebook</option>
            <option value="Friend">Friend</option>
            <option value="IEC Material">IEC Material</option>
            <option value="Instagram">Instagram</option>
            <option value="News Papers">News Papers</option>
            <option value="NGO/CSO/Partners">NGO/CSO/Partners</option>
            <option value="Radio">Radio</option>
            <option value="Relative/Family Member">Relative/Family Member</option>
            <option value="School">School</option>
            <option value="Television">Television</option>
            <option value="WhatsApp">WhatsApp</option>
            <option value="Word of Mouth">Word of Mouth</option>
            <option value="Other">Other</option>
          </select>
        </div>
      </div>

      <!-- Actions -->
      <div class="form-actions">
        <BaseButton variant="secondary" @click="$emit('go-to-step', 3)">Back</BaseButton>
        <div>
          <BaseButton variant="secondary" @click="$emit('skip-step', 4)">Skip</BaseButton>
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

const props = defineProps({
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
  "go-to-step",
  "skip-step",
])

// Local copy so edits don’t immediately mutate parent
const localForm = reactive({ ...props.formData })

// Sync changes back up
watch(localForm, (newVal) => {
  emit("form-update", newVal)
}, { deep: true })

function onSaveAndProceed() {
  emit("save-and-proceed", localForm)
}
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
  justify-content: flex-end;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--color-border);
}
</style>
<template>
  <!-- Step 2: Reporter Details -->
  <div v-show="currentStep === 2" class="step-content">
    <form class="case-form" @submit.prevent="saveAndProceed(2)">
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

        <div class="form-row">
          <div class="form-group">
            <label>Is Reporter also a Client?</label>
            <div class="radio-group">
              <label class="radio-option">
                <input v-model="formData.isClient" type="radio" :value="true" />
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
              <div v-if="formData.perpetrators.length" class="perpetrators-list">
                <div
                  v-for="(perpetrator, index) in formData.perpetrators"
                  :key="index"
                  class="perpetrator-item"
                >
                  <div class="perpetrator-info">
                    <div class="perpetrator-name">{{ perpetrator.name }}</div>
                    <div class="perpetrator-details">
                      {{ perpetrator.age }} {{ perpetrator.sex }} - {{ perpetrator.location }}
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
              <button
                type="button"
                class="btn btn--primary btn--sm add-perpetrator-btn"
                @click="openPerpetratorModal"
              >
                + Add Perpetrator
              </button>
            </div>
          </div>

        <!-- Clients Section - Only show if "Is Reporter a Client?" is "No" -->
<div v-if="formData.isClient === false" class="form-group">
  <label>Clients</label>
  <div class="clients-section">
    <div v-if="formData.clients && formData.clients.length" class="clients-list">
      <div
        v-for="(client, index) in formData.clients"
        :key="index"
        class="client-item"
      >
        <div class="client-info">
          <div class="client-name">{{ client.name }}</div>
          <div class="client-details">
            {{ client.age }} {{ client.sex }} - {{ client.phone || "No phone" }}
          </div>
        </div>
        <button
          type="button"
          class="remove-client"
          @click="removeClient(index)"
        >
          ×
        </button>
      </div>
    </div>

    <div v-else class="empty-state">
      <p>No clients added yet</p>
    </div>

    <button
      type="button"
      class="btn btn--primary btn--sm add-client-btn"
      @click="openClientModal"
    >
      + Add Client
    </button>
  </div>
</div>

        </div>
      </div>

      <div class="form-actions">
        <BaseButton variant="secondary" @click="goToStep(1)">Back</BaseButton>
        <div>
          <BaseButton variant="secondary" @click="skipStep(2)">Skip</BaseButton>
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
]);

// Navigation
const goToStep = (step) => emit("step-change", step);
const skipStep = (step) => emit("skip-step", { step, data: props.formData });
const saveAndProceed = (step) =>
  emit("save-step", { step, data: props.formData });

// Perpetrators
const removePerpetrator = (index) => {
  props.formData.perpetrators.splice(index, 1);
  emit("update:formData", props.formData);
};

// Remove a client from step2.clients
const removeClient = (index) => {
  props.formData.clients.splice(index, 1);
  emit("update:formData", props.formData);
};


const openPerpetratorModal = () => emit("open-perpetrator-modal");
const openClientModal = () => emit("open-client-modal");


const handleClientSelection = () => {
  props.formData.isClient = props.formData.isClient === true; // ensure boolean
  if (!props.formData.isClient) {
    props.formData.clients = props.formData.clients || [];
  } else {
    props.formData.clients = [];
  }
  emit("update:formData", props.formData);
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
  justify-content: flex-end;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--color-border);
}
</style>
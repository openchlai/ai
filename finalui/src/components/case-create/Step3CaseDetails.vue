<template>
  <div class="min-h-96">
    <form class="flex flex-col gap-3.5" @submit.prevent="handleFormSubmit">
      <div>
        <div class="text-xl font-semibold text-gray-900 mb-2">Case Information</div>
        <p class="text-sm text-gray-600 mb-5">
          Provide detailed information about the case and incident.
        </p>

        <div class="mb-5">
          <BaseTextarea
            id="case-narrative"
            label="Case Narrative*"
            v-model="formData.narrative"
            placeholder="Describe the case details, incident, and circumstances in detail..."
            :rows="6"
            @input="updateForm"
          />
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-5">
          <div>
            <label for="incident-date" class="block font-semibold mb-2 text-gray-900">Date of Incident</label>
            <input v-model="formData.incidentDate" type="date" id="incident-date" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white text-gray-900 transition-all focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100" @input="updateForm" />
          </div>
          <div>
            <label for="incident-time" class="block font-semibold mb-2 text-gray-900">Time of Incident</label>
            <input v-model="formData.incidentTime" type="time" id="incident-time" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white text-gray-900 transition-all focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100" @input="updateForm" />
          </div>
        </div>

        <div class="mb-5">
          <label for="incident-location" class="block font-semibold mb-2 text-gray-900">Location of Incident</label>
          <input v-model="formData.location" type="text" id="incident-location" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white text-gray-900 transition-all focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100" placeholder="Enter location where incident occurred" @input="updateForm" />
        </div>

        <div class="mb-5">
          <label class="block font-semibold mb-2 text-gray-900">Is this Case GBV Related?*</label>
          <BaseSelect
            v-model="formData.isGBVRelated"
            placeholder="Select an option"
            :category-id="118"
            @change="updateForm"
          />
        </div>

        <div class="mb-5">
          <label for="case-plan" class="block font-semibold mb-2 text-gray-900">Case Plan</label>
          <textarea v-model="formData.casePlan" id="case-plan" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white text-gray-900 transition-all focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100 resize-vertical" placeholder="Outline the planned interventions and support services..." rows="4" @input="updateForm"></textarea>
        </div>
      </div>

      <div class="flex gap-3 justify-between mt-6 pt-5 border-t border-gray-200">
        <button type="button" class="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors" @click="goToStep(2)">Back</button>
        <div class="flex gap-3">
          <button type="button" class="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors" @click="handleSkipStep">Skip</button>
          <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors">Next</button>
        </div>
      </div>
    </form>
  </div>
</template>

<script setup>
import BaseSelect from "@/components/base/BaseSelect.vue";
import BaseTextarea from "@/components/base/BaseTextarea.vue";

const props = defineProps({
  currentStep: { type: Number, required: true },
  formData: { type: Object, required: true }
});

const emit = defineEmits([
  "form-update",
  "save-and-proceed", 
  "step-change",
  "skip-step"
]);

function updateForm() {
  emit("form-update", props.formData);
}

function goToStep(step) {
  emit("form-update", props.formData);
  emit("step-change", step);
}

function handleSkipStep() {
  emit("skip-step", { step: 3, data: props.formData });
}

function validateForm() {
  const errors = [];
  if (!props.formData.narrative?.trim()) {
    errors.push('Case Narrative is required');
  }
  if (!props.formData.isGBVRelated) {
    errors.push('Please specify if this case is GBV related');
  }
  if (errors.length > 0) {
    alert('Please fix the following errors:\n\n' + errors.join('\n'));
    return false;
  }
  return true;
}

function handleFormSubmit() {
  if (!validateForm()) return;
  emit("save-and-proceed", { step: 3, data: props.formData });
}
</script>
<template>
  <div class="min-h-96">
    <div class="flex flex-col gap-3">
      <div class="border border-gray-200 rounded-xl bg-white">
        <div class="flex items-center justify-between p-2.5 px-3 border-b border-gray-200">
          <div class="text-xl font-semibold text-gray-900">Reporter Information</div>
          <button class="flex items-center gap-2 px-3 py-1.5 bg-gray-100 text-gray-700 rounded-md text-sm hover:bg-gray-200 transition-colors" @click="goToStep(2)">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Edit
          </button>
        </div>
        <div class="p-2.5 px-3 grid grid-cols-2 gap-2.5">
          <div>
            <div class="font-semibold text-gray-500 text-sm">Name</div>
            <div class="text-gray-900">{{ formData.step2.name || "N/A" }}</div>
          </div>
          <div>
            <div class="font-semibold text-gray-500 text-sm">Phone</div>
            <div class="text-gray-900">{{ formData.step2.phone || "N/A" }}</div>
          </div>
          <div>
            <div class="font-semibold text-gray-500 text-sm">Location</div>
            <div class="text-gray-900">{{ formData.step2.location || "N/A" }}</div>
          </div>
          <div>
            <div class="font-semibold text-gray-500 text-sm">Is Client</div>
            <div>
              <span class="inline-block px-2 py-0.5 rounded text-xs font-medium" :class="formData.step2.isClient ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'">
                {{ formData.step2.isClient ? "Yes" : "No" }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div class="border border-gray-200 rounded-xl bg-white">
        <div class="flex items-center justify-between p-2.5 px-3 border-b border-gray-200">
          <div class="text-xl font-semibold text-gray-900">Case Details</div>
          <button class="flex items-center gap-2 px-3 py-1.5 bg-gray-100 text-gray-700 rounded-md text-sm hover:bg-gray-200 transition-colors" @click="goToStep(3)">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Edit
          </button>
        </div>
        <div class="p-2.5 px-3 grid grid-cols-2 gap-2.5">
          <div class="col-span-2">
            <div class="font-semibold text-gray-500 text-sm">Case Narrative</div>
            <div class="text-gray-900">{{ formData.step3.narrative || "N/A" }}</div>
          </div>
          <div>
            <div class="font-semibold text-gray-500 text-sm">GBV Related</div>
            <div>
              <span class="inline-block px-2 py-0.5 rounded text-xs font-medium" :class="formData.step3.isGBVRelated ? 'bg-yellow-100 text-yellow-800' : 'bg-blue-100 text-blue-800'">
                {{ formData.step3.isGBVRelated ? "Yes" : "No" }}
              </span>
            </div>
          </div>
          <div>
            <div class="font-semibold text-gray-500 text-sm">Incident Date</div>
            <div class="text-gray-900">{{ formData.step3.incidentDate || "N/A" }}</div>
          </div>
          <div>
            <div class="font-semibold text-gray-500 text-sm">Location</div>
            <div class="text-gray-900">{{ formData.step3.location || "N/A" }}</div>
          </div>
        </div>
      </div>

      <div class="border border-gray-200 rounded-xl bg-white">
        <div class="flex items-center justify-between p-2.5 px-3 border-b border-gray-200">
          <div class="text-xl font-semibold text-gray-900">Classification</div>
          <button class="flex items-center gap-2 px-3 py-1.5 bg-gray-100 text-gray-700 rounded-md text-sm hover:bg-gray-200 transition-colors" @click="goToStep(4)">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Edit
          </button>
        </div>
        <div class="p-2.5 px-3 grid grid-cols-2 gap-2.5">
          <div>
            <div class="font-semibold text-gray-500 text-sm">Department</div>
            <div class="text-gray-900">{{ formatDepartment(formData.step4.department) || "N/A" }}</div>
          </div>
          <div class="col-span-2">
            <div class="font-semibold text-gray-500 text-sm">Categories</div>
            <div>
              <div v-if="formData.step4.categories.length > 0" class="flex flex-wrap gap-1.5 min-h-8 p-1">
                <span v-for="category in formData.step4.categories" :key="category" class="inline-flex items-center gap-1 px-1.5 py-0.5 bg-blue-600 text-white rounded-xl text-xs font-medium">
                  {{ category }}
                </span>
              </div>
              <span v-else class="text-gray-900">N/A</span>
            </div>
          </div>
          <div>
            <div class="font-semibold text-gray-500 text-sm">Priority</div>
            <div>
              <span v-if="formData.step4.priority" class="inline-block px-2 py-0.5 rounded text-xs font-medium" :class="`priority-${formData.step4.priority}`">
                {{ formatPriority(formData.step4.priority) }}
              </span>
              <span v-else class="text-gray-900">N/A</span>
            </div>
          </div>
          <div>
            <div class="font-semibold text-gray-500 text-sm">Status</div>
            <div>
              <span v-if="formData.step4.status" class="inline-block px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                {{ formatStatus(formData.step4.status) }}
              </span>
              <span v-else class="text-gray-900">N/A</span>
            </div>
          </div>
          <div>
            <div class="font-semibold text-gray-500 text-sm">Justice System State</div>
            <div class="text-gray-900">{{ formData.step4.justiceSystemState || "N/A" }}</div>
          </div>
          <div>
            <div class="font-semibold text-gray-500 text-sm">General Assessment</div>
            <div class="text-gray-900">{{ formData.step4.generalAssessment || "N/A" }}</div>
          </div>
          <div>
            <div class="font-semibold text-gray-500 text-sm">Services Offered</div>
            <div class="text-gray-900">{{ formData.step4.servicesOffered || "N/A" }}</div>
          </div>
          <div>
            <div class="font-semibold text-gray-500 text-sm">Referral Source</div>
            <div class="text-gray-900">{{ formData.step4.referralSource || "N/A" }}</div>
          </div>
        </div>
      </div>
    </div>

    <div class="flex gap-3 justify-end mt-6 pt-5 border-t border-gray-200">
      <button type="button" class="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors" @click="goToStep(4)">Back</button>
      <button type="button" class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors" @click="submitCase">Create Case</button>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  currentStep: { type: Number, required: true },
  formData: { type: Object, required: true }
});

const emit = defineEmits(["go-to-step", "submit-case"]);

function goToStep(step) {
  emit("go-to-step", step);
}

function submitCase() {
  emit("submit-case", props.formData);
}

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
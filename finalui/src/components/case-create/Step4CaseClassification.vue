<template>
  <div class="min-h-96">
    <form class="flex flex-col gap-3.5" @submit.prevent="handleFormSubmit">
      <div>
        <div class="text-xl font-semibold text-gray-900 mb-2">Case Classification & Assignment</div>
        <p class="text-sm text-gray-600 mb-5">
          Classify the case and set priority levels for proper handling.
        </p>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-5">
          <div class="mb-5">
            <label class="block font-semibold mb-2 text-gray-900">Department*</label>
            <div class="flex gap-4 mt-2">
              <label class="flex items-center gap-1.5 cursor-pointer">
                <input v-model="localForm.department" type="radio" value="116" required @change="handleDepartmentChange" class="w-4 h-4 text-blue-600" />
                <span class="text-sm">116</span>
              </label>
              <label class="flex items-center gap-1.5 cursor-pointer">
                <input v-model="localForm.department" type="radio" value="labor" required @change="handleDepartmentChange" class="w-4 h-4 text-blue-600" />
                <span class="text-sm">Labor</span>
              </label>
            </div>
            
            <div v-if="showPassportField" class="mt-4 p-4 bg-gray-50 border border-gray-300 rounded-lg animate-fadeIn">
              <label for="client-passport" class="block font-semibold mb-2 text-gray-900">Client's Passport Number</label>
              <input id="client-passport" v-model="localForm.clientPassportNumber" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white text-gray-900 transition-all focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100" placeholder="Enter client's passport number" @input="updateForm" />
            </div>
          </div>

          <div class="mb-5">
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

        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-5">
          <div class="mb-5">
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
          <div class="mb-5">
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

        <div class="mb-5">
          <label for="escalated-to" class="block font-semibold mb-2 text-gray-900">Escalated To</label>
          <select v-model="localForm.escalatedTo" id="escalated-to" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white text-gray-900 transition-all focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100" @change="updateForm">
            <option value="0">None</option>
            <option value="1">Supervisor</option>
            <option value="2">Manager</option>
            <option value="3">Director</option>
            <option value="4">External Agency</option>
            <option value="5">Law Enforcement</option>
          </select>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-5">
          <div class="mb-5">
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
          <div class="mb-5">
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

        <div class="mb-5">
          <BaseOptions
            id="services-offered"
            label="Services Offered"
            v-model="localForm.servicesOffered"
            placeholder="Select services..."
            :category-id="113"
            @selection-change="handleServicesChange"
          />

          <div v-if="showReferralsField" class="mt-4 p-4 bg-gray-50 border border-gray-300 rounded-lg animate-fadeIn">
            <BaseOptions
              id="referrals-type"
              label="Referral Types"
              v-model="localForm.referralsType"
              placeholder="Select referral types..."
              :category-id="114"
              @selection-change="updateForm"
            />
          </div>

          <div v-if="showPoliceField" class="mt-4 p-4 bg-gray-50 border border-gray-300 rounded-lg animate-fadeIn">
            <label for="police-details" class="block font-semibold mb-2 text-gray-900">Police Report Details</label>
            <textarea id="police-details" v-model="localForm.policeDetails" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white text-gray-900 transition-all focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100 resize-vertical" placeholder="Enter police report details, case number, station, etc." rows="3" @input="updateForm"></textarea>
          </div>

          <div v-if="showOthersField" class="mt-4 p-4 bg-gray-50 border border-gray-300 rounded-lg animate-fadeIn">
            <label for="other-services" class="block font-semibold mb-2 text-gray-900">Other Services Details</label>
            <textarea id="other-services" v-model="localForm.otherServicesDetails" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white text-gray-900 transition-all focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100 resize-vertical" placeholder="Please specify the other services provided" rows="3" @input="updateForm"></textarea>
          </div>
        </div>

        <div class="mb-5">
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

        <div class="mb-5">
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

      <div class="flex gap-3 justify-between mt-6 pt-5 border-t border-gray-200">
        <button type="button" class="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors" @click="goToStep(3)">Back</button>
        <div class="flex gap-3">
          <button type="button" class="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors" @click="handleSkipStep">Skip</button>
          <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors">Next</button>
        </div>
      </div>
    </form>
  </div>
</template>

<script setup>
import { reactive, watch, computed, ref } from "vue"
import BaseSelect from "@/components/base/BaseSelect.vue"
import BaseOptions from "@/components/base/BaseOptions.vue"
import AttachmentUpload from "@/components/case-create/AttachmentUpload.vue"

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

const localForm = reactive({ 
  ...props.formData,
  clientPassportNumber: props.formData.clientPassportNumber || '',
  referralsType: props.formData.referralsType || [],
  policeDetails: props.formData.policeDetails || '',
  otherServicesDetails: props.formData.otherServicesDetails || '',
  attachments: props.formData.attachments || [],
  servicesOfferedText: props.formData.servicesOfferedText || []
})

const selectedServicesOptions = ref([])

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

const handleDepartmentChange = () => {
  if (localForm.department !== 'labor') {
    localForm.clientPassportNumber = ''
  }
  updateForm()
}

const handleServicesChange = (selectionData) => {
  localForm.servicesOffered = selectionData.values || []
  localForm.servicesOfferedText = selectionData.options?.map(opt => opt.text) || []
  selectedServicesOptions.value = selectionData.options || []
  
  if (!showReferralsField.value) {
    localForm.referralsType = []
  }
  if (!showPoliceField.value) {
    localForm.policeDetails = ''
  }
  if (!showOthersField.value) {
    localForm.otherServicesDetails = ''
  }
  updateForm()
}

const handleAttachmentUploadComplete = (uploadData) => {
  updateForm()
}

const handleAttachmentUploadError = (errorData) => {
  console.error('Attachment upload error:', errorData)
}

watch(() => props.formData, (newData) => {
  Object.assign(localForm, newData);
}, { deep: true });

const updateForm = () => {
  const updatePayload = {
    ...localForm,
    servicesOfferedSelection: {
      values: localForm.servicesOffered,
      options: selectedServicesOptions.value
    }
  };
  emit("form-update", updatePayload);
};

watch(localForm, (newVal) => {
  const payload = {
    ...newVal,
    servicesOfferedSelection: {
      values: localForm.servicesOffered,
      options: selectedServicesOptions.value
    }
  }
  emit("form-update", payload)
}, { deep: true })

const goToStep = (step) => {
  updateForm();
  emit("step-change", step);
};

const handleSkipStep = () => {
  emit("skip-step", { step: 4, data: localForm });
};

const validateForm = () => {
  const errors = [];
  if (!localForm.department) {
    errors.push('Department selection is required');
  }
  if (!localForm.priority) {
    errors.push('Priority is required');
  }
  if (!localForm.status) {
    errors.push('Status is required');
  }
  if (errors.length > 0) {
    alert('Please fix the following errors:\n\n' + errors.join('\n'));
    return false;
  }
  return true;
};

const handleFormSubmit = () => {
  if (!validateForm()) return;
  
  const completeData = {
    ...localForm,
    servicesOfferedSelection: {
      values: localForm.servicesOffered,
      options: selectedServicesOptions.value
    }
  };
  emit("save-and-proceed", { step: 4, data: completeData });
};
</script>

<style scoped>
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

.animate-fadeIn {
  animation: fadeIn 0.3s ease-in-out;
}
</style>
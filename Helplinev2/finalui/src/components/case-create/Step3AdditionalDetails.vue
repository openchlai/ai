<template>
  <div class="min-h-96">
    <form class="flex flex-col gap-3.5" @submit.prevent="handleFormSubmit">
      <div>
        <div 
          class="text-xl font-semibold mb-2"
          :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
        >
          Additional Case Information
        </div>
        <p 
          class="text-sm mb-5"
          :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
        >
          Add clients, perpetrators, and other relevant case information.
        </p>

        <!-- Clients Section -->
        <div class="mb-5">
          <label 
            class="block font-semibold mb-2"
            :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
          >
            Clients
          </label>
          <div class="flex flex-col gap-3">
            <div v-if="localForm.clients && localForm.clients.length > 0" class="flex flex-col gap-2">
              <div 
                v-for="(client, index) in localForm.clients" 
                :key="`client-${index}`" 
                class="flex items-center justify-between p-3 border rounded-lg"
                :class="isDarkMode 
                  ? 'bg-gray-700 border-transparent' 
                  : 'bg-gray-50 border-transparent'"
              >
                <div>
                  <div 
                    class="font-semibold text-sm"
                    :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
                  >
                    {{ client.name || 'Unnamed Client' }}
                  </div>
                  <div 
                    class="text-xs"
                    :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
                  >
                    {{ client.age ? client.age + ' years' : 'Age unknown' }} • {{ client.sex || 'Gender unknown' }} • {{ client.phone || "No phone" }}
                  </div>
                </div>
                <button 
                  type="button" 
                  class="w-6 h-6 flex items-center justify-center bg-red-600 text-white rounded-full hover:bg-red-700 text-sm transition-all hover:scale-110" 
                  @click="handleRemoveClient(index)" 
                  title="Remove client"
                >
                  <i-mdi-close class="w-4 h-4" />
                </button>
              </div>
            </div>

            <div 
              v-else 
              class="text-center p-5 border border-dashed rounded-lg"
              :class="isDarkMode 
                ? 'text-gray-500 bg-gray-800 border-transparent' 
                : 'text-gray-500 bg-white border-transparent'"
            >
              <i-mdi-account-group class="mx-auto text-3xl mb-2 opacity-50" />
              <p class="text-sm font-medium m-0">No clients added yet</p>
              <p class="text-xs mt-1 opacity-70">Click below to add a client</p>
            </div>

            <button 
              type="button" 
              class="self-start mt-2 px-3 py-1.5 text-white rounded-lg text-sm font-medium transition-colors flex items-center gap-2"
              :class="isDarkMode 
                ? 'bg-gray-600 hover:bg-gray-700' 
                : 'bg-gray-700 hover:bg-gray-800'"
              @click="$emit('open-client-modal')"
            >
              <i-mdi-plus class="w-4 h-4" />
              {{ localForm.clients.length > 0 ? 'Add Another Client' : 'Add Client' }}
            </button>
          </div>
        </div>

        <!-- Perpetrators Section -->
        <div class="mb-5">
          <label 
            class="block font-semibold mb-2"
            :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
          >
            Perpetrators
          </label>
          <div class="flex flex-col gap-3">
            <div v-if="localForm.perpetrators && localForm.perpetrators.length" class="flex flex-col gap-2">
              <div 
                v-for="(perpetrator, index) in localForm.perpetrators" 
                :key="index" 
                class="flex items-center justify-between p-3 border rounded-lg"
                :class="isDarkMode 
                  ? 'bg-gray-700 border-transparent' 
                  : 'bg-gray-50 border-transparent'"
              >
                <div>
                  <div 
                    class="font-semibold text-sm"
                    :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
                  >
                    {{ perpetrator.name || 'Unnamed' }}
                  </div>
                  <div 
                    class="text-xs"
                    :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
                  >
                    {{ perpetrator.age || 'Unknown age' }} • {{ perpetrator.sex || 'Unknown gender' }} • {{ perpetrator.location || 'Unknown location' }}
                  </div>
                </div>
                <button 
                  type="button" 
                  class="w-6 h-6 flex items-center justify-center bg-red-600 text-white rounded-full hover:bg-red-700 text-sm transition-all hover:scale-110" 
                  @click="handleRemovePerpetrator(index)"
                >
                  <i-mdi-close class="w-4 h-4" />
                </button>
              </div>
            </div>
            <div 
              v-else 
              class="p-5 text-center italic border border-dashed rounded-lg"
              :class="isDarkMode 
                ? 'text-gray-500 bg-gray-800 border-transparent' 
                : 'text-gray-500 bg-white border-transparent'"
            >
              <p class="text-sm m-0">No perpetrators added yet</p>
            </div>
            <button 
              type="button" 
              class="self-start mt-2 px-3 py-1.5 text-white rounded-lg text-sm font-medium transition-colors flex items-center gap-2"
              :class="isDarkMode 
                ? 'bg-amber-600 hover:bg-amber-700' 
                : 'bg-amber-700 hover:bg-amber-800'"
              @click="$emit('open-perpetrator-modal')"
            >
              <i-mdi-plus class="w-4 h-4" />
              Add Perpetrator
            </button>
          </div>
        </div>

        <!-- Services Offered -->
        <div class="mb-5">
          <BaseOptions
            id="services-offered"
            label="Services Offered"
            v-model="localForm.servicesOffered"
            placeholder="Select services..."
            :category-id="113"
            @selection-change="handleServicesChange"
          />

          <div 
            v-if="showReferralsField" 
            class="mt-4 p-4 border rounded-lg animate-fadeIn"
            :class="isDarkMode 
              ? 'bg-gray-800 border-transparent' 
              : 'bg-gray-50 border-transparent'"
          >
            <BaseOptions
              id="referrals-type"
              label="Referral Types"
              v-model="localForm.referralsType"
              placeholder="Select referral types..."
              :category-id="236707"
              @selection-change="updateForm"
            />
          </div>

          <div 
            v-if="showPoliceField" 
            class="mt-4 p-4 border rounded-lg animate-fadeIn"
            :class="isDarkMode 
              ? 'bg-gray-800 border-transparent' 
              : 'bg-gray-50 border-transparent'"
          >
            <label 
              for="police-details" 
              class="block font-semibold mb-2"
              :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
            >
              Police Report Details
            </label>
            <textarea 
              id="police-details" 
              v-model="localForm.policeDetails" 
              class="w-full px-3 py-2 border rounded-lg text-sm transition-all focus:outline-none focus:ring-2 focus:border-transparent resize-vertical"
              :class="isDarkMode 
                ? 'bg-gray-700 border-transparent text-gray-100 placeholder-gray-500 focus:ring-amber-500' 
                : 'bg-white border-transparent text-gray-900 placeholder-gray-400 focus:ring-amber-600'"
              placeholder="Enter police report details, case number, station, etc." 
              rows="3" 
              @input="updateForm"
            ></textarea>
          </div>

          <div 
            v-if="showOthersField" 
            class="mt-4 p-4 border rounded-lg animate-fadeIn"
            :class="isDarkMode 
              ? 'bg-gray-800 border-transparent' 
              : 'bg-gray-50 border-transparent'"
          >
            <label 
              for="other-services" 
              class="block font-semibold mb-2"
              :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
            >
              Other Services Details
            </label>
            <textarea 
              id="other-services" 
              v-model="localForm.otherServicesDetails" 
              class="w-full px-3 py-2 border rounded-lg text-sm transition-all focus:outline-none focus:ring-2 focus:border-transparent resize-vertical"
              :class="isDarkMode 
                ? 'bg-gray-700 border-transparent text-gray-100 placeholder-gray-500 focus:ring-amber-500' 
                : 'bg-white border-transparent text-gray-900 placeholder-gray-400 focus:ring-amber-600'"
              placeholder="Please specify the other services provided" 
              rows="3" 
              @input="updateForm"
            ></textarea>
          </div>
        </div>

        <!-- How did you know about 116? -->
        <div class="mb-5">
          <BaseSelect
            id="know about 116"
            label="How did you know about 116?"
            v-model="localForm.referralSource"
            placeholder="Select an option"
            :category-id="236700"
            @change="updateForm"
          />
        </div>

        <!-- Attachments -->
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

      <div 
        class="flex gap-3 justify-between mt-6 pt-5 border-t"
        :class="isDarkMode ? 'border-transparent' : 'border-transparent'"
      >
        <button 
          type="button" 
          class="px-4 py-2 border rounded-lg transition-colors"
          :class="isDarkMode 
            ? 'bg-gray-700 text-gray-300 border-transparent hover:bg-gray-600' 
            : 'bg-white text-gray-700 border-transparent hover:bg-gray-50'"
          @click="goToStep(2)"
        >
          Back
        </button>
        <div class="flex gap-3">
          <button 
            type="submit" 
            class="px-4 py-2 text-white rounded-lg transition-colors"
            :class="isDarkMode 
              ? 'bg-amber-600 hover:bg-amber-700' 
              : 'bg-amber-700 hover:bg-amber-800'"
          >
            Continue to Review
          </button>
        </div>
      </div>
    </form>
  </div>
</template>

<script setup>
import { reactive, watch, computed, ref, inject } from "vue"
import BaseSelect from "@/components/base/BaseSelect.vue"
import BaseOptions from "@/components/base/BaseOptions.vue"
import AttachmentUpload from "@/components/case-create/AttachmentUpload.vue"

const props = defineProps({
  currentStep: { type: Number, required: true },
  formData: { type: Object, required: true }
})

const emit = defineEmits([
  "form-update",
  "open-client-modal",
  "open-perpetrator-modal",
  "remove-client",
  "remove-perpetrator",
  "save-and-proceed",
  "step-change"
])

// Inject theme
const isDarkMode = inject('isDarkMode')

const localForm = reactive({ ...props.formData })
const selectedServicesOptions = ref([])

watch(() => props.formData, (newData) => {
  Object.assign(localForm, newData)
}, { deep: true })

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

const handleRemoveClient = (index) => {
  emit('remove-client', index)
}

const handleRemovePerpetrator = (index) => {
  emit('remove-perpetrator', index)
}

function updateForm() {
  const payload = {
    ...localForm,
    servicesOfferedSelection: {
      values: localForm.servicesOffered,
      options: selectedServicesOptions.value
    }
  }
  emit("form-update", payload)
}

function goToStep(step) {
  updateForm()
  emit("step-change", step)
}

function handleFormSubmit() {
  const payload = {
    step: 3,
    data: {
      ...localForm,
      servicesOfferedSelection: {
        values: localForm.servicesOffered,
        options: selectedServicesOptions.value
      }
    }
  }
  emit("save-and-proceed", payload)
}
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
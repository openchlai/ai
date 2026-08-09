<template>
  <div class="min-h-96">
    <form class="flex flex-col gap-3.5" @submit.prevent="handleFormSubmit">
      <div>
        <div class="text-xl font-semibold text-gray-900 mb-2">
          {{ selectedReporter ? "Reporter Details" : "New Reporter Information" }}
        </div>
        <p class="text-sm text-gray-600 mb-5">
          Enter the reporter's contact information and details.
        </p>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-5">
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

        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-5">
          <BaseInput
            id="reporter-dob"
            label="DOB"
            type="date"
            v-model="formData.dob"
            @input="handleDobChange"
          />
          <BaseSelect
            id="reporter-age-group"
            label="Age Group"
            v-model="formData.ageGroup"
            placeholder="Select age group"
            :category-id="101"
          />
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-5">
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

        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-5">
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

        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-5">
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

        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-5">
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

        <div class="mb-5">
          <BaseInput
            id="reporter-email"
            label="Email Address"
            type="email"
            v-model="formData.email"
            placeholder="Enter email address"
          />
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-5">
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

        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-5">
          <div class="mb-5">
            <label class="block font-semibold mb-2 text-gray-900">Is Reporter also a Client?</label>
            <div class="flex gap-4">
              <label class="flex items-center gap-1.5 cursor-pointer">
                <input v-model="formData.isClient" type="radio" :value="true" @change="handleClientSelection" class="w-4 h-4 text-blue-600" />
                <span class="text-sm">Yes</span>
              </label>
              <label class="flex items-center gap-1.5 cursor-pointer">
                <input v-model="formData.isClient" type="radio" :value="false" @change="handleClientSelection" class="w-4 h-4 text-blue-600" />
                <span class="text-sm">No</span>
              </label>
            </div>
          </div>

          <div class="mb-5">
            <label class="block font-semibold mb-2 text-gray-900">Perpetrators</label>
            <div class="flex flex-col gap-3">
              <div v-if="formData.perpetrators && formData.perpetrators.length" class="flex flex-col gap-2">
                <div v-for="(perpetrator, index) in formData.perpetrators" :key="index" class="flex items-center justify-between p-3 bg-gray-50 border border-gray-200 rounded-lg">
                  <div>
                    <div class="font-semibold text-gray-900 text-sm">{{ perpetrator.name || 'Unnamed' }}</div>
                    <div class="text-xs text-gray-600">{{ perpetrator.age || 'Unknown age' }} {{ perpetrator.sex || 'Unknown gender' }} - {{ perpetrator.location || 'Unknown location' }}</div>
                  </div>
                  <button type="button" class="w-6 h-6 flex items-center justify-center bg-red-500 text-white rounded-full hover:bg-red-600 text-sm transition-all hover:scale-110" @click="removePerpetrator(index)">×</button>
                </div>
              </div>
              <div v-else class="p-5 text-center text-gray-500 italic bg-gray-50 border border-dashed border-gray-300 rounded-lg">
                <p class="text-sm m-0">No perpetrators added yet</p>
              </div>
              <button type="button" class="self-start mt-2 px-3 py-1.5 bg-blue-600 text-white rounded text-sm font-medium hover:bg-blue-700 transition-colors" @click="openPerpetratorModal">+ Add Perpetrator</button>
            </div>
          </div>
        </div>

        <div class="mb-5">
          <label class="block font-semibold mb-2 text-gray-900">Clients</label>
          <div class="flex flex-col gap-3">
            <div v-if="formData.clients && formData.clients.length > 0" class="flex flex-col gap-2">
              <div v-for="(client, index) in formData.clients" :key="`client-${index}`" class="flex items-center justify-between p-3 bg-gray-50 border rounded-lg" :class="client.isReporter ? 'border-blue-500 bg-blue-50' : 'border-gray-200'">
                <div>
                  <div class="font-semibold text-gray-900 text-sm">
                    {{ client.name || 'Unnamed Client' }}
                    <span v-if="client.isReporter" class="inline-block bg-blue-600 text-white px-2 py-0.5 rounded-xl text-xs font-medium ml-2 align-top">Reporter</span>
                  </div>
                  <div class="text-xs text-gray-600">{{ client.age ? client.age + ' years' : 'Age unknown' }} • {{ client.sex || 'Gender unknown' }} • {{ client.phone || "No phone" }}</div>
                </div>
                <button v-if="!client.isReporter" type="button" class="w-6 h-6 flex items-center justify-center bg-red-500 text-white rounded-full hover:bg-red-600 text-sm transition-all hover:scale-110" @click="removeClient(index)" title="Remove client">×</button>
                <span v-else class="text-xs text-gray-500 italic px-2 py-1">Auto-added</span>
              </div>
            </div>

            <div v-else class="text-center p-5 text-gray-500 bg-gray-50 border border-dashed border-gray-300 rounded-lg">
              <div class="text-3xl mb-2 opacity-50">👥</div>
              <p class="text-sm font-medium m-0">No clients added yet</p>
              <p class="text-xs mt-1 opacity-70">{{ formData.isClient === true ? 'Reporter will be added as client automatically' : 'Click below to add a client' }}</p>
            </div>

            <button type="button" class="self-start mt-2 px-3 py-1.5 bg-gray-600 text-white rounded text-sm font-medium hover:bg-gray-700 transition-colors" @click="handleAddClient">
              <span class="mr-1">+</span>{{ formData.clients.length > 0 ? 'Add Another Client' : 'Add Client' }}
            </button>
          </div>
        </div>

      </div>

      <div class="flex gap-3 justify-between mt-6 pt-5 border-t border-gray-200">
        <button type="button" class="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors" @click="goToStep(1)">Back</button>
        <div class="flex gap-3">
          <button type="button" class="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors" @click="handleSkipStep">Skip</button>
          <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors">Next</button>
        </div>
      </div>
    </form>
  </div>
</template>

<script setup>
import BaseInput from "@/components/base/BaseInput.vue";
import BaseSelect from "@/components/base/BaseSelect.vue";

const props = defineProps({
  currentStep: { type: Number, required: true },
  selectedReporter: { type: Object, default: null },
  formData: { type: Object, required: true },
});

const emit = defineEmits([
  "update:formData",
  "step-change",
  "skip-step",
  "save-step",
  "open-perpetrator-modal",
  "open-client-modal",
  "remove-client",
  "remove-perpetrator"
]);

const goToStep = (step) => {
  emit("update:formData", props.formData);
  emit("step-change", step);
};

const handleSkipStep = () => {
  emit("skip-step", { step: 2, data: props.formData });
};

const handleFormSubmit = () => {
  if (!validateForm()) return;
  emit("save-step", { step: 2, data: props.formData });
};

const validateForm = () => {
  const errors = [];
  if (!props.formData.name?.trim()) errors.push('Full Name is required');
  if (!props.formData.phone?.trim()) errors.push('Phone Number is required');
  if (errors.length > 0) {
    alert('Please fix the following errors:\n\n' + errors.join('\n'));
    return false;
  }
  return true;
};

const removePerpetrator = (index) => {
  emit("remove-perpetrator", index);
};

const removeClient = (index) => {
  emit("remove-client", index);
};

const openPerpetratorModal = () => {
  emit("open-perpetrator-modal");
};

const handleAddClient = () => {
  emit("open-client-modal");
};

const calculateAge = (dob) => {
  if (!dob) return null;
  const birthDate = new Date(dob);
  const today = new Date();
  let age = today.getFullYear() - birthDate.getFullYear();
  const monthDiff = today.getMonth() - birthDate.getMonth();
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
    age--;
  }
  return age >= 0 ? age : null;
};

const getAgeGroup = (age) => {
  if (!age || age < 0) return '';
  if (age < 6) return '0-5';
  if (age <= 12) return '6-12';
  if (age <= 17) return '13-17';
  if (age <= 25) return '18-25';
  if (age <= 35) return '26-35';
  if (age <= 50) return '36-50';
  return '51+';
};

const handleDobChange = (event) => {
  const dob = event.target ? event.target.value : event;
  if (dob) {
    const calculatedAge = calculateAge(dob);
    const ageGroup = getAgeGroup(calculatedAge);
    props.formData.dob = dob;
    if (calculatedAge !== null) {
      props.formData.age = calculatedAge.toString();
      props.formData.ageGroup = ageGroup;
    }
    emit("update:formData", props.formData);
  } else {
    props.formData.age = '';
    props.formData.ageGroup = '';
    emit("update:formData", props.formData);
  }
};

const handleClientSelection = () => {
  if (props.formData.isClient === true) {
    const reporterAsClient = {
      name: props.formData.name || '',
      age: props.formData.age || '',
      dob: props.formData.dob || '',
      ageGroup: props.formData.ageGroup || '',
      location: props.formData.location || '',
      sex: props.formData.gender || '',
      landmark: props.formData.nearestLandmark || '',
      nationality: props.formData.nationality || '',
      idType: props.formData.idType || '',
      idNumber: props.formData.idNumber || '',
      language: props.formData.language || '',
      tribe: props.formData.tribe || '',
      phone: props.formData.phone || '',
      alternativePhone: props.formData.altPhone || '',
      email: props.formData.email || '',
      isReporter: true,
      relationship: 'Self',
      relationshipComment: 'Reporter is also the client'
    };

    const existingReporterIndex = props.formData.clients.findIndex(client => client.isReporter);
    if (existingReporterIndex >= 0) {
      props.formData.clients[existingReporterIndex] = reporterAsClient;
    } else {
      props.formData.clients.unshift(reporterAsClient);
    }
  } else if (props.formData.isClient === false) {
    props.formData.clients = props.formData.clients.filter(client => !client.isReporter);
  }
  props.formData.clients = props.formData.clients || [];
  emit("update:formData", props.formData);
};
</script>
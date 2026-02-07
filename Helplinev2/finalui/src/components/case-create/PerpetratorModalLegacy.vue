<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <!-- Backdrop -->
    <div class="fixed inset-0 bg-black/50 backdrop-blur-sm transition-opacity" @click="$emit('close')"></div>

    <!-- Modal Content -->
    <div
      class="relative bg-white dark:bg-neutral-900 rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto flex flex-col">
      <!-- Header -->
      <div class="flex items-center justify-between p-6 border-b dark:border-neutral-800">
        <h3 class="text-xl font-bold dark:text-white">New Perpetrator</h3>
        <button @click="$emit('close')"
          class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">
          <i-mdi-close class="w-6 h-6" />
        </button>
      </div>

      <!-- Form Body -->
      <div class="p-6 space-y-6 flex-1 overflow-y-auto">
        <!-- Row 1: Name, Age, DOB, Age Group -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <BaseInput label="Perpetrator Name" v-model="form.name" placeholder="Name" />
          <BaseInput label="Age" type="number" v-model="form.age" placeholder="Age" />
          <BaseInput label="DOB" type="date" v-model="form.dob" />
          <TaxonomySelect label="Age Group" v-model="form.ageGroup" root-key="AGE_GROUP" placeholder="Select" />
        </div>

        <!-- Row 2: Location, Sex -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <TaxonomySelect label="Location" v-model="form.location" root-key="LOCATION" placeholder="Select Location"
            :searchable="true" />
          <TaxonomySelect label="Sex" v-model="form.sex" root-key="GENDER" placeholder="Select Sex" />
        </div>

        <!-- Row 3: Landmark, Nationality -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <BaseInput label="Nearest Landmark" v-model="form.landmark" placeholder="Landmark" />
          <TaxonomySelect label="Nationality" v-model="form.nationality" root-key="NATIONALITY"
            placeholder="Select Nationality" />
        </div>

        <!-- Row 4: ID Type, ID Number, Language -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <TaxonomySelect label="ID Type" v-model="form.idType" root-key="ID_TYPE" placeholder="Select Type" />
          <BaseInput label="ID Number" v-model="form.idNumber" placeholder="ID Number" />
          <TaxonomySelect label="Language" v-model="form.language" root-key="LANGUAGE" placeholder="Select Language" />
        </div>

        <!-- Row 5: Refugee, Tribe -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-semibold mb-2"
              :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'">Refugee?</label>
            <div class="flex gap-4">
              <label class="flex items-center gap-2"><input type="radio" v-model="form.isRefugee" value="1"
                  class="text-[#003366] dark:text-[#2DD4BF] focus:ring-[#003366] dark:focus:ring-[#2DD4BF]"> Yes</label>
              <label class="flex items-center gap-2"><input type="radio" v-model="form.isRefugee" value="0"
                  class="text-[#003366] dark:text-[#2DD4BF] focus:ring-[#003366] dark:focus:ring-[#2DD4BF]"> No</label>
              <label class="flex items-center gap-2"><input type="radio" v-model="form.isRefugee" value="2"
                  class="text-[#003366] dark:text-[#2DD4BF] focus:ring-[#003366] dark:focus:ring-[#2DD4BF]">
                Unknown</label>
            </div>
          </div>

          <TaxonomySelect label="Tribe" v-model="form.tribe" root-key="TRIBE" placeholder="Select Tribe" />
        </div>

        <!-- Row 6: Phones, Email -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <BaseInput label="Phone Number" v-model="form.phone" placeholder="Phone" />
          <BaseInput label="Alternative Phone" v-model="form.alternativePhone" placeholder="Alt Phone" />
          <BaseInput label="Email" v-model="form.email" placeholder="Email" />
        </div>

        <!-- Row 7: Relationship, Shares Home -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <TaxonomySelect label="Relationship with Client?" v-model="form.relationship" root-key="RELATIONSHIP"
            placeholder="Select Relationship" />

          <div>
            <label class="block text-sm font-semibold mb-2"
              :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'">Shares Home with Client?</label>
            <div class="flex gap-4">
              <!-- Assuming this is dropdown as per prompt, but 'Yes/No' usually imply radio/select. Prompt says dropdown. -->
              <!-- If it's a dropdown, I need a category-id. Or just options. -->
              <!-- I'll use simple select with yes/no hardcoded if no category. Or just re-use BaseSelect with generic yesno category if I knew it. -->
              <!-- I'll simulate a dropdown with <select> since BaseSelect needs categoryId usually. Or I use BaseSelect if I know category. -->
              <!-- Wait, for simple Yes/No dropdown, I can use a standard selector or assume category exists. -->
              <!-- Prompt: Shares Home with Client? (dropdown) -->
              <!-- I'll use a hardcoded select styled like BaseSelect -->
              <select v-model="form.sharesHome"
                class="w-full px-4 py-3 border rounded-lg text-sm bg-gray-50 focus:ring-2 focus:ring-[#003366] dark:focus:ring-[#2DD4BF] outline-none dark:bg-gray-700 dark:border-transparent dark:text-gray-100">
                <option value="">Select Option</option>
                <option value="1">Yes</option>
                <option value="0">No</option>
                <option value="2">Unknown</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Row 8: Health, Profession, Marital -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <TaxonomySelect label="Health Status" v-model="form.healthStatus" root-key="HEALTH_STATUS"
            placeholder="Select Health" />
          <TaxonomySelect label="Profession" v-model="form.profession" root-key="OCCUPATION"
            placeholder="Select Profession" />
          <TaxonomySelect label="Marital Status" v-model="form.maritalStatus" root-key="MARITAL_STATUS"
            placeholder="Select Status" />
        </div>

        <!-- Row 9: Guardian Name -->
        <div>
          <BaseInput label="Guardian Name" v-model="form.guardianName" placeholder="Guardian Name" />
        </div>

        <!-- Row 10: Additional Details -->
        <div>
          <BaseTextarea label="Additional Details" v-model="form.additionalDetails" placeholder="Details..."
            :rows="3" />
        </div>

      </div>

      <!-- Footer -->
      <div
        class="p-6 border-t dark:border-neutral-800 flex justify-end gap-4 bg-gray-50 dark:bg-neutral-900/50 rounded-b-xl">
        <button @click="$emit('close')" class="px-6 py-2.5 rounded-lg border font-medium transition-colors"
          :class="isDarkMode ? 'border-neutral-700 text-gray-300 hover:bg-neutral-800' : 'border-gray-300 text-gray-700 hover:bg-gray-100'">
          Cancel
        </button>
        <button @click="handleCreate" class="px-6 py-2.5 rounded-lg font-medium text-white transition-colors shadow-sm"
          :class="isDarkMode ? 'bg-[#008080] hover:bg-[#006666]' : 'bg-[#003366] hover:bg-[#002244]'">
          Create
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
  import { reactive, watch, inject, ref } from 'vue';
  import BaseInput from '@/components/base/BaseInput.vue';
  import BaseSelect from '@/components/base/BaseSelect.vue';
  import BaseTextarea from '@/components/base/BaseTextarea.vue';
  import TaxonomySelect from '@/components/base/TaxonomySelect.vue';
  import { useAgeCalculator } from '@/composables/useAgeCalculator';

  const props = defineProps({
    isOpen: Boolean,
    perpetratorData: {
      type: Object,
      default: () => ({})
    }
  });

  const emit = defineEmits(['close', 'create']);
  const isDarkMode = inject('isDarkMode');
  const { getAgeGroupId, calculateAgeFromDob, calculateDobFromAge } = useAgeCalculator();

  const form = reactive({
    name: '',
    age: '',
    dob: '',
    ageGroup: '',
    location: '',
    sex: '',
    landmark: '',
    nationality: '',
    idType: '',
    idNumber: '',
    language: '',
    isRefugee: '',
    tribe: '',
    phone: '',
    alternativePhone: '',
    email: '',
    relationship: '',
    sharesHome: '',
    healthStatus: '',
    profession: '',
    maritalStatus: '',
    guardianName: '',
    additionalDetails: ''
  });

  // Sync
  watch(() => props.isOpen, (val) => {
    if (val && props.perpetratorData) {
      Object.assign(form, props.perpetratorData);
    } else if (val) {
      // Reset keys if new
      Object.keys(form).forEach(k => form[k] = '');
    }
  });

  // Age Calculation
  const isAutoUpdating = ref(false);

  watch(() => form.dob, (newDob) => {
    if (isAutoUpdating.value) return;
    if (newDob) {
      const age = calculateAgeFromDob(newDob);
      if (age !== form.age) {
        isAutoUpdating.value = true;
        form.age = age;
        form.ageGroup = getAgeGroupId(age);
        setTimeout(() => isAutoUpdating.value = false, 0);
      }
    }
  });

  watch(() => form.age, (newAge) => {
    if (isAutoUpdating.value) return;
    if (newAge) {
      isAutoUpdating.value = true;
      form.ageGroup = getAgeGroupId(newAge);

      const currentAgeFromDob = calculateAgeFromDob(form.dob);
      if (currentAgeFromDob !== newAge) {
        form.dob = calculateDobFromAge(newAge);
      }
      setTimeout(() => isAutoUpdating.value = false, 0);
    }
  });

  const handleCreate = () => {
    emit('create', { ...form });
    emit('close');
  };
</script>

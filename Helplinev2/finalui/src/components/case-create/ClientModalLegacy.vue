<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <!-- Backdrop -->
    <div class="fixed inset-0 bg-black/50 backdrop-blur-sm transition-opacity" @click="$emit('close')"></div>

    <!-- Modal Content -->
    <div class="relative bg-white dark:bg-neutral-900 rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto flex flex-col">
      <!-- Header -->
      <div class="flex items-center justify-between p-6 border-b dark:border-neutral-800">
        <h3 class="text-xl font-bold dark:text-white">Edit Client Details</h3>
        <button @click="$emit('close')" class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">
          <i-mdi-close class="w-6 h-6" />
        </button>
      </div>

      <!-- Form Body -->
      <div class="p-6 space-y-6 flex-1 overflow-y-auto">
        <!-- Row 1: Name, Age, DOB, Age Group -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <BaseInput label="Client Name" v-model="form.name" placeholder="Name" />
          <BaseInput label="Age" type="number" v-model="form.age" placeholder="Age" />
          <BaseInput label="DOB" type="date" v-model="form.dob" />
          <TaxonomySelect label="Age Group" v-model="form.ageGroup" root-key="AGE_GROUP" placeholder="Select" />
        </div>

        <!-- Row 2: Location, Sex -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <TaxonomySelect label="Location" v-model="form.location" root-key="LOCATION" placeholder="Select Location" :searchable="true" />
          <TaxonomySelect label="Sex" v-model="form.sex" root-key="GENDER" placeholder="Select Sex" />
        </div>

        <!-- Row 3: Landmark, Nationality -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <BaseInput label="Nearest Landmark" v-model="form.landmark" placeholder="Landmark" />
          <TaxonomySelect label="Nationality" v-model="form.nationality" root-key="NATIONALITY" placeholder="Select Nationality" />
        </div>

        <!-- Row 4: Phones, Email -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <BaseInput label="Phone Number" v-model="form.phone" placeholder="Phone" />
          <BaseInput label="Alternative Phone" v-model="form.alternativePhone" placeholder="Alt Phone" />
          <BaseInput label="Email" v-model="form.email" placeholder="Email" />
        </div>

        <!-- Row 5: Relationship, Comment -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <TaxonomySelect label="Reporter’s Relationship with Client" v-model="form.relationship" root-key="RELATIONSHIP" placeholder="Select Relationship" />
          <BaseTextarea label="Relationship Comment" v-model="form.relationshipComment" placeholder="Comment..." :rows="1" />
        </div>

        <!-- Row 6: Household Info -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <BaseInput label="Number of Adults in Household" type="number" v-model="form.adultsInHousehold" placeholder="#" />
          <TaxonomySelect label="Household Type" v-model="form.householdType" root-key="HOUSEHOLD_TYPE" placeholder="Select Type" />
          <TaxonomySelect label="Head of Household Occupation" v-model="form.headOccupation" root-key="OCCUPATION" placeholder="Select Occupation" />
        </div>

        <!-- Row 7: Parent Info -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <BaseInput label="Parent/Guardian Name" v-model="form.parentGuardianName" placeholder="Name" />
          <TaxonomySelect label="Parent/Guardian Marital Status" v-model="form.parentMaritalStatus" root-key="MARITAL_STATUS" placeholder="Select Status" />
        </div>

        <!-- Row 8: Parent ID -->
        <div>
           <BaseInput label="Parent/Guardian Identification Number" v-model="form.parentIdNumber" placeholder="ID Number" />
        </div>

        <!-- Row 9: Health, HIV, Marital -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <TaxonomySelect label="Client Health Status" v-model="form.healthStatus" root-key="HEALTH_STATUS" placeholder="Select Health" />
          <TaxonomySelect label="Client HIV Status" v-model="form.hivStatus" root-key="HIV_STATUS" placeholder="Select HIV Status" />
          <TaxonomySelect label="Client Marital Status" v-model="form.maritalStatus" root-key="MARITAL_STATUS" placeholder="Select Marital Status" />
        </div>

        <!-- Row 10: School, Disabled -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
           <div>
              <label class="block text-sm font-semibold mb-2" :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'">Attending School?</label>
              <div class="flex gap-4">
                 <label class="flex items-center gap-2"><input type="radio" v-model="form.attendingSchool" value="1" class="text-amber-600 focus:ring-amber-500"> Yes</label>
                 <label class="flex items-center gap-2"><input type="radio" v-model="form.attendingSchool" value="0" class="text-amber-600 focus:ring-amber-500"> No</label>
                 <label class="flex items-center gap-2"><input type="radio" v-model="form.attendingSchool" value="2" class="text-amber-600 focus:ring-amber-500"> Unknown</label>
              </div>
           </div>
           
           <div>
              <label class="block text-sm font-semibold mb-2" :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'">Disabled?</label>
              <div class="flex gap-4">
                 <label class="flex items-center gap-2"><input type="radio" v-model="form.isDisabled" value="1" class="text-amber-600 focus:ring-amber-500"> Yes</label>
                 <label class="flex items-center gap-2"><input type="radio" v-model="form.isDisabled" value="0" class="text-amber-600 focus:ring-amber-500"> No</label>
                 <label class="flex items-center gap-2"><input type="radio" v-model="form.isDisabled" value="2" class="text-amber-600 focus:ring-amber-500"> Unknown</label>
              </div>
           </div>
        </div>

      </div>

      <!-- Footer -->
      <div class="p-6 border-t dark:border-neutral-800 flex justify-end gap-4 bg-gray-50 dark:bg-neutral-900/50 rounded-b-xl">
        <button 
          @click="$emit('close')" 
          class="px-6 py-2.5 rounded-lg border font-medium transition-colors"
          :class="isDarkMode ? 'border-neutral-700 text-gray-300 hover:bg-neutral-800' : 'border-gray-300 text-gray-700 hover:bg-gray-100'"
        >
          Cancel
        </button>
        <button 
          @click="handleUpdate" 
          class="px-6 py-2.5 rounded-lg font-medium text-white transition-colors shadow-sm"
          :class="isDarkMode ? 'bg-amber-600 hover:bg-amber-700' : 'bg-amber-700 hover:bg-amber-800'"
        >
          Update
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
  clientData: {
    type: Object,
    default: () => ({})
  }
});

const emit = defineEmits(['close', 'update']);
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
   phone: '',
   alternativePhone: '',
   email: '',
   relationship: '',
   relationshipComment: '',
   adultsInHousehold: '',
   householdType: '',
   headOccupation: '',
   parentGuardianName: '',
   parentMaritalStatus: '',
   parentIdNumber: '',
   healthStatus: '',
   hivStatus: '',
   maritalStatus: '',
   attendingSchool: '',
   isDisabled: ''
});

// Sync
watch(() => props.isOpen, (val) => {
  if (val && props.clientData) {
     Object.assign(form, props.clientData);
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

const handleUpdate = () => {
  emit('update', { ...form });
  emit('close');
};
</script>

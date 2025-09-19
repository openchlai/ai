<template>
  <div class="case-creation-container">
    <!-- Header Component -->
    <CaseHeader 
      :isAIEnabled="isAIEnabled" 
      @toggle-ai="handleAIToggle"
    />
    
    <!-- Progress Tracker Component -->
    <ProgressTracker 
      :currentStep="currentStep"
      :totalSteps="totalSteps"
      :stepStatus="stepStatus"
      :stepLabels="stepLabels"
      @step-change="navigateToStep"
    />
    
    <!-- Step Content Components -->
    <Step1ReporterSelection
  v-if="currentStep === 1"
  :currentStep="currentStep"
  :searchQuery="formData.step1.searchQuery"
  :filteredContacts="formData.step1.filteredContacts"
  :selectedReporter="formData.step1.selectedReporter"
  @search-change="handleSearchChange"
  @select-reporter="selectExistingReporter"
  @create-new-reporter="createNewReporter"
  @validate-and-proceed="validateAndProceed(1)"
  @skip-step="skipStep(1)"
  @cancel-form="cancelForm"
/>

    
   <Step2ReporterDetails
  v-if="currentStep === 2"
  :formData="formData.step2"
  :currentStep="currentStep"
  @update:formData="(val) => (formData.step2 = val)"
  @step-change="goToStep"
  @skip-step="skipStep"
  @save-step="saveStep"
  @open-client-modal="openClientModal"
  @open-perpetrator-modal="openPerpetratorModal"
/>
 
    <Step3CaseDetails
      v-if="currentStep === 3"
       :currentStep="currentStep"
      :formData="formData.step3"
      @form-update="updateFormData('step3', $event)"
      @save-and-proceed="saveAndProceed(3)"
      @go-to-step="goToStep(3)"
      @skip-step="skipStep(3)"
    />
    
    <Step4CaseClassification
      v-if="currentStep === 4"
      :formData="formData.step4"
      :clientSearchResults="clientSearchResults"
      :hasSearched="hasSearched"
      @form-update="updateFormData('step4', $event)"
      @search-client-by-passport="searchClientByPassport"
      @select-client="selectClient"
      @create-new-client="createNewClient"
      @save-and-proceed="saveAndProceed(4)"
      @go-to-step="goToStep(4)"
      @skip-step="skipStep(4)"
    />
    
    <Step5Review
  v-if="currentStep === 5"
  :currentStep="currentStep"
  :formData="formData"
  @go-to-step="goToStep"
  @submit-case="submitCase"
/>
    
    <!-- Modals -->
    <ClientModal
      v-if="clientModalOpen"
      :clients="formData.step2.clients"
      :clientForm="clientForm"
      :currentClientStep="currentClientStep"
      :showSpecialServicesDropdown="showSpecialServicesDropdown"
      :specialServicesSearch="specialServicesSearch"
      :filteredSpecialServices="filteredSpecialServices"
      @close-modal="closeClientModal"
      @remove-client="removeClient"
      @update-client-form="updateClientForm"
      @toggle-special-services-dropdown="toggleSpecialServicesDropdown"
      @prev-client-step="prevClientStep"
      @next-client-step="nextClientStep"
      @add-client="addClient"
    />
    
   <PerpetratorModal
  v-if="perpetratorModalOpen"
  :perpetrators="formData.step2.perpetrators"
  :perpetratorForm="perpetratorForm"
  :currentPerpetratorStep="currentPerpetratorStep"
  :perpetratorModalOpen="perpetratorModalOpen"
  @close-modal="closePerpetratorModal"
  @remove-perpetrator="removePerpetrator"
  @update-perpetrator-form="updatePerpetratorForm"
  @prev-perpetrator-step="prevPerpetratorStep"
  @next-perpetrator-step="nextPerpetratorStep"
  @add-perpetrator="addPerpetrator"
/>

  </div>
</template>

<script>
import { ref, reactive, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useCaseStore } from '@/stores/cases';

// Import components
import CaseHeader from '@/components/cases/CaseHeader.vue';
import ProgressTracker from '@/components/cases/ProgressTracker.vue';
import Step1ReporterSelection from '@/components/cases/Step1ReporterSelection.vue';
import Step2ReporterDetails from '@/components/cases/Step2ReporterDetails.vue';
import Step3CaseDetails from '@/components/cases/Step3CaseDetails.vue';
import Step4CaseClassification from '@/components/cases/Step4CaseClassification.vue';
import Step5Review from '@/components/cases/Step5Review.vue';
import ClientModal from '@/components/cases/ClientModal.vue';
import PerpetratorModal from '@/components/cases/PerpetratorModal.vue';

export default {
  name: 'CaseCreation',
  components: {
    CaseHeader,
    ProgressTracker,
    Step1ReporterSelection,
    Step2ReporterDetails,
    Step3CaseDetails,
    Step4CaseClassification,
    Step5Review,
    ClientModal,
    PerpetratorModal
  },
  setup() {
    const router = useRouter();
    const casesStore = useCaseStore();
    
    // UI State
    const currentStep = ref(1);
    const totalSteps = 5;
    const isAIEnabled = ref(false);
    // Track each step status: "pending" | "active" | "completed" | "skipped"
const stepStatus = reactive({
  1: "active",
  2: "pending",
  3: "pending",
  4: "pending",
  5: "pending"
});
    const stepLabels = [
      'Reporter Selection',
      'Reporter Details',
      'Case Details',
      'Classification',
      'Review'
    ];
    const stepDescriptions = [
      'Choose an existing contact or create a new reporter for this case.',
      'Enter the reporter\'s contact information and details.',
      'Provide detailed information about the case and incident.',
      'Classify the case and set priority levels for proper handling.',
      'Review all information before creating the case.'
    ];
    
    // Form Data
    const formData = reactive({
      step1: {
        searchQuery: '',
        selectedReporter: null,
        filteredContacts: []
      },
      step2: {
        name: '',
        age: '',
        dob: '',
        ageGroup: '',
        gender: '',
        location: '',
        nearestLandmark: '',
        nationality: '',
        language: '',
        tribe: '',
        phone: '',
        altPhone: '',
        email: '',
        idType: '',
        idNumber: '',
        isClient: null,
        perpetrators: [],
        clients: []
      },
      step3: {
        narrative: '',
        incidentDate: '',
        incidentTime: '',
        location: '',
        isGBVRelated: '',
        casePlan: ''
      },
      step4: {
        department: '',
        clientPassportNumber: '',
        categories: '',
        priority: '',
        status: '',
        escalatedTo: '',
        justiceSystemState: '',
        generalAssessment: '',
        servicesOffered: '',
        referralSource: ''
      }
    });
    
    // Search & Filtering
    const searchQuery = ref('');
    const debouncedQuery = ref('');
    const filteredContacts = ref([]);
    const clientSearchResults = ref([]);
    const hasSearched = ref(false);
    
    // Modal State
    const clientModalOpen = ref(false);
    const perpetratorModalOpen = ref(false);
    
    // Client Modal State
    const currentClientStep = ref(0);
    const clientForm = reactive({
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
      schoolName: '',
      schoolLevel: '',
      schoolAddress: '',
      schoolType: '',
      schoolAttendance: '',
      isDisabled: '',
      disability: '',
      specialServicesReferred: '',
      specialServicesReferral: []
    });
    
    const showSpecialServicesDropdown = ref(false);
    const specialServicesSearch = ref('');
    const filteredSpecialServices = ref([]);
    
    // Perpetrator Modal State
    const currentPerpetratorStep = ref(0);
    const perpetratorForm = reactive({
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
    
    // Helper function to update form data
    const updateFormData = (step, data) => {
      formData[step] = { ...formData[step], ...data };
    };
    
    // Navigation methods
  // Update statuses when navigating
const navigateToStep = (step) => {
  if (step >= 1 && step <= totalSteps) {
    // Mark all previous steps as completed if not already
    for (let i = 1; i < step; i++) {
      if (stepStatus[i] !== "completed") {
        stepStatus[i] = "completed";
      }
    }
    // Mark the current step as active
    stepStatus[step] = "active";
    // Mark all later steps as pending
    for (let i = step + 1; i <= totalSteps; i++) {
      if (stepStatus[i] !== "completed") {
        stepStatus[i] = "pending";
      }
    }

    currentStep.value = step;
  }
};
    
    const goToStep = (step) => {
      navigateToStep(step);
    };
    

const validateAndProceed = (step) => {
  // Add validation logic here
  stepStatus[step] = "completed";
  navigateToStep(step + 1);
};
    
   const saveAndProceed = (step) => {
  // Add save logic here
  stepStatus[step] = "completed";
  navigateToStep(step + 1);
};
    
    const skipStep = (step) => {
      navigateToStep(step + 1);
    };
    
    const cancelForm = () => {
      router.push('/cases');
    };
    
    // Modal methods
    const openClientModal = () => {
      clientModalOpen.value = true;
    };
    
    const closeClientModal = () => {
      clientModalOpen.value = false;
      currentClientStep.value = 0;
      // Reset client form
      Object.keys(clientForm).forEach(key => {
        clientForm[key] = '';
      });
      clientForm.specialServicesReferral = [];
    };
    
    const openPerpetratorModal = () => {
      perpetratorModalOpen.value = true;
    };
    
    const closePerpetratorModal = () => {
      perpetratorModalOpen.value = false;
      currentPerpetratorStep.value = 0;
      // Reset perpetrator form
      Object.keys(perpetratorForm).forEach(key => {
        perpetratorForm[key] = '';
      });
    };
    
    // Client modal methods
    const updateClientForm = (data) => {
      Object.assign(clientForm, data);
    };
    
    const toggleSpecialServicesDropdown = () => {
      showSpecialServicesDropdown.value = !showSpecialServicesDropdown.value;
    };
    
    const prevClientStep = () => {
      if (currentClientStep.value > 0) {
        currentClientStep.value--;
      }
    };
    
    const nextClientStep = () => {
      if (currentClientStep.value < 4) { // Assuming 5 steps (0-4)
        currentClientStep.value++;
      }
    };
    
    const addClient = () => {
      formData.step2.clients.push({ ...clientForm });
      closeClientModal();
    };
    
    const removeClient = (index) => {
      formData.step2.clients.splice(index, 1);
    };
    
    // Perpetrator modal methods
    const updatePerpetratorForm = (data) => {
      Object.assign(perpetratorForm, data);
    };
    
    const prevPerpetratorStep = () => {
      if (currentPerpetratorStep.value > 0) {
        currentPerpetratorStep.value--;
      }
    };
    
    const nextPerpetratorStep = () => {
      if (currentPerpetratorStep.value < 3) { // Assuming 4 steps (0-3)
        currentPerpetratorStep.value++;
      }
    };
    
    const addPerpetrator = () => {
      formData.step2.perpetrators.push({ ...perpetratorForm });
      closePerpetratorModal();
    };
    
    const removePerpetrator = (index) => {
      formData.step2.perpetrators.splice(index, 1);
    };
    
    // Search methods
    const handleSearchChange = (query) => {
      searchQuery.value = query;
      // Implement debounced search logic
    };
    
    const selectExistingReporter = (reporter) => {
      formData.step1.selectedReporter = reporter;
      // Populate formData.step2 with reporter data
      if (reporter) {
        const rep = reporter;
        formData.step2.name = rep[casesStore.cases_k.reporter_fullname[0]] || '';
        formData.step2.age = rep[casesStore.cases_k.reporter_age[0]] || '';
        formData.step2.gender = rep[casesStore.cases_k.reporter_sex[0]] || '';
        formData.step2.location = rep[casesStore.cases_k.reporter_location[0]] || '';
        formData.step2.phone = rep[casesStore.cases_k.reporter_phone[0]] || '';
      }
    };
    
    const createNewReporter = () => {
      formData.step1.selectedReporter = null;
      // Clear any previously populated data
      Object.keys(formData.step2).forEach(key => {
        if (typeof formData.step2[key] === 'string') {
          formData.step2[key] = '';
        }
      });
      formData.step2.perpetrators = [];
      formData.step2.clients = [];
    };
    
    const searchClientByPassport = () => {
      // Implement passport search logic
      hasSearched.value = true;
    };
    
    const selectClient = (client) => {
      // Handle client selection from search results
    };
    
    const createNewClient = () => {
      // Open client modal or navigate to client creation
      openClientModal();
    };
    
    // AI Toggle
    const handleAIToggle = (value) => {
      isAIEnabled.value = value;
    };
    
    // Submit case to backend
    const submitCase = async () => {
      // Map form data to backend payload structure
      const casePayload = {
  src: "ceemis",
  src_uid: "ceemis-d0a0fca3-1753869019",
  src_address: formData.step2.phone || "256701234567",
  src_uid2: "walkin-100-1743763537",
  src_usr: "ceemis",
  src_vector: "2",
  src_callid: "44dea031-f268-4ed6-af7b-9231dc3c1b29",
  src_ts: "1753869019.836215",
  reporter_nickname: "ceemis_user",
  case_category: "COMPLAINT",
  case_category_id: "362484",
  narrative: formData.step3.narrative || "",
  complaint_text: null,
  complaint_image: null,
  complaint_audio: null,
  complaint_video: null,
  message_id_ref: "",
  session_id: "d47e3704-1dbb-45f1-82c8-9a8902005a60",
  plan: formData.step3.casePlan || "---",
  priority: "1",
  status:  "1",
  escalated_to_id: mapEscalationToBackend(formData.step4.escalatedTo) || "0",
  gbv_related: mapGBVRelatedToBackend(formData.step3.isGBVRelated) || "0",

  reporters_uuid: {
    fname: formData.step2.name || "",
    age_t: "0",
    age: formData.step2.age || "",
    dob: "",
    age_group_id: mapAgeGroupToBackend(formData.step2.ageGroup) || "",
    location_id: mapLocationToBackend(formData.step2.location) || "258783",
    sex_id: mapGenderToBackend(formData.step2.gender) || "",
    landmark: formData.step2.nearestLandmark || "",
    nationality_id: mapNationalityToBackend(formData.step2.nationality) || "",
    national_id_type_id: mapIdTypeToBackend(formData.step2.idType) || "1",
    national_id: formData.step2.idNumber || "C7845123",
    lang_id: mapLanguageToBackend(formData.step2.language) || "",
    tribe_id: mapTribeToBackend(formData.step2.tribe) || "",
    phone: formData.step2.phone || "256701234567",
    phone2: formData.step2.altPhone || "",
    email: formData.step2.email || "",
    ".id": ""
  },

  clients_case: (formData.step2.clients.length > 0 ? formData.step2.clients : [{}]).map(client => ({
    fname: client.name || formData.step2.name || "",
    age_t: "0",
    age: client.age || formData.step2.age || "",
    dob: client.dob || "",
    age_group_id: mapAgeGroupToBackend(client.ageGroup || formData.step2.ageGroup) || "",
    location_id: mapLocationToBackend(client.location || formData.step2.location) || "258783",
    sex_id: mapGenderToBackend(client.sex || formData.step2.gender) || "",
    landmark: client.landmark || formData.step2.nearestLandmark || "",
    nationality_id: mapNationalityToBackend(client.nationality || formData.step2.nationality) || "",
    national_id_type_id: mapIdTypeToBackend(client.idType || formData.step2.idType) || "1",
    national_id: client.idNumber || formData.step2.idNumber || "C7845123",
    lang_id: mapLanguageToBackend(client.language || formData.step2.language) || "",
    tribe_id: mapTribeToBackend(client.tribe || formData.step2.tribe) || "",
    phone: client.phone || formData.step2.phone || "256701234567",
    phone2: client.alternativePhone || formData.step2.altPhone || "",
    email: client.email || formData.step2.email || "",
    ".id": ""
  })),

  perpetrators_case: (formData.step2.perpetrators.length > 0 ? formData.step2.perpetrators : [{}]).map(perpetrator => ({
    fname: perpetrator.name || "",
    age_t: "0",
    age: perpetrator.age || "",
    dob: perpetrator.dob || "",
    age_group_id: mapAgeGroupToBackend(perpetrator.ageGroup) || "",
    age_group: perpetrator.ageGroup || "",
    location_id: mapLocationToBackend(perpetrator.location) || "258783",
    sex_id: mapGenderToBackend(perpetrator.sex) || "",
    sex: perpetrator.sex || "",
    landmark: perpetrator.landmark || "",
    nationality_id: mapNationalityToBackend(perpetrator.nationality) || "",
    national_id_type_id: mapIdTypeToBackend(perpetrator.idType) || "2",
    national_id: perpetrator.idNumber || "EMP789456",
    lang_id: mapLanguageToBackend(perpetrator.language) || "",
    tribe_id: mapTribeToBackend(perpetrator.tribe) || "",
    phone: perpetrator.phone || "",
    phone2: perpetrator.alternativePhone || "",
    email: perpetrator.email || "",
    relationship_id: mapRelationshipToBackend(perpetrator.relationship) || "",
    relationship: perpetrator.relationship || "Employer",
    shareshome_id: mapSharesHomeToBackend(perpetrator.sharesHome) || "",
    health_id: mapHealthStatusToBackend(perpetrator.healthStatus) || "",
    employment_id: mapEmploymentToBackend(perpetrator.profession) || "1",
    marital_id: mapMaritalStatusToBackend(perpetrator.maritalStatus) || "",
    guardian_fullname: perpetrator.guardianName || "",
    notes: perpetrator.additionalDetails || "Employer in Housemaid sector",
    ".id": ""
  })),

  attachments_case: [],
  services: Array.isArray(formData.step4.servicesOffered) ? formData.step4.servicesOffered : (formData.step4.servicesOffered ? [formData.step4.servicesOffered] : [])
};  
      try {
        console.log('Case created:', casePayload);
        await casesStore.createCase(casePayload);
        alert("Case created successfully!");
       // router.push("/cases");
      } catch (error) {
        console.error("Failed to create case:", error);
        alert("An error occurred while creating the case.");
      }
    };
    
   // Mapping functions for backend values
const mapPriorityToBackend = (priority) => {
  const priorityMap = {
    'low': '1',      // Low -> 1
    'medium': '2',   // Medium -> 2
    'high': '3',     // High -> 3
    'none': '0',     // None -> 0
    '': '0'          // Blank -> 0
  };
  console.log('Priority:', priority);
  return priorityMap[priority?.toLowerCase()] || '1'; // default Low
};

const mapStatusToBackend = (status) => {
  const statusMap = {
    'ongoing': '1',       // Ongoing -> 1
    'closed': '2',        // Closed -> 2
    'escalated': '3',     // Escalated -> 3
    'none': '0',          // None -> 0
    '': '0'               // Blank -> 0
  };
  console.log('Status:', status);
  return statusMap[status?.toLowerCase()] || '1'; // default Ongoing
};

    
    const mapEscalationToBackend = (escalatedTo) => {
      const escalationMap = {
        "": '0',
        'none': '0',
        'supervisor': '1',
        'manager': '2',
        'director': '3',
        'external-agency': '4',
        'law-enforcement': '5'
      };
      return escalationMap[escalatedTo?.toLowerCase()]|| '0';
    };
    
    // Add other mapping functions as needed
    const mapAgeGroupToBackend = (ageGroup) => {
      // Implementation depends on your age group mapping
      return '';
    };
    
    const mapLocationToBackend = (location) => {
      // Implementation depends on your location mapping
      return '';
    };
    
    const mapGenderToBackend = (gender) => {
      const genderMap = {
        'male': '1',
        'female': '2',
        'other': '3'
      };
      return genderMap[gender] || '';
    };
    
    const mapNationalityToBackend = (nationality) => {
      // Implementation depends on your nationality mapping
      return '';
    };
    
    const mapIdTypeToBackend = (idType) => {
      const idTypeMap = {
        'national-id': '1',
        'passport': '2',
        'birth-certificate': '3',
        'refugee-id': '4',
        'other': '5'
      };
      return idTypeMap[idType] || '1';
    };
    
    const mapLanguageToBackend = (language) => {
      // Implementation depends on your language mapping
      return '';
    };
    
    const mapTribeToBackend = (tribe) => {
      // Implementation depends on your tribe mapping
      return '';
    };
    
    const mapRelationshipToBackend = (relationship) => {
      // Implementation depends on your relationship mapping
      return '';
    };
    
    const mapSharesHomeToBackend = (sharesHome) => {
      const sharesHomeMap = {
        'yes': '1',
        'no': '0',
        'unknown': '2'
      };
      return sharesHomeMap[sharesHome] || '';
    };
    
    const mapGBVRelatedToBackend = (gbv) => {
  const gbvMap = {
    'Not GBV': '0',
    'Test GBV': '1',
    0: '0',
    1: '1',
    '': '0',      // default
    null: '0',    // default
    undefined: '0'
  };
  return gbvMap[gbv] || '0';
};

    const mapHealthStatusToBackend = (healthStatus) => {
      const healthMap = {
        'good': '1',
        'fair': '2',
        'poor': '3',
        'unknown': '4'
      };
      return healthMap[healthStatus] || '';
    };
    
    const mapEmploymentToBackend = (employment) => {
      const employmentMap = {
        'employed': '1',
        'self-employed': '2',
        'unemployed': '3',
        'student': '4',
        'retired': '5',
        'other': '6'
      };
      return employmentMap[employment] || '1';
    };
    
    const mapMaritalStatusToBackend = (maritalStatus) => {
      const maritalMap = {
        'single': '1',
        'married': '2',
        'divorced': '3',
        'widowed': '4',
        'separated': '5'
      };
      return maritalMap[maritalStatus] || '';
    };
    
    // Add inside setup()
const saveStep = ({ step, data }) => {
  formData[step] = { ...formData[step], ...data };
  stepStatus[step] = "completed";
  console.log("Step saved:", step, data);
};

    return {
      // State
      currentStep,
      totalSteps,
      isAIEnabled,
      stepStatus,
      stepLabels,
      stepDescriptions,
      formData,
      searchQuery,
      debouncedQuery,
      filteredContacts,
      clientSearchResults,
      hasSearched,
      clientModalOpen,
      perpetratorModalOpen,
      currentClientStep,
      clientForm,
      showSpecialServicesDropdown,
      specialServicesSearch,
      filteredSpecialServices,
      currentPerpetratorStep,
      perpetratorForm,
      
      // Methods
      updateFormData,
      navigateToStep,
      goToStep,
      validateAndProceed,
      saveAndProceed,
      skipStep,
      cancelForm,
      openClientModal,
      closeClientModal,
      openPerpetratorModal,
      closePerpetratorModal,
      updateClientForm,
      toggleSpecialServicesDropdown,
      prevClientStep,
      nextClientStep,
      addClient,
      removeClient,
      updatePerpetratorForm,
      prevPerpetratorStep,
      nextPerpetratorStep,
      addPerpetrator,
      removePerpetrator,
      handleSearchChange,
      selectExistingReporter,
      createNewReporter,
      searchClientByPassport,
      selectClient,
      createNewClient,
      handleAIToggle,
      saveStep,
      submitCase
    };
  }
};
</script>

<style scoped>
.case-creation-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}
</style>
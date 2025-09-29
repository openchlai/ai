<template>
  <div class="case-creation-container">
    <CaseHeader 
      :isAIEnabled="isAIEnabled" 
      @toggle-ai="handleAIToggle"
    />
    
    <ProgressTracker 
      :currentStep="currentStep"
      :totalSteps="totalSteps"
      :stepStatus="stepStatus"
      :stepLabels="stepLabels"
      @step-change="navigateToStep"
    />
    
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
      :selectedReporter="formData.step1.selectedReporter"
      @update:formData="(val) => (formData.step2 = val)"
      @step-change="goToStep"
      @skip-step="skipStep"
      @save-step="saveStep"
      @open-client-modal="openClientModal"
      @open-perpetrator-modal="openPerpetratorModal"
      @remove-client="removeClient"
      @remove-perpetrator="removePerpetrator"
    />
    
    <Step3CaseDetails
      v-if="currentStep === 3"
      :currentStep="currentStep"
      :formData="formData.step3"
      @form-update="updateFormData('step3', $event)"
      @save-and-proceed="saveAndProceed(3)"
      @step-change="goToStep"            
      @skip-step="skipStep(3)"
    />
    
    <Step4CaseClassification
      v-if="currentStep === 4"
      :currentStep="currentStep"              
      :formData="formData.step4"
      :clientSearchResults="clientSearchResults"
      :hasSearched="hasSearched"
      @form-update="updateFormData('step4', $event)"
      @search-client-by-passport="searchClientByPassport"
      @select-client="selectClient"
      @create-new-client="createNewClient"
      @save-and-proceed="saveAndProceed(4)"
      @step-change="goToStep"                 
      @skip-step="skipStep(4)"
    />
    
    <Step5Review
      v-if="currentStep === 5"
      :currentStep="currentStep"
      :formData="formData"
      @go-to-step="goToStep"
      @submit-case="submitCase"
    />
    
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
import { useReporterStore } from '@/stores/reporters';
import { useCategoryStore } from '@/stores/categories';

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
    const reporterStore = useReporterStore();
    const categoryStore = useCategoryStore();
    
    const getValue = (contact, fieldName) => {
      if (!contact || !Array.isArray(contact)) return '';
      
      const mapping = reporterStore.reporters_k?.[`contact_${fieldName}`] || reporterStore.reporters_k?.[fieldName];
      if (mapping && Array.isArray(mapping) && mapping.length > 0) {
        const idx = mapping[0];
        return contact[idx] || '';
      }
      return '';
    };
    
    const currentStep = ref(1);
    const totalSteps = 5;
    const isAIEnabled = ref(false);
    
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
        servicesOffered: [],
        servicesOfferedText: [],
        referralSource: '',
        referralsType: [],
        policeDetails: '',
        otherServicesDetails: '',
        attachments: []
      }
    });
    
    const searchQuery = ref('');
    const debouncedQuery = ref('');
    const filteredContacts = ref([]);
    const clientSearchResults = ref([]);
    const hasSearched = ref(false);
    
    const clientModalOpen = ref(false);
    const perpetratorModalOpen = ref(false);
    
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
    
    const updateFormData = (step, data) => {
      if (step === 'step4') {
        if (data.servicesOfferedSelection) {
          formData.step4.servicesOffered = data.servicesOfferedSelection.values || [];
          formData.step4.servicesOfferedText = data.servicesOfferedSelection.texts || [];
        }
        Object.keys(data).forEach(key => {
          if (key !== 'servicesOfferedSelection') {
            formData.step4[key] = data[key];
          }
        });
      } else {
        formData[step] = { ...formData[step], ...data };
      }
    };
    
    const navigateToStep = (step) => {
      if (step >= 1 && step <= totalSteps) {
        for (let i = 1; i < step; i++) {
          if (stepStatus[i] !== "completed") {
            stepStatus[i] = "completed";
          }
        }
        stepStatus[step] = "active";
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
      stepStatus[step] = "completed";
      navigateToStep(step + 1);
    };
    
    const saveAndProceed = (step) => {
      stepStatus[step] = "completed";
      navigateToStep(step + 1);
    };
    
    const skipStep = (step) => {
      navigateToStep(step + 1);
    };
    
    const cancelForm = () => {
      router.push('/cases');
    };
    
    const openClientModal = () => {
      clientModalOpen.value = true;
    };
    
    const closeClientModal = () => {
      clientModalOpen.value = false;
      currentClientStep.value = 0;
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
      Object.keys(perpetratorForm).forEach(key => {
        perpetratorForm[key] = '';
      });
    };
    
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
      if (currentClientStep.value < 4) {
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
    
    const updatePerpetratorForm = (data) => {
      Object.assign(perpetratorForm, data);
    };
    
    const prevPerpetratorStep = () => {
      if (currentPerpetratorStep.value > 0) {
        currentPerpetratorStep.value--;
      }
    };
    
    const nextPerpetratorStep = () => {
      if (currentPerpetratorStep.value < 3) {
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
    
    const handleSearchChange = (query) => {
      searchQuery.value = query;
    };
    
    const selectExistingReporter = (reporter) => {
      formData.step1.selectedReporter = reporter;
      
      if (reporter && Array.isArray(reporter)) {
        formData.step2.name = getValue(reporter, 'fullname');
        formData.step2.age = getValue(reporter, 'age');
        formData.step2.dob = getValue(reporter, 'dob');
        formData.step2.ageGroup = getValue(reporter, 'age_group');
        formData.step2.gender = getValue(reporter, 'sex');
        formData.step2.location = getValue(reporter, 'location');
        formData.step2.nearestLandmark = getValue(reporter, 'landmark');
        formData.step2.nationality = getValue(reporter, 'nationality');
        formData.step2.language = getValue(reporter, 'language');
        formData.step2.tribe = getValue(reporter, 'tribe');
        formData.step2.phone = getValue(reporter, 'phone');
        formData.step2.altPhone = getValue(reporter, 'alternative_phone');
        formData.step2.email = getValue(reporter, 'email');
        formData.step2.idType = getValue(reporter, 'id_type');
        formData.step2.idNumber = getValue(reporter, 'id_number');
        
        formData.step2.isClient = null;
        formData.step2.clients = [];
        formData.step2.perpetrators = [];
      }
    };
    
    const createNewReporter = () => {
      formData.step1.selectedReporter = null;
      Object.keys(formData.step2).forEach(key => {
        if (typeof formData.step2[key] === 'string') {
          formData.step2[key] = '';
        }
      });
      formData.step2.perpetrators = [];
      formData.step2.clients = [];
      formData.step2.isClient = null;
    };
    
    const searchClientByPassport = () => {
      hasSearched.value = true;
    };
    
    const selectClient = (client) => {
      // Handle client selection
    };
    
    const createNewClient = () => {
      openClientModal();
    };
    
    const handleAIToggle = (value) => {
      isAIEnabled.value = value;
    };
    
    const submitCase = async () => {
      const timestamp = Date.now();
      const timestampSeconds = (timestamp / 1000).toFixed(3);
      const userId = "100";
      const srcUid = `walkin-${userId}-${timestamp}`;
      const srcUid2 = `${srcUid}-1`;
      const srcCallId = srcUid2;
      
      const getValueOrDefault = (value, defaultValue = "") => {
        return value !== null && value !== undefined && value !== "" ? value : defaultValue;
      };
      
      const baseSourceFields = {
        src: "walkin",
        src_ts: timestampSeconds,
        src_uid: srcUid,
        src_uid2: srcUid2,
        src_callid: srcCallId,
        src_usr: userId,
        src_vector: "2"
      };
      
      const clientsPayload = formData.step2.clients.map(client => ({
        client_id: client.id || ""
      }));
      
      const perpetratorsPayload = formData.step2.perpetrators.map(perpetrator => ({
        perpetrator_id: perpetrator.id || ""
      }));
      
      const servicesPayload = (formData.step4.servicesOffered || []).map(serviceId => ({
        category_id: String(serviceId)
      }));
      
      const referralsPayload = (formData.step4.referralsType || []).map(referralId => ({
        category_id: String(referralId)
      }));
      
      const attachmentsPayload = (formData.step4.attachments || []).map((file, index) => ({
        attachment_id: String(index + 1)
      }));
      
      const mapDepartmentToBackend = (dept) => {
        const deptMap = {
          '116': '1',
          'labor': '2'
        };
        return deptMap[dept] || '0';
      };
      
      const mapGBVRelatedToBackend = (gbvId) => {
        if (!gbvId) return '0';
        const gbvRelatedIds = ['118002', '363070'];
        return gbvRelatedIds.includes(String(gbvId)) ? '1' : '0';
      };
      
      const casePayload = {
        ".id": "",
        ...baseSourceFields,
        src_address: getValueOrDefault(formData.step2.phone),
        
        reporter_contact_id: "86808",
        reporter_fullname: getValueOrDefault(formData.step2.name),
        reporter_age_group_id: getValueOrDefault(formData.step2.ageGroup),
        reporter_sex_id: getValueOrDefault(formData.step2.gender),
        
        reporter_age: getValueOrDefault(formData.step2.age),
        reporter_phone: getValueOrDefault(formData.step2.phone),
        reporter_location_id: getValueOrDefault(formData.step2.location),
        reporter_nationality_id: getValueOrDefault(formData.step2.nationality),
        
        case_category_id: getValueOrDefault(formData.step4.categories),
        narrative: getValueOrDefault(formData.step3.narrative),
        plan: getValueOrDefault(formData.step3.casePlan),
        dept: mapDepartmentToBackend(formData.step4.department),
        disposition_id: "363037",
        escalated_to_id: getValueOrDefault(formData.step4.escalatedTo, "0"),
        gbv_related: mapGBVRelatedToBackend(formData.step3.isGBVRelated),
        knowabout116_id: getValueOrDefault(formData.step4.referralSource),
        police_ob_no: getValueOrDefault(formData.step4.policeDetails),
        priority: getValueOrDefault(formData.step4.priority) || "1",
        status: getValueOrDefault(formData.step4.status) || "1",
        
        reporters_uuid: formData.step1.selectedReporter ? undefined : {
          fname: formData.step2.name || "",
          age_t: "0",
          age: formData.step2.age || "",
          dob: formData.step2.dob || "",
          age_group_id: formData.step2.ageGroup || "",
          location_id: formData.step2.location || "",
          sex_id: formData.step2.gender || "",
          landmark: formData.step2.nearestLandmark || "",
          nationality_id: formData.step2.nationality || "",
          national_id_type_id: formData.step2.idType || "",
          national_id: formData.step2.idNumber || "",
          lang_id: formData.step2.language || "",
          tribe_id: formData.step2.tribe || "",
          phone: formData.step2.phone || "",
          phone2: formData.step2.altPhone || "",
          email: formData.step2.email || "",
          ".id": ""
        },
        
        services: servicesPayload,
        referals: referralsPayload,
        specify_service: getValueOrDefault(formData.step4.otherServicesDetails),
        clients_case: clientsPayload,
        perpetrators_case: perpetratorsPayload,
        attachments_case: attachmentsPayload
      };
      
      Object.keys(casePayload).forEach(key => {
        if (casePayload[key] === undefined) {
          delete casePayload[key];
        }
      });
      
      // FORCE REMOVE reporter_uuid_id if it somehow gets added
      delete casePayload.reporter_uuid_id;
      
      try {
        console.log('Submitting payload:', JSON.stringify(casePayload, null, 2));
        await casesStore.createCase(casePayload);
        alert("Case created successfully!");
        router.push("/cases");
      } catch (error) {
        console.error("Failed to create case:", error);
        alert("An error occurred while creating the case: " + error.message);
      }
    };
    
    const saveStep = ({ step, data }) => {
      const stepNumber = typeof step === 'string' ? parseInt(step.replace('step', '')) : step;
      const stepKey = typeof step === 'string' ? step : `step${step}`;
      
      if (stepKey === 'step4' && data.servicesOfferedSelection) {
        formData.step4 = { ...formData.step4, ...data };
        formData.step4.servicesOffered = data.servicesOfferedSelection.values || [];
        formData.step4.servicesOfferedText = data.servicesOfferedSelection.texts || [];
      } else {
        formData[stepKey] = { ...formData[stepKey], ...data };
      }
      
      stepStatus[stepNumber] = "completed";
      
      const nextStep = stepNumber + 1;
      if (nextStep <= totalSteps) {
        navigateToStep(nextStep);
      }
    };

    return {
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
      submitCase,
      getValue
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
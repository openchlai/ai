<template>
  <div class="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
    <div class="max-w-5xl mx-auto">
      <!-- Header Section -->
      <div class="mb-8">
        <CaseHeader 
          :isAIEnabled="isAIEnabled" 
          @toggle-ai="handleAIToggle"
          class="mb-6"
        />
        
        <ProgressTracker 
          :currentStep="currentStep"
          :totalSteps="totalSteps"
          :stepStatus="stepStatus"
          :stepLabels="stepLabels"
          @step-change="navigateToStep"
        />
      </div>
      
      <!-- Step Content Area -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 sm:p-8 mb-6">
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
      </div>
    </div>
    
    <!-- Modals -->
    <ClientModal
      v-if="clientModalOpen"
      :clients="formData.step2.clients"
      :clientForm="clientForm"
      :currentClientStep="currentClientStep"
      :showSpecialServicesDropdown="showSpecialServicesDropdown"
      :specialServicesSearch="specialServicesSearch"
      :filteredSpecialServices="filteredSpecialServices"
      :loading="clientStore.loading"
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
      :loading="perpetratorStore.loading"
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
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { useCaseStore } from '@/stores/cases';
import { useReporterStore } from '@/stores/reporters';
import { useCategoryStore } from '@/stores/categories';
import { useClientStore } from '@/stores/clients';
import { usePerpetratorStore } from '@/stores/perpetrators';
import { useFilesStore } from '@/stores/files';

import CaseHeader from '@/components/case-create/CaseHeader.vue';
import ProgressTracker from '@/components/case-create/ProgressTracker.vue';
import Step1ReporterSelection from '@/components/case-create/Step1ReporterSelection.vue';
import Step2ReporterDetails from '@/components/case-create/Step2ReporterDetails.vue';
import Step3CaseDetails from '@/components/case-create/Step3CaseDetails.vue';
import Step4CaseClassification from '@/components/case-create/Step4CaseClassification.vue';
import Step5Review from '@/components/case-create/Step5Review.vue';
import ClientModal from '@/components/case-create/ClientModal.vue';
import PerpetratorModal from '@/components/case-create/PerpetratorModal.vue';

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
    // Initialize stores first
    const router = useRouter();
    const casesStore = useCaseStore();
    const reporterStore = useReporterStore();
    const categoryStore = useCategoryStore();
    const clientStore = useClientStore();
    const perpetratorStore = usePerpetratorStore();
    const filesStore = useFilesStore();
    
    // Initialize basic reactive variables first
    const currentStep = ref(1);
    const totalSteps = 5;
    const isAIEnabled = ref(false);
    const isSubmittingCase = ref(false);
    
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
    
    // Initialize formData AFTER other variables
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
    
    // Initialize other reactive variables
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

    // Helper function
    const getValue = (contact, fieldName) => {
      if (!contact || !Array.isArray(contact)) return '';
      
      const mapping = reporterStore.reporters_k?.[`contact_${fieldName}`] || reporterStore.reporters_k?.[fieldName];
      if (mapping && Array.isArray(mapping) && mapping.length > 0) {
        const idx = mapping[0];
        return contact[idx] || '';
      }
      return '';
    };
    
    // Methods
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
    
    const addClient = async () => {
      // Validate required field
      if (!clientForm.name || clientForm.name.trim() === '') {
        alert('Client name is required');
        return;
      }

      try {
        // Generate unique identifiers for this client creation
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

        // Build client payload
        const clientPayload = {
          ".id": "",
          ...baseSourceFields,
          fname: getValueOrDefault(clientForm.name),
          age_t: "0",
          age: getValueOrDefault(clientForm.age),
          dob: getValueOrDefault(clientForm.dob),
          age_group_id: getValueOrDefault(clientForm.ageGroup),
          location_id: getValueOrDefault(clientForm.location),
          sex_id: getValueOrDefault(clientForm.sex),
          landmark: getValueOrDefault(clientForm.landmark),
          nationality_id: getValueOrDefault(clientForm.nationality),
          national_id_type_id: getValueOrDefault(clientForm.idType),
          national_id: getValueOrDefault(clientForm.idNumber),
          lang_id: getValueOrDefault(clientForm.language),
          is_refugee: getValueOrDefault(clientForm.isRefugee),
          tribe_id: getValueOrDefault(clientForm.tribe),
          phone: getValueOrDefault(clientForm.phone),
          phone2: getValueOrDefault(clientForm.alternativePhone),
          email: getValueOrDefault(clientForm.email),
          relationship_to_reporter_id: getValueOrDefault(clientForm.relationship),
          relationship_comment: getValueOrDefault(clientForm.relationshipComment),
          adults_in_household: getValueOrDefault(clientForm.adultsInHousehold),
          household_type_id: getValueOrDefault(clientForm.householdType),
          head_occupation_id: getValueOrDefault(clientForm.headOccupation),
          parent_guardian_name: getValueOrDefault(clientForm.parentGuardianName),
          parent_marital_status_id: getValueOrDefault(clientForm.parentMaritalStatus),
          parent_id_number: getValueOrDefault(clientForm.parentIdNumber),
          health_status_id: getValueOrDefault(clientForm.healthStatus),
          hiv_status_id: getValueOrDefault(clientForm.hivStatus),
          marital_status_id: getValueOrDefault(clientForm.maritalStatus),
          attending_school_id: getValueOrDefault(clientForm.attendingSchool),
          school_name: getValueOrDefault(clientForm.schoolName),
          school_level_id: getValueOrDefault(clientForm.schoolLevel),
          school_address: getValueOrDefault(clientForm.schoolAddress),
          school_type_id: getValueOrDefault(clientForm.schoolType),
          school_attendance_id: getValueOrDefault(clientForm.schoolAttendance),
          is_disabled: getValueOrDefault(clientForm.isDisabled),
          disability_id: getValueOrDefault(clientForm.disability),
          special_services_referred: getValueOrDefault(clientForm.specialServicesReferred),
          special_services_referral: (clientForm.specialServicesReferral || []).map(serviceId => ({
            category_id: String(serviceId)
          }))
        };

        // Call the API to create client
        const result = await clientStore.createClient(clientPayload);
        
        if (result && result.id) {
          // Add the client data with the returned ID to the formData
          const clientData = { 
            ...clientForm, 
            id: result.id  // Store the returned ID
          };
          
          formData.step2.clients.push(clientData);
          console.log('Client created successfully with ID:', result.id);
          closeClientModal();
        } else {
          throw new Error('No client ID returned from server');
        }

      } catch (error) {
        console.error('Error creating client:', error);
        alert(`Failed to create client: ${error.message}`);
        // Don't close the modal so user can retry
      }
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
    
    const addPerpetrator = async () => {
      // Validate required field
      if (!perpetratorForm.name || perpetratorForm.name.trim() === '') {
        alert('Perpetrator name is required');
        return;
      }

      try {
        // Generate unique identifiers for this perpetrator creation
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

        // Build perpetrator payload
        const perpetratorPayload = {
          ".id": "",
          ...baseSourceFields,
          fname: getValueOrDefault(perpetratorForm.name),
          age_t: "0",
          age: getValueOrDefault(perpetratorForm.age),
          dob: getValueOrDefault(perpetratorForm.dob),
          age_group_id: getValueOrDefault(perpetratorForm.ageGroup),
          location_id: getValueOrDefault(perpetratorForm.location),
          sex_id: getValueOrDefault(perpetratorForm.sex),
          landmark: getValueOrDefault(perpetratorForm.landmark),
          nationality_id: getValueOrDefault(perpetratorForm.nationality),
          national_id_type_id: getValueOrDefault(perpetratorForm.idType),
          national_id: getValueOrDefault(perpetratorForm.idNumber),
          lang_id: getValueOrDefault(perpetratorForm.language),
          is_refugee: getValueOrDefault(perpetratorForm.isRefugee),
          tribe_id: getValueOrDefault(perpetratorForm.tribe),
          phone: getValueOrDefault(perpetratorForm.phone),
          phone2: getValueOrDefault(perpetratorForm.alternativePhone),
          email: getValueOrDefault(perpetratorForm.email),
          relationship_to_reporter_id: getValueOrDefault(perpetratorForm.relationship),
          shares_home: getValueOrDefault(perpetratorForm.sharesHome),
          health_status_id: getValueOrDefault(perpetratorForm.healthStatus),
          profession_id: getValueOrDefault(perpetratorForm.profession),
          marital_status_id: getValueOrDefault(perpetratorForm.maritalStatus),
          guardian_name: getValueOrDefault(perpetratorForm.guardianName),
          additional_details: getValueOrDefault(perpetratorForm.additionalDetails)
        };

        // Call the API to create perpetrator
        const result = await perpetratorStore.createPerpetrator(perpetratorPayload);
        
        if (result && result.id) {
          // Add the perpetrator data with the returned ID to the formData
          const perpetratorData = { 
            ...perpetratorForm, 
            id: result.id  // Store the returned ID
          };
          
          formData.step2.perpetrators.push(perpetratorData);
          console.log('Perpetrator created successfully with ID:', result.id);
          closePerpetratorModal();
        } else {
          throw new Error('No perpetrator ID returned from server');
        }

      } catch (error) {
        console.error('Error creating perpetrator:', error);
        alert(`Failed to create perpetrator: ${error.message}`);
        // Don't close the modal so user can retry
      }
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
      // Prevent double submission
      if (isSubmittingCase.value) {
        console.log('Case submission already in progress, ignoring duplicate request');
        return;
      }

      isSubmittingCase.value = true;

      try {
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
        
        // Now using the actual IDs stored when creating clients/perpetrators
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
        
        // Updated attachments payload to use real IDs
        const attachmentsPayload = (formData.step4.attachments || []).map((attachment) => ({
          attachment_id: String(attachment.id || attachment.attachment_id || "")
        })).filter(item => item.attachment_id !== "");
        
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
          
          reporter_id: "1",  // Hardcoded for now
          reporter_contact_id: "1",  // Changed from 86808 to 1 since 86808 doesn't exist
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
        
        // Step 1: Handle reporter as client if needed
        let reporterAsClientId = null;
        if (formData.step2.isClient) {
          console.log('Reporter is also a client, creating client record...');
          
          const reporterClientPayload = {
            ".id": "",
            ...baseSourceFields,
            fname: getValueOrDefault(formData.step2.name),
            age_t: "0",
            age: getValueOrDefault(formData.step2.age),
            dob: getValueOrDefault(formData.step2.dob),
            age_group_id: getValueOrDefault(formData.step2.ageGroup),
            location_id: getValueOrDefault(formData.step2.location),
            sex_id: getValueOrDefault(formData.step2.gender),
            landmark: getValueOrDefault(formData.step2.nearestLandmark),
            nationality_id: getValueOrDefault(formData.step2.nationality),
            national_id_type_id: getValueOrDefault(formData.step2.idType),
            national_id: getValueOrDefault(formData.step2.idNumber),
            lang_id: getValueOrDefault(formData.step2.language),
            is_refugee: "", // Reporter form doesn't have this field
            tribe_id: getValueOrDefault(formData.step2.tribe),
            phone: getValueOrDefault(formData.step2.phone),
            phone2: getValueOrDefault(formData.step2.altPhone),
            email: getValueOrDefault(formData.step2.email),
            relationship_to_reporter_id: "", // Reporter is self, so relationship might be empty or "self"
            relationship_comment: "Reporter is also the client",
            // Other client-specific fields can be empty since reporter form doesn't have them
            adults_in_household: "",
            household_type_id: "",
            head_occupation_id: "",
            parent_guardian_name: "",
            parent_marital_status_id: "",
            parent_id_number: "",
            health_status_id: "",
            hiv_status_id: "",
            marital_status_id: "",
            attending_school_id: "",
            school_name: "",
            school_level_id: "",
            school_address: "",
            school_type_id: "",
            school_attendance_id: "",
            is_disabled: "",
            disability_id: "",
            special_services_referred: "",
            special_services_referral: []
          };

          const reporterClientResult = await clientStore.createClient(reporterClientPayload);
          if (reporterClientResult && reporterClientResult.id) {
            reporterAsClientId = reporterClientResult.id;
            console.log('Reporter created as client with ID:', reporterAsClientId);
          } else {
            throw new Error('Failed to create reporter as client - no ID returned');
          }
        }

        // Step 2: Update clients payload to include reporter as client if created
        const allClientIds = [...formData.step2.clients.map(client => client.id || "")];
        if (reporterAsClientId) {
          allClientIds.push(reporterAsClientId);
        }
        
        const finalClientsPayload = allClientIds.filter(id => id !== "").map(clientId => ({
          client_id: clientId
        }));

        // Update the casePayload with the final clients list
        casePayload.clients_case = finalClientsPayload;

        console.log('Submitting payload:', JSON.stringify(casePayload, null, 2));
        await casesStore.createCase(casePayload);
        alert("Case created successfully!");
        router.push("/cases");
      } catch (error) {
        console.error("Failed to create case:", error);
        alert("An error occurred while creating the case: " + error.message);
      } finally {
        isSubmittingCase.value = false;
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

    // Return all variables and methods
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
      // Store access for loading states
      clientStore,
      perpetratorStore,
      filesStore,
      isSubmittingCase,
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
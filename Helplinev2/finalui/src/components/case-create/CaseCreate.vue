<template>
  <div 
    class="min-h-screen py-8 px-4 sm:px-6 lg:px-8"
    :class="isDarkMode ? 'bg-black' : 'bg-gray-50'"
  >
    <div class="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-8">
      
      <!-- Left Column: Case Wizard -->
      <div 
        class="space-y-8 transition-all duration-500"
        :class="aiEnabled ? 'lg:col-span-2' : 'lg:col-span-3'"
      >
        <!-- Header Section -->
        <div>
          <CaseHeader 
            :currentStep="currentStep"
            :stepDescriptions="stepDescriptions"
            v-model:aiEnabled="aiEnabled"
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
        <div 
          class="rounded-xl shadow-xl border p-6 sm:p-8"
          :class="isDarkMode 
            ? 'bg-neutral-900 border-transparent' 
            : 'bg-white border-transparent'"
        >
          <!-- Step 1: Reporter Selection -->
          <Step1ReporterSelection
            v-if="currentStep === 1"
            :currentStep="currentStep"
            :searchQuery="formData.step1.searchQuery"
            :filteredContacts="formData.step1.filteredContacts"
            :selectedReporter="formData.step1.selectedReporter"
            :reporterId="reporterId"
            @search-change="handleSearchChange"
            @select-reporter="selectExistingReporter"
            @create-new-reporter="createNewReporter"
            @reporter-created="handleReporterCreated"
            @validate-and-proceed="validateAndProceed(1)"
            @cancel-form="cancelForm"
          />
          
          <!-- Step 2: Case Details -->
          <Step2CaseDetails
            v-if="currentStep === 2"
            :currentStep="currentStep"
            :formData="formData.step2"
            @form-update="updateFormData('step2', $event)"
            @save-and-proceed="saveAndProceed(2)"
            @step-change="goToStep"            
          />
          
          <!-- Step 3: Additional Details -->
          <Step3AdditionalDetails
            v-if="currentStep === 3"
            :currentStep="currentStep"
            :formData="formData.step3"
            @form-update="updateFormData('step3', $event)"
            @open-client-modal="openClientModal"
            @open-perpetrator-modal="openPerpetratorModal"
            @remove-client="removeClient"
            @remove-perpetrator="removePerpetrator"
            @save-and-proceed="saveAndProceed(3)"
            @step-change="goToStep"
          />
          
          <!-- Step 4: Review -->
          <Step4Review
            v-if="currentStep === 4"
            :currentStep="currentStep"
            :formData="formData"
            :reporterId="reporterId"
            @go-to-step="goToStep"
            @submit-case="submitCase"
          />
        </div>
      </div>

      <!-- Right Column: Insights Panel (1/3 width) -->
      <div v-if="aiEnabled" class="lg:col-span-1 animate-in fade-in slide-in-from-right-8 duration-500">
        <div class="sticky top-6">
          <CaseInsightsPanel :aiEnabled="aiEnabled" />
        </div>
      </div>

    </div>
    
    <!-- Modals -->
    <ClientModal
      v-if="clientModalOpen"
      :clients="formData.step3.clients"
      :clientForm="clientForm"
      :currentClientStep="currentClientStep"
      :loading="clientStore.loading"
      @close-modal="closeClientModal"
      @remove-client="removeClient"
      @update-client-form="updateClientForm"
      @prev-client-step="prevClientStep"
      @next-client-step="nextClientStep"
      @add-client="addClient"
    />
    
    <PerpetratorModal
      v-if="perpetratorModalOpen"
      :perpetrators="formData.step3.perpetrators"
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
import { ref, reactive, inject } from 'vue';
import { useRouter } from 'vue-router';
import { toast } from 'vue-sonner';
import { useCaseStore } from '@/stores/cases';
import { useReporterStore } from '@/stores/reporters';
import { useClientStore } from '@/stores/clients';
import { usePerpetratorStore } from '@/stores/perpetrators';

import CaseHeader from '@/components/case-create/CaseHeader.vue';
import ProgressTracker from '@/components/case-create/ProgressTracker.vue';
import Step1ReporterSelection from '@/components/case-create/Step1ReporterSelection.vue';
import Step2CaseDetails from '@/components/case-create/Step2CaseDetails.vue';
import Step3AdditionalDetails from '@/components/case-create/Step3AdditionalDetails.vue';
import Step4Review from '@/components/case-create/Step4Review.vue';
import ClientModal from '@/components/case-create/ClientModal.vue';
import PerpetratorModal from '@/components/case-create/PerpetratorModal.vue';
import CaseInsightsPanel from '@/components/case-create/CaseInsightsPanel.vue';

export default {
  name: 'CaseCreation',
  components: {
    CaseHeader,
    ProgressTracker,
    Step1ReporterSelection,
    Step2CaseDetails,
    Step3AdditionalDetails,
    Step4Review,
    ClientModal,
    PerpetratorModal,
    CaseInsightsPanel
  },
  setup() {
    const router = useRouter();
    const casesStore = useCaseStore();
    const reporterStore = useReporterStore();
    const clientStore = useClientStore();
    const perpetratorStore = usePerpetratorStore();
    
    // Inject theme
    const isDarkMode = inject('isDarkMode');
    
    const currentStep = ref(1);
    const totalSteps = 4;
    const isSubmittingCase = ref(false);
    const aiEnabled = ref(false);
    
    // ✅ Store BOTH reporter IDs separately
    const reporterRecordId = ref(null);  // Index 0 - for reporter_uuid_id
    const reporterContactId = ref(null); // Index 5 - for contact_uuid_id
    
    const stepStatus = reactive({
      1: "active",
      2: "pending",
      3: "pending",
      4: "pending"
    });
    
    const stepLabels = [
      'Reporter',
      'Case Details',
      'Additional Info',
      'Review'
    ];
    
    const stepDescriptions = [
      'Search for an existing reporter or create a new one.',
      'Enter case details including narrative, priority, and classification.',
      'Add clients, perpetrators, and additional case information.',
      'Review all information before creating the case.'
    ];
    
    const formData = reactive({
      step1: {
        searchQuery: '',
        selectedReporter: null,
        filteredContacts: []
      },
      step2: {
        narrative: '',
        plan: '',
        isGBVRelated: '',
        categories: '',
        priority: '',
        status: '',
        department: '',
        escalatedTo: '',
        clientPassportNumber: '',
        justiceSystemState: '',
        generalAssessment: '',
        isGBVRelatedText: '',
        categoriesText: '',
        priorityText: '',
        statusText: '',
        departmentText: '',
        escalatedToText: '',
        justiceSystemStateText: '',
        generalAssessmentText: ''
      },
      step3: {
        clients: [],
        perpetrators: [],
        attachments: [],
        servicesOffered: [],
        servicesOfferedText: [],
        referralSource: '',
        referralSourceText: '',
        referralsType: [],
        referralsTypeText: [],
        policeDetails: '',
        otherServicesDetails: ''
      }
    });
    
    // Client Modal State
    const clientModalOpen = ref(false);
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
    
    // Perpetrator Modal State
    const perpetratorModalOpen = ref(false);
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

    // Helper function to get field index from reporter store
    const getReporterFieldIndex = (fieldName) => {
      const mapping = reporterStore.reporters_k?.[`contact_${fieldName}`];
      if (mapping && Array.isArray(mapping) && mapping.length > 0) {
        return mapping[0];
      }
      const fallbackMapping = reporterStore.reporters_k?.[fieldName];
      if (fallbackMapping && Array.isArray(fallbackMapping) && fallbackMapping.length > 0) {
        return fallbackMapping[0];
      }
      return null;
    };

    // Helper function to get value from reporter contact array
    const getReporterValue = (contact, fieldName) => {
      if (!contact || !Array.isArray(contact)) return "";
      const idx = getReporterFieldIndex(fieldName);
      if (idx !== null && idx >= 0 && idx < contact.length) {
        return contact[idx] || "";
      }
      return "";
    };

    // Methods
    const updateFormData = (step, data) => {
      if (step === 'step2') {
        Object.keys(data).forEach(key => {
          formData.step2[key] = data[key];
        });
      } else if (step === 'step3') {
        if (data.servicesOfferedSelection) {
          formData.step3.servicesOffered = data.servicesOfferedSelection.values || [];
          formData.step3.servicesOfferedText = data.servicesOfferedSelection.texts || [];
        }
        Object.keys(data).forEach(key => {
          if (key !== 'servicesOfferedSelection') {
            formData.step3[key] = data[key];
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
      if (step === 1) {
        if (!reporterRecordId.value || !reporterContactId.value) {
          toast.error('Please select or create a reporter before proceeding');
          return;
        }
      }
      
      stepStatus[step] = "completed";
      navigateToStep(step + 1);
    };
    
    const saveAndProceed = (step) => {
      if (step === 2) {
        const errors = [];
        if (!formData.step2.isGBVRelated) errors.push('GBV Related is required');
        if (!formData.step2.categories) errors.push('Case Category is required');
        if (!formData.step2.priority) errors.push('Priority is required');
        if (!formData.step2.status) errors.push('Status is required');
        if (!formData.step2.narrative || !formData.step2.narrative.trim()) errors.push('Narrative is required');
        if (!formData.step2.plan || !formData.step2.plan.trim()) errors.push('Plan is required');
        
        if (errors.length > 0) {
          toast.error('Please fill in all required fields', {
            description: errors.join(', ')
          });
          return;
        }
      }
      
      stepStatus[step] = "completed";
      navigateToStep(step + 1);
    };
    
    const cancelForm = () => {
      router.push('/cases');
    };
    
    const handleSearchChange = (query) => {
      formData.step1.searchQuery = query;
    };
    
    const selectExistingReporter = (reporter) => {
      formData.step1.selectedReporter = reporter;
    };
    
    const createNewReporter = () => {
      formData.step1.selectedReporter = null;
      reporterRecordId.value = null;
      reporterContactId.value = null;
    };
    
    // ✅ FIXED: Receive BOTH IDs from child component
    const handleReporterCreated = (ids) => {
      reporterRecordId.value = ids.reporterId;   // Index 0
      reporterContactId.value = ids.contactId;   // Index 5
      
      console.log('✅ Reporter IDs stored in parent:', {
        reporterRecordId: reporterRecordId.value,
        reporterContactId: reporterContactId.value
      });
      
      toast.success('Reporter selected successfully!');
    };
    
    // Client Modal Methods
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
    
    const updateClientForm = (data) => {
      Object.assign(clientForm, data);
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
      if (!clientForm.name || clientForm.name.trim() === '') {
        toast.error('Client name is required');
        return;
      }

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

        const result = await clientStore.createClient(clientPayload);
        
        if (result && result.id) {
          const clientData = { 
            ...clientForm, 
            id: result.id
          };
          
          formData.step3.clients.push(clientData);
          toast.success('Client added successfully!');
          closeClientModal();
        } else {
          throw new Error('No client ID returned from server');
        }

      } catch (error) {
        console.error('Error creating client:', error);
        toast.error('Failed to create client', {
          description: error.message
        });
      }
    };
    
    const removeClient = (index) => {
      formData.step3.clients.splice(index, 1);
      toast.info('Client removed');
    };
    
    // Perpetrator Modal Methods
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
      if (!perpetratorForm.name || perpetratorForm.name.trim() === '') {
        toast.error('Perpetrator name is required');
        return;
      }

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

        const perpetratorPayload = {
          ".id": "",
          ...baseSourceFields,
          fname: getValueOrDefault(perpetratorForm.name),
          age_t: "0",
          age: getValueOrDefault(perpetratorForm.age),
          dob: getValueOrDefault(perpetratorForm.dob),
          age_group_id: getValueOrDefault(perpetratorForm.ageGroup),
          location_id: getValueOrDefault(perpetratorForm.sex),
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

        const result = await perpetratorStore.createPerpetrator(perpetratorPayload);
        
        if (result && result.id) {
          const perpetratorData = { 
            ...perpetratorForm, 
            id: result.id
          };
          
          formData.step3.perpetrators.push(perpetratorData);
          toast.success('Perpetrator added successfully!');
          closePerpetratorModal();
        } else {
          throw new Error('No perpetrator ID returned from server');
        }

      } catch (error) {
        console.error('Error creating perpetrator:', error);
        toast.error('Failed to create perpetrator', {
          description: error.message
        });
      }
    };
    
    const removePerpetrator = (index) => {
      formData.step3.perpetrators.splice(index, 1);
      toast.info('Perpetrator removed');
    };
    
    const submitCase = async () => {
      if (isSubmittingCase.value) {
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
        
        const clientsPayload = formData.step3.clients.map(client => ({
          client_id: client.id || ""
        }));
        
        const perpetratorsPayload = formData.step3.perpetrators.map(perpetrator => ({
          perpetrator_id: perpetrator.id || ""
        }));
        
        const servicesPayload = (formData.step3.servicesOffered || []).map(serviceId => ({
          category_id: String(serviceId)
        }));
        
        const referralsPayload = (formData.step3.referralsType || []).map(referralId => ({
          category_id: String(referralId)
        }));
        
        const attachmentsPayload = (formData.step3.attachments || []).map((attachment) => ({
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
        
        console.log('='.repeat(80));
        console.log('📤 SUBMITTING CASE WITH IDs:');
        console.log('reporter_uuid_id (Index 0):', reporterRecordId.value);
        console.log('contact_uuid_id (Index 5):', reporterContactId.value);
        console.log('='.repeat(80));
        
        // ✅ FIXED: Use the correct IDs
        const casePayload = {
          ".id": "",
          ...baseSourceFields,
          src_address: getValueOrDefault(formData.step3.clients[0]?.phone || ""),
          
          // ✅ CRITICAL FIX: Use DIFFERENT IDs for each field
          reporter_uuid_id: reporterRecordId.value || "",  // Index 0
          contact_uuid_id: reporterContactId.value || "",  // Index 5
          
          case_category_id: getValueOrDefault(formData.step2.categories),
          narrative: getValueOrDefault(formData.step2.narrative),
          plan: getValueOrDefault(formData.step2.plan),
          dept: mapDepartmentToBackend(formData.step2.department),
          disposition_id: "363037",
          escalated_to_id: getValueOrDefault(formData.step2.escalatedTo, "0"),
          gbv_related: mapGBVRelatedToBackend(formData.step2.isGBVRelated),
          knowabout116_id: getValueOrDefault(formData.step3.referralSource),
          police_ob_no: getValueOrDefault(formData.step3.policeDetails),
          priority: getValueOrDefault(formData.step2.priority) || "1",
          status: getValueOrDefault(formData.step2.status) || "1",
          
          national_id_: getValueOrDefault(formData.step2.clientPassportNumber),
          justice_id: getValueOrDefault(formData.step2.justiceSystemState),
          assessment_id: getValueOrDefault(formData.step2.generalAssessment),
          
          services: servicesPayload,
          referals: referralsPayload,
          specify_service: getValueOrDefault(formData.step3.otherServicesDetails),
          clients_case: clientsPayload,
          perpetrators_case: perpetratorsPayload,
          attachments_case: attachmentsPayload,
          
          activity_id: "",
          activity_ca_id: ""
        };
        
        // Remove undefined fields
        Object.keys(casePayload).forEach(key => {
          if (casePayload[key] === undefined) {
            delete casePayload[key];
          }
        });
        
        console.log('✅ Final payload:', casePayload);
        
        await casesStore.createCase(casePayload);
        
        toast.success('Case created successfully!', {
          description: 'The case has been submitted to the system.'
        });
        
        setTimeout(() => {
          router.push("/cases");
        }, 1500);
        
      } catch (error) {
        console.error("Failed to create case:", error);
        toast.error('Failed to create case', {
          description: error.message || 'An error occurred while creating the case'
        });
      } finally {
        isSubmittingCase.value = false;
      }
    };

    return {
      isDarkMode,
      currentStep,
      totalSteps,
      stepStatus,
      stepLabels,
      stepDescriptions,
      formData,
      reporterRecordId,
      reporterContactId,
      clientModalOpen,
      perpetratorModalOpen,
      currentClientStep,
      clientForm,
      currentPerpetratorStep,
      perpetratorForm,
      clientStore,
      perpetratorStore,
      isSubmittingCase,
      updateFormData,
      aiEnabled,
      navigateToStep,
      goToStep,
      validateAndProceed,
      saveAndProceed,
      cancelForm,
      openClientModal,
      closeClientModal,
      openPerpetratorModal,
      closePerpetratorModal,
      updateClientForm,
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
      handleReporterCreated,
      submitCase
    };
  }
};
</script>
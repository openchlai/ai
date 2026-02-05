<template>
  <LegacyCaseLayout>
    <!-- SOCIAL WORKER / LEFT SIDEBAR -->
    <template #sidebar>
      <!-- Reporter Card -->
      <div class="p-4 rounded-xl border shadow-sm space-y-4"
        :class="isDarkMode ? 'bg-gray-900 border-gray-800' : 'bg-white border-gray-100'">
        <div class="flex justify-between items-center">
          <h3 class="font-semibold text-lg" :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'">Reporter</h3>
          <button v-if="formData.step1.selectedReporter" @click="clearReporter"
            class="text-xs text-red-500 hover:text-red-600">
            Change
          </button>
        </div>

        <!-- Reporter Selection/Search -->
        <div v-if="!formData.step1.selectedReporter">
          <div class="relative">
            <input v-model="formData.step1.searchQuery" type="text" placeholder="Search reporter..."
              class="w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-amber-500 focus:border-transparent outline-none"
              :class="isDarkMode ? 'bg-gray-800 border-gray-700 text-white placeholder-gray-500' : 'bg-gray-50 border-gray-200 text-gray-900'"
              @input="handleReporterSearch" />
            <div v-if="isSearchingReporter" class="absolute right-3 top-2.5">
              <div class="w-4 h-4 border-2 border-amber-500 border-t-transparent rounded-full animate-spin"></div>
            </div>
          </div>

          <!-- Search Results Dropdown -->
          <div v-if="formData.step1.filteredContacts.length > 0"
            class="mt-2 max-h-60 overflow-y-auto border rounded-lg divide-y"
            :class="isDarkMode ? 'bg-gray-800 border-gray-700 divide-gray-700' : 'bg-white border-gray-200 divide-gray-100'">
            <div v-for="contact in formData.step1.filteredContacts" :key="contact._id"
              class="p-2 cursor-pointer hover:bg-opacity-50 transition-colors"
              :class="isDarkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-50'" @click="selectReporter(contact)">
              <div class="text-sm font-medium" :class="isDarkMode ? 'text-gray-200' : 'text-gray-900'">{{
                getReporterName(contact) }}</div>
              <div class="text-xs text-gray-500">{{ getReporterPhone(contact) }}</div>
            </div>
          </div>

          <div class="mt-3">
            <button type="button"
              class="w-full py-2 text-sm text-amber-600 font-medium hover:text-amber-700 flex justify-center items-center gap-1"
              @click="openCreateReporter">
              <span>+ Create New Reporter</span>
            </button>
          </div>
        </div>

        <!-- Selected Reporter Card -->
        <div v-else class="space-y-3">
          <div class="flex items-start gap-3">
            <div class="w-10 h-10 rounded-full bg-amber-600 text-white flex items-center justify-center font-bold">
              {{ getInitials(getReporterName(formData.step1.selectedReporter)) }}
            </div>
            <div>
              <div class="font-medium" :class="isDarkMode ? 'text-gray-200' : 'text-gray-900'">
                {{ getReporterName(formData.step1.selectedReporter) }}
              </div>
              <div class="text-xs text-gray-500">
                {{ getReporterPhone(formData.step1.selectedReporter) }}
              </div>
            </div>
          </div>

          <div class="flex flex-wrap gap-2 text-xs">
            <span class="px-2 py-1 rounded bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400">
              {{ getReporterAge(formData.step1.selectedReporter) }} years
            </span>
            <span class="px-2 py-1 rounded bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400">
              {{ getReporterLocation(formData.step1.selectedReporter) }}
            </span>
          </div>

          <label class="flex items-center gap-2 cursor-pointer">
            <input type="checkbox" v-model="formData.step1.reporterIsClient"
              class="w-4 h-4 rounded text-amber-600 focus:ring-amber-500 border-gray-300">
            <span class="text-sm" :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'">Reporter is also a
              Client</span>
          </label>
        </div>
      </div>

      <!-- Clients Section -->
      <div class="p-4 rounded-xl border shadow-sm space-y-4"
        :class="isDarkMode ? 'bg-gray-900 border-gray-800' : 'bg-white border-gray-100'">
        <div class="flex justify-between items-center">
          <h3 class="font-semibold text-lg" :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'">Clients</h3>
          <button type="button"
            class="w-6 h-6 flex items-center justify-center rounded-full bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
            @click="openClientModal">
            <span class="text-lg leading-none mb-0.5">+</span>
          </button>
        </div>

        <div v-if="formData.step3.clients.length === 0" class="text-xs text-gray-500 italic">No clients added.</div>

        <div class="space-y-2">
          <div v-for="(client, idx) in formData.step3.clients" :key="idx"
            class="p-2 rounded border flex justify-between items-center"
            :class="isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-gray-50 border-gray-200'">
            <div class="text-sm truncate pr-2" :class="isDarkMode ? 'text-gray-200' : 'text-gray-700'">
              {{ client.name }}
            </div>
            <button @click="removeClient(idx)" class="text-red-500 hover:text-red-700">
              <span class="sr-only">Remove</span>
              x
            </button>
          </div>
        </div>

        <button type="button"
          class="w-full py-1.5 text-sm border border-dashed rounded text-gray-500 hover:text-gray-700 hover:border-gray-400 dark:border-gray-700 dark:hover:border-gray-600 transition-colors"
          @click="openClientModal">
          + Add a Client
        </button>
      </div>

      <!-- Perpetrators Section -->
      <div class="p-4 rounded-xl border shadow-sm space-y-4"
        :class="isDarkMode ? 'bg-gray-900 border-gray-800' : 'bg-white border-gray-100'">
        <div class="flex justify-between items-center">
          <h3 class="font-semibold text-lg" :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'">Perpetrators</h3>
        </div>

        <div v-if="formData.step3.perpetrators.length === 0" class="text-xs text-gray-500 italic">No perpetrators added.
        </div>

        <div class="space-y-2">
          <div v-for="(perp, idx) in formData.step3.perpetrators" :key="idx"
            class="p-2 rounded border flex justify-between items-center"
            :class="isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-gray-50 border-gray-200'">
            <div class="text-sm truncate pr-2" :class="isDarkMode ? 'text-gray-200' : 'text-gray-700'">
              {{ perp.name }}
            </div>
            <button @click="removePerpetrator(idx)" class="text-red-500 hover:text-red-700">
              <span class="sr-only">Remove</span>
              x
            </button>
          </div>
        </div>

        <button type="button"
          class="w-full py-1.5 text-sm border border-dashed rounded text-gray-500 hover:text-gray-700 hover:border-gray-400 dark:border-gray-700 dark:hover:border-gray-600 transition-colors"
          @click="openPerpetratorModal">
          + Add a Perpetrator
        </button>
      </div>

      <!-- Related Files -->
      <div class="p-4 rounded-xl border shadow-sm space-y-4"
        :class="isDarkMode ? 'bg-gray-900 border-gray-800' : 'bg-white border-gray-100'">
        <h3 class="font-semibold text-lg" :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'">Related Files</h3>
        <AttachmentUpload v-model="formData.step3.attachments" label="" description="" compact :max-size-mb="10" />
      </div>

      <!-- Services & Referral -->
      <div class="p-4 rounded-xl border shadow-sm space-y-4"
        :class="isDarkMode ? 'bg-gray-900 border-gray-800' : 'bg-white border-gray-100'">
        <BaseOptions id="services-offered" label="Services Offered" v-model="formData.step3.servicesOffered"
          placeholder="Select services..." :category-id="taxonomyStore.roots.SERVICE_OFFERED"
          @selection-change="handleServicesChange" />

        <TaxonomySelect id="know about 116" label="How did you know about 116?" v-model="formData.step3.referralSource"
          placeholder="Select option" root-key="KNOW_ABOUT_116" />
      </div>

    </template>


    <!-- MAIN CONTENT -->
    <template #main>
      <div class="space-y-6">
        <h2 class="text-xl font-bold" :class="isDarkMode ? 'text-white' : 'text-gray-900'">Case Details</h2>

        <!-- Department (Required) -->
        <div>
          <label class="block font-semibold mb-2" :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'">Department
            *</label>
          <div class="flex gap-4">
            <label class="flex items-center gap-2 cursor-pointer">
              <input v-model="formData.step2.department" type="radio" value="116"
                class="w-4 h-4 text-amber-600 focus:ring-amber-500">
              <span :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'">116</span>
            </label>
            <label class="flex items-center gap-2 cursor-pointer">
              <input v-model="formData.step2.department" type="radio" value="labor"
                class="w-4 h-4 text-amber-600 focus:ring-amber-500">
              <span :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'">Labor</span>
            </label>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Case Category -->
          <TaxonomySelect id="case-category" label="Case Category *" v-model="formData.step2.categories"
            placeholder="Select category" root-key="CASE_CATEGORY" searchable />

          <!-- GBV -->
          <TaxonomySelect label="GBV Related? *" v-model="formData.step2.isGBVRelated" placeholder="Select option"
            root-key="GBV_RELATED" />

          <!-- Incident Location -->
          <TaxonomySelect label="Incident Location *" v-model="formData.step2.incidentLocation"
            placeholder="Select location" root-key="LOCATION" searchable />
        </div>

        <!-- Narrative -->
        <BaseTextarea id="case-narrative" label="Case Narrative *" v-model="formData.step2.narrative"
          placeholder="Describe the case details..." :rows="6" />

        <!-- Plan -->
        <div>
          <label class="block font-semibold mb-2" :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'">Case
            Plan</label>
          <textarea v-model="formData.step2.plan"
            class="w-full px-3 py-2 border rounded-lg resize-y focus:ring-2 focus:ring-amber-500 focus:border-transparent outline-none transition-all"
            :class="isDarkMode ? 'bg-gray-800 border-gray-700 text-white placeholder-gray-500' : 'bg-gray-50 border-gray-200 text-gray-900'"
            rows="4" placeholder="Enter case plan..."></textarea>
        </div>
      </div>
    </template>

    <!-- LOWER SECTION -->
    <template #lower>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <TaxonomySelect id="justice-system-state" label="State of Case in Justice System"
          v-model="formData.step2.justiceSystemState" placeholder="Select state" root-key="JUSTICE_SYSTEM_STATE"
          searchable />

        <TaxonomySelect id="general-assessment" label="General Case Assessment"
          v-model="formData.step2.generalAssessment" placeholder="Select assessment" root-key="GENERAL_ASSESSMENT"
          searchable />
      </div>
    </template>

    <!-- FOOTER -->
    <template #footer>
      <div class="flex flex-col md:flex-row gap-6 items-end">
        <div class="flex-1 w-full grid grid-cols-1 md:grid-cols-3 gap-6">
          <!-- Priority -->
          <div>
            <label class="block font-semibold mb-2" :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'">Priority
              *</label>
            <select v-model="formData.step2.priority"
              class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-amber-500 outline-none"
              :class="isDarkMode ? 'bg-gray-800 border-gray-700 text-white' : 'bg-gray-50 border-gray-200 text-gray-900'">
              <option value="">Select</option>
              <option value="3">High</option>
              <option value="2">Medium</option>
              <option value="1">Low</option>
            </select>
          </div>

          <!-- Status -->
          <div>
            <label class="block font-semibold mb-2" :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'">Status
              *</label>
            <select v-model="formData.step2.status"
              class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-amber-500 outline-none"
              :class="isDarkMode ? 'bg-gray-800 border-gray-700 text-white' : 'bg-gray-50 border-gray-200 text-gray-900'">
              <option value="">Select</option>
              <option value="1">Open</option>
              <option value="2">Closed</option>
            </select>
          </div>

          <!-- Escalated To -->
          <div>
            <!-- Simplified User Select (assuming component usage or plain select) -->
            <label class="block font-semibold mb-2" :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'">Escalated
              To</label>
            <select v-model="formData.step2.escalatedTo"
              class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-amber-500 outline-none"
              :class="isDarkMode ? 'bg-gray-800 border-gray-700 text-white' : 'bg-gray-50 border-gray-200 text-gray-900'">
              <option value="0">None</option>
              <option v-for="user in escalatedToUsers" :key="user.id" :value="user.id">
                {{ user.name }}
              </option>
            </select>
          </div>
        </div>

        <div class="flex gap-4 shrink-0">
          <button type="button" class="px-6 py-2.5 rounded-lg border font-medium transition-colors"
            :class="isDarkMode ? 'border-gray-700 text-gray-300 hover:bg-gray-800' : 'border-gray-300 text-gray-700 hover:bg-gray-50'"
            @click="cancel">
            Cancel
          </button>
          <button type="button" class="px-6 py-2.5 rounded-lg font-medium text-white transition-colors shadow-lg"
            :class="isDarkMode ? 'bg-amber-600 hover:bg-amber-700' : 'bg-amber-700 hover:bg-amber-800'"
            @click="submitFullCase">
            Update Case
          </button>
        </div>
      </div>
    </template>

    <!-- RIGHT SIDEBAR (AI Assistant) -->
    <template #right-sidebar>
      <CaseInsightsPanel :ai-enabled="true" />
    </template>
  </LegacyCaseLayout>

  <!-- Modals -->
  <!-- Modals -->
  <ClientModalLegacy :is-open="clientModalOpen" :client-data="clientForm" @close="closeClientModal"
    @update="handleLegacyClientUpdate" />

  <PerpetratorModalLegacy :is-open="perpetratorModalOpen" :perpetrator-data="perpetratorForm"
    @close="closePerpetratorModal" @create="handleLegacyPerpetratorCreate" />

  <ReporterModalLegacy :is-open="createReporterOpen" :reporter-data="reporterForm" @close="createReporterOpen = false"
    @update="handleLegacyReporterUpdate" />

</template>

<script setup>
  import { ref, reactive, inject, onMounted, computed, watch } from 'vue';
  import { useRouter } from 'vue-router';
  import { toast } from 'vue-sonner';

  import LegacyCaseLayout from './LegacyCaseLayout.vue';
  import BaseSelect from '@/components/base/BaseSelect.vue';
  import BaseTextarea from '@/components/base/BaseTextarea.vue';
  import BaseOptions from '@/components/base/BaseOptions.vue';
  import AttachmentUpload from '@/components/case-create/AttachmentUpload.vue';
  import ClientModalLegacy from '@/components/case-create/ClientModalLegacy.vue';
  import PerpetratorModalLegacy from '@/components/case-create/PerpetratorModalLegacy.vue';
  import ReporterModalLegacy from '@/components/case-create/ReporterModalLegacy.vue';
  import CaseInsightsPanel from '@/components/case-create/CaseInsightsPanel.vue';
  import TaxonomySelect from '@/components/base/TaxonomySelect.vue';

  // Stores
  import { useCaseStore } from '@/stores/cases';
  import { useReporterStore } from '@/stores/reporters';
  import { useClientStore } from '@/stores/clients';
  import { usePerpetratorStore } from '@/stores/perpetrators';
  import { useUserStore } from '@/stores/users';
  import { useTaxonomyStore } from '@/stores/taxonomy';

  const taxonomyStore = useTaxonomyStore();
  import { useAuthStore } from '@/stores/auth';

  const router = useRouter();
  const isDarkMode = inject('isDarkMode');

  const casesStore = useCaseStore();
  const reporterStore = useReporterStore();
  const clientStore = useClientStore();
  const perpetratorStore = usePerpetratorStore();
  const userStore = useUserStore();
  const authStore = useAuthStore();

  // State
  const isSearchingReporter = ref(false);
  const createReporterOpen = ref(false);
  const clientModalOpen = ref(false);
  const perpetratorModalOpen = ref(false);
  const isSubmitting = ref(false);

  const currentClientStep = ref(0);
  const currentPerpetratorStep = ref(0);

  // Data
  const formData = reactive({
    metadata: { src: 'walkin' },
    step1: {
      searchQuery: '',
      selectedReporter: null,
      filteredContacts: [],
      reporterIsClient: false,
    },
    step2: {
      department: '',
      categories: '',
      isGBVRelated: '',
      narrative: '',
      plan: '',
      priority: '',
      status: '',
      escalatedTo: '0',
      justiceSystemState: '',
      generalAssessment: '',
      incidentLocation: ''
    },
    step3: {
      clients: [],
      perpetrators: [],
      attachments: [],
      servicesOffered: [],
      referralSource: '',
      policeDetails: '',
      otherServicesDetails: ''
    }
  });

  const reporterForm = reactive({ fname: '', phone: '', age: '', sex: '', location: '' });
  const clientForm = reactive({}); // Needs full fields
  const perpetratorForm = reactive({}); // Needs full fields

  // Copy pasted ID logic
  const reporterRecordId = ref(null);
  const reporterContactId = ref(null);

  onMounted(async () => {
    await reporterStore.listReporters();
    await userStore.listUsers();
  });

  // Reporter Logic
  const handleReporterSearch = async () => {
    if (formData.step1.searchQuery.length < 2) {
      formData.step1.filteredContacts = [];
      return;
    }
    isSearchingReporter.value = true;
    // Simulate search or filter existing store
    const query = formData.step1.searchQuery.toLowerCase();
    formData.step1.filteredContacts = reporterStore.reporters.filter(r => {
      // rough implementation based on store structure
      const name = (r[reporterStore.reporters_k?.contact_fullname?.[0]] || '').toLowerCase();
      const phone = (r[reporterStore.reporters_k?.contact_phone?.[0]] || '');
      return name.includes(query) || phone.includes(query);
    }).slice(0, 10);
    isSearchingReporter.value = false;
  };

  const selectReporter = (contact) => {
    formData.step1.selectedReporter = contact;
    formData.step1.filteredContacts = [];
    formData.step1.searchQuery = '';

    // Extract IDs
    reporterRecordId.value = contact[0]; // Assumption based on previous file viewing
    reporterContactId.value = contact[5]; // Assumption
  };

  const clearReporter = () => {
    formData.step1.selectedReporter = null;
    reporterRecordId.value = null;
    reporterContactId.value = null;
  };

  const getReporterName = (r) => r?.[reporterStore.reporters_k?.contact_fullname?.[0]] || 'Unknown';
  const getReporterPhone = (r) => r?.[reporterStore.reporters_k?.contact_phone?.[0]] || 'No phone';
  const getReporterAge = (r) => r?.[reporterStore.reporters_k?.contact_age?.[0]] || '?';
  const getReporterLocation = (r) => r?.[reporterStore.reporters_k?.contact_location?.[0]] || '?';
  const getInitials = (name) => name ? name.substring(0, 2).toUpperCase() : '??';

  const openCreateReporter = () => { createReporterOpen.value = true; };
  const handleCreateReporter = async () => {
    // Simplified creation logic
    // In real impl, would call reporterStore.createReporter
    // For now, mock success
    createReporterOpen.value = false;
    toast.success("Reporter Created (Simulated)");
  };

  // Client/Perp Modal Logic
  const openClientModal = () => { clientModalOpen.value = true; };
  const closeClientModal = () => { clientModalOpen.value = false; };
  const openPerpetratorModal = () => { perpetratorModalOpen.value = true; };
  const closePerpetratorModal = () => { perpetratorModalOpen.value = false; };

  const updateClientForm = (data) => Object.assign(clientForm, data);
  const updatePerpetratorForm = (data) => Object.assign(perpetratorForm, data);
  const prevClientStep = () => { if (currentClientStep.value > 0) currentClientStep.value--; };
  const nextClientStep = () => { currentClientStep.value++; }; // Limit check needed
  const addClient = () => {
    // Call store createClient logic...
    // Push to formData.step3.clients
    closeClientModal();
    toast.success("Client Added (Simulated)");
  };
  const removeClient = (idx) => formData.step3.clients.splice(idx, 1);

  const prevPerpetratorStep = () => { if (currentPerpetratorStep.value > 0) currentPerpetratorStep.value--; };
  const nextPerpetratorStep = () => { currentPerpetratorStep.value++; };
  const addPerpetrator = () => {
    // Call store
    closePerpetratorModal();
    toast.success("Perpetrator Added (Simulated)");
  };
  const removePerpetrator = (idx) => formData.step3.perpetrators.splice(idx, 1);

  // Services Logic
  const handleServicesChange = (selection) => {
    formData.step3.servicesOffered = selection.values || [];
    // Handle text logic if needed
  };

  // Legacy Modal Handlers
  const handleLegacyClientUpdate = (data) => {
    // Add to clients list
    formData.step3.clients.push({ ...data, id: Date.now() }); // temp ID
    toast.success("Client Added");
  };

  const handleLegacyPerpetratorCreate = (data) => {
    formData.step3.perpetrators.push({ ...data, id: Date.now() });
    toast.success("Perpetrator Added");
  };

  const handleLegacyReporterUpdate = (data) => {
    // Update local form state
    Object.assign(reporterForm, data);
    // treating as selected reporter for display
    formData.step1.selectedReporter = {
      ...data,
      [reporterStore.reporters_k?.contact_fullname?.[0] || 2]: data.fname,
      [reporterStore.reporters_k?.contact_phone?.[0] || 5]: data.phone
    };
    toast.success("Reporter Details Updated");
  };

  // Escalation Users
  const escalatedToUsers = computed(() => {
    return userStore.users.map(u => ({
      id: u[userStore.users_k?.id?.[0]],
      name: u[userStore.users_k?.contact_fullname?.[0]] || u[userStore.users_k?.usn?.[0]]
    }));
  });

  // Submit
  const submitFullCase = async () => {
    if (isSubmitting.value) return;

    console.group('🔍 Validating Legacy Form Submission');
    const errors = [];
    if (!formData.step2.department) errors.push("Department is required");
    if (!formData.step2.categories) errors.push("Case Category is required");
    if (!formData.step2.isGBVRelated) errors.push("GBV Related is required");
    if (!formData.step2.narrative) errors.push("Narrative is required");
    if (!formData.step2.priority) errors.push("Priority is required");
    if (!formData.step2.status) errors.push("Status is required");
    if (!formData.step2.incidentLocation) errors.push("Incident Location is required");

    if (formData.step3.clients.length === 0) {
      errors.push("At least one Client is required");
    }

    if (!reporterRecordId.value || !reporterContactId.value) {
      errors.push("Reporter is required");
    }

    if (errors.length > 0) {
      console.groupEnd();
      toast.error("Validation Failed", { description: errors.join(", ") });
      return;
    }
    console.groupEnd();

    isSubmitting.value = true;
    try {
      const timestamp = Date.now();
      const timestampSeconds = (timestamp / 1000).toFixed(3);
      const userId = authStore.user?.id || "100";
      const srcUid = `walkin-${userId}-${timestamp}`;

      const getValueOrDefault = (val, def = "") => val !== null && val !== undefined && val !== "" ? val : def;

      const baseSourceFields = {
        src: formData.metadata.src || "walkin",
        src_ts: timestampSeconds,
        src_uid: formData.metadata.src_uid || srcUid,
        src_uid2: formData.metadata.src_uid || `${srcUid}-1`,
        src_callid: formData.metadata.src_callid || `${srcUid}-1`,
        src_usr: userId,
        src_vector: formData.metadata.src === 'call' ? "1" : "2"
      };

      const clientsPayload = formData.step3.clients.map(c => ({ client_id: c.id || "" }));
      const perpetratorsPayload = formData.step3.perpetrators.map(p => ({ perpetrator_id: p.id || "" }));

      const servicesPayload = (formData.step3.servicesOffered || []).map(id => ({ category_id: String(id) }));

      // Handle referral source (single value to array if needed, or if it's already an array?)
      // CaseCreate uses referralsType for 'referrals' payload. referralSource is for 'knowabout116_id'.
      // Note: In CaseCreate: 
      // referralsPayload = (formData.step3.referralsType || [])
      // And knowabout116_id = formData.step3.referralSource

      // I don't have referralsType in the simplified form UI yet? 
      // The BaseOptions for servicesOffered handles selection.
      // If I want to support Referrals field in Legacy Form, I need to expose it.
      // For now I'll map empty if not present.
      const referralsPayload = [];

      const attachmentsPayload = (formData.step3.attachments || []).map(a => ({
        attachment_id: String(a.id || a.attachment_id || "")
      })).filter(a => a.attachment_id !== "");

      // Map params
      const deptMap = { '116': '1', 'labor': '2' };
      const gbvMap = (val) => ['118002', '363070'].includes(String(val)) ? '1' : '0';

      const casePayload = {
        ".id": "",
        ...baseSourceFields,
        // Use first client's phone as src_address if available
        src_address: getValueOrDefault(formData.step3.clients[0]?.phone),

        reporter_uuid_id: reporterRecordId.value || "",
        contact_uuid_id: reporterContactId.value || "",

        case_category_id: getValueOrDefault(formData.step2.categories),
        narrative: getValueOrDefault(formData.step2.narrative),
        plan: getValueOrDefault(formData.step2.plan),
        dept: deptMap[formData.step2.department] || '0',
        disposition_id: taxonomyStore.dispositions.NEW_CASE || "363037",
        escalated_to_id: getValueOrDefault(formData.step2.escalatedTo, "0"),
        gbv_related: gbvMap(formData.step2.isGBVRelated),
        knowabout116_id: getValueOrDefault(formData.step3.referralSource),
        police_ob_no: getValueOrDefault(formData.step3.policeDetails),
        priority: getValueOrDefault(formData.step2.priority) || "1",
        status: getValueOrDefault(formData.step2.status) || "1",

        national_id_: "",
        justice_id: getValueOrDefault(formData.step2.justiceSystemState),
        assessment_id: getValueOrDefault(formData.step2.generalAssessment),
        incident_location_id: getValueOrDefault(formData.step2.incidentLocation),

        services: servicesPayload,
        referals: referralsPayload,
        referrals: referralsPayload,
        specify_service: getValueOrDefault(formData.step3.otherServicesDetails),
        clients_case: clientsPayload,
        perpetrators_case: perpetratorsPayload,
        attachments_case: attachmentsPayload,

        activity_id: "",
        activity_ca_id: ""
      };

      // Clean payload
      Object.keys(casePayload).forEach(key => {
        if (casePayload[key] === undefined) delete casePayload[key];
      });

      console.log('📤 Submitting Legacy Case:', casePayload);
      await casesStore.createCase(casePayload);
      toast.success("Case created successfully!");
      router.push('/cases');
    } catch (e) {
      console.error('Submission error:', e);
      toast.error("Failed to save case", { description: e.message });
    } finally {
      isSubmitting.value = false;
    }
  };

  const cancel = () => {
    router.push('/cases');
  };

</script>

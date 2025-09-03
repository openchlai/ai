<template>
  <div>
    <!-- SidePanel Component -->
    <SidePanel
      :userRole="userRole"
      :isInQueue="isInQueue"
      :isProcessingQueue="isProcessingQueue"
      :currentCall="currentCall"
      @toggle-queue="handleQueueToggle"
      @logout="handleLogout"
      @sidebar-toggle="handleSidebarToggle"
    />

    <!-- Main Content -->
    <div class="main-content">
      <div class="cases-container">
        <!-- Cleaned up header section with better structure and spacing -->
        <header class="page-header">
          <div class="header-top">
            <div class="header-left">
              <h1 class="page-title">Cases</h1>
              <router-link to="/case-creation" class="btn btn--primary btn--sm">Add New Case</router-link>
            </div>
            
          </div>
          
          <!-- Combined search and view toggle into single horizontal row -->
          <div class="search-and-controls-section">
            <div class="search-container">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Search case by title, assignee, or filter..."
                class="input"
              />
            </div>
            
            <div class="view-toggle">
              <button class="btn btn--secondary btn--sm" :class="{ active: currentView === 'table' }" @click="currentView = 'table'">Table View</button>
              <button class="btn btn--secondary btn--sm" :class="{ active: currentView === 'timeline' }" @click="currentView = 'timeline'">Timeline</button>
            </div>
          </div>

          <!-- Moved filter tabs to separate section -->
          <div class="filter-section">
            <button
              v-for="filter in filters"
              :key="filter.id"
              class="btn btn--secondary btn--sm"
              :class="{ active: activeFilter === filter.id }"
              @click="setActiveFilter(filter.id)"
            >
              {{ filter.name }}
            </button>
          </div>
        </header>

        <!-- Added conditional rendering for table view and timeline view -->
        <!-- Table View -->
        <div v-if="currentView === 'table'" class="cases-table-container">
          <div class="cases-table-wrapper card" style="padding:0;">
            <table class="cases-table">
              <thead>
                <tr>
                  <!-- Improved table headers with better labels and spacing -->
                  <th class="case-id-header">Case ID</th>
                  <th class="created-by-header">Created By</th>
                  <th class="created-on-header">Created On</th>
                  <th class="source-header">Source</th>
                  <th class="priority-header">Priority</th>
                  <th class="status-header">Status</th>
                  <th class="actions-header">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="caseItem in filteredCases"
                  :key="casesStore.cases_k?.id ? caseItem[casesStore.cases_k.id[0]] : caseItem.id"
                  :class="['table-row', {
                    selected: selectedCaseId === (casesStore.cases_k?.id ? caseItem[casesStore.cases_k.id[0]] : caseItem.id)
                  }]"
                  @click="selectCase(casesStore.cases_k?.id ? caseItem[casesStore.cases_k.id[0]] : caseItem.id)"
                >
                  <td class="case-id-cell">
                    {{ casesStore.cases_k?.id ? caseItem[casesStore.cases_k.id[0]] : caseItem.id || 'N/A' }}
                  </td>
                  <td class="created-by-cell">
                    {{ casesStore.cases_k?.created_by ? caseItem[casesStore.cases_k.created_by[0]] || 'N/A' : 'N/A' }}
                  </td>
                  <td class="created-on-cell">
                    {{ casesStore.cases_k?.dt ? new Date(
                      caseItem[casesStore.cases_k.dt[0]] < 10000000000
                        ? caseItem[casesStore.cases_k.dt[0]] * 1000
                        : caseItem[casesStore.cases_k.dt[0]] * 3600 * 1000
                    ).toLocaleDateString() : 'N/A' }}
                  </td>
                  <td class="source-cell">
                    {{ casesStore.cases_k?.source ? caseItem[casesStore.cases_k.source[0]] || 'N/A' : 'N/A' }}
                  </td>
                  <td class="priority-cell">
                    <span class="priority-badge" :class="(casesStore.cases_k?.priority ? caseItem[casesStore.cases_k.priority[0]] || 'normal' : 'normal').toLowerCase()">
                      <span
                        :class="['priority-dot', (casesStore.cases_k?.priority ? caseItem[casesStore.cases_k.priority[0]] || '' : '').toLowerCase()]"
                      />
                      {{ casesStore.cases_k?.priority ? caseItem[casesStore.cases_k.priority[0]] || 'Normal' : 'Normal' }}
                    </span>
                  </td>
                  <td class="status-cell">
                    <span class="status-badge" :class="(casesStore.cases_k?.status ? caseItem[casesStore.cases_k.status[0]] || 'open' : 'open').toLowerCase()">
                      {{ casesStore.cases_k?.status ? caseItem[casesStore.cases_k.status[0]] || 'Open' : 'Open' }}
                    </span>
                  </td>
                  <td class="actions-cell">
                    <button class="btn btn--secondary btn--sm" @click.stop="selectCase(casesStore.cases_k?.id ? caseItem[casesStore.cases_k.id[0]] : caseItem.id)">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                        <circle cx="12" cy="12" r="3"/>
                      </svg>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Timeline View (Original Card Layout) -->
        <div v-else class="cases-container-inner">
          <div class="cases-list">
            <h2 class="cases-title">Cases</h2>

            <div
              v-for="caseItem in filteredCases"
              :key="casesStore.cases_k?.id ? caseItem[casesStore.cases_k.id[0]] : caseItem.id"
              :class="[
                'case-item card',
                {
                  selected: selectedCaseId === (casesStore.cases_k?.id ? caseItem[casesStore.cases_k.id[0]] : caseItem.id),
                },
              ]"
              @click="selectCase(casesStore.cases_k?.id ? caseItem[casesStore.cases_k.id[0]] : caseItem.id)"
            >
              <div class="case-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                  <path
                    d="M12 22C12 22 20 18 20 12V5L12 2L4 5V12C4 18 12 22 12 22Z"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                  <path
                    d="M9 12L11 14L15 10"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                </svg>
              </div>
              <div class="case-details">
                <div class="case-title">
                  {{ casesStore.cases_k?.cat_1 ? caseItem[casesStore.cases_k.cat_1[0]] : "Untitled Case" }}
                </div>
                <div class="case-meta">
                  <span class="case-priority">
                    <span
                      :class="['priority-dot', (casesStore.cases_k?.priority ? caseItem[casesStore.cases_k.priority[0]] || '' : '').toLowerCase()]"
                    />
                    {{ casesStore.cases_k?.priority ? caseItem[casesStore.cases_k.priority[0]] || "Normal" : "Normal" }}
                    priority
                  </span>
                  <span class="case-date">
                    {{ casesStore.cases_k?.dt ? new Date(
                      caseItem[casesStore.cases_k.dt[0]] < 10000000000
                        ? caseItem[casesStore.cases_k.dt[0]] * 1000
                        : caseItem[casesStore.cases_k.dt[0]] * 3600 * 1000
                    ).toLocaleString() : "No Date" }}
                  </span>
                  <span class="case-assigned">
                    {{ casesStore.cases_k?.assigned_to && caseItem[casesStore.cases_k.assigned_to[0]]
                      ? `Assigned: ${caseItem[casesStore.cases_k.assigned_to[0]]}`
                      : "Unassigned" }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Case Detail Drawer (unchanged) -->
        <div class="case-detail-drawer" v-if="selectedCaseDetails">
          <div class="case-detail-drawer-header">
            <div class="case-detail-title">
              {{ casesStore.cases_k?.cat_1 ? selectedCaseDetails[casesStore.cases_k.cat_1[0]] : "Case Details" }}
            </div>
            <div class="case-detail-id">
              Case ID: {{ casesStore.cases_k?.id ? selectedCaseDetails[casesStore.cases_k.id[0]] : "" }}
            </div>
            <button class="close-details" @click="selectedCaseId = null">×</button>
          </div>
          <div class="case-detail-content">
            <div class="detail-item">
              <div class="detail-label">Case Filler</div>
              <div class="detail-value">
                {{ casesStore.cases_k?.created_by ? selectedCaseDetails[casesStore.cases_k.created_by[0]] || "N/A" : "N/A" }}
              </div>
            </div>
            <div class="detail-item">
              <div class="detail-label">Assigned To</div>
              <div class="detail-value">
                {{ casesStore.cases_k?.assigned_to ? selectedCaseDetails[casesStore.cases_k.assigned_to[0]] || "Unassigned" : "Unassigned" }}
              </div>
            </div>
            <div class="detail-item">
              <div class="detail-label">Priority</div>
              <div
                :class="['detail-value', (casesStore.cases_k?.priority ? selectedCaseDetails[casesStore.cases_k.priority[0]] || '' : '').toLowerCase()]"
              >
                {{ casesStore.cases_k?.priority ? selectedCaseDetails[casesStore.cases_k.priority[0]] || "Normal" : "Normal" }}
              </div>
            </div>
            <div class="detail-item">
              <div class="detail-label">Status</div>
              <div class="detail-value">
                {{ casesStore.cases_k?.status ? selectedCaseDetails[casesStore.cases_k.status[0]] || "Open" : "Open" }}
              </div>
            </div>
            <div class="detail-item">
              <div class="detail-label">Source</div>
              <div class="detail-value">
                {{ casesStore.cases_k?.source ? selectedCaseDetails[casesStore.cases_k.source[0]] || "N/A" : "N/A" }}
              </div>
            </div>
            <div class="detail-item">
              <div class="detail-label">Disposition</div>
              <div class="detail-value">
                {{ casesStore.cases_k?.disposition ? selectedCaseDetails[casesStore.cases_k.disposition[0]] || "N/A" : "N/A" }}
              </div>
            </div>
            <div class="detail-item">
              <div class="detail-label">Date</div>
              <div class="detail-value">
                {{ casesStore.cases_k?.dt ? new Date(
                  selectedCaseDetails[casesStore.cases_k.dt[0]] < 10000000000
                    ? selectedCaseDetails[casesStore.cases_k.dt[0]] * 1000
                    : selectedCaseDetails[casesStore.cases_k.dt[0]] * 3600 * 1000
                ).toLocaleString() : "N/A" }}
              </div>
            </div>
            <div class="detail-item">
              <div class="detail-label">Escalated To</div>
              <div class="detail-value">
                {{ casesStore.cases_k?.escalated_to ? selectedCaseDetails[casesStore.cases_k.escalated_to[0]] || "N/A" : "N/A" }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import SidePanel from "@/components/SidePanel.vue";
import { useCaseStore } from "@/stores/cases";

const casesStore = useCaseStore();
const router = useRouter();

// Reactive state
const searchQuery = ref("");
const activeFilter = ref("all");
const selectedCaseId = ref(null);
const currentTheme = ref("light");
const currentView = ref("table"); // Default to table view

// SidePanel related state
const userRole = ref("super-admin");
const isInQueue = ref(false);
const isProcessingQueue = ref(false);
const currentCall = ref(null);

// Filter options
const filters = ref([
  { id: "all", name: "All" },
  { id: "open", name: "Open", status: "open" },
  { id: "pending", name: "Pending", status: "pending" },
  { id: "assigned", name: "Assigned" },
  { id: "closed", name: "Closed", status: "closed" },
  { id: "today", name: "Today" },
  { id: "priority", name: "Priority" },
]);

// Computed properties
const filteredCases = computed(() => {
  let filtered = casesStore.cases || [];
 
  const normalizeStatus = (value) => {
    if (!value && value !== 0) return '';
    const v = String(value).toLowerCase();
    if (v === '1') return 'open';
    if (v === '2') return 'closed';
    if (v === '0') return 'pending';
    return v; // already a label like 'open', 'closed', 'pending'
  };

  const normalizePriority = (value) => {
    if (!value && value !== 0) return '';
    const v = String(value).toLowerCase();
    if (v === '3') return 'high';
    if (v === '2') return 'medium';
    if (v === '1') return 'low';
    return v; // already a label
  };

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    filtered = filtered.filter((c) => {
      // Search in case title/category
      const title = casesStore.cases_k?.cat_1 ? c[casesStore.cases_k.cat_1[0]] : '';
      // Search in assigned to
      const assignedTo = casesStore.cases_k?.assigned_to ? c[casesStore.cases_k.assigned_to[0]] : '';
      // Search in created by
      const createdBy = casesStore.cases_k?.created_by ? c[casesStore.cases_k.created_by[0]] : '';
      // Search in source
      const source = casesStore.cases_k?.source ? c[casesStore.cases_k.source[0]] : '';
      
      return (
        (title && title.toString().toLowerCase().includes(query)) ||
        (assignedTo && assignedTo.toString().toLowerCase().includes(query)) ||
        (createdBy && createdBy.toString().toLowerCase().includes(query)) ||
        (source && source.toString().toLowerCase().includes(query))
      );
    });
  }

  if (activeFilter.value !== "all") {
    const filterStatus = filters.value.find(
      (f) => f.id === activeFilter.value
    )?.status;
    if (filterStatus) {
      filtered = filtered.filter((c) => {
        const raw = casesStore.cases_k?.status ? c[casesStore.cases_k.status[0]] : '';
        const status = normalizeStatus(raw);
        return status && status === filterStatus.toLowerCase();
      });
    } else if (activeFilter.value === "assigned") {
      filtered = filtered.filter((c) => {
        const assignedTo = casesStore.cases_k?.assigned_to ? c[casesStore.cases_k.assigned_to[0]] : '';
        return assignedTo && assignedTo.trim() !== '';
      });
    } else if (activeFilter.value === "priority") {
      filtered = filtered.filter((c) => {
        const raw = casesStore.cases_k?.priority ? c[casesStore.cases_k.priority[0]] : '';
        const priority = normalizePriority(raw);
        return priority === 'high';
      });
    } else if (activeFilter.value === "today") {
      // Filter for today's cases
      const today = new Date().toDateString();
      filtered = filtered.filter((c) => {
        if (casesStore.cases_k?.dt && c[casesStore.cases_k.dt[0]]) {
          const caseDate = new Date(
            c[casesStore.cases_k.dt[0]] < 10000000000
              ? c[casesStore.cases_k.dt[0]] * 1000
              : c[casesStore.cases_k.dt[0]] * 3600 * 1000
          );
          return caseDate.toDateString() === today;
        }
        return false;
      });
    }
  }

  return filtered;
});

const selectedCaseDetails = computed(() => {
  if (!casesStore.cases_k?.id) return null;
  return casesStore.cases.find(
    (caseItem) => caseItem[casesStore.cases_k.id[0]] === selectedCaseId.value
  );
});

const setCurrentView = (view) => {
  currentView.value = view;
};

// SidePanel event handlers
const handleQueueToggle = () => {
  isInQueue.value = !isInQueue.value;
  console.log("Queue toggled:", isInQueue.value);
};

const handleLogout = () => {
  router.push("/");
};

const handleSidebarToggle = (collapsed) => {
  console.log("Sidebar toggled:", collapsed);
};

// Theme methods (unchanged)
const applyTheme = (theme) => {
  const root = document.documentElement;

  if (theme === "light") {
    root.style.setProperty("--background-color", "#f5f5f5");
    root.style.setProperty("--sidebar-bg", "#ffffff");
    root.style.setProperty("--content-bg", "#ffffff");
    root.style.setProperty("--text-color", "#333");
    root.style.setProperty("--text-secondary", "#666");
    root.style.setProperty("--border-color", "#ddd");
    root.style.setProperty("--card-bg", "#ffffff");
    root.style.setProperty("--header-bg", "#ffffff");
    root.style.setProperty("--input-bg", "#f0f0f0");
    root.setAttribute("data-theme", "light");
  } else {
    root.style.setProperty("--background-color", "#0a0a0a");
    root.style.setProperty("--sidebar-bg", "#111");
    root.style.setProperty("--content-bg", "#222");
    root.style.setProperty("--text-color", "#fff");
    root.style.setProperty("--text-secondary", "#aaa");
    root.style.setProperty("--border-color", "#333");
    root.style.setProperty("--card-bg", "#222");
    root.style.setProperty("--header-bg", "#333");
    root.style.setProperty("--input-bg", "#1a1a1a");
    root.setAttribute("data-theme", "dark");
  }

  // Common variables
      root.style.setProperty("--accent-color", "#8B4513");
    root.style.setProperty("--accent-hover", "#A0522D");
  root.style.setProperty("--danger-color", "#ff3b30");
  root.style.setProperty("--success-color", "#4CAF50");
  root.style.setProperty("--pending-color", "#FFA500");
  root.style.setProperty("--unassigned-color", "#808080");
  root.style.setProperty("--highlight-color", "#ff3b30");
  root.style.setProperty("--high-priority", "#ff3b30");
  root.style.setProperty("--medium-priority", "#FFA500");
  root.style.setProperty("--low-priority", "#4CAF50");
};

const toggleTheme = () => {
  const newTheme = currentTheme.value === "dark" ? "light" : "dark";
  localStorage.setItem("theme", newTheme);
  currentTheme.value = newTheme;
  applyTheme(newTheme);
};

const setActiveFilter = (filterId) => {
  activeFilter.value = filterId;
};

const selectCase = (caseId) => {
  selectedCaseId.value = caseId;
};

const handleSearch = () => {
  // Filtering handled by 'filteredCases'
};

// Lifecycle hooks
onMounted(() => {
  casesStore.listCases();
  console.log("Cases loaded:", casesStore.raw);
  const savedTheme = localStorage.getItem("theme") || "light";
  currentTheme.value = savedTheme;
  applyTheme(savedTheme);
});
</script>

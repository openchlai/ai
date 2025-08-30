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
              <router-link to="/case-creation" class="add-new-case-btn">
                Add New Case
              </router-link>
            </div>
            <button class="theme-toggle" @click="toggleTheme">
              <svg
                v-show="currentTheme === 'dark'"
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
              </svg>
              <svg
                v-show="currentTheme === 'light'"
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <circle cx="12" cy="12" r="5"/>
                <path d="m21 21-4.35-4.35"/>
              </svg>
              <span class="theme-toggle-text">Dark Mode</span>
            </button>
          </div>
          
          <!-- Combined search and view toggle into single horizontal row -->
          <div class="search-and-controls-section">
            <div class="search-container">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Search case by title, assignee, or filter..."
                class="search-input"
              />
            </div>
            
            <div class="view-toggle">
              <button
                :class="['view-btn', { active: currentView === 'table' }]"
                @click="currentView = 'table'"
              >
                Table View
              </button>
              <button
                :class="['view-btn', { active: currentView === 'timeline' }]"
                @click="currentView = 'timeline'"
              >
                Timeline
              </button>
            </div>
          </div>

          <!-- Moved filter tabs to separate section -->
          <div class="filter-section">
            <button
              v-for="filter in filters"
              :key="filter.id"
              :class="['filter-tab', { active: activeFilter === filter.id }]"
              @click="setActiveFilter(filter.id)"
            >
              {{ filter.name }}
            </button>
          </div>
        </header>

        <!-- Added conditional rendering for table view and timeline view -->
        <!-- Table View -->
        <div v-if="currentView === 'table'" class="cases-table-container">
          <div class="cases-table-wrapper">
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
                    <button class="action-btn view-btn" @click.stop="selectCase(casesStore.cases_k?.id ? caseItem[casesStore.cases_k.id[0]] : caseItem.id)">
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
                'case-item glass-card fine-border',
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
const currentTheme = ref(localStorage.getItem("theme") || "dark");
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
        const status = casesStore.cases_k?.status ? c[casesStore.cases_k.status[0]] : '';
        return status && status.toLowerCase() === filterStatus.toLowerCase();
      });
    } else if (activeFilter.value === "assigned") {
      filtered = filtered.filter((c) => {
        const assignedTo = casesStore.cases_k?.assigned_to ? c[casesStore.cases_k.assigned_to[0]] : '';
        return assignedTo && assignedTo.trim() !== '';
      });
    } else if (activeFilter.value === "priority") {
      filtered = filtered.filter((c) => {
        const priority = casesStore.cases_k?.priority ? c[casesStore.cases_k.priority[0]] : '';
        return priority && priority.toLowerCase() === "high";
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
    root.style.setProperty("--header-bg", "#f0f0f0");
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
  root.style.setProperty("--accent-color", "#964B00");
  root.style.setProperty("--accent-hover", "#b25900");
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
  const savedTheme = localStorage.getItem("theme");
  if (savedTheme) {
    currentTheme.value = savedTheme;
  }
  applyTheme(currentTheme.value);
});
</script>

<style scoped>
/* Global styles - not scoped */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: "Inter", sans-serif;
}

body {
  background-color: var(--background-color);
  color: var(--text-color);
  display: flex;
  min-height: 100vh;
  transition: background-color 0.3s, color 0.3s;
  overflow: hidden;
}

.main-content {
  flex: 1;
  margin-left: var(--sidebar-width, 250px);
  height: 100vh;
  background-color: var(--content-bg);
  transition: margin-left 0.3s ease, background-color 0.3s;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.cases-container {
  flex: 1;
  padding: 24px;
  height: auto;
  overflow: visible;
  display: flex;
  flex-direction: column;
}

.cases-container::-webkit-scrollbar {
  width: 8px;
}

.cases-container::-webkit-scrollbar-track {
  background: transparent;
}

.cases-container::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: 4px;
}

.cases-container::-webkit-scrollbar-thumb:hover {
  background-color: rgba(255, 255, 255, 0.5);
}

/* Improved header styles with better organization */
.page-header {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
  flex-shrink: 0;
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-color);
  margin: 0;
}

.add-new-case-btn {
  background: var(--accent-color);
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 10px 20px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.add-new-case-btn:hover {
  background: var(--accent-hover);
  transform: translateY(-1px);
}

.theme-toggle {
  background-color: var(--content-bg);
  color: var(--text-color);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
  font-weight: 500;
}

.theme-toggle:hover {
  background-color: var(--border-color);
  transform: translateY(-1px);
}

.theme-toggle svg {
  width: 18px;
  height: 18px;
}

.theme-toggle-text {
  font-size: 13px;
}

.search-and-controls-section {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 12px;
}

.search-container {
  position: relative;
  flex: 1;
  max-width: 400px;
}

.search-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--content-bg);
  color: var(--text-color);
  font-size: 14px;
  transition: all 0.2s ease;
}

.search-input:focus {
  outline: none;
  border-color: var(--accent-color);
  box-shadow: 0 0 0 3px rgba(150, 75, 0, 0.1);
}

.search-input::placeholder {
  color: #999;
}

.view-toggle {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.view-btn {
  /* Updated to match Calls page rounded button styling */
  padding: 10px 20px;
  border: none;
  background: var(--content-bg);
  color: var(--text-color);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.view-btn:hover {
  background: rgba(150, 75, 0, 0.05);
}

.view-btn.active {
  background: var(--accent-color);
  color: white;
  border-color: var(--accent-color);
}

.filter-section {
  margin-bottom: 16px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.filter-tab {
  background-color: var(--input-bg);
  color: var(--text-color);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 8px 16px;
  font-size: 13px;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s ease;
  font-weight: 500;
}

.filter-tab.active {
  background-color: var(--accent-color);
  color: white;
  border-color: var(--accent-color);
}

.filter-tab:hover:not(.active) {
  background-color: rgba(150, 75, 0, 0.1);
  border-color: var(--accent-color);
}

.cases-container-inner {
  display: flex;
  gap: 20px;
  flex: 1;
  height: auto;
  overflow: visible;
}

.cases-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  /* Make cards stretch to container width */
  width: 100%;
  max-width: 900px;
  min-width: 400px;
  /* Center cards in container */
  align-self: center;
}

.cases-list::-webkit-scrollbar {
  width: 8px;
}

.cases-list::-webkit-scrollbar-track {
  background: transparent;
}

.cases-list::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: 4px;
}

.cases-list::-webkit-scrollbar-thumb:hover {
  background-color: rgba(255, 255, 255, 0.5);
}

.cases-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 15px;
}

.case-item {
  display: flex;
  align-items: flex-start;
  cursor: pointer;
  padding: 18px 32px;
  border-radius: 18px;
  transition: all 0.3s ease;
  position: relative;
  background: var(--content-bg);
  color: var(--text-color);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  border: 1.5px solid transparent;
  font-size: 15px;
  margin-bottom: 0;
  width: 100%;
  max-width: 900px;
  min-width: 400px;
  /* Center cards in container */
  align-self: center;
}

.case-item.selected {
  background-color: rgba(255, 59, 48, 0.1);
  border: 1.5px solid var(--highlight-color);
}

.case-item:hover {
  background-color: rgba(150, 75, 0, 0.04);
  transform: translateX(5px);
}

.case-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--accent-color);
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: 15px;
  color: #fff;
  flex-shrink: 0;
}
.case-icon svg {
  width: 18px;
  height: 18px;
  stroke: #fff;
}
.case-details {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
  justify-content: center;
  width: 100%;
  overflow: hidden;
}

.case-title {
  font-size: 1.08rem;
  font-weight: 700;
  margin-bottom: 2px;
  width: 100%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
 
.case-id {
  font-size: 0.95rem;
  color: #bbb;
  margin-bottom: 8px;
}
.case-priority {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 700;
  margin-bottom: 2px;
}
.case-assigned {
  display: flex;
  align-items: center;
  font-weight: 400;
  color: #888;
  margin-top: 2px;
}
.case-assigned span {
  word-wrap: break-word;
  overflow-wrap: break-word;
  font-size: 12px;
  width: 100%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.priority-dot {
  width: 11px;
  height: 11px;
  border-radius: 50%;
  flex-shrink: 0;
  border: 1.5px solid #fff;
  box-shadow: 0 0 0 2px rgba(0,0,0,0.08);
}
.priority-dot.high {
  background-color: var(--high-priority);
}
.priority-dot.medium {
  background-color: var(--medium-priority);
}
.priority-dot.low {
  background-color: var(--low-priority);
}
.case-detail-drawer {
  position: fixed;
  top: 0;
  right: 0;
  height: 100vh;
  width: 400px;
  max-width: 100vw;
  background: rgba(34, 34, 34, 0.98);
  box-shadow: -4px 0 24px rgba(0, 0, 0, 0.18);
  border-top-left-radius: 18px;
  border-bottom-left-radius: 18px;
  z-index: 1002;
  display: flex;
  flex-direction: column;
  padding: 0 0 0 0;
  animation: slideInDrawer 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
@keyframes slideInDrawer {
  from {
    right: -400px;
    opacity: 0;
  }
  to {
    right: 0;
    opacity: 1;
  }
}
.case-detail-drawer-header {
  padding: 32px 24px 0 24px;
  position: relative;
  min-height: 56px;
}
.case-detail-drawer .case-detail-title {
  font-size: 1.35rem;
  font-weight: 800;
  margin-bottom: 2px;
  color: #fff;
  letter-spacing: 0.01em;
}
.case-detail-drawer .case-detail-id {
  font-size: 0.95rem;
  color: #bbb;
  margin-bottom: 8px;
}
.case-detail-drawer .close-details {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 40px;
  height: 40px;
  background: rgba(0, 0, 0, 0.06);
  border: none;
  color: #222;
  font-size: 2.1rem;
  font-weight: bold;
  border-radius: 50%;
  cursor: pointer;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s, color 0.2s;
}
[data-theme="dark"] .case-detail-drawer .close-details {
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
}
.case-detail-drawer .case-detail-content {
  padding: 18px 24px 24px 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  scrollbar-width: thin;
  scrollbar-color: var(--accent-color) var(--content-bg);
  overflow-y: auto;
  max-height: calc(100vh - 100px);
}
.case-detail-drawer .detail-item {
  background: rgba(255, 255, 255, 0.07);
  border-radius: 14px;
  padding: 16px 18px;
  margin-bottom: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.07);
  border: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.case-detail-drawer .detail-label {
  font-size: 1.01rem;
  color: #bbb;
  font-weight: 700;
  margin-bottom: 2px;
  letter-spacing: 0.01em;
}
.case-detail-drawer .detail-value {
  font-size: 1.13rem;
  color: #fff;
  font-weight: 600;
  letter-spacing: 0.01em;
}
.case-detail-drawer .detail-value.high {
  color: #ff3b30;
  font-weight: 700;
}
.case-detail-drawer .detail-value.medium {
  color: #ffa500;
  font-weight: 700;
}
.case-detail-drawer .detail-value.low {
  color: #4caf50;
  font-weight: 700;
}
.case-detail-drawer .detail-value.abusive {
  color: #ff3b30;
}

/* Added comprehensive table styles */
.cases-table-container {
  flex: 1;
  overflow: hidden;
  background: var(--content-bg);
  border-radius: 12px;
  border: 1px solid var(--border-color);
}

.cases-table-wrapper {
  overflow-x: auto;
  overflow-y: auto;
  max-height: calc(100vh - 300px);
}

.cases-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.cases-table thead {
  background: var(--header-bg);
  position: sticky;
  top: 0;
  z-index: 10;
}

.cases-table th {
  padding: 14px 12px;
  text-align: left;
  font-weight: 600;
  color: var(--text-color);
  border-bottom: 2px solid var(--border-color);
  white-space: nowrap;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.cases-table td {
  padding: 12px;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-color);
  vertical-align: middle;
}

.table-row {
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.table-row:hover {
  background: rgba(150, 75, 0, 0.05);
}

.table-row.selected {
  background: rgba(150, 75, 0, 0.1);
  border-left: 3px solid var(--accent-color);
}

.case-id-cell {
  font-weight: 600;
  color: var(--accent-color);
  min-width: 120px;
}

.created-by-cell,
.source-cell {
  min-width: 120px;
}

.created-on-cell {
  min-width: 100px;
  font-size: 13px;
}

.priority-cell,
.status-cell {
  min-width: 100px;
}

.priority-badge,
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  text-transform: capitalize;
}

.priority-badge.high {
  background: rgba(255, 59, 48, 0.1);
  color: var(--high-priority);
}

.priority-badge.medium {
  background: rgba(255, 165, 0, 0.1);
  color: var(--medium-priority);
}

.priority-badge.low,
.priority-badge.normal {
  background: rgba(76, 175, 80, 0.1);
  color: var(--low-priority);
}

.status-badge.open {
  background: rgba(76, 175, 80, 0.1);
  color: var(--success-color);
}

.status-badge.pending {
  background: rgba(255, 165, 0, 0.1);
  color: var(--pending-color);
}

.status-badge.closed {
  background: rgba(128, 128, 128, 0.1);
  color: var(--unassigned-color);
}

.actions-cell {
  width: 60px;
  text-align: center;
}

.action-btn {
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 6px;
  cursor: pointer;
  color: var(--text-color);
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.action-btn:hover {
  background: var(--accent-color);
  color: white;
  border-color: var(--accent-color);
}

/* Responsive styles */
@media (max-width: 1024px) {
  .cases-container-inner {
    flex-direction: column;
  }
  .case-detail-drawer {
    width: 100vw;
    border-radius: 0;
    left: 0;
    right: 0;
  }
  
  .controls-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .cases-table {
    font-size: 13px;
  }
  
  .cases-table th,
  .cases-table td {
    padding: 10px 8px;
  }
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 0;
  }

  .cases-container {
    padding: 16px;
  }

  .header-top {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .header-left {
    width: 100%;
    justify-content: space-between;
  }

  .page-title {
    font-size: 24px;
  }

  .search-container {
    max-width: 100%;
  }
  
  .view-toggle {
    width: 100%;
    gap: 4px;
  }
  
  .view-btn {
    flex: 1;
    text-align: center;
  }
  
  .filter-section {
    width: 100%;
    justify-content: flex-start;
  }
  
  .cases-table-wrapper {
    max-height: calc(100vh - 350px);
  }
  
  .cases-table {
    font-size: 12px;
  }
  
  .cases-table th,
  .cases-table td {
    padding: 8px 6px;
  }

  .case-meta {
    font-size: 11px;
  }

  .cases-main-content {
    padding-top: 4px;
  }
}

.cases-main-content {
  padding-top: 4px;
}

:root {
  --drawer-bg-dark: rgba(34, 34, 34, 0.98);
  --drawer-bg-light: #fff;
  --drawer-card-bg-dark: rgba(255, 255, 255, 0.07);
  --drawer-card-bg-light: #f5f5f5;
  --drawer-card-border-dark: 1px solid rgba(255, 255, 255, 0.08);
  --drawer-card-border-light: 1px solid #e0e0e0;
  --drawer-title-dark: #fff;
  --drawer-title-light: #222;
  --drawer-label-dark: #bbb;
  --drawer-label-light: #555;
  --drawer-value-dark: #fff;
  --drawer-value-light: #222;
  --drawer-value-high: #ff3b30;
  --drawer-value-medium: #ffa500;
  --drawer-value-low: #4caf50;
  --priority-dot-border-dark: #fff;
  --priority-dot-border-light: #fff;
  --priority-dot-shadow: 0 0 0 2px rgba(0, 0, 0, 0.08);
}

[data-theme="light"] .case-detail-drawer {
  background: var(--drawer-bg-light);
}
[data-theme="dark"] .case-detail-drawer {
  background: var(--drawer-bg-dark);
}
[data-theme="light"] .case-detail-drawer .detail-item {
  background: var(--drawer-card-bg-light);
  border: var(--drawer-card-border-light);
}
[data-theme="dark"] .case-detail-drawer .detail-item {
  background: var(--drawer-card-bg-dark);
  border: var(--drawer-card-border-dark);
}
[data-theme="light"] .case-detail-drawer .case-detail-title {
  color: var(--drawer-title-light);
}
[data-theme="dark"] .case-detail-drawer .case-detail-title {
  color: var(--drawer-title-dark);
}
[data-theme="light"] .case-detail-drawer .detail-label {
  color: var(--drawer-label-light);
}
[data-theme="dark"] .case-detail-drawer .detail-label {
  color: var(--drawer-label-dark);
}
[data-theme="light"] .case-detail-drawer .detail-value {
  color: var(--drawer-value-light);
}
[data-theme="dark"] .case-detail-drawer .detail-value {
  color: var(--drawer-value-dark);
}
[data-theme="light"] .case-detail-drawer .detail-value.high {
  color: var(--drawer-value-high);
}
[data-theme="light"] .case-detail-drawer .detail-value.medium {
  color: var(--drawer-value-medium);
}
[data-theme="light"] .case-detail-drawer .detail-value.low {
  color: var(--drawer-value-low);
}
[data-theme="dark"] .case-detail-drawer .detail-value.high {
  color: var(--drawer-value-high);
}
[data-theme="dark"] .case-detail-drawer .detail-value.medium {
  color: var(--drawer-value-medium);
}
[data-theme="dark"] .case-detail-drawer .detail-value.low {
  color: var(--drawer-value-low);
}
[data-theme="light"] .priority-dot {
  border: 1.5px solid var(--priority-dot-border-light);
  box-shadow: var(--priority-dot-shadow);
}
[data-theme="dark"] .priority-dot {
  border: 1.5px solid var(--priority-dot-border-dark);
  box-shadow: var(--priority-dot-shadow);
}
[data-theme="light"] .case-item.selected {
  border: 2px solid var(--accent-color);
  background: #fff8f0;
}
[data-theme="dark"] .case-item.selected {
  border: 2px solid var(--accent-color);
  background: rgba(150, 75, 0, 0.08);
}
body.high-contrast .case-detail-drawer,
body.high-contrast .case-detail-drawer .detail-item,
body.high-contrast .case-detail-drawer .case-detail-title,
body.high-contrast .case-detail-drawer .detail-label,
body.high-contrast .case-detail-drawer .detail-value,
body.high-contrast .case-item.selected,
body.high-contrast .priority-dot {
  background: #000 !important;
  color: #fff !important;
  border-color: #fff !important;
}
body.high-contrast .priority-dot.high {
  background: #ff3b30 !important;
}
body.high-contrast .priority-dot.medium {
  background: #ffa500 !important;
}
body.high-contrast .priority-dot.low {
  background: #4caf50 !important;
}
@media (max-width: 900px) {
  .case-item {
    padding: 20px 18px 22px 18px;
    gap: 12px;
  }
  .case-icon {
    width: 36px;
    height: 36px;
    min-width: 36px;
    min-height: 36px;
    max-width: 36px;
    max-height: 36px;
    margin-right: 12px;
  }
  .case-title {
    font-size: 1rem;
  }
  .case-meta {
    font-size: 12px;
  }
}
@media (max-width: 600px) {
  .case-item {
    padding: 12px 6px 14px 6px;
    gap: 8px;
    border-radius: 12px;
  }
  .case-icon {
    width: 28px;
    height: 28px;
    min-width: 28px;
    min-height: 28px;
    max-width: 28px;
    max-height: 28px;
    margin-right: 6px;
  }
  .case-title {
    font-size: 0.95rem;
  }
  .case-meta {
    font-size: 11px;
  }
}
</style>

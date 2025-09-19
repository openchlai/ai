<template>
  <!-- Step 1: Reporter Selection -->
  <div v-show="currentStep === 1" class="step-content">
    <form class="case-form" @submit.prevent="validateAndProceed(1)">
      <div class="form-section">
        <div class="section-title">Select Reporter</div>
        <p class="section-description">
          Choose an existing contact or create a new reporter for this case.
        </p>

        <div class="search-section">
          <div class="search-row">
            <div class="search-box">
              <svg
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <circle
                  cx="11"
                  cy="11"
                  r="8"
                  stroke="currentColor"
                  stroke-width="2"
                />
                <path
                  d="m21 21-4.35-4.35"
                  stroke="currentColor"
                  stroke-width="2"
                />
              </svg>
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Search by name or phone..."
                class="search-input"
              />
            </div>
            <button
              type="button"
              class="btn btn--primary new-reporter-btn"
              @click="createNewReporter"
            >
              + New Reporter
            </button>
          </div>
        </div>

        <!-- Inline results under search -->
        <div
          class="contacts-list"
          v-if="debouncedQuery && filteredContacts.length"
        >
          <div
            v-for="contact in filteredContacts"
            :key="contact[reportersStore.reporters_k.id?.[0]]"
            class="contact-item"
            :class="{
              selected:
                selectedReporter &&
                selectedReporter[reportersStore.reporters_k.id?.[0]] ===
                  contact[reportersStore.reporters_k.id?.[0]],
            }"
            @click="selectExistingReporter(contact)"
          >
            <div class="contact-avatar">
              <span>{{
                getInitials(
                  contact[reportersStore.reporters_k.fullname?.[0]] || "NA"
                )
                  .slice(0, 2)
                  .toUpperCase()
              }}</span>
            </div>
            <div class="contact-details">
              <div class="contact-main-info">
                <div class="contact-name">
                  {{
                    contact[reportersStore.reporters_k.fullname?.[0]] ||
                    "Unnamed Reporter"
                  }}
                </div>
                <div class="contact-phone">
                  {{ contact[reportersStore.reporters_k.phone?.[0]] }}
                </div>
              </div>
              <div class="contact-meta-info">
                <div class="contact-tags">
                  <span class="contact-tag">{{
                    contact[reportersStore.reporters_k.age?.[0]]
                  }}y</span>
                  <span class="contact-tag">{{
                    contact[reportersStore.reporters_k.sex?.[0]]
                  }}</span>
                  <span class="contact-tag location"
                    >📍
                    {{ contact[reportersStore.reporters_k.location?.[0]] }}</span
                  >
                </div>
              </div>
            </div>
            <div class="contact-select-indicator">
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <polyline
                  points="9,18 15,12 9,6"
                  stroke="currentColor"
                  stroke-width="2"
                />
              </svg>
            </div>
          </div>
        </div>

        <div
          class="search-empty"
          v-else-if="debouncedQuery && !filteredContacts.length"
        >
          No matches found
        </div>

        <div class="action-buttons">
          <button
            v-if="selectedReporter"
            type="submit"
            class="btn btn-primary btn-large"
          >
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M5 12l5 5L20 7"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
            Continue with
            {{ selectedReporter?.[reportersStore.reporters_k.fullname[0]] }}
          </button>
        </div>
      </div>

      <div class="form-actions">
        <button type="button" class="btn btn-cancel" @click="cancelForm">
          Cancel
        </button>
        <div>
          <BaseButton variant="secondary" @click="skipStep(1)">Skip</BaseButton>
          <BaseButton type="submit" :disabled="!selectedReporter"
            >Next</BaseButton
          >
        </div>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from "vue"
import { useReporterStore } from "@/stores/reporters"
import BaseButton from "@/components/base/BaseButton.vue"

const props = defineProps({
  currentStep: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(["validate-and-proceed", "skip-step", "cancel-form"])

// ✅ Access reporters store
const reportersStore = useReporterStore()

// Fetch reporters on mount
onMounted(() => {
  if (!reportersStore.reporters.length) {
    reportersStore.listReporters()
  }
})

// State
const searchQuery = ref("")
const debouncedQuery = ref("")
const selectedReporter = ref(null)

// Debounce search input
let debounceTimeout
watch(searchQuery, (newVal) => {
  clearTimeout(debounceTimeout)
  debounceTimeout = setTimeout(() => {
    debouncedQuery.value = newVal.trim()
  }, 300)
})

// ✅ Filter contacts from reporters
const filteredContacts = computed(() => {
  if (!debouncedQuery.value) return []
  const query = debouncedQuery.value.toLowerCase()

  return reportersStore.reporters.filter((contact) => {
    const name =
      contact[reportersStore.reporters_k.fullname?.[0]]?.toLowerCase() || ""
    const phone =
      contact[reportersStore.reporters_k.phone?.[0]]?.toLowerCase() || ""
    return name.includes(query) || phone.includes(query)
  })
})


// ✅ Select reporter
const selectExistingReporter = (contact) => {
  selectedReporter.value = contact
}

// Create new reporter (placeholder)
const createNewReporter = () => {
  selectedReporter.value = {
    [reportersStore.reporters_k.fullname[0]]: "New Reporter",
    [reportersStore.reporters_k.phone[0]]: "",
    [reportersStore.reporters_k.age[0]]: "",
    [reportersStore.reporters_k.sex[0]]: "",
    [reportersStore.reporters_k.location[0]]: ""
  }
}

// Utils
const getInitials = (name) => {
  return name
    .split(" ")
    .map((n) => n[0] || "")
    .join("")
}

// Step control
const validateAndProceed = (step) => {
  if (selectedReporter.value) {
    emit("validate-and-proceed", { step, reporter: selectedReporter.value })
  }
}

const skipStep = (step) => {
  emit("skip-step", step)
}

const cancelForm = () => {
  emit("cancel-form")
}
</script>

<style scoped>
.step-content {
  min-height: 400px;
}

.case-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.search-row {
  display: flex;
  gap: 8px;
  align-items: center;
}


/* Form Actions */
.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--color-border);
}

.search-empty {
  margin-top: 8px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 10px;
  color: var(--color-muted);
}

.contact-select-indicator {
  color: var(--color-muted);
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 8px 10px;
  background: var(--color-surface);
  color: var(--text-color);
  width: 180px;
}
.new-reporter-btn {
  height: 36px;
}
.search-input {
  border: 0;
  outline: 0;
  width: 100%;
  background: transparent;
  font-size: 13px;
  color: var(--text-color);
}
.search-empty {
  margin-top: 8px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 10px;
  color: var(--color-muted);
}

.create-reporter-btn {
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  padding: 8px 12px;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
}
.create-reporter-btn:hover {
  transform: translateY(-1px);
}

.contacts-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 8px;
}
.contact-item {
  display: flex;
  align-items: center;
  gap: 12px;
  border: 1px solid var(--color-border);
  border-radius: 14px;
  padding: 12px;
  background: var(--color-surface);
  cursor: pointer;
  transition: background 0.15s ease, border-color 0.15s ease;
}
.contact-item:hover {
  background: var(--color-surface-muted);
}
.contact-item.selected {
  outline: 2px solid color-mix(in oklab, var(--color-primary) 28%, transparent);
}
.contact-avatar {
  width: 40px;
  height: 40px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-surface-muted);
  font-weight: 700;
}
.contact-details {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: center;
  column-gap: 12px;
  min-width: 0;
}
.contact-main-info {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}
.contact-name {
  font-weight: 700;
  font-size: 16px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.contact-phone {
  color: var(--color-muted);
  font-size: 12px;
  white-space: nowrap;
}
.contact-meta-info {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.contact-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  max-width: 420px;
}
.contact-tag {
  border: 1px solid var(--color-border);
  border-radius: 999px;
  padding: 2px 8px;
  font-size: 12px;
}
.contact-tag.location {
  background: var(--color-surface-muted);
}
</style>

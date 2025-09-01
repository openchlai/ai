<template>
    <div class="reporter-container">
        <h3>New Reporter</h3>

        <form class="case-form" @submit.prevent="validateAndProceed(1)">
            <div class="form-section">
                <div class="section-title">Select Reporter</div>
                <p class="section-description">
                    Choose an existing contact or create a new reporter for this case.
                </p>

                <div class="search-section">
                    <div class="search-row">
                        <div class="search-box">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
                                xmlns="http://www.w3.org/2000/svg">
                                <circle cx="11" cy="11" r="8" stroke="currentColor" stroke-width="2" />
                                <path d="m21 21-4.35-4.35" stroke="currentColor" stroke-width="2" />
                            </svg>
                            <input v-model="searchQuery" type="text" placeholder="Search by name or phone..."
                                class="search-input" />
                            <!-- Live suggestions -->
                            <ul class="search-suggestions" v-if="debouncedQuery && filteredContacts.length"
                                :style="{ width: suggestionWidth }">
                                <li v-for="contact in filteredContacts.slice(0, 8)"
                                    :key="contact[casesStore.cases_k.id[0]]" class="suggestion-item"
                                    @click="selectExistingReporter(contact)">
                                    <span class="suggestion-name">{{ contact[casesStore.cases_k.reporter_fullname[0]] ||
                                        'Unnamed' }}</span>
                                    <span class="suggestion-phone">{{ contact[casesStore.cases_k.reporter_phone[0]] ||
                                        '' }}</span>
                                </li>
                            </ul>
                            <div class="search-empty" v-else-if="debouncedQuery && !filteredContacts.length"
                                :style="{ width: suggestionWidth }">
                                No matches found
                            </div>
                        </div>
                        <button type="button" class="create-reporter-btn" @click="createNewReporter">
                            + New Reporter
                        </button>
                    </div>
                </div>

                <!-- Updated contacts list format -->
                <div class="contacts-list" v-if="searchQuery && filteredContacts.length">
                    <div v-for="contact in filteredContacts" :key="contact[casesStore.cases_k.id[0]]"
                        class="contact-item"
                        :class="{ selected: selectedReporter && selectedReporter[casesStore.cases_k.id[0]] === contact[casesStore.cases_k.id[0]] }"
                        @click="selectExistingReporter(contact)">
                        <div class="contact-avatar">
                            <span>{{
                                getInitials(
                                    contact[casesStore.cases_k.reporter_fullname[0]] ||
                                    "NA"
                                )
                                    .slice(0, 2)
                                .toUpperCase()
                                }}</span>
                        </div>
                        <div class="contact-details">
                            <div class="contact-main-info">
                                <div class="contact-name">
                                    {{
                                        contact[casesStore.cases_k.reporter_fullname[0]] ||
                                        "Untitled Case"
                                    }}
                                </div>
                                <div class="contact-phone">{{ contact[casesStore.cases_k.reporter_phone[0]] }}</div>
                            </div>
                            <div class="contact-meta-info">
                                <div class="contact-tags">
                                    <span class="contact-tag">{{ contact[casesStore.cases_k.reporter_age[0]] }}y</span>
                                    <span class="contact-tag">{{ contact[casesStore.cases_k.reporter_sex[0]] }}</span>
                                    <span class="contact-tag location">📍 {{
                                        contact[casesStore.cases_k.reporter_location[0]]}}</span>
                                </div>
                                <div class="contact-timestamp">{{ new Date(contact[casesStore.cases_k.dt[0]] *
                                    1000).toLocaleString('en-US') }}</div>
                            </div>
                        </div>
                        <div class="contact-select-indicator">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none"
                                xmlns="http://www.w3.org/2000/svg">
                                <polyline points="9,18 15,12 9,6" stroke="currentColor" stroke-width="2" />
                            </svg>
                        </div>
                    </div>
                </div>

                <div class="action-buttons">
                    <button v-if="selectedReporter" type="submit" class="btn btn-primary btn-large">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M5 12l5 5L20 7" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                stroke-linejoin="round" />
                        </svg>
                        Continue with {{ selectedReporter?.[casesStore.cases_k.reporter_fullname[0]] }}
                    </button>
                </div>
            </div>
            <div class="form-actions">
                <button type="button" class="btn btn-cancel" @click="cancelForm">
                    Cancel
                </button>
                <div>
                    <button type="button" class="btn btn-skip" @click="skipStep(1)">
                        Skip
                    </button>
                    <button type="submit" class="btn btn-next" :disabled="!selectedReporter">
                        Next
                    </button>
                </div>
            </div>
        </form>

        <!-- Personal Information -->

    </div>
</template>

<script setup>
    import { ref } from "vue";

    const reporter = ref({
        name: "",
        dob: "",
        ageRange: "",
        gender: "",
        location: "",
        landmark: "",
        nationality: "",
        idType: "",
        idNumber: "",
        language: "",
        isRefugee: "",
        tribe: "",
        phone: "",
        altPhone: "",
        email: "",
        isClient: false,
    });

    // Options for select fields
    const ageOptions = ["0-17", "18-24", "25-40", "41-60", "60+"];
    const genderOptions = ["Male", "Female", "Other"];
    const locationOptions = ["EASTERN", "WESTERN", "NORTHERN", "CENTRAL"];
    const nationalityOptions = ["Ugandan", "Kenyan", "Tanzanian", "Rwandese", "South Sudanese", "Congolese", "Other"];
    const idTypeOptions = ["National ID", "Passport", "Driving Permit", "Voter's ID", "Other"];
    const languageOptions = ["English", "Luganda", "Ateso", "Lugbara", "Acholi", "Other"];
    const refugeeOptions = ["Yes", "No", "Unknown"];
    const tribeOptions = ["Baganda", "Banyankole", "Bakiga", "Langi", "Acholi", "Other"];
</script>

<style scoped>

    /* ROOT CSS */
    :root {
        --background-color: #f5f7fa;
        --content-bg: #ffffff;
        --card-bg: #ffffff;
        --text-color: #222;
        --text-secondary: #666;
        --border-color: #ddd;

        --accent-color: #964b00;
        --accent-hover: #7a3c00;

        --success-color: #28a745;
        --danger-color: #dc3545;
        --pending-color: #ffc107;
        --unassigned-color: #6c757d;

        --prank-color: #e67e22;
        --counsellor-color: #17a2b8;

        --sidebar-width: 250px;

        --border-radius: 8px;
        --spacing-sm: 0.5rem;
        --spacing-md: 1rem;
        --spacing-lg: 1.5rem;
    }

    :root.dark {
        --background-color: #181a1b;
        --content-bg: #222;
        --card-bg: #2a2d2f;
        --text-color: #f5f5f5;
        --text-secondary: #aaa;
        --border-color: #444;

        --accent-color: #ff9f43;
        --accent-hover: #e67e22;
    }

    * {
        box-sizing: border-box;
        margin: 0;
        padding: 0;
    }

    .reporter-container {
        max-width: 800px;
        margin: 0 auto;
        background-color: var(--content-bg);
        border-radius: var(--border-radius);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        padding: var(--spacing-lg);
    }

    .section-title {
        color: var(--accent-color);
        margin-bottom: var(--spacing-md);
        padding-bottom: var(--spacing-sm);
        border-bottom: 2px solid var(--border-color);
        font-weight: 600;
    }

    .form-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: var(--spacing-md);
    }

    .form-group {
        margin-bottom: var(--spacing-md);
    }

    label {
        display: block;
        margin-bottom: var(--spacing-sm);
        font-weight: 500;
        color: var(--text-secondary);
        font-size: 0.9rem;
    }

    input,
    select {
        width: 100%;
        padding: 0.75rem;
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius);
        background-color: var(--card-bg);
        color: var(--text-color);
        font-size: 1rem;
        transition: border-color 0.3s, box-shadow 0.3s;
    }

    input:focus,
    select:focus {
        outline: none;
        border-color: var(--accent-color);
        box-shadow: 0 0 0 3px rgba(150, 75, 0, 0.1);
    }

    .checkbox-group {
        display: flex;
        align-items: center;
        margin-top: var(--spacing-lg);
        padding-top: var(--spacing-md);
        border-top: 1px solid var(--border-color);
    }

    .checkbox-group input[type="checkbox"] {
        width: auto;
        margin-right: var(--spacing-sm);
    }

    .form-section {
        margin-bottom: var(--spacing-lg);
    }

    h3 {
        color: var(--accent-color);
        margin-bottom: var(--spacing-lg);
        text-align: center;
        font-size: 1.5rem;
    }

    @media (max-width: 600px) {
        .form-grid {
            grid-template-columns: 1fr;
        }

        .reporter-container {
            padding: var(--spacing-md);
        }
    }
</style>

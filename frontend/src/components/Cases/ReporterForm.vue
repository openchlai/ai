<template>
    <div class="reporter-container">
        <h3>New Reporter</h3>

        <!-- Personal Information -->
        <div class="form-section">
            <h4 class="section-title">Personal Information</h4>
            <div class="form-grid">
                <div class="form-group">
                    <label for="name">Name</label>
                    <input id="name" type="text" placeholder="Enter Contact's Names" v-model="reporter.name" />
                </div>

                <div class="form-group">
                    <label for="dob">Date of Birth</label>
                    <input id="dob" type="date" v-model="reporter.dob" />
                </div>

                <div class="form-group">
                    <label for="ageRange">Age Group</label>
                    <select id="ageRange" v-model="reporter.ageRange">
                        <option value="">Select Age Group</option>
                        <option v-for="option in ageOptions" :key="option" :value="option">{{ option }}</option>
                    </select>
                </div>

                <div class="form-group">
                    <label for="gender">Sex</label>
                    <select id="gender" v-model="reporter.gender">
                        <option value="">Select Gender</option>
                        <option v-for="option in genderOptions" :key="option" :value="option">{{ option }}</option>
                    </select>
                </div>
            </div>
        </div>

        <!-- Location Information -->
        <div class="form-section">
            <h4 class="section-title">Location Information</h4>
            <div class="form-grid">
                <div class="form-group">
                    <label for="location">Location</label>
                    <select id="location" v-model="reporter.location">
                        <option value="">Select Location</option>
                        <option v-for="option in locationOptions" :key="option" :value="option">{{ option }}</option>
                    </select>
                </div>

                <div class="form-group">
                    <label for="landmark">Nearest Landmark</label>
                    <input id="landmark" type="text" placeholder="Enter Nearest Landmark" v-model="reporter.landmark" />
                </div>

                <div class="form-group">
                    <label for="nationality">Nationality</label>
                    <select id="nationality" v-model="reporter.nationality">
                        <option value="">Select Nationality</option>
                        <option v-for="option in nationalityOptions" :key="option" :value="option">{{ option }}</option>
                    </select>
                </div>

                <div class="form-group">
                    <label for="tribe">Tribe</label>
                    <select id="tribe" v-model="reporter.tribe">
                        <option value="">Select Tribe</option>
                        <option v-for="option in tribeOptions" :key="option" :value="option">{{ option }}</option>
                    </select>
                </div>
            </div>
        </div>

        <!-- Identification -->
        <div class="form-section">
            <h4 class="section-title">Identification</h4>
            <div class="form-grid">
                <div class="form-group">
                    <label for="idType">ID Type</label>
                    <select id="idType" v-model="reporter.idType">
                        <option value="">Select ID Type</option>
                        <option v-for="option in idTypeOptions" :key="option" :value="option">{{ option }}</option>
                    </select>
                </div>

                <div class="form-group">
                    <label for="idNumber">ID Number</label>
                    <input id="idNumber" type="text" placeholder="Enter Reporter's ID Number"
                        v-model="reporter.idNumber" />
                </div>

                <div class="form-group">
                    <label for="language">Language</label>
                    <select id="language" v-model="reporter.language">
                        <option value="">Select Language</option>
                        <option v-for="option in languageOptions" :key="option" :value="option">{{ option }}</option>
                    </select>
                </div>

                <div class="form-group">
                    <label for="isRefugee">Is a Refugee?</label>
                    <select id="isRefugee" v-model="reporter.isRefugee">
                        <option value="">Select Option</option>
                        <option v-for="option in refugeeOptions" :key="option" :value="option">{{ option }}</option>
                    </select>
                </div>
            </div>
        </div>

        <!-- Contact Information -->
        <div class="form-section">
            <h4 class="section-title">Contact Information</h4>
            <div class="form-grid">
                <div class="form-group">
                    <label for="phone">Phone Number</label>
                    <input id="phone" type="tel" placeholder="Enter Reporter's Phone Number" v-model="reporter.phone" />
                </div>

                <div class="form-group">
                    <label for="altPhone">Alternative Phone</label>
                    <input id="altPhone" type="tel" placeholder="Enter Alternate Phone Number"
                        v-model="reporter.altPhone" />
                </div>

                <div class="form-group">
                    <label for="email">Email</label>
                    <input id="email" type="email" placeholder="Enter Reporter's Email Address"
                        v-model="reporter.email" />
                </div>
            </div>
        </div>

        <!-- Checkbox -->
        <div class="checkbox-group">
            <input id="isClient" type="checkbox" v-model="reporter.isClient" />
            <label for="isClient">Reporter is also a Client</label>
        </div>

        <!-- Debug JSON -->
        <div
            style="margin-top: 20px; padding: 10px; background-color: var(--card-bg); border-radius: var(--border-radius);">
            <h4 style="color: var(--accent-color); margin-bottom: 10px;">Current Data:</h4>
            <pre style="font-size: 12px; overflow: auto;">{{ JSON.stringify(reporter, null, 2) }}</pre>
        </div>
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

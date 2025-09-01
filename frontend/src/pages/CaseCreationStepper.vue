<script setup>
    import { ref } from "vue"

    // Import the step components
    import ReporterForm from "@/components/Cases/ReporterForm.vue"
    import ClientsForm from "@/components/Cases/ClientsForm.vue"
    import PerpetratorsForm from "@/components/Cases/PerpetratorsForm.vue"
    import FilesUpload from "@/components/Cases/FilesUpload.vue"
    import ServicesForm from "@/components/Cases/ServicesForm.vue"
    import CaseDetails from "@/components/Cases/CaseDetails.vue"

    const currentStep = ref(1)

    const stepDescriptions = [
        "Reporter Information",
        "Clients",
        "Perpetrators",
        "Attach Related Files",
        "Services Offered",
        "Case Details"
    ]

    const totalSteps = stepDescriptions.length

    function nextStep() {
        if (currentStep.value < totalSteps) {
            currentStep.value++
        }
    }

    function prevStep() {
        if (currentStep.value > 1) {
            currentStep.value--
        }
    }

    function createCase() {
        // Later: submit Pinia state
        alert("Case created!")
    }
</script>

<template>
    <div class="case-creation-page">
        <router-link class="back-button" to="/cases">
            ← Back to Cases
        </router-link>

        <div class="case-container">
            <div class="main-form-container">
                <div class="case-header">
                    <div>
                        <h1>Create New Case</h1>
                        <p>{{ stepDescriptions[currentStep - 1] }}</p>
                    </div>
                </div>

                <!-- Stepper navigation -->
                <div class="stepper">
                    <div v-for="(desc, index) in stepDescriptions" :key="index"
                        :class="['step', { active: currentStep === index + 1, completed: currentStep > index + 1 }]">
                        <span class="circle">{{ index + 1 }}</span>
                        <span class="label">{{ desc }}</span>
                    </div>
                </div>

                <!-- Step content -->
                <div class="step-content">
                    <ReporterForm v-if="currentStep === 1" />
                    <ClientsForm v-else-if="currentStep === 2" />
                    <PerpetratorsForm v-else-if="currentStep === 3" />
                    <FilesUpload v-else-if="currentStep === 4" />
                    <ServicesForm v-else-if="currentStep === 5" />
                    <CaseDetails v-else-if="currentStep === 6" />
                </div>

                <!-- Navigation buttons -->
                <div class="actions">
                    <button class="btn secondary" @click="prevStep" :disabled="currentStep === 1">
                        Back
                    </button>
                    <button class="btn primary" @click="nextStep" v-if="currentStep < totalSteps">
                        Next
                    </button>
                    <button class="btn success" v-if="currentStep === totalSteps" @click="createCase">
                        Create Case
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
    .case-creation-page {
        max-width: 900px;
        margin: 0 auto;
        padding: 1.5rem;
        font-family: Arial, sans-serif;
    }

    .back-button {
        display: inline-block;
        margin-bottom: 1rem;
        text-decoration: none;
        color: #0077cc;
        font-weight: bold;
    }

    .case-container {
        background: #fff;
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.08);
    }

    .case-header {
        margin-bottom: 2rem;
    }

    .case-header h1 {
        margin: 0;
        font-size: 1.8rem;
    }

    .case-header p {
        margin: 0.3rem 0 0;
        color: #666;
    }

    /* Stepper */
    .stepper {
        display: flex;
        justify-content: space-between;
        margin-bottom: 2rem;
        position: relative;
    }

    .step {
        text-align: center;
        flex: 1;
        position: relative;
    }

    .step .circle {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: #ddd;
        color: #333;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }

    .step .label {
        display: block;
        font-size: 0.85rem;
        color: #666;
    }

    .step.active .circle {
        background: #0077cc;
        color: #fff;
    }

    .step.completed .circle {
        background: #28a745;
        color: #fff;
    }

    .step-content {
        min-height: 200px;
        margin-bottom: 2rem;
    }

    /* Buttons */
    .actions {
        display: flex;
        justify-content: flex-end;
        gap: 1rem;
    }

    .btn {
        padding: 0.6rem 1.2rem;
        border-radius: 6px;
        border: none;
        cursor: pointer;
        font-size: 0.95rem;
    }

    .btn.primary {
        background: #0077cc;
        color: #fff;
    }

    .btn.secondary {
        background: #e0e0e0;
        color: #333;
    }

    .btn.success {
        background: #28a745;
        color: #fff;
    }

    .btn:disabled {
        background: #ccc;
        cursor: not-allowed;
    }
</style>

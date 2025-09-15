<script setup>
    import { ref } from "vue"

    const filters = ref({
        case: {
            search: "",
            caseId: "",
            createdOn: "",
            createdBy: "",
            source: "",
            category: "",
            gbvRelated: "",
            priority: "",
            status: "",
            escalatedTo: "",
            caseAssessment: "",
            justiceStatus: "",
        },
        reporter: {
            name: "",
            phone: "",
            age: "",
            sex: "",
            location: "",
            idType: "",
            nationality: "",
            language: "",
            tribe: "",
            relationshipToClient: "",
        },
        // keep same structure for client, perpetrator, services, referrals...
    })

    const emit = defineEmits(["apply-filters", "reset-filters"])

    const applyFilters = () => {
        emit("apply-filters", filters.value)
    }

    const resetFilters = () => {
        Object.keys(filters.value).forEach(group => {
            Object.keys(filters.value[group]).forEach(key => {
                filters.value[group][key] = ""
            })
        })
        emit("reset-filters")
    }
</script>

<template>
    <div class="filter-container">
        <!-- Accordion -->
        <details open>
            <summary class="accordion-header">Case</summary>
            <div class="accordion-content">
                <input v-model="filters.case.search" placeholder="Search Case" class="input" />
                <input v-model="filters.case.caseId" placeholder="Case ID" class="input" />
                <input type="date" v-model="filters.case.createdOn" class="input" />
                <input v-model="filters.case.createdBy" placeholder="Created By" class="input" />
                <input v-model="filters.case.source" placeholder="Source" class="input" />
                <input v-model="filters.case.category" placeholder="Category" class="input" />
                <select v-model="filters.case.gbvRelated" class="input">
                    <option value="">GBV Related?</option>
                    <option value="yes">Yes</option>
                    <option value="no">No</option>
                </select>
                <select v-model="filters.case.priority" class="input">
                    <option value="">Priority</option>
                    <option>Low</option>
                    <option>Medium</option>
                    <option>High</option>
                </select>
                <input v-model="filters.case.status" placeholder="Status" class="input" />
                <input v-model="filters.case.escalatedTo" placeholder="Escalated To" class="input" />
                <input v-model="filters.case.caseAssessment" placeholder="Case Assessment" class="input" />
                <input v-model="filters.case.justiceStatus" placeholder="Justice System Status" class="input" />
            </div>
        </details>

        <!-- Reporter -->
        <details>
            <summary class="accordion-header">Reporter</summary>
            <div class="accordion-content">
                <input v-model="filters.reporter.name" placeholder="Name" class="input" />
                <input v-model="filters.reporter.phone" placeholder="Phone" class="input" />
                <input v-model="filters.reporter.age" placeholder="Age" class="input" />
                <select v-model="filters.reporter.sex" class="input">
                    <option value="">Sex</option>
                    <option>Male</option>
                    <option>Female</option>
                </select>
                <input v-model="filters.reporter.location" placeholder="Location" class="input" />
                <input v-model="filters.reporter.idType" placeholder="ID Type" class="input" />
                <input v-model="filters.reporter.nationality" placeholder="Nationality" class="input" />
                <input v-model="filters.reporter.language" placeholder="Language" class="input" />
                <input v-model="filters.reporter.tribe" placeholder="Tribe" class="input" />
                <input v-model="filters.reporter.relationshipToClient" placeholder="Relationship to Client"
                    class="input" />
            </div>
        </details>

        <!-- Buttons -->
        <div class="actions">
            <button @click="resetFilters" class="btn btn-reset">Reset</button>
            <button @click="applyFilters" class="btn btn-apply">Apply</button>
        </div>
    </div>
</template>

<style scoped>

    /* Container */
    .filter-container {
        width: 100%;
        padding: 16px;
        background: #ffffff;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        font-family: Arial, sans-serif;
        font-size: 14px;
    }

    /* Accordion */
    details {
        margin-bottom: 12px;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
    }

    summary {
        padding: 10px 12px;
        font-weight: 600;
        cursor: pointer;
        background: #f7f7f7;
        border-radius: 8px 8px 0 0;
        outline: none;
        user-select: none;
    }

    .accordion-content {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
        gap: 10px;
        padding: 12px;
        background: #fafafa;
        border-top: 1px solid #e0e0e0;
        border-radius: 0 0 8px 8px;
    }

    /* Inputs */
    .input {
        padding: 8px 10px;
        border: 1px solid #ccc;
        border-radius: 6px;
        font-size: 13px;
        width: 100%;
        box-sizing: border-box;
        transition: border-color 0.2s;
    }

    .input:focus {
        outline: none;
        border-color: #3b82f6;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
    }

    /* Actions */
    .actions {
        display: flex;
        justify-content: flex-end;
        gap: 10px;
        margin-top: 16px;
    }

    .btn {
        padding: 8px 14px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 500;
        cursor: pointer;
        border: none;
        transition: background 0.2s, transform 0.1s;
    }

    .btn:active {
        transform: scale(0.97);
    }

    .btn-reset {
        background: #f0f0f0;
        color: #333;
    }

    .btn-reset:hover {
        background: #e0e0e0;
    }

    .btn-apply {
        background: #2563eb;
        color: #fff;
    }

    .btn-apply:hover {
        background: #1e4fd7;
    }
</style>

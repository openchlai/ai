<script setup>
    import { ref } from "vue"
    import BaseSelect from "@/components/base/BaseSelect.vue"
    import BaseRadio from "@/components/base/BaseRadio.vue"
    import BaseTextarea from "@/components/base/BaseTextarea.vue"
    import BaseInput from "@/components/base/BaseInput.vue"

    const caseDetails = ref({
        department: "116",
        category: "",
        gbv: "No",
        narrative: "",
        plan: "",
        priority: "Medium",
        status: "Open",
        escalatedTo: ""
    })
</script>

<template>
    <div>
        <h3>Case Details</h3>

        <BaseSelect label="Department" v-model="caseDetails.department" placeholder="Select department">
            <option value="116">116</option>
            <option value="Labor">Labor</option>
        </BaseSelect>

        <BaseSelect label="Case Category" v-model="caseDetails.category" placeholder="Select category">
            <option value="Violence">Violence</option>
            <option value="Neglect">Neglect</option>
            <option value="Exploitation">Exploitation</option>
        </BaseSelect>

        <div class="form-group">
            <div class="form-label">GBV Related?</div>
            <div style="display:flex; gap:12px;">
                <BaseRadio name="gbv" value="Yes" v-model="caseDetails.gbv">Yes</BaseRadio>
                <BaseRadio name="gbv" value="No" v-model="caseDetails.gbv">No</BaseRadio>
            </div>
        </div>

        <BaseTextarea label="Case Narrative" v-model="caseDetails.narrative" :rows="4" />

        <BaseTextarea label="Case Plan" v-model="caseDetails.plan" :rows="3" />

        <BaseSelect label="Priority" v-model="caseDetails.priority" placeholder="Select priority">
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
        </BaseSelect>

        <BaseSelect label="Status" v-model="caseDetails.status" placeholder="Select status">
            <option value="Open">Open</option>
            <option value="Closed">Closed</option>
            <option value="Pending">Pending</option>
        </BaseSelect>

        <BaseInput label="Escalated To" v-model="caseDetails.escalatedTo" placeholder="Enter Department/Staff" />
    </div>
</template>

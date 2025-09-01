<script setup>
    import { ref } from "vue"

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

        <label>Department</label>
        <select v-model="caseDetails.department">
            <option>116</option>
            <option>Labor</option>
        </select>

        <label>Case Category</label>
        <select v-model="caseDetails.category">
            <option>Violence</option>
            <option>Neglect</option>
            <option>Exploitation</option>
        </select>

        <label>GBV Related?</label>
        <input type="radio" value="Yes" v-model="caseDetails.gbv" /> Yes
        <input type="radio" value="No" v-model="caseDetails.gbv" /> No

        <label>Case Narrative</label>
        <textarea v-model="caseDetails.narrative"></textarea>

        <label>Case Plan</label>
        <textarea v-model="caseDetails.plan"></textarea>

        <label>Priority</label>
        <select v-model="caseDetails.priority">
            <option>High</option>
            <option>Medium</option>
            <option>Low</option>
        </select>

        <label>Status</label>
        <select v-model="caseDetails.status">
            <option>Open</option>
            <option>Closed</option>
            <option>Pending</option>
        </select>

        <label>Escalated To</label>
        <input v-model="caseDetails.escalatedTo" placeholder="Enter Department/Staff" />
    </div>
</template>

<script setup>
    import { ref } from "vue"

    const services = ref([])
</script>

<template>
    <div>
        <h3>Services Offered</h3>
        <label><input type="checkbox" value="Counseling" v-model="services" /> Counseling</label>
        <label><input type="checkbox" value="Medical" v-model="services" /> Medical</label>
        <label><input type="checkbox" value="Shelter" v-model="services" /> Shelter</label>
    </div>
</template>

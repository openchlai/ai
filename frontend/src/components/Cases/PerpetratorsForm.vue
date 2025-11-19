<script setup>
    import { ref } from "vue"

    const perpetrators = ref([{ name: "Perp 1" }])

    function addPerpetrator() {
        perpetrators.value.push({ name: "" })
    }
</script>

<template>
    <div>
        <h3>Perpetrators</h3>
        <div v-for="(perp, i) in perpetrators" :key="i">
            <input v-model="perp.name" placeholder="Perpetrator Name" />
        </div>
        <button @click="addPerpetrator">+ Add a Perpetrator</button>
    </div>
</template>

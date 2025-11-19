<script setup>
    import { ref } from "vue"

    const clients = ref([{ name: "Client 1", age: 22 }])

    function addClient() {
        clients.value.push({ name: "", age: "" })
    }
</script>

<template>
    <div>
        <h3>Clients</h3>
        <div v-for="(client, i) in clients" :key="i">
            
            <input v-model="client.name" placeholder="Client Name" />
            <input v-model="client.age" placeholder="Age" type="number" />
        </div>
        <button @click="addClient">+ Add a Client</button>
    </div>
</template>

<script setup>
    import { ref } from "vue"

    const files = ref([])
    function handleFiles(event) {
        files.value = [...event.target.files]
    }
</script>

<template>
    <div>
        <h3>Attach Files</h3>
        <input type="file" multiple @change="handleFiles" />
        <ul>
            <li v-for="(file, i) in files" :key="i">{{ file.name }}</li>
        </ul>
    </div>
</template>

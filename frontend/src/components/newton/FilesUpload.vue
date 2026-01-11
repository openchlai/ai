<script setup>
    import { ref } from "vue"

    const files = ref([])
    function handleFiles(event) {
        files.value = [...event.target.files]
    }
</script>

<template>
    <div class="modal">
        <div class="modal__header">Attach Files</div>
        <div class="modal__body">
            <div class="popup-section">
                <div class="section-title">Upload documents</div>
                <div class="section-subtitle">Supported types: PDF, DOCX, PNG, JPG</div>
                <input class="input" type="file" multiple @change="handleFiles" />
                <ul class="file-list">
                    <li v-for="(file, i) in files" :key="i">{{ file.name }}</li>
                </ul>
            </div>
        </div>
        <div class="modal__footer">
            <button class="btn btn--secondary btn--sm">Cancel</button>
            <button class="btn btn--primary btn--sm" :disabled="files.length === 0">Save</button>
        </div>
    </div>
</template>

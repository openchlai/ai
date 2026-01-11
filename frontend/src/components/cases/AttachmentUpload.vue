<template>
  <div class="attachment-upload">
    <!-- Label and Description -->
    <label class="form-label">{{ label }}</label>
    <p v-if="description" class="field-description">{{ description }}</p>
    
    <div class="attachments-container">
      <!-- File Upload Area -->
      <div 
        class="file-upload-area"
        :class="{ 'drag-over': isDragOver, 'disabled': filesStore.loading }"
        @dragover.prevent="handleDragOver"
        @dragleave.prevent="handleDragLeave"
        @drop.prevent="handleDrop"
        @click="triggerFileInput"
      >
        <input
          ref="fileInput"
          type="file"
          multiple
          :accept="acceptedTypes"
          @change="handleFileSelect"
          class="hidden-file-input"
          :disabled="filesStore.loading"
        />
        
        <div class="upload-content">
          <div class="upload-icon">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="7,10 12,15 17,10"/>
              <line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
          </div>
          <div class="upload-text">
            <p class="primary-text">
              {{ filesStore.loading ? 'Uploading...' : 'Drop files here or click to browse' }}
            </p>
            <p class="secondary-text">{{ acceptedTypesText }} (Max {{ maxSizeMB }}MB each)</p>
          </div>
        </div>
      </div>

      <!-- Uploaded Files List -->
      <div v-if="attachments && attachments.length > 0" class="uploaded-files">
        <h4 class="files-header">Uploaded Files ({{ attachments.length }})</h4>
        <div class="files-list">
          <div
            v-for="(file, index) in attachments"
            :key="index"
            class="file-item"
          >
            <div class="file-info">
              <div class="file-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <polyline points="14,2 14,8 20,8"/>
                </svg>
              </div>
              <div class="file-details">
                <div class="file-name">{{ file.name }}</div>
                <div class="file-meta">
                  {{ formatFileSize(file.size) }} • {{ getFileType(file.name) }}
                  {{ file.id ? ` • ID: ${file.id}` : '' }}
                </div>
              </div>
            </div>
            
            <div class="file-actions">
              <button
                type="button"
                class="remove-file-btn"
                @click="removeFile(index)"
                title="Remove file"
                :disabled="filesStore.loading"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="18" y1="6" x2="6" y2="18"/>
                  <line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Upload Progress -->
      <div v-if="uploadProgress > 0 && uploadProgress < 100" class="upload-progress">
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
        </div>
        <span class="progress-text">Uploading attachments... {{ Math.round(uploadProgress) }}%</span>
      </div>

      <!-- Upload Status -->
      <div v-if="filesStore.loading" class="upload-status">
        <div class="loading-indicator">
          <svg width="20" height="20" viewBox="0 0 24 24" class="spinner">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none" opacity="0.3"/>
            <path d="M12,2 A10,10 0 0,1 22,12" stroke="currentColor" stroke-width="2" fill="none"/>
          </svg>
          <span>Processing uploads...</span>
        </div>
      </div>

      <!-- Error Display -->
      <div v-if="filesStore.error" class="upload-error">
        <div class="error-message">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="15" y1="9" x2="9" y2="15"/>
            <line x1="9" y1="9" x2="15" y2="15"/>
          </svg>
          <span>{{ filesStore.error }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useFilesStore } from '@/stores/files'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  label: {
    type: String,
    default: 'Attachments'
  },
  description: {
    type: String,
    default: 'Upload relevant documents, images, or files.'
  },
  maxSizeMB: {
    type: Number,
    default: 10
  },
  acceptedTypes: {
    type: String,
    default: '.pdf,.doc,.docx,.jpg,.jpeg,.png,.gif,.txt,.xls,.xlsx'
  },
  acceptedMimeTypes: {
    type: Array,
    default: () => [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'image/jpeg',
      'image/jpg',
      'image/png',
      'image/gif',
      'text/plain',
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ]
  }
})

const emit = defineEmits(['update:modelValue', 'upload-complete', 'upload-error'])

// Store and refs
const filesStore = useFilesStore()
const fileInput = ref(null)
const isDragOver = ref(false)
const uploadProgress = ref(0)

// Computed properties
const attachments = computed(() => props.modelValue)

const acceptedTypesText = computed(() => {
  return 'Supported: ' + props.acceptedTypes.replace(/\./g, '').toUpperCase()
})

const maxSizeBytes = computed(() => props.maxSizeMB * 1024 * 1024)

// File upload methods
const triggerFileInput = () => {
  if (!filesStore.loading) {
    fileInput.value?.click()
  }
}

const handleDragOver = (e) => {
  e.preventDefault()
  if (!filesStore.loading) {
    isDragOver.value = true
  }
}

const handleDragLeave = (e) => {
  e.preventDefault()
  isDragOver.value = false
}

const handleDrop = (e) => {
  e.preventDefault()
  isDragOver.value = false
  
  if (!filesStore.loading) {
    const files = Array.from(e.dataTransfer.files)
    processFiles(files)
  }
}

const handleFileSelect = (e) => {
  if (!filesStore.loading) {
    const files = Array.from(e.target.files)
    processFiles(files)
  }
}

const validateFile = (file) => {
  const errors = []
  
  // Check file size
  if (file.size > maxSizeBytes.value) {
    errors.push(`File "${file.name}" is too large. Maximum size is ${props.maxSizeMB}MB.`)
  }
  
  // Check file type
  const isValidMimeType = props.acceptedMimeTypes.includes(file.type)
  const isValidExtension = isValidFileExtension(file.name)
  
  if (!isValidMimeType && !isValidExtension) {
    errors.push(`File "${file.name}" is not a supported format.`)
  }
  
  return errors
}

const isValidFileExtension = (filename) => {
  const validExtensions = props.acceptedTypes.split(',').map(ext => ext.trim().toLowerCase())
  const extension = filename.toLowerCase().substring(filename.lastIndexOf('.'))
  return validExtensions.includes(extension)
}

const processFiles = async (files) => {
  // Validate all files first
  const allErrors = []
  const validFiles = []
  
  files.forEach(file => {
    const errors = validateFile(file)
    if (errors.length > 0) {
      allErrors.push(...errors)
    } else {
      validFiles.push(file)
    }
  })
  
  // Show validation errors
  if (allErrors.length > 0) {
    alert('File validation errors:\n\n' + allErrors.join('\n'))
  }
  
  // Process valid files
  if (validFiles.length > 0) {
    await uploadAttachments(validFiles)
  }
}

const uploadAttachments = async (files) => {
  uploadProgress.value = 0
  let uploadedCount = 0
  const totalFiles = files.length
  const uploadedAttachments = []
  let hasErrors = false

  for (const file of files) {
    try {
      console.log(`Uploading file: ${file.name}`)
      
      // Use the files store to upload and get attachment ID
      const result = await filesStore.uploadFileAndGetAttachmentId(file)
      
      if (result && result.id) {
        // Create attachment object
        const attachmentData = {
          id: result.id,
          attachment_id: result.id,
          name: file.name,
          size: file.size,
          type: file.type,
          file: file,
          uploadedAt: new Date().toISOString(),
          attachmentResponse: result.attachmentResponse
        }
        
        uploadedAttachments.push(attachmentData)
        console.log(`File uploaded successfully: ${file.name} (ID: ${result.id})`)
      } else {
        throw new Error('No attachment ID returned from server')
      }
      
    } catch (error) {
      console.error(`Failed to upload file: ${file.name}`, error)
      hasErrors = true
      emit('upload-error', { file, error })
      // Show individual file error but continue with others
      alert(`Failed to upload "${file.name}": ${error.message}`)
    }
    
    // Update progress
    uploadedCount++
    uploadProgress.value = (uploadedCount / totalFiles) * 100
  }

  // Update the model with new attachments
  if (uploadedAttachments.length > 0) {
    const updatedAttachments = [...attachments.value, ...uploadedAttachments]
    emit('update:modelValue', updatedAttachments)
    emit('upload-complete', {
      uploaded: uploadedAttachments,
      total: updatedAttachments,
      hasErrors
    })
    
    console.log(`Successfully uploaded ${uploadedAttachments.length} out of ${totalFiles} files`)
    console.log('Attachments with IDs:', uploadedAttachments.map(a => ({ name: a.name, id: a.id })))
  }

  // Reset progress after a short delay
  setTimeout(() => {
    uploadProgress.value = 0
  }, 1000)
  
  // Clear file input
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const removeFile = (index) => {
  if (!filesStore.loading) {
    const updatedAttachments = [...attachments.value]
    const removedFile = updatedAttachments.splice(index, 1)[0]
    emit('update:modelValue', updatedAttachments)
    console.log('Removed file:', removedFile.name)
  }
}

// Utility functions
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const getFileType = (filename) => {
  const extension = filename.toLowerCase().substring(filename.lastIndexOf('.') + 1)
  const typeMap = {
    'pdf': 'PDF Document',
    'doc': 'Word Document',
    'docx': 'Word Document',
    'jpg': 'Image',
    'jpeg': 'Image',
    'png': 'Image',
    'gif': 'Image',
    'txt': 'Text File',
    'xls': 'Excel File',
    'xlsx': 'Excel File'
  }
  
  return typeMap[extension] || 'Unknown'
}

// Expose methods for parent component if needed
defineExpose({
  triggerFileInput,
  uploadAttachments,
  removeFile
})
</script>

<style scoped>
/* Form Label and Description */
.form-label {
  display: block;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--color-fg);
}

.field-description {
  font-size: 14px;
  color: var(--color-muted);
  margin-bottom: 16px;
  margin-top: -4px;
}

/* Main Container */
.attachments-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* File Upload Area */
.file-upload-area {
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-md);
  padding: 32px 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  background: var(--color-surface-muted);
}

.file-upload-area:hover:not(.disabled) {
  border-color: var(--color-primary);
  background: rgba(var(--color-primary-rgb), 0.05);
}

.file-upload-area.drag-over {
  border-color: var(--color-primary);
  background: rgba(var(--color-primary-rgb), 0.1);
  transform: scale(1.02);
}

.file-upload-area.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.hidden-file-input {
  display: none;
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.upload-icon {
  color: var(--color-muted);
  opacity: 0.7;
}

.file-upload-area:hover:not(.disabled) .upload-icon {
  color: var(--color-primary);
  opacity: 1;
}

.upload-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.primary-text {
  font-size: 16px;
  font-weight: 500;
  color: var(--color-fg);
  margin: 0;
}

.secondary-text {
  font-size: 12px;
  color: var(--color-muted);
  margin: 0;
}

/* Uploaded Files List */
.uploaded-files {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 16px;
}

.files-header {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-fg);
  margin: 0 0 12px 0;
}

.files-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.file-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  background: var(--color-surface-muted);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  transition: all 0.2s ease;
}

.file-item:hover {
  border-color: var(--color-primary);
}

.file-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.file-icon {
  color: var(--color-muted);
  flex-shrink: 0;
}

.file-details {
  min-width: 0;
}

.file-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-fg);
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-meta {
  font-size: 12px;
  color: var(--color-muted);
}

.file-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.remove-file-btn {
  background: none;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 6px;
  cursor: pointer;
  color: var(--color-muted);
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.remove-file-btn:hover:not(:disabled) {
  background: var(--color-danger);
  border-color: var(--color-danger);
  color: white;
}

.remove-file-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Upload Progress */
.upload-progress {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 16px;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: var(--color-surface-muted);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.progress-fill {
  height: 100%;
  background: var(--color-primary);
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 12px;
  color: var(--color-muted);
  text-align: center;
  display: block;
}

/* Upload Status */
.upload-status {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 16px;
}

.loading-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  font-size: 14px;
  color: var(--color-muted);
}

.spinner {
  animation: spin 1s linear infinite;
}

/* Upload Error */
.upload-error {
  background: var(--color-surface);
  border: 1px solid var(--color-danger);
  border-radius: var(--radius-md);
  padding: 16px;
}

.error-message {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  color: var(--color-danger);
}

/* Animations */
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .file-upload-area {
    padding: 24px 16px;
  }
  
  .upload-content {
    gap: 12px;
  }
  
  .primary-text {
    font-size: 14px;
  }
  
  .file-item {
    padding: 10px;
  }
  
  .file-name {
    font-size: 13px;
  }
}
</style>
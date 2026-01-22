<template>
  <div class="attachment-upload">
    <!-- Label and Description -->
    <label 
      class="block font-semibold mb-2"
      :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
    >
      {{ label }}
    </label>
    <p 
      v-if="description" 
      class="text-sm mb-4 -mt-1"
      :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
    >
      {{ description }}
    </p>
    
    <div class="flex flex-col gap-4">
      <!-- File Upload Area -->
      <div 
        :class="[
          'border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all duration-200',
          isDragOver 
            ? isDarkMode 
              ? 'border-amber-500 bg-amber-600/10 scale-[1.02]' 
              : 'border-amber-600 bg-amber-50 scale-[1.02]'
            : isDarkMode
              ? 'border-transparent bg-gray-800/50'
              : 'border-transparent bg-gray-50',
          filesStore.loading 
            ? 'opacity-60 cursor-not-allowed' 
            : isDarkMode
              ? 'hover:border-amber-500 hover:bg-amber-600/5'
              : 'hover:border-amber-600 hover:bg-amber-50'
        ]"
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
          class="hidden"
          :disabled="filesStore.loading"
        />
        
        <div class="flex flex-col items-center gap-4">
          <div 
            :class="[
              'opacity-70',
              isDarkMode ? 'text-gray-500' : 'text-gray-400',
              !filesStore.loading && 'group-hover:opacity-100',
              !filesStore.loading && (isDarkMode ? 'group-hover:text-amber-500' : 'group-hover:text-amber-700')
            ]"
          >
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="7,10 12,15 17,10"/>
              <line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
          </div>
          <div class="flex flex-col gap-1">
            <p 
              class="text-base font-medium"
              :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
            >
              {{ filesStore.loading ? 'Uploading...' : 'Drop files here or click to browse' }}
            </p>
            <p 
              class="text-xs"
              :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
            >
              {{ acceptedTypesText }} (Max {{ maxSizeMB }}MB each)
            </p>
          </div>
        </div>
      </div>

      <!-- Uploaded Files List -->
      <div 
        v-if="attachments && attachments.length > 0" 
        class="border rounded-lg p-4"
        :class="isDarkMode 
          ? 'bg-gray-800 border-transparent' 
          : 'bg-white border-transparent'"
      >
        <h4 
          class="text-sm font-semibold mb-3"
          :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
        >
          Uploaded Files ({{ attachments.length }})
        </h4>
        <div class="flex flex-col gap-2">
          <div
            v-for="(file, index) in attachments"
            :key="index"
            class="flex items-center justify-between p-3 border rounded-md transition-all duration-200"
            :class="isDarkMode 
              ? 'bg-gray-700/50 border-transparent hover:border-amber-500' 
              : 'bg-gray-50 border-transparent hover:border-amber-600'"
          >
            <div class="flex items-center gap-3 flex-1 min-w-0">
              <div 
                class="flex-shrink-0"
                :class="isDarkMode ? 'text-gray-400' : 'text-gray-500'"
              >
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <polyline points="14,2 14,8 20,8"/>
                </svg>
              </div>
              <div class="min-w-0 flex-1">
                <div 
                  class="text-sm font-medium mb-0.5 truncate whitespace-nowrap overflow-hidden"
                  :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
                >
                  {{ file.name }}
                </div>
                <div 
                  class="text-xs"
                  :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
                >
                  {{ formatFileSize(file.size) }} • {{ getFileType(file.name) }}
                  {{ file.id ? ` • ID: ${file.id}` : '' }}
                </div>
              </div>
            </div>
            
            <div class="flex gap-2 items-center">
              <button
                type="button"
                class="bg-transparent border rounded px-1.5 py-1.5 cursor-pointer transition-all duration-200 flex items-center justify-center hover:bg-red-600 hover:border-red-600 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed"
                :class="isDarkMode 
                  ? 'border-transparent text-gray-400' 
                  : 'border-transparent text-gray-500'"
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
      <div 
        v-if="uploadProgress > 0 && uploadProgress < 100" 
        class="border rounded-lg p-4"
        :class="isDarkMode 
          ? 'bg-gray-800 border-transparent' 
          : 'bg-white border-transparent'"
      >
        <div 
          class="w-full h-2 rounded overflow-hidden mb-2"
          :class="isDarkMode ? 'bg-gray-700' : 'bg-gray-200'"
        >
          <div 
            class="h-full transition-all duration-300"
            :class="isDarkMode ? 'bg-amber-600' : 'bg-amber-700'"
            :style="{ width: uploadProgress + '%' }"
          ></div>
        </div>
        <span 
          class="text-xs text-center block"
          :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
        >
          Uploading attachments... {{ Math.round(uploadProgress) }}%
        </span>
      </div>

      <!-- Upload Status -->
      <div 
        v-if="filesStore.loading" 
        class="border rounded-lg p-4"
        :class="isDarkMode 
          ? 'bg-gray-800 border-transparent' 
          : 'bg-white border-transparent'"
      >
        <div 
          class="flex items-center justify-center gap-3 text-sm"
          :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" class="animate-spin">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none" opacity="0.3"/>
            <path d="M12,2 A10,10 0 0,1 22,12" stroke="currentColor" stroke-width="2" fill="none"/>
          </svg>
          <span>Processing uploads...</span>
        </div>
      </div>

      <!-- Error Display -->
      <div 
        v-if="filesStore.error" 
        class="border rounded-lg p-4"
        :class="isDarkMode 
          ? 'bg-red-600/20 border-red-600/50' 
          : 'bg-red-50 border-red-300'"
      >
        <div 
          class="flex items-center gap-3 text-sm"
          :class="isDarkMode ? 'text-red-400' : 'text-red-700'"
        >
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
import { ref, computed, inject } from 'vue'
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

// Inject theme
const isDarkMode = inject('isDarkMode')

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
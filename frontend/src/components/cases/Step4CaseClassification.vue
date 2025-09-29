<template>
  <!-- Step 4: Case Classification -->
  <div class="step-content">
    <form class="case-form" @submit.prevent="handleFormSubmit">
      <div class="form-section">
        <div class="section-title">Case Classification & Assignment</div>
        <p class="section-description">
          Classify the case and set priority levels for proper handling.
        </p>

        <div class="form-row">
          <!-- Department -->
          <div class="form-group">
            <label>Department*</label>
            <div class="radio-group">
              <label class="radio-option">
                <input
                  v-model="localForm.department"
                  type="radio"
                  value="116"
                  required
                  @change="handleDepartmentChange"
                />
                <span class="radio-indicator"></span>
                <span class="radio-label">116</span>
              </label>
              <label class="radio-option">
                <input
                  v-model="localForm.department"
                  type="radio"
                  value="labor"
                  required
                  @change="handleDepartmentChange"
                />
                <span class="radio-indicator"></span>
                <span class="radio-label">Labor</span>
              </label>
            </div>
            
            <!-- Conditional Field: Labor Department - Client Passport -->
            <div v-if="showPassportField" class="conditional-field">
              <label for="client-passport">Client's Passport Number</label>
              <input
                id="client-passport"
                v-model="localForm.clientPassportNumber"
                type="text"
                class="form-control"
                placeholder="Enter client's passport number"
                @input="updateForm"
              />
            </div>
          </div>

          <!-- Category -->
          <div class="form-group">
            <BaseSelect
              id="case-category"
              label="case category"
              v-model="localForm.categories"
              placeholder="Select case category"
              :category-id="362557"
              @change="updateForm"
            />
          </div>
        </div>

        <!-- Priority + Status -->
        <div class="form-row">
          <div class="form-group">
            <BaseSelect
              id="priority"
              label="priority"
              v-model="localForm.priority"
              placeholder="Select priority"
              :category-id="236683"
              required
              @change="updateForm"
            />
          </div>
          <div class="form-group">
            <BaseSelect
              id="status"
              label="status"
              v-model="localForm.status"
              placeholder="Select status"
              :category-id="236696"
              required
              @change="updateForm"
            />
          </div>
        </div>

        <!-- Updated Escalated To with numeric values -->
        <div class="form-group">
          <label for="escalated-to">Escalated To</label>
          <select v-model="localForm.escalatedTo" id="escalated-to" class="form-control" @change="updateForm">
            <option value="0">None</option>
            <option value="1">Supervisor</option>
            <option value="2">Manager</option>
            <option value="3">Director</option>
            <option value="4">External Agency</option>
            <option value="5">Law Enforcement</option>
          </select>
        </div>

        <div class="form-row">
          <div class="form-group">
            <BaseSelect
              id="State of the Case in the Justice System"
              label="State of the Case in the Justice System"
              v-model="localForm.justiceSystemState"
              placeholder="Select an option"
              :category-id="236687"
              required
              @change="updateForm"
            />
          </div>
          <div class="form-group">
            <BaseSelect
              id="General Case Assessment"
              label="General Case Assessment"
              v-model="localForm.generalAssessment"
              placeholder="Select an option"
              :category-id="236694"
              required
              @change="updateForm"
            />
          </div>
        </div>

        <!-- Services Offered with Conditional Fields -->
        <div class="form-group">
          <BaseOptions
            id="services-offered"
            label="Services Offered"
            v-model="localForm.servicesOffered"
            placeholder="Select services..."
            :category-id="113"
            @selection-change="handleServicesChange"
          />

          <!-- Conditional Field: Referrals -->
          <div v-if="showReferralsField" class="conditional-field">
            <BaseOptions
              id="referrals-type"
              label="Referral Types"
              v-model="localForm.referralsType"
              placeholder="Select referral types..."
              :category-id="114"
              @selection-change="updateForm"
            />
          </div>

          <!-- Conditional Field: Police Report -->
          <div v-if="showPoliceField" class="conditional-field">
            <label for="police-details">Police Report Details</label>
            <textarea
              id="police-details"
              v-model="localForm.policeDetails"
              class="form-control"
              placeholder="Enter police report details, case number, station, etc."
              rows="3"
              @input="updateForm"
            ></textarea>
          </div>

          <!-- Conditional Field: Others -->
          <div v-if="showOthersField" class="conditional-field">
            <label for="other-services">Other Services Details</label>
            <textarea
              id="other-services"
              v-model="localForm.otherServicesDetails"
              class="form-control"
              placeholder="Please specify the other services provided"
              rows="3"
              @input="updateForm"
            ></textarea>
          </div>
        </div>

        <div class="form-group">
          <BaseSelect
            id="know about 116"
            label="How did you know about 116?"
            v-model="localForm.referralSource"
            placeholder="Select an option"
            :category-id="236700"
            required
            @change="updateForm"
          />
        </div>

        <!-- Attachments Section -->
        <div class="form-group">
          <label class="form-label">Case Attachments</label>
          <p class="field-description">Upload relevant documents, images, or files related to this case.</p>
          
          <div class="attachments-container">
            <!-- File Upload Area -->
            <div 
              class="file-upload-area"
              :class="{ 'drag-over': isDragOver }"
              @dragover.prevent="handleDragOver"
              @dragleave.prevent="handleDragLeave"
              @drop.prevent="handleDrop"
              @click="triggerFileInput"
            >
              <input
                ref="fileInput"
                type="file"
                multiple
                accept=".pdf,.doc,.docx,.jpg,.jpeg,.png,.gif,.txt,.xls,.xlsx"
                @change="handleFileSelect"
                class="hidden-file-input"
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
                  <p class="primary-text">Drop files here or click to browse</p>
                  <p class="secondary-text">Supported: PDF, DOC, DOCX, JPG, PNG, GIF, TXT, XLS, XLSX (Max 10MB each)</p>
                </div>
              </div>
            </div>

            <!-- Uploaded Files List -->
            <div v-if="localForm.attachments && localForm.attachments.length > 0" class="uploaded-files">
              <h4 class="files-header">Uploaded Files ({{ localForm.attachments.length }})</h4>
              <div class="files-list">
                <div
                  v-for="(file, index) in localForm.attachments"
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
                      </div>
                    </div>
                  </div>
                  
                  <div class="file-actions">
                    <button
                      type="button"
                      class="remove-file-btn"
                      @click="removeFile(index)"
                      title="Remove file"
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

            <!-- Upload Progress (if needed) -->
            <div v-if="uploadProgress > 0 && uploadProgress < 100" class="upload-progress">
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
              </div>
              <span class="progress-text">Uploading... {{ uploadProgress }}%</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="form-actions">
        <BaseButton type="button" variant="secondary" @click="goToStep(3)">Back</BaseButton>
        <div>
          <BaseButton type="button" variant="secondary" @click="handleSkipStep">Skip</BaseButton>
          <BaseButton type="submit">Next</BaseButton>
        </div>
      </div>
    </form>
  </div>
</template>

<script setup>
import { reactive, watch, computed, ref } from "vue"
import BaseSelect from "@/components/base/BaseSelect.vue"
import BaseButton from "@/components/base/BaseButton.vue"
import BaseOptions from "@/components/base/BaseOptions.vue"

const props = defineProps({
  currentStep: { type: Number, required: true },
  formData: { type: Object, required: true },
  clientSearchResults: { type: Array, default: () => [] },
  hasSearched: { type: Boolean, default: false },
})

// Match parent component event listeners
const emit = defineEmits([
  "form-update",
  "search-client-by-passport",
  "select-client",
  "create-new-client",
  "save-and-proceed",
  "step-change",
  "skip-step",
])

// Local copy with conditional fields initialized and new service fields
const localForm = reactive({ 
  ...props.formData,
  // Initialize conditional fields
  clientPassportNumber: props.formData.clientPassportNumber || '',
  referralsType: props.formData.referralsType || [],
  policeDetails: props.formData.policeDetails || '',
  otherServicesDetails: props.formData.otherServicesDetails || '',
  attachments: props.formData.attachments || [],
  // Add service text storage
  servicesOfferedText: props.formData.servicesOfferedText || []
})

// Store selected services options for conditional logic
const selectedServicesOptions = ref([])

// File upload state
const fileInput = ref(null)
const isDragOver = ref(false)
const uploadProgress = ref(0)

// Computed properties for conditional field visibility
const showPassportField = computed(() => {
  return localForm.department === 'labor'
})

const showReferralsField = computed(() => {
  return selectedServicesOptions.value.some(option => 
    option.text?.toLowerCase().includes('referral')
  )
})

const showPoliceField = computed(() => {
  return selectedServicesOptions.value.some(option => 
    option.text?.toLowerCase().includes('police') || 
    option.text?.toLowerCase().includes('report to police')
  )
})

const showOthersField = computed(() => {
  return selectedServicesOptions.value.some(option => 
    option.text?.toLowerCase().includes('other')
  )
})

// Handle department change with conditional field management
const handleDepartmentChange = () => {
  console.log('Department changed:', localForm.department)
  
  // Clear passport field if not labor department
  if (localForm.department !== 'labor') {
    localForm.clientPassportNumber = ''
  }
  
  // Update parent
  updateForm()
}

// UPDATED: Handle services selection change with proper text storage
const handleServicesChange = (selectionData) => {
  console.log('Services selection changed:', selectionData)
  
  // Store both IDs and text values
  localForm.servicesOffered = selectionData.values || []
  localForm.servicesOfferedText = selectionData.options?.map(opt => opt.text) || []
  selectedServicesOptions.value = selectionData.options || []
  
  // Clear conditional fields if their trigger options are no longer selected
  if (!showReferralsField.value) {
    localForm.referralsType = []
  }
  if (!showPoliceField.value) {
    localForm.policeDetails = ''
  }
  if (!showOthersField.value) {
    localForm.otherServicesDetails = ''
  }
  
  // Update parent with both service IDs and text
  updateForm()
}

// File upload methods
const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleDragOver = (e) => {
  e.preventDefault()
  isDragOver.value = true
}

const handleDragLeave = (e) => {
  e.preventDefault()
  isDragOver.value = false
}

const handleDrop = (e) => {
  e.preventDefault()
  isDragOver.value = false
  
  const files = Array.from(e.dataTransfer.files)
  processFiles(files)
}

const handleFileSelect = (e) => {
  const files = Array.from(e.target.files)
  processFiles(files)
}

const processFiles = (files) => {
  const maxSize = 10 * 1024 * 1024 // 10MB
  const allowedTypes = [
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
  
  const validFiles = files.filter(file => {
    if (file.size > maxSize) {
      alert(`File "${file.name}" is too large. Maximum size is 10MB.`)
      return false
    }
    
    if (!allowedTypes.includes(file.type) && !isValidFileExtension(file.name)) {
      alert(`File "${file.name}" is not a supported format.`)
      return false
    }
    
    return true
  })
  
  if (validFiles.length > 0) {
    // Simulate upload progress (replace with actual upload logic)
    simulateUpload(validFiles)
  }
}

const isValidFileExtension = (filename) => {
  const validExtensions = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.gif', '.txt', '.xls', '.xlsx']
  const extension = filename.toLowerCase().substring(filename.lastIndexOf('.'))
  return validExtensions.includes(extension)
}

const simulateUpload = (files) => {
  uploadProgress.value = 0
  
  // Simulate upload progress
  const interval = setInterval(() => {
    uploadProgress.value += 10
    
    if (uploadProgress.value >= 100) {
      clearInterval(interval)
      
      // Add files to attachments
      files.forEach(file => {
        localForm.attachments.push({
          name: file.name,
          size: file.size,
          type: file.type,
          file: file, // Store the actual file object
          uploadedAt: new Date().toISOString()
        })
      })
      
      uploadProgress.value = 0
      updateForm()
      
      // Clear file input
      if (fileInput.value) {
        fileInput.value.value = ''
      }
    }
  }, 200)
}

const removeFile = (index) => {
  localForm.attachments.splice(index, 1)
  updateForm()
}

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

// Watch for changes from parent
watch(() => props.formData, (newData) => {
  Object.assign(localForm, newData);
}, { deep: true });

// UPDATED: Update parent when local form changes with complete data
const updateForm = () => {
  console.log('Step4: Form data updated');
  
  // Create payload with all fields including service text
  const updatePayload = {
    ...localForm,
    servicesOfferedSelection: {
      values: localForm.servicesOffered,
      options: selectedServicesOptions.value
    }
  };
  
  emit("form-update", updatePayload);
};

// Sync changes back up (keep existing watch for backward compatibility)
watch(localForm, (newVal) => {
  // Include service selection data
  const payload = {
    ...newVal,
    servicesOfferedSelection: {
      values: localForm.servicesOffered,
      options: selectedServicesOptions.value
    }
  }
  emit("form-update", payload)
}, { deep: true })

// Navigation functions
const goToStep = (step) => {
  console.log('Step4: Going to step', step);
  // Update parent with current data before navigating
  updateForm();
  emit("step-change", step);
};

const handleSkipStep = () => {
  console.log('Step4: Skipping step');
  emit("skip-step", { step: 4, data: localForm });
};

// Form validation
const validateForm = () => {
  const errors = [];
  
  // Check required fields
  if (!localForm.department) {
    errors.push('Department selection is required');
  }
  
  if (!localForm.priority) {
    errors.push('Priority is required');
  }
  
  if (!localForm.status) {
    errors.push('Status is required');
  }
  
  // Show validation errors if any
  if (errors.length > 0) {
    alert('Please fix the following errors:\n\n' + errors.join('\n'));
    console.log('Step4 validation errors:', errors);
    return false;
  }
  
  console.log('Step4: Form validation passed');
  return true;
};

// UPDATED: Handle form submission with complete data
const handleFormSubmit = () => {
  console.log('Step4: Form submitted - Next button clicked');
  
  // Basic validation
  if (!validateForm()) {
    return;
  }
  
  // Prepare complete data payload
  const completeData = {
    ...localForm,
    servicesOfferedSelection: {
      values: localForm.servicesOffered,
      options: selectedServicesOptions.value
    }
  };
  
  // Save and proceed to next step
  console.log('Step4: Emitting save-and-proceed with data:', completeData);
  emit("save-and-proceed", { step: 4, data: completeData });
};
</script>
<style>
.step-content {
  min-height: 400px;
}

/* Forms */
.case-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--color-fg);
}

.form-control {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 14px;
  background: var(--color-surface);
  color: var(--color-fg);
  transition: all 0.2s ease;
}

.form-control:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(var(--color-primary-rgb), 0.1);
}

.radio-group {
  display: flex;
  gap: 16px;
  margin-top: 8px;
}

.radio-option {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
}

.radio-option input[type="radio"] {
  margin: 0;
  cursor: pointer;
}

.radio-indicator {
  /* Add custom radio styling if needed */
}

.radio-label {
  cursor: pointer;
  font-weight: normal;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}
@media (min-width: 780px) {
  .form-row {
    grid-template-columns: 1fr 1fr;
  }
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: space-between;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--color-border);
}

.form-actions > div {
  display: flex;
  gap: 12px;
}

/* Conditional Fields Styling */
.conditional-field {
  margin-top: 16px;
  padding: 16px;
  background: var(--color-surface-muted);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  animation: fadeIn 0.3s ease-in-out;
}

.conditional-field label {
  display: block;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--color-fg);
}

.conditional-field textarea {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 14px;
  background: var(--color-surface);
  color: var(--color-fg);
  transition: all 0.2s ease;
  resize: vertical;
}

.conditional-field textarea:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(var(--color-primary-rgb), 0.1);
}

@keyframes fadeIn {
  from { 
    opacity: 0; 
    transform: translateY(-10px); 
  }
  to { 
    opacity: 1; 
    transform: translateY(0); 
  }
}

/* Attachments Section Styling */
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

.attachments-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.file-upload-area {
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-md);
  padding: 32px 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  background: var(--color-surface-muted);
}

.file-upload-area:hover {
  border-color: var(--color-primary);
  background: rgba(var(--color-primary-rgb), 0.05);
}

.file-upload-area.drag-over {
  border-color: var(--color-primary);
  background: rgba(var(--color-primary-rgb), 0.1);
  transform: scale(1.02);
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

.file-upload-area:hover .upload-icon {
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

.remove-file-btn:hover {
  background: var(--color-danger);
  border-color: var(--color-danger);
  color: white;
}

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
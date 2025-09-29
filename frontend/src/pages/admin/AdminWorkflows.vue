<template>
  <div class="main-scroll-content">
    <!-- Workflows Header -->
    <div class="workflows-header glass-card fine-border">
      <div class="section-title">Workflow Management</div>
      <button class="create-workflow-btn" @click="showCreateWorkflowModal = true">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
        Create Workflow
      </button>
    </div>

    <!-- Workflows List -->
    <div class="workflows-list">
      <div
        v-for="workflow in workflows"
        :key="workflow.id"
        class="workflow-card glass-card fine-border"
      >
        <div class="workflow-header">
          <div class="workflow-info">
            <div class="workflow-name">{{ workflow.name }}</div>
            <div class="workflow-description">{{ workflow.description }}</div>
          </div>
          <div class="workflow-status">
            <button
              class="toggle-btn"
              :class="{ active: workflow.status === 'Active' }"
              @click="toggleWorkflow(workflow.id)"
            >
              {{ workflow.status }}
            </button>
          </div>
        </div>

        <div class="workflow-steps">
          <div
            v-for="(step, index) in workflow.steps"
            :key="index"
            class="workflow-step"
          >
            <div class="step-number">{{ index + 1 }}</div>
            <div class="step-content">
              <div class="step-name">{{ step.name }}</div>
              <div class="step-assignee">{{ step.assignee }}</div>
            </div>
            <div v-if="index < workflow.steps.length - 1" class="step-connector"></div>
          </div>
        </div>

        <div class="workflow-actions">
          <button class="action-btn edit-btn" @click="editWorkflow(workflow.id)">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
            </svg>
            Edit
          </button>
        </div>
      </div>
    </div>

    <!-- Create Workflow Modal -->
    <div v-if="showCreateWorkflowModal" class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <h2>Create New Workflow</h2>
          <button class="close-btn" @click="showCreateWorkflowModal = false">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="form-group">
              <label class="form-label">Workflow Name *</label>
              <input
                class="form-input"
                type="text"
                v-model="newWorkflow.name"
                placeholder="Enter workflow name"
              />
            </div>
            <div class="form-group full-width">
              <label class="form-label">Description</label>
              <textarea
                class="form-textarea"
                v-model="newWorkflow.description"
                placeholder="Enter workflow description"
                rows="3"
              ></textarea>
            </div>
            <div class="form-group full-width">
              <label class="form-label">Workflow Steps</label>
              <div class="workflow-steps-builder">
                <div
                  v-for="(step, index) in newWorkflow.steps"
                  :key="index"
                  class="step-builder"
                >
                  <input
                    class="step-input"
                    type="text"
                    v-model="step.name"
                    placeholder="Step name"
                  />
                  <select class="step-select" v-model="step.assignee">
                    <option value="">Select assignee</option>
                    <option value="Case Worker">Case Worker</option>
                    <option value="Supervisor">Supervisor</option>
                    <option value="Manager">Manager</option>
                    <option value="Admin">Admin</option>
                  </select>
                  <button
                    v-if="newWorkflow.steps.length > 1"
                    class="remove-step-btn"
                    @click="removeWorkflowStep(index)"
                  >
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <line x1="18" y1="6" x2="6" y2="18"></line>
                      <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                  </button>
                </div>
                <button class="add-step-btn" @click="addWorkflowStep">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="12" y1="5" x2="12" y2="19"></line>
                    <line x1="5" y1="12" x2="19" y2="12"></line>
                  </svg>
                  Add Step
                </button>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="cancel-btn" @click="showCreateWorkflowModal = false">Cancel</button>
          <button class="submit-btn" @click="createWorkflow">Create Workflow</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// Reactive data
const showCreateWorkflowModal = ref(false)

const newWorkflow = ref({
  name: '',
  description: '',
  steps: [{ name: '', assignee: '' }]
})

const workflows = ref([
  {
    id: 1,
    name: 'Standard Case Processing',
    description: 'Standard workflow for processing new cases',
    status: 'Active',
    steps: [
      { name: 'Initial Assessment', assignee: 'Case Worker' },
      { name: 'Investigation', assignee: 'Supervisor' },
      { name: 'Review', assignee: 'Manager' },
      { name: 'Resolution', assignee: 'Case Worker' }
    ]
  },
  {
    id: 2,
    name: 'Emergency Response',
    description: 'Urgent workflow for emergency cases',
    status: 'Active',
    steps: [
      { name: 'Immediate Assessment', assignee: 'Case Worker' },
      { name: 'Emergency Action', assignee: 'Supervisor' },
      { name: 'Follow-up', assignee: 'Case Worker' }
    ]
  },
  {
    id: 3,
    name: 'Legal Proceedings',
    description: 'Workflow for cases requiring legal action',
    status: 'Inactive',
    steps: [
      { name: 'Legal Review', assignee: 'Manager' },
      { name: 'Documentation', assignee: 'Case Worker' },
      { name: 'Court Filing', assignee: 'Admin' },
      { name: 'Follow-up', assignee: 'Case Worker' }
    ]
  }
])

// Methods
const addWorkflowStep = () => {
  newWorkflow.value.steps.push({ name: '', assignee: '' })
}

const removeWorkflowStep = (index) => {
  newWorkflow.value.steps.splice(index, 1)
}

const editWorkflow = (workflowId) => {
  console.log('Edit workflow:', workflowId)
  alert(`Edit workflow ${workflowId} functionality would be implemented here.`)
}

const toggleWorkflow = (workflowId) => {
  const workflowIndex = workflows.value.findIndex((w) => w.id === workflowId)
  if (workflowIndex !== -1) {
    const workflow = workflows.value[workflowIndex]
    workflow.status = workflow.status === "Active" ? "Inactive" : "Active"
    alert(`Workflow ${workflow.name} has been ${workflow.status.toLowerCase()}.`)
  }
}

const createWorkflow = () => {
  if (!newWorkflow.value.name || newWorkflow.value.steps.some((step) => !step.name)) {
    alert('Please fill in all required fields.')
    return
  }

  const newWorkflowObj = {
    id: workflows.value.length + 1,
    name: newWorkflow.value.name,
    description: newWorkflow.value.description,
    status: 'Active',
    steps: [...newWorkflow.value.steps]
  }

  workflows.value.push(newWorkflowObj)

  newWorkflow.value = {
    name: '',
    description: '',
    steps: [{ name: '', assignee: '' }]
  }

  showCreateWorkflowModal.value = false
  alert('Workflow created successfully!')
}
</script>

<style scoped>
/* Workflows specific styles are inherited from global components.css */
</style>

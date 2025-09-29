<template>
  <div class="main-scroll-content">
    <!-- Categories Header -->
    <div class="categories-header glass-card fine-border">
      <div class="section-title">Case Categories</div>
      <button class="create-category-btn" @click="showCreateCategoryModal = true">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
        Create Category
      </button>
    </div>

    <!-- Categories Grid -->
    <div class="categories-grid">
      <div
        v-for="category in categories"
        :key="category.id"
        class="category-card glass-card fine-border"
      >
        <div class="category-header">
          <div
            class="category-icon"
            :style="{ backgroundColor: category.color }"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 3h18v18H3z"></path>
              <path d="M9 9h6v6H9z"></path>
            </svg>
          </div>
          <div class="category-actions">
            <button class="action-btn edit-btn" @click="editCategory(category.id)">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
              </svg>
              Edit
            </button>
          </div>
        </div>
        <div class="category-content">
          <div class="category-name">{{ category.name }}</div>
          <div class="category-description">{{ category.description }}</div>
          <div class="category-stats">
            <div class="case-count">{{ category.caseCount }} cases</div>
            <div
              class="status-indicator"
              :class="{ active: category.isActive }"
            >
              {{ category.isActive ? 'Active' : 'Inactive' }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Category Modal -->
    <div v-if="showCreateCategoryModal" class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <h2>Create New Category</h2>
          <button class="close-btn" @click="showCreateCategoryModal = false">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="form-group">
              <label class="form-label">Category Name *</label>
              <input
                class="form-input"
                type="text"
                v-model="newCategory.name"
                placeholder="Enter category name"
              />
            </div>
            <div class="form-group full-width">
              <label class="form-label">Description</label>
              <textarea
                class="form-textarea"
                v-model="newCategory.description"
                placeholder="Enter category description"
                rows="3"
              ></textarea>
            </div>
            <div class="form-group full-width">
              <label class="form-label">Color</label>
              <div class="color-picker">
                <div
                  v-for="color in categoryColors"
                  :key="color"
                  class="color-option"
                  :style="{ backgroundColor: color }"
                  :class="{ selected: newCategory.color === color }"
                  @click="newCategory.color = color"
                ></div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="cancel-btn" @click="showCreateCategoryModal = false">Cancel</button>
          <button class="submit-btn" @click="createCategory">Create Category</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// Reactive data
const showCreateCategoryModal = ref(false)

const newCategory = ref({
  name: '',
  description: '',
  color: '#FF6B6B'
})

const categoryColors = ref([
  "#FF6B6B",
  "#4ECDC4",
  "#45B7D1",
  "#96CEB4",
  "#FFEAA7",
  "#DDA0DD",
  "#98D8C8",
  "#F7DC6F"
])

const categories = ref([
  {
    id: 1,
    name: 'Child Protection',
    description: 'Cases related to child safety and protection',
    color: '#FF6B6B',
    caseCount: 45,
    isActive: true
  },
  {
    id: 2,
    name: 'Family Support',
    description: 'Support services for families in need',
    color: '#4ECDC4',
    caseCount: 32,
    isActive: true
  },
  {
    id: 3,
    name: 'Education',
    description: 'Educational support and interventions',
    color: '#45B7D1',
    caseCount: 28,
    isActive: true
  },
  {
    id: 4,
    name: 'Health',
    description: 'Health-related cases and medical support',
    color: '#96CEB4',
    caseCount: 19,
    isActive: true
  },
  {
    id: 5,
    name: 'Legal',
    description: 'Legal cases and court proceedings',
    color: '#FFEAA7',
    caseCount: 12,
    isActive: true
  }
])

// Methods
const editCategory = (categoryId) => {
  console.log('Edit category:', categoryId)
  alert(`Edit category ${categoryId} functionality would be implemented here.`)
}

const createCategory = () => {
  if (!newCategory.value.name) {
    alert('Please fill in all required fields.')
    return
  }

  const newCategoryObj = {
    id: categories.value.length + 1,
    name: newCategory.value.name,
    description: newCategory.value.description,
    color: newCategory.value.color,
    caseCount: 0,
    isActive: true
  }

  categories.value.push(newCategoryObj)

  newCategory.value = {
    name: '',
    description: '',
    color: '#FF6B6B'
  }

  showCreateCategoryModal.value = false
  alert('Category created successfully!')
}
</script>

<style scoped>
/* Categories specific styles are inherited from global components.css */
</style>

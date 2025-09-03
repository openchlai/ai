<template>
  <div class="categories-page">
    <button class="mobile-menu-btn" @click="toggleMobileMenu">
      <svg fill="none" height="24" viewbox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">
        <path d="M3 12H21M3 6H21M3 18H21" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" />
      </svg>
    </button>

    <div class="sidebar" :class="{ 'collapsed': isSidebarCollapsed }">
      <div class="toggle-btn" @click="toggleSidebar">
        {{ isSidebarCollapsed ? '>' : '<' }}
      </div>
      <div class="sidebar-content">
        <div class="logo-container">
          <div class="logo">
            <img src="/Openchs logo-1.png" alt="Openchs logo-1.png" />
          </div>
        </div>
        
        <router-link v-for="item in navigationItems" 
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: currentRoute === item.path }"
        >
          <div class="nav-icon">
            <component :is="item.icon" v-if="item.icon" />
          </div>
          <div class="nav-text">{{ item.text }}</div>
        </router-link>

        <div class="user-profile">
          <router-link class="user-avatar" to="/edit-profile">
            <svg fill="currentColor" viewbox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 12C14.2091 12 16 10.2091 16 8C16 5.79086 14.2091 4 12 4C9.79086 4 8 5.79086 8 8C8 10.2091 9.79086 12 12 12Z" />
              <path d="M12 14C7.58172 14 4 17.5817 4 22H20C20 17.5817 16.4183 14 12 14Z" />
            </svg>
          </router-link>
        </div>

        <div class="status">
          <div class="status-dot" :class="{ 'online': isOnline }"></div>
          <span>Status: {{ isOnline ? 'Online' : 'Offline' }}</span>
        </div>

        <div class="button-container">
          <button class="join-queue-btn" @click="toggleQueueStatus">
            {{ isInQueue ? 'Leave Queue' : 'Join Queue' }}
          </button>
          <button class="logout-btn" @click="handleLogout">Logout</button>
        </div>
      </div>
    </div>

    <div class="main-content">
      <div class="header">
        <h1>Categories</h1>
        <div class="search-container">
          <input 
            v-model="searchQuery"
            class="input" 
            placeholder="Search categories..." 
            type="text"
            @input="handleSearch"
          />
          <button class="btn btn--primary btn--sm" @click="openAddCategoryModal">
            <svg fill="none" height="16" viewbox="0 0 24 24" width="16" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 5V19M5 12H19" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" />
            </svg>
            Add Category
          </button>
        </div>
      </div>

      <div class="view-tabs" style="display:flex; gap:8px; padding: 8px 0;">
        <button
          v-for="view in viewOptions"
          :key="view.id"
          class="btn btn--secondary btn--sm"
          :class="{ active: currentView === view.id }"
          @click="handleViewChange(view.id)"
        >
          {{ view.label }}
        </button>
      </div>

      <!-- Grid View -->
      <div v-if="currentView === 'grid'" class="view-container">
        <div v-if="isLoading" class="loading-state">
          <div class="spinner"></div>
          <p>Loading categories...</p>
        </div>
        
        <div v-else-if="error" class="error-state">
          <p>{{ error }}</p>
          <button @click="fetchCategories">Retry</button>
        </div>

        <div v-else-if="filteredCategories.length === 0" class="empty-state">
          <p>No categories found</p>
          <button @click="openAddCategoryModal">Add New Category</button>
        </div>

        <div v-else class="categories-container">
          <div 
            v-for="category in filteredCategories" 
            :key="category.id"
            class="category-card card"
          >
            <div class="category-header">
              <div class="category-title">{{ category.title }}</div>
              <div class="category-count">{{ category.count }}</div>
            </div>
            <div class="category-description">{{ category.description }}</div>
            <div class="category-footer">
              <div>Last updated: {{ formatLastUpdated(category.lastUpdated) }}</div>
              <div class="category-actions">
                <button class="btn btn--secondary btn--sm" @click="editCategory(category)">
                  <svg fill="none" height="16" viewbox="0 0 24 24" width="16" xmlns="http://www.w3.org/2000/svg">
                    <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" />
                    <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" />
                  </svg>
                </button>
                <button class="btn btn--danger btn--sm" @click="confirmDeleteCategory(category)">
                  <svg fill="none" height="16" viewbox="0 0 24 24" width="16" xmlns="http://www.w3.org/2000/svg">
                    <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2M10 11v6M14 11v6" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Timeline View -->
      <div v-else-if="currentView === 'timeline'" class="view-container">
        <div class="timeline-container">
          <div v-for="category in filteredCategories" :key="category.id" class="timeline-item">
            <div class="timeline-date">{{ formatLastUpdated(category.lastUpdated) }}</div>
            <div class="timeline-content">
              <h3>{{ category.title }}</h3>
              <p>{{ category.description }}</p>
              <div class="timeline-actions">
                <button @click="editCategory(category)">Edit</button>
                <button @click="confirmDeleteCategory(category)">Delete</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Table View -->
      <div v-else-if="currentView === 'table'" class="view-container">
        <table class="categories-table card" style="width:100%;">
          <thead>
            <tr>
              <th>Title</th>
              <th>Description</th>
              <th>Count</th>
              <th>Last Updated</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="category in filteredCategories" :key="category.id">
              <td>{{ category.title }}</td>
              <td>{{ category.description }}</td>
              <td>{{ category.count }}</td>
              <td>{{ formatLastUpdated(category.lastUpdated) }}</td>
              <td>
                <button class="btn btn--secondary btn--sm" @click="editCategory(category)">Edit</button>
                <button class="btn btn--danger btn--sm" @click="confirmDeleteCategory(category)">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Add/Edit Category Modal -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal" @click.stop>
        <div class="modal__header">{{ isEditing ? 'Edit Category' : 'Add New Category' }}</div>
        <div class="modal__body">
          <form @submit.prevent="handleCategorySubmit">
            <div class="form-group">
              <label class="form-label" for="title">Title</label>
              <input class="input" id="title" v-model="categoryForm.title" type="text" required />
            </div>
            <div class="form-group">
              <label class="form-label" for="description">Description</label>
              <textarea class="input" id="description" v-model="categoryForm.description" required></textarea>
            </div>
            <div class="modal__footer">
              <button type="button" class="btn btn--secondary" @click="closeModal">Cancel</button>
              <button type="submit" class="btn btn--primary">{{ isEditing ? 'Save Changes' : 'Add Category' }}</button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal">
      <div class="modal-content">
        <h2>Confirm Delete</h2>
        <p>Are you sure you want to delete this category? This action cannot be undone.</p>
        <div class="modal-actions">
          <button @click="closeDeleteModal">Cancel</button>
          <button class="delete-btn" @click="handleDeleteCategory">Delete</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { formatDistanceToNow } from 'date-fns'
import type { Category, CategoryForm } from '../types/category'
import { useCategoryStore } from '../stores/category'
import { useAuthStore } from '../stores/auth'
import { useNotificationStore } from '../stores/notification'

// Store instances
const categoryStore = useCategoryStore()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()

// Router and route
const router = useRouter()
const route = useRoute()

// State
const isSidebarCollapsed = ref(false)
const isOnline = ref(true)
const isInQueue = ref(false)
const searchQuery = ref('')
const currentView = ref('table')
const isLoading = ref(false)
const error = ref<string | null>(null)
const showModal = ref(false)
const showDeleteModal = ref(false)
const isEditing = ref(false)
const selectedCategory = ref<Category | null>(null)

// Form state
const categoryForm = ref<CategoryForm>({
  title: '',
  description: ''
})

// Navigation items
const navigationItems = [
  { path: '/dashboard', text: 'Dashboard', icon: 'DashboardIcon' },
  { path: '/calls', text: 'Calls', icon: 'CallsIcon' },
  { path: '/cases', text: 'Cases', icon: 'CasesIcon' },
  { path: '/chats', text: 'Chats', icon: 'ChatsIcon' },
  { path: '/qa-statistics', text: 'QA Statistics', icon: 'QAIcon' },
  { path: '/wallboard', text: 'Wallboard', icon: 'WallboardIcon' },
  { path: '/categories', text: 'Categories', icon: 'CategoriesIcon' },
  { path: '/settings', text: 'Settings', icon: 'SettingsIcon' }
]

// View options
const viewOptions = [
  { id: 'table', label: 'Table View' },
  { id: 'timeline', label: 'Timeline' },
  { id: 'grid', label: 'Grid View' }
]

// Computed
const currentRoute = computed(() => route.path)
const filteredCategories = computed(() => {
  if (!searchQuery.value) return categoryStore.categories
  const query = searchQuery.value.toLowerCase()
  return categoryStore.categories.filter(category => 
    category.title.toLowerCase().includes(query) ||
    category.description.toLowerCase().includes(query)
  )
})

// Methods
const toggleMobileMenu = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
}

const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
}

const toggleQueueStatus = () => {
  isInQueue.value = !isInQueue.value
}

const handleLogout = async () => {
  try {
    await authStore.logout()
    router.push('/login')
  } catch (error) {
    notificationStore.error('Failed to logout. Please try again.')
  }
}

const fetchCategories = async () => {
  isLoading.value = true
  error.value = null
  try {
    await categoryStore.fetchCategories()
  } catch (err) {
    error.value = 'Failed to load categories. Please try again.'
    notificationStore.error(error.value)
  } finally {
    isLoading.value = false
  }
}

const handleSearch = () => {
  // Debounced search could be implemented here
}

const handleViewChange = (viewId: string) => {
  currentView.value = viewId
}

const openAddCategoryModal = () => {
  isEditing.value = false
  categoryForm.value = {
    title: '',
    description: ''
  }
  showModal.value = true
}

const editCategory = (category: Category) => {
  isEditing.value = true
  selectedCategory.value = category
  categoryForm.value = {
    title: category.title,
    description: category.description
  }
  showModal.value = true
}

const confirmDeleteCategory = (category: Category) => {
  selectedCategory.value = category
  showDeleteModal.value = true
}

const closeModal = () => {
  showModal.value = false
  categoryForm.value = {
    title: '',
    description: ''
  }
  selectedCategory.value = null
}

const closeDeleteModal = () => {
  showDeleteModal.value = false
  selectedCategory.value = null
}

const handleCategorySubmit = async () => {
  try {
    if (isEditing.value && selectedCategory.value) {
      await categoryStore.updateCategory(selectedCategory.value.id, categoryForm.value)
      notificationStore.success('Category updated successfully')
    } else {
      await categoryStore.createCategory(categoryForm.value)
      notificationStore.success('Category created successfully')
    }
    closeModal()
  } catch (error) {
    notificationStore.error('Failed to save category. Please try again.')
  }
}

const handleDeleteCategory = async () => {
  if (!selectedCategory.value) return
  
  try {
    await categoryStore.deleteCategory(selectedCategory.value.id)
    notificationStore.success('Category deleted successfully')
    closeDeleteModal()
  } catch (error) {
    notificationStore.error('Failed to delete category. Please try again.')
  }
}

const formatLastUpdated = (date: Date) => {
  return formatDistanceToNow(date, { addSuffix: true })
}

// Lifecycle hooks
onMounted(() => {
  fetchCategories()
})
</script>

<style scoped>
/* Categories styles moved to global components.css */
</style>

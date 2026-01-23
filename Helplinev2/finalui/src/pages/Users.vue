<template>
  <div 
    class="space-y-6"
  >

    <!-- Filters -->
    <UsersFilter @update:filters="applyFilters" />

    <!-- Loading State -->
    <div 
      v-if="store.loading" 
      class="flex justify-center items-center py-12 rounded-xl shadow-xl border"
      :class="isDarkMode 
        ? 'bg-black border-transparent' 
        : 'bg-white border-transparent'"
    >
      <div 
        :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
      >
        Loading users...
      </div>
    </div>

    <!-- Content when loaded -->
    <div v-else>
      <!-- View Toggle Buttons and Stats Row -->
      <div class="flex justify-between items-center mb-6">
        <!-- Total Count with Pagination Info -->
        <div
          class="flex items-center gap-2"
          :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
        >
          <i-mdi-account-multiple
            class="w-5 h-5"
            :class="isDarkMode ? 'text-amber-500' : 'text-amber-700'"
          />
          <span class="text-sm">
            Showing {{ store.paginationInfo.rangeStart }} - {{ store.paginationInfo.rangeEnd }} of
          </span>
          <span
            class="text-lg font-bold"
            :class="isDarkMode ? 'text-amber-500' : 'text-amber-700'"
          >
            {{ store.paginationInfo.total }}
          </span>
          <span class="text-sm">users</span>
        </div>

        <!-- View Toggle Buttons -->
        <div class="flex gap-3">
          <button
            @click="view = 'timeline'"
            :class="getViewButtonClass(view === 'timeline')"
          >
            <i-mdi-timeline-text-outline class="w-5 h-5" />
            Timeline
          </button>

          <button
            @click="view = 'table'"
            :class="getViewButtonClass(view === 'table')"
          >
            <i-mdi-table class="w-5 h-5" />
            Table
          </button>

          <button
            @click="showCreateModal = true"
            class="px-5 py-2.5 rounded-xl font-medium transition-all duration-200 flex items-center gap-2 text-sm bg-green-600 text-white hover:bg-green-700 shadow-lg active:scale-95"
          >
            <i-mdi-plus-circle class="w-5 h-5" />
            Create User
          </button>

          <button
            @click="refreshUsers"
            :disabled="store.loading"
            class="px-5 py-2.5 rounded-xl font-medium transition-all duration-200 flex items-center gap-2 text-sm border disabled:opacity-50 disabled:cursor-not-allowed"
            :class="isDarkMode 
              ? 'bg-black text-gray-300 border-transparent hover:border-green-500 hover:text-green-400' 
              : 'bg-white text-gray-700 border-transparent hover:border-green-600 hover:text-green-700'"
          >
            <i-mdi-refresh class="w-5 h-5" />
            Refresh
          </button>
        </div>
      </div>

      <!-- Timeline view -->
      <div v-if="view === 'timeline'">
        <UsersTimeline @refresh="refreshUsers" @edit="handleEditUser" />
      </div>

      <!-- Table view -->
      <div v-if="view === 'table'">
        <UsersTable @refresh="refreshUsers" @edit="handleEditUser" />
      </div>

      <!-- Pagination Controls -->
      <Pagination
        :paginationInfo="store.paginationInfo"
        :hasNextPage="store.hasNextPage"
        :hasPrevPage="store.hasPrevPage"
        :loading="store.loading"
        :pageSize="selectedPageSize"
        @prev="goToPrevPage"
        @next="goToNextPage"
        @goToPage="goToPage"
        @changePageSize="changePageSize"
      />
    </div>

    <!-- Create User Modal -->
    <Transition name="modal">
      <div 
        v-if="showCreateModal"
        class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4 overflow-y-auto"
      >
        <div class="my-8">
          <UserForm @saved="handleSaved" @cancel="showCreateModal = false" />
        </div>
      </div>
    </Transition>

    <!-- Edit User Modal -->
    <Transition name="modal">
      <div 
        v-if="showEditModal"
        class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4 overflow-y-auto"
      >
        <div class="my-8">
          <UserEditForm 
            :user="userToEdit"
            @saved="handleEditSaved" 
            @cancel="showEditModal = false" 
          />
        </div>
      </div>
    </Transition>

  </div>
</template>

<script setup>
import { ref, onMounted, inject, watch } from 'vue'
import { toast } from 'vue-sonner'
import { useUserStore } from '@/stores/users'
import { useSearchStore } from '@/stores/search'
import UsersTable from '@/components/users/Table.vue'
import UsersTimeline from '@/components/users/Timeline.vue'
import UserForm from '@/components/users/UserForm.vue'
import UserEditForm from '@/components/users/UserEditForm.vue'
import UsersFilter from '@/components/users/UsersFilter.vue'
import Pagination from '@/components/base/Pagination.vue'

const store = useUserStore()
const searchStore = useSearchStore()
const view = ref('timeline')
const showCreateModal = ref(false)
const showEditModal = ref(false)
const userToEdit = ref(null)
const currentFilters = ref({})
const selectedPageSize = ref(20)

// Debounce handle for global search
let searchDebounce = null

// Watch for global search query changes
watch(() => searchStore.query, (newQuery) => {
  clearTimeout(searchDebounce)
  searchDebounce = setTimeout(() => {
    // Merge search query with existing filters
    const searchParams = { ...currentFilters.value }
    if (newQuery) {
      searchParams.q = newQuery
    } else {
      delete searchParams.q
    }
    applyFilters(searchParams)
  }, 500)
})

// Inject theme
const isDarkMode = inject('isDarkMode')

// Dynamic button class for view toggle
const getViewButtonClass = (isActive) => {
  const baseClasses = 'px-5 py-2.5 rounded-xl font-medium transition-all duration-200 flex items-center gap-2 text-sm'
  
  if (isActive) {
    return isDarkMode.value
      ? `${baseClasses} bg-amber-600 text-white shadow-lg shadow-amber-900/50`
      : `${baseClasses} bg-amber-700 text-white shadow-lg shadow-amber-900/30`
  } else {
    return isDarkMode.value
      ? `${baseClasses} bg-black text-gray-300 border border-transparent hover:border-amber-600 hover:text-amber-500`
      : `${baseClasses} bg-white text-gray-700 border border-transparent hover:border-amber-600 hover:text-amber-700`
  }
}

onMounted(async () => {
  try {
    await store.listUsers({ _o: 0, _c: selectedPageSize.value })
    console.log('Users fetched:', store.users?.length)
    console.log('Pagination info:', store.paginationInfo)
  } catch (err) {
    console.error('Failed to fetch users:', err)
    toast.error('Failed to load users. Please try again.')
  }
})

async function applyFilters(filters) {
  currentFilters.value = filters
  try {
    console.log('Applying filters:', filters)
    store.resetPagination()
    await store.listUsers({ ...filters, _o: 0, _c: selectedPageSize.value })
    console.log('Filtered users fetched:', store.users)
  } catch (err) {
    console.error('Error fetching filtered users:', err)
    toast.error('Failed to apply filters. Please try again.')
  }
}

async function refreshUsers() {
  try {
    console.log('Refreshing users...')
    await store.listUsers({
      ...currentFilters.value,
      _o: store.pagination.offset,
      _c: store.pagination.limit
    })
    console.log('Users refreshed')
    toast.success('Users refreshed successfully!')
  } catch (err) {
    console.error('Error refreshing users:', err)
    toast.error('Failed to refresh users. Please try again.')
  }
}

// Pagination handlers
async function goToNextPage() {
  try {
    await store.nextPage(currentFilters.value)
  } catch (err) {
    console.error('Error going to next page:', err)
    toast.error('Failed to load next page.')
  }
}

async function goToPrevPage() {
  try {
    await store.prevPage(currentFilters.value)
  } catch (err) {
    console.error('Error going to previous page:', err)
    toast.error('Failed to load previous page.')
  }
}

async function goToPage(page) {
  if (page === '...') return
  try {
    await store.goToPage(page, currentFilters.value)
  } catch (err) {
    console.error('Error going to page:', err)
    toast.error('Failed to load page.')
  }
}

async function changePageSize(size) {
  selectedPageSize.value = size
  try {
    await store.setPageSize(size, currentFilters.value)
  } catch (err) {
    console.error('Error changing page size:', err)
    toast.error('Failed to change page size.')
  }
}

const handleSaved = async () => {
  showCreateModal.value = false
  // Refresh maintaining current pagination
  await store.listUsers({
    ...currentFilters.value,
    _o: store.pagination.offset,
    _c: store.pagination.limit
  })
  toast.success('User saved successfully!')
}

const handleEditUser = (user) => {
  userToEdit.value = user
  showEditModal.value = true
}

const handleEditSaved = async () => {
  showEditModal.value = false
  userToEdit.value = null
  // Refresh maintaining current pagination
  await store.listUsers({
    ...currentFilters.value,
    _o: store.pagination.offset,
    _c: store.pagination.limit
  })
  toast.success('User updated successfully!')
}
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>
<template>
  <div class="main-scroll-content">
    <!-- Page Header -->
    <div class="page-header glass-card fine-border">
      <div class="header-content">
        <div class="header-info">
          <h1 class="page-title">Team Management</h1>
          <p class="page-subtitle">Manage team members and their roles</p>
        </div>
        <div class="header-stats">
          <div class="stat-item">
            <span class="stat-value">{{ totalUsers }}</span>
            <span class="stat-label">Total Users</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ activeUsers }}</span>
            <span class="stat-label">Active</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ pendingUsers }}</span>
            <span class="stat-label">Pending</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Table Controls -->
    <div class="table-card glass-card fine-border">
      <div class="table-controls">
        <button class="create-user-btn" @click="showInviteUserModal = true">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
            <circle cx="8.5" cy="7" r="4"></circle>
            <line x1="20" y1="8" x2="20" y2="14"></line>
            <line x1="23" y1="11" x2="17" y2="11"></line>
          </svg>
          Invite User
        </button>
        <div class="controls-right">
          <button class="filter-btn" @click="toggleUserFilters">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="22,3 2,3 10,12.46 10,19 14,21 14,12.46"></polygon>
            </svg>
            Filters
            <span v-if="activeFiltersCount > 0" class="filter-badge">{{ activeFiltersCount }}</span>
          </button>
          <button class="export-btn" @click="exportUsers">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="7,10 12,15 17,10"></polyline>
              <line x1="12" y1="15" x2="12" y2="3"></line>
            </svg>
            Export
          </button>
        </div>
      </div>

      <!-- User Filters -->
      <div v-if="showUserFilters" class="user-filters">
        <div class="filters-row">
          <div class="filter-group">
            <label class="filter-label">Role</label>
            <select class="filter-select" v-model="userFilters.role">
              <option value="">All Roles</option>
              <option value="Admin">Admin</option>
              <option value="Manager">Manager</option>
              <option value="Case Worker">Case Worker</option>
              <option value="Supervisor">Supervisor</option>
            </select>
          </div>
          <div class="filter-group">
            <label class="filter-label">Status</label>
            <select class="filter-select" v-model="userFilters.status">
              <option value="">All Status</option>
              <option value="Active">Active</option>
              <option value="Inactive">Inactive</option>
              <option value="Pending">Pending</option>
            </select>
          </div>
          <div class="filter-group">
            <label class="filter-label">Search</label>
            <input
              class="filter-input"
              type="text"
              placeholder="Search users..."
              v-model="userFilters.search"
            />
          </div>
        </div>
        <div class="filters-actions">
          <button class="clear-filters-btn" @click="clearFilters">Clear All</button>
          <button class="apply-filters-btn" @click="applyFilters">Apply Filters</button>
        </div>
      </div>

      <!-- Users Table -->
      <div class="table-container">
        <div v-if="filteredUsers.length === 0" class="empty-state">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
            <circle cx="9" cy="7" r="4"></circle>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
          </svg>
          <h3>No users found</h3>
          <p v-if="hasActiveFilters">Try adjusting your filters or search terms</p>
          <p v-else>Get started by inviting your first team member</p>
          <button class="create-user-btn" @click="showInviteUserModal = true">Invite User</button>
        </div>

        <table v-else class="users-table">
          <thead>
            <tr>
              <th>User</th>
              <th>Role</th>
              <th>Status</th>
              <th>Cases Assigned</th>
              <th>Last Active</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in filteredUsers" :key="user.id" class="user-row">
              <td>
                <div class="user-cell">
                  <div class="user-avatar">
                    {{ getInitials(user.name) }}
                  </div>
                  <div class="user-details">
                    <div class="user-name">{{ user.name }}</div>
                    <div class="user-email">{{ user.email }}</div>
                    <div class="user-phone" v-if="user.phone">{{ user.phone }}</div>
                  </div>
                </div>
              </td>
              <td>
                <div class="role-cell">
                  <div v-if="editingRole !== user.id" class="role-display" @click="startEditingRole(user.id)">
                    <span class="role-badge" :class="user.role.toLowerCase()">
                      {{ user.role }}
                    </span>
                    <svg class="edit-icon" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                    </svg>
                  </div>
                  <select
                    v-else
                    class="role-select"
                    v-model="user.role"
                    @change="saveUserRole(user.id, user.role)"
                    @blur="editingRole = null"
                  >
                    <option value="Admin">Admin</option>
                    <option value="Manager">Manager</option>
                    <option value="Case Worker">Case Worker</option>
                    <option value="Supervisor">Supervisor</option>
                  </select>
                </div>
              </td>
              <td>
                <div class="status-cell">
                  <span class="status-badge" :class="user.status.toLowerCase()">
                    {{ user.status }}
                  </span>
                  <button 
                    class="toggle-status-btn" 
                    @click="toggleUserStatus(user.id)"
                    :title="user.status === 'Active' ? 'Deactivate User' : 'Activate User'"
                  >
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M18 8L22 12L18 16"></path>
                      <path d="M6 8L2 12L6 16"></path>
                      <path d="M14 4L10 20"></path>
                    </svg>
                  </button>
                </div>
              </td>
              <td>
                <div class="cases-info">
                  <span class="cases-count">{{ getUserCasesCount(user.id) }}</span>
                  <span class="cases-label">cases</span>
                </div>
              </td>
              <td>
                <div class="last-active">
                  <div class="active-date">{{ formatDate(user.lastActive || user.createdAt) }}</div>
                  <div class="active-time">{{ formatTime(user.lastActive || user.createdAt) }}</div>
                </div>
              </td>
              <td>
                <div class="user-actions">
                  <button class="action-btn view-btn" @click="viewUser(user.id)" title="View Profile">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                      <circle cx="12" cy="12" r="3"></circle>
                    </svg>
                  </button>
                  <button class="action-btn edit-btn" @click="editUser(user.id)" title="Edit User">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Invite User Modal -->
    <div v-if="showInviteUserModal" class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <h2>Invite New User</h2>
          <button class="close-btn" @click="showInviteUserModal = false">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="form-group">
              <label class="form-label">Full Name *</label>
              <input
                class="form-input"
                type="text"
                v-model="newUser.name"
                placeholder="Enter full name"
              />
            </div>
            <div class="form-group">
              <label class="form-label">Email Address *</label>
              <input
                class="form-input"
                type="email"
                v-model="newUser.email"
                placeholder="Enter email address"
              />
            </div>
            <div class="form-group">
              <label class="form-label">Phone Number</label>
              <input
                class="form-input"
                type="tel"
                v-model="newUser.phone"
                placeholder="Enter phone number"
              />
            </div>
            <div class="form-group">
              <label class="form-label">Role *</label>
              <select class="form-select" v-model="newUser.role">
                <option value="">Select role</option>
                <option value="Admin">Admin</option>
                <option value="Manager">Manager</option>
                <option value="Case Worker">Case Worker</option>
                <option value="Supervisor">Supervisor</option>
              </select>
            </div>
            <div class="form-group full-width">
              <label class="form-label">Welcome Message</label>
              <textarea
                class="form-textarea"
                v-model="newUser.message"
                placeholder="Optional welcome message..."
                rows="3"
              ></textarea>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="cancel-btn" @click="showInviteUserModal = false">Cancel</button>
          <button class="submit-btn" @click="inviteUser">Send Invitation</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted } from 'vue'
import { useUserStore } from '../../stores/users'
import { useCaseStore } from '../../stores/cases'

const userStore = useUserStore()
const caseStore = useCaseStore()

// Reactive data
const showInviteUserModal = ref(false)
const showUserFilters = ref(false)
const editingRole = ref(null)
const userFilters = ref({
  role: '',
  status: '',
  search: ''
})

const newUser = ref({
  name: '',
  email: '',
  phone: '',
  role: '',
  message: ''
})

// Computed properties
const totalUsers = computed(() => userStore.users.length)
const activeUsers = computed(() => userStore.users.filter(u => u.status === 'Active').length)
const pendingUsers = computed(() => userStore.users.filter(u => u.status === 'Pending').length)

const filteredUsers = computed(() => {
  let filtered = userStore.users

  if (userFilters.value.role) {
    filtered = filtered.filter(u => u.role === userFilters.value.role)
  }
  if (userFilters.value.status) {
    filtered = filtered.filter(u => u.status === userFilters.value.status)
  }
  if (userFilters.value.search) {
    const search = userFilters.value.search.toLowerCase()
    filtered = filtered.filter(u => 
      u.name.toLowerCase().includes(search) ||
      u.email.toLowerCase().includes(search)
    )
  }

  return filtered
})

const activeFiltersCount = computed(() => {
  return Object.values(userFilters.value).filter(value => value !== '').length
})

const hasActiveFilters = computed(() => activeFiltersCount.value > 0)

// Methods
const toggleUserFilters = () => {
  showUserFilters.value = !showUserFilters.value
}

const clearFilters = () => {
  userFilters.value = {
    role: '',
    status: '',
    search: ''
  }
}

const applyFilters = () => {
  showUserFilters.value = false
}

const startEditingRole = (userId) => {
  editingRole.value = userId
  nextTick(() => {
    const select = document.querySelector('.role-select')
    if (select) select.focus()
  })
}

const saveUserRole = (userId, newRole) => {
  const userIndex = userStore.users.findIndex((user) => user.id === userId)
  if (userIndex !== -1) {
    const oldRole = userStore.users[userIndex].role
    const user = userStore.users[userIndex]

    userStore.editUser(userId, { ...user, role: newRole }).then(() => {
      userStore.listUsers()
      alert(`User role updated from ${oldRole} to ${newRole}`)
    }).catch(error => {
      console.error('Error updating user role:', error)
      alert('Failed to update user role. Please try again.')
    })
  }
  editingRole.value = null
}

const toggleUserStatus = (userId) => {
  const userIndex = userStore.users.findIndex((user) => user.id === userId)
  if (userIndex !== -1) {
    const user = userStore.users[userIndex]
    const newStatus = user.status === "Active" ? "Inactive" : "Active"

    userStore.editUser(userId, { ...user, status: newStatus }).then(() => {
      userStore.listUsers()
      alert(`User ${user.name} has been ${newStatus.toLowerCase()}.`)
    }).catch(error => {
      console.error('Error updating user status:', error)
      alert('Failed to update user status. Please try again.')
    })
  }
}

const inviteUser = () => {
  if (!newUser.value.name || !newUser.value.email || !newUser.value.role) {
    alert('Please fill in all required fields')
    return
  }

  const newUserObj = {
    name: newUser.value.name,
    email: newUser.value.email,
    role: newUser.value.role,
    phone: newUser.value.phone,
    status: 'Pending'
  }

  userStore.createUser(newUserObj).then(() => {
    userStore.listUsers()
    alert('Invitation sent successfully!')
  }).catch(error => {
    console.error('Error creating user:', error)
    alert('Failed to invite user. Please try again.')
  })

  newUser.value = {
    name: '',
    email: '',
    phone: '',
    role: '',
    message: ''
  }
  showInviteUserModal.value = false
}

const viewUser = (userId) => {
  console.log('View user:', userId)
  alert(`View user ${userId} functionality would be implemented here.`)
}

const editUser = (userId) => {
  console.log('Edit user:', userId)
  alert(`Edit user ${userId} functionality would be implemented here.`)
}

const exportUsers = () => {
  console.log('Exporting users...')
  alert('Exporting users to CSV...')
}

const getUserCasesCount = (userId) => {
  return caseStore.cases.filter(c => c.assignedTo === userStore.users.find(u => u.id === userId)?.name).length
}

const getInitials = (name) => {
  if (!name || typeof name !== 'string') return ''
  return name
    .split(' ')
    .map(part => part[0])
    .join('')
    .toUpperCase()
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString()
}

const formatTime = (date) => {
  return new Date(date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

onMounted(async () => {
  await userStore.listUsers()
  await caseStore.listCases()
})
</script>

<style scoped>
/* Users specific styles are inherited from global components.css */
</style>

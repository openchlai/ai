// src/stores/notifications.js
import { defineStore } from 'pinia'
import axiosInstance from '@/utils/axios'
import { useAuthStore } from './auth'

export const useNotificationsStore = defineStore('notificationsStore', {
  state: () => ({
    notifications: [],      // array of notifications (raw array format)
    notifications_k: {},    // metadata keys
    notifications_ctx: [],  // context (pagination etc.)
    loading: false,
    error: null,
    // Pagination state
    pagination: {
      offset: 0,
      limit: 10,
      currentPage: 1,
      totalRecords: 0,
      rangeStart: 1,
      rangeEnd: 10
    }
  }),

  getters: {
    notificationCount: (state) => state.pagination.totalRecords,
    unreadCount: (state) => {
      // Count notifications where read_on is empty/null
      // If read_on field doesn't exist in API response, return the total count from pagination
      const readOnIndex = parseInt(state.notifications_k?.read_on?.[0] ?? -1)
      if (readOnIndex === -1) return state.pagination.totalRecords
      return state.notifications.filter(notif => !notif[readOnIndex] || notif[readOnIndex] === '0').length
    },

    // Pagination getters
    totalRecords: (state) => state.pagination.totalRecords,
    currentPage: (state) => state.pagination.currentPage,
    pageSize: (state) => state.pagination.limit,
    totalPages: (state) => Math.ceil(state.pagination.totalRecords / state.pagination.limit) || 1,
    hasNextPage: (state) => state.pagination.rangeEnd < state.pagination.totalRecords,
    hasPrevPage: (state) => state.pagination.currentPage > 1,
    paginationInfo: (state) => ({
      rangeStart: state.pagination.rangeStart,
      rangeEnd: state.pagination.rangeEnd,
      total: state.pagination.totalRecords,
      currentPage: state.pagination.currentPage,
      totalPages: Math.ceil(state.pagination.totalRecords / state.pagination.limit) || 1
    }),

    // Get notification by ID
    getNotificationById: (state) => (id) => {
      const index = parseInt(state.notifications_k?.id?.[0] ?? 0)
      return state.notifications.find(notif => notif[index] === id) || null
    },

    // Helper to map single notification array to object
    mapNotificationToObject: (state) => (notificationArray) => {
      const obj = {}
      for (const [fieldName, fieldInfo] of Object.entries(state.notifications_k)) {
        const index = fieldInfo[0]
        obj[fieldName] = notificationArray[index] || ''
      }
      return obj
    }
  },

  actions: {
    // Helper to get auth headers
    getAuthHeaders() {
      const authStore = useAuthStore()
      return {
        'Session-Id': authStore.sessionId
      }
    },

    // Parse notifications_ctx to update pagination state
    parsePaginationContext(ctx) {
      if (ctx && ctx[0] && Array.isArray(ctx[0])) {
        const [offset, limit, rangeStart, rangeEnd, total] = ctx[0]
        this.pagination.offset = parseInt(offset) || 0
        this.pagination.limit = parseInt(limit) || 10
        this.pagination.rangeStart = parseInt(rangeStart) || 1
        this.pagination.rangeEnd = parseInt(rangeEnd) || 10
        this.pagination.totalRecords = parseInt(total) || 0
        this.pagination.currentPage = Math.floor(this.pagination.offset / this.pagination.limit) + 1
      }
    },

    // Fetch notifications from the activities API endpoint
    async fetchNotifications(params = {}) {
      this.loading = true
      this.error = null

      try {
        // Build pagination params
        const paginationParams = {
          _c: params._c || this.pagination.limit,
          _o: params._o !== undefined ? params._o : this.pagination.offset,
          _a: 0, // Include activities parameter
          action: 'notify', // Filter for notification-type activities only
          ...params
        }
        delete paginationParams.page

        const { data } = await axiosInstance.get('api/activities/', {
          params: paginationParams,
          headers: this.getAuthHeaders()
        })

        console.log('📬 Notifications API Response:', {
          activities: data.activities?.length,
          activities_ctx: data.activities_ctx
        })

        // Extract notification data from the activities API response
        this.notifications = data.activities || []
        this.notifications_k = data.activities_k || {}
        this.notifications_ctx = data.activities_ctx || []

        // Parse pagination context
        this.parsePaginationContext(data.activities_ctx)

        return {
          notifications: this.notifications,
          total: this.pagination.totalRecords,
          unread: this.unreadCount
        }
      } catch (err) {
        this.error = err.message || 'Failed to fetch notifications'
        console.error('❌ Failed to fetch notifications:', err)
        throw err
      } finally {
        this.loading = false
      }
    },

    // Mark notification as read
    async markAsRead(notificationId) {
      try {
        // Call the activities endpoint to mark as read
        const { data } = await axiosInstance.put(
          `api/activities/${notificationId}`,
          { read_on: Math.floor(Date.now() / 1000) },
          { headers: this.getAuthHeaders() }
        )

        // Update local state
        const idIndex = parseInt(this.notifications_k?.id?.[0] ?? 0)
        const readOnIndex = parseInt(this.notifications_k?.read_on?.[0] ?? -1)

        if (readOnIndex !== -1) {
          const notification = this.notifications.find(n => n[idIndex] === notificationId)
          if (notification) {
            notification[readOnIndex] = Math.floor(Date.now() / 1000).toString()
          }
        }

        return data
      } catch (err) {
        console.error('❌ Failed to mark notification as read:', err)
        throw err
      }
    },

    // Mark all notifications as read
    async markAllAsRead() {
      try {
        const idIndex = parseInt(this.notifications_k?.id?.[0] ?? 0)
        const readOnIndex = parseInt(this.notifications_k?.read_on?.[0] ?? -1)

        if (readOnIndex === -1) return

        // Get all unread notification IDs
        const unreadIds = this.notifications
          .filter(n => !n[readOnIndex] || n[readOnIndex] === '0')
          .map(n => n[idIndex])

        // Mark each as read (could be optimized with a batch endpoint if available)
        await Promise.all(unreadIds.map(id => this.markAsRead(id)))

        // Refresh notifications
        await this.fetchNotifications()
      } catch (err) {
        console.error('❌ Failed to mark all as read:', err)
        throw err
      }
    },

    // Go to next page
    async nextPage(filters = {}) {
      if (!this.hasNextPage) return
      const newOffset = this.pagination.offset + this.pagination.limit
      await this.fetchNotifications({ ...filters, _o: newOffset, _c: this.pagination.limit })
    },

    // Go to previous page
    async prevPage(filters = {}) {
      if (!this.hasPrevPage) return
      const newOffset = Math.max(0, this.pagination.offset - this.pagination.limit)
      await this.fetchNotifications({ ...filters, _o: newOffset, _c: this.pagination.limit })
    },

    // Go to specific page
    async goToPage(page, filters = {}) {
      const newOffset = (page - 1) * this.pagination.limit
      await this.fetchNotifications({ ...filters, _o: newOffset, _c: this.pagination.limit })
    },

    // Change page size
    async setPageSize(size, filters = {}) {
      this.pagination.limit = size
      this.pagination.offset = 0
      await this.fetchNotifications({ ...filters, _o: 0, _c: size })
    },

    // Reset pagination to first page
    resetPagination() {
      this.pagination.offset = 0
      this.pagination.currentPage = 1
      this.pagination.rangeStart = 1
      this.pagination.rangeEnd = this.pagination.limit
    },

    // Reset store
    resetStore() {
      this.notifications = []
      this.notifications_k = {}
      this.notifications_ctx = []
      this.loading = false
      this.error = null
      this.resetPagination()
    }
  }
})

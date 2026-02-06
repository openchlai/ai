// src/stores/notifications.js
import { defineStore } from 'pinia'
import axiosInstance from '@/utils/axios'
import { useTaxonomyStore } from './taxonomy'

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
    },
    actions: {
        async fetchCounts() {
            if (this.loading) return
            this.loading = true
            try {
                const activitiesStore = useActivitiesStore()
                const messagesStore = useMessagesStore()

                // Fetch limited results just to get context totals
                await Promise.all([
                    activitiesStore.listActivities({ _c: 1 }),
                    messagesStore.fetchAllMessages({ _c: 1 })
                ])

                this.activityCount = activitiesStore.paginationInfo.total
                // this.atiCount = messagesStore.paginationInfo.total // Logic might differ, keep for now

                // simulation for callCount for now
                this.callCount = 0

            } catch (err) {
                console.error('Failed to fetch notifications:', err)
            } finally {
                this.loading = false
            }
        },

        async startPolling() {
            // Temporarily disabled polling for ati/sync per user request
            /*
            if (this.isPolling) return
            this.isPolling = true
            this.poll()
            */
        },

        stopPolling() {
            this.isPolling = false
            if (this.pollingInterval) {
                clearTimeout(this.pollingInterval)
                this.pollingInterval = null
            }
        },

        async poll() {
            if (!this.isPolling) return

            try {
                const taxonomyStore = useTaxonomyStore()
                const atiHost = taxonomyStore.endpoints?.ATI_HOST || '/ati/sync'

                let targetHost = atiHost;
                // Smart Dev Proxy: Route traffic through dynamic registry paths
                if (import.meta.env.DEV) {
                    const endpoints = taxonomyStore.endpoints || {};
                    const targetDomain = endpoints.DEV_TARGET_ATI?.replace('https://', '').replace('http://', '').split(':')[0];

                    if (atiHost.includes(targetDomain) || atiHost.includes('192.168.10.3')) {
                        if (atiHost.includes(':8384/ati/sync')) targetHost = endpoints.ATI_WS_PATH || '/ati/sync';
                    }
                }

                // If it's a URL (starts with http/ws), convert to http for ajax
                let syncUrl = targetHost.replace('wss://', 'https://').replace('ws://', 'http://')

                const params = this.syncCursor !== -1 ? `${syncUrl.includes('?') ? '&' : '?'}c=${this.syncCursor}` : ''

                // Use absolute URL if it starts with http, otherwise relative to current host
                const fullUrl = syncUrl.startsWith('http') ? `${syncUrl}${params}` : `${window.location.origin}${syncUrl}${params}`

                const response = await axiosInstance.get(fullUrl, {
                    baseURL: '' // Bypass global baseURL
                })

                const data = response.data
                if (data) {
                    // Update cursor
                    if (data.c) {
                        this.syncCursor = data.c
                    }

                    // Process notifications
                    if (data.ati) {
                        this.processNotifications(data.ati)
                    }
                }
            } catch (err) {
                console.error('Notification polling error:', err)
            } finally {
                // Poll again after delay (long polling or short polling)
                // If it's long polling, the server would hold; if short, we delay.
                // Assuming standard polling for now or whatever the server supports.
                if (this.isPolling) {
                    this.pollingInterval = setTimeout(() => this.poll(), 2000)
                }
            }
        },

        processNotifications(atiData) {
            // atiData is object: { "timestamp": ["col1", ..., "base64", ...] }
            // Sort by timestamp if needed, though usually keys are unordered
            const sortedKeys = Object.keys(atiData).sort().reverse()

            sortedKeys.forEach(key => {
                const row = atiData[key]
                // Try multiple potential indices for the message payload (21 or 27)
                const base64Content = row[21] || row[27]

                if (base64Content && typeof base64Content === 'string' && base64Content.length > 4) {
                    try {
                        // Resilient decoding: clean up string and fix padding if necessary
                        const cleanBase64 = base64Content.trim().replace(/[^A-Za-z0-9+/=]/g, "");
                        const decodedString = atob(cleanBase64)
                        const payload = JSON.parse(decodedString)

                        // Add metadata
                        const notification = {
                            id: key, // Use timestamp as ID
                            timestamp: key,
                            ...payload,
                            read: false
                        }

                        // Avoid duplicates
                        if (!this.notifications.find(n => n.id === notification.id)) {
                            this.notifications.unshift(notification)
                            this.atiCount++
                        }
                    } catch (e) {
                        console.warn('Failed to decode notification:', e)
                    }
                }
            })
        },

        markAsRead(id) {
            const notif = this.notifications.find(n => n.id === id)
            if (notif && !notif.read) {
                notif.read = true
                if (this.atiCount > 0) this.atiCount--
            }
        },

        markAllAsRead() {
            this.notifications.forEach(n => n.read = true)
            this.atiCount = 0
        },

        setCallCount(count) {
            this.callCount = count
        },
        setAtiCount(count) {
            this.atiCount = count
        },
        setActivityCount(count) {
            this.activityCount = count
        },
        incrementActivity() {
            this.activityCount++
        },
        resetCounts() {
            this.callCount = 0
            this.atiCount = 0
            this.activityCount = 0
            this.notifications = []
            this.syncCursor = -1
        }

        if (readTimestamp && readTimestamp !== '0') {
          isRead = true
        }

        return {
          ...notification,
          readableDate,
          isRead
        }
      })
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

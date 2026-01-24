// stores/messages.js
import { defineStore } from 'pinia'
import axiosInstance from '@/utils/axios'
import { useAuthStore } from './auth'
import { normalizeMessages, normalizeMessage } from '@/utils/messageNormalizer'

export const useMessagesStore = defineStore('messages', {
  state: () => ({
    pmessages: [],
    pmessages_k: {},
    pmessages_ctx: [],
    loading: false,
    error: null,
    // Pagination state
    pagination: {
      offset: 0,
      limit: 20,
      currentPage: 1,
      totalRecords: 0,
      rangeStart: 1,
      rangeEnd: 20
    }
  }),

  getters: {
    messageCount: (state) => state.pmessages?.length || 0,
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

    // Normalized Data Getters
    normalizedMessages: (state) => {
      return normalizeMessages(state.pmessages, state.pmessages_k)
    },

    // Group by conversation (threadId) and filter active
    activeConversations: (state) => {
      const messages = normalizeMessages(state.pmessages, state.pmessages_k)
      const groups = new Map()

      // Group by threadId, keeping the latest message
      for (const msg of messages) {
        // Skip calling AI predictions 'conversations' in the main list if desired, 
        // strictly speaking they are messages too.

        const threadId = msg.threadId
        if (!groups.has(threadId)) {
          groups.set(threadId, msg)
        } else {
          // Assuming the list is roughly ordered, but let's check timestamps
          const existing = groups.get(threadId)
          if (new Date(msg.timestamp) > new Date(existing.timestamp)) {
            groups.set(threadId, msg)
          }
        }
      }

      // Filter closed and sort by date desc
      const active = []
      for (const msg of groups.values()) {
        if (!msg.isClosed) {
          active.push(msg)
        }
      }

      return active.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
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

    // Parse pmessages_ctx to update pagination state
    parsePaginationContext(ctx) {
      if (ctx && ctx[0] && Array.isArray(ctx[0])) {
        const [offset, limit, rangeStart, rangeEnd, total] = ctx[0]
        this.pagination.offset = parseInt(offset) || 0
        this.pagination.limit = parseInt(limit) || 20
        this.pagination.rangeStart = parseInt(rangeStart) || 1
        this.pagination.rangeEnd = parseInt(rangeEnd) || 20
        this.pagination.totalRecords = parseInt(total) || 0
        this.pagination.currentPage = Math.floor(this.pagination.offset / this.pagination.limit) + 1
      }
    },

    async fetchAllMessages(params = {}) {
      this.loading = true
      this.error = null
      try {
        // Build pagination params
        const paginationParams = {
          _c: params._c || this.pagination.limit,
          _o: params._o !== undefined ? params._o : this.pagination.offset,
          _a: 0,
          ...params
        }
        delete paginationParams.page

        const { data } = await axiosInstance.get('api/pmessages/', {
          params: paginationParams,
          headers: this.getAuthHeaders()
        })
        // console.log('[ALL] Messages:', data)
        this.pmessages = data.pmessages || []
        this.pmessages_k = data.pmessages_k || {}
        this.pmessages_ctx = data.pmessages_ctx || []

        // Parse pagination context
        this.parsePaginationContext(data.pmessages_ctx)
        return data
      } catch (err) {
        this.error = err.message
        throw err
      } finally {
        this.loading = false
      }
    },

    async fetchMessagesBySource(src, params = {}) {
      this.loading = true
      this.error = null
      try {
        // Build pagination params
        const paginationParams = {
          src,
          _c: params._c || this.pagination.limit,
          _o: params._o !== undefined ? params._o : this.pagination.offset,
          _a: 0,
          ...params
        }
        delete paginationParams.page

        const { data } = await axiosInstance.get('api/pmessages/', {
          params: paginationParams,
          headers: this.getAuthHeaders()
        })
        console.log(`[${src.toUpperCase()}] Messages:`, data)
        this.pmessages = data.pmessages || []
        this.pmessages_k = data.pmessages_k || {}
        this.pmessages_ctx = data.pmessages_ctx || []

        // Parse pagination context
        this.parsePaginationContext(data.pmessages_ctx)
        return data
      } catch (err) {
        this.error = err.message
        throw err
      } finally {
        this.loading = false
      }
    },

    async closeConversation(payload) {
      this.loading = true
      try {
        console.log('Ending conversation with payload:', payload)
        const response = await axiosInstance.post('api/messages/', payload, {
          headers: this.getAuthHeaders()
        })
        return response.data
      } catch (err) {
        console.error('Error ending conversation:', err)
        throw err
      } finally {
        this.loading = false
      }
    },

    async sendMessage(payload) {
      // this.loading = true // Don't block whole UI for sending
      try {
        console.log('Sending message:', payload)
        const response = await axiosInstance.post('api/messages/', payload, {
          headers: this.getAuthHeaders()
        })
        return response.data
      } catch (err) {
        console.error('Error sending message:', err)
        throw err
      }
    },

    async fetchConversationHistory(src, callId) {
      if (!src || !callId) return

      try {
        const { data } = await axiosInstance.get('api/messages/', {
          params: {
            src: src,
            src_callid: callId
          },
          headers: this.getAuthHeaders()
        })
        // Parse both array format (pmessages) and object list (messages) if API varies
        const rawParams = data.pmessages_k || data.messages_k || {}
        let history = []

        if (data.pmessages && Array.isArray(data.pmessages)) {
          history = normalizeMessages(data.pmessages, data.pmessages_k)
        } else if (data.messages && Array.isArray(data.messages)) {
          // Normalizes list of arrays using the messages_k schema
          history = normalizeMessages(data.messages, data.messages_k)
        }

        return history
      } catch (err) {
        console.error('Error fetching conversation history:', err)
        return []
      }
    },

    // Go to next page
    async nextPage(filters = {}) {
      if (!this.hasNextPage) return
      const newOffset = this.pagination.offset + this.pagination.limit
      if (filters.src && filters.src !== 'all') {
        await this.fetchMessagesBySource(filters.src, { _o: newOffset, _c: this.pagination.limit })
      } else {
        await this.fetchAllMessages({ ...filters, _o: newOffset, _c: this.pagination.limit })
      }
    },

    // Go to previous page
    async prevPage(filters = {}) {
      if (!this.hasPrevPage) return
      const newOffset = Math.max(0, this.pagination.offset - this.pagination.limit)
      if (filters.src && filters.src !== 'all') {
        await this.fetchMessagesBySource(filters.src, { _o: newOffset, _c: this.pagination.limit })
      } else {
        await this.fetchAllMessages({ ...filters, _o: newOffset, _c: this.pagination.limit })
      }
    },

    // Go to specific page
    async goToPage(page, filters = {}) {
      const newOffset = (page - 1) * this.pagination.limit
      if (filters.src && filters.src !== 'all') {
        await this.fetchMessagesBySource(filters.src, { _o: newOffset, _c: this.pagination.limit })
      } else {
        await this.fetchAllMessages({ ...filters, _o: newOffset, _c: this.pagination.limit })
      }
    },

    // Change page size
    async setPageSize(size, filters = {}) {
      this.pagination.limit = size
      this.pagination.offset = 0
      if (filters.src && filters.src !== 'all') {
        await this.fetchMessagesBySource(filters.src, { _o: 0, _c: size })
      } else {
        await this.fetchAllMessages({ ...filters, _o: 0, _c: size })
      }
    },

    // Reset pagination to first page
    resetPagination() {
      this.pagination.offset = 0
      this.pagination.currentPage = 1
      this.pagination.rangeStart = 1
      this.pagination.rangeEnd = this.pagination.limit
    }
  }
})
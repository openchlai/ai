// src/stores/activitiesStore.js
import { defineStore } from 'pinia'
import axiosInstance from '@/utils/axios'
import { useAuthStore } from './auth'

export const useActivitiesStore = defineStore('activitiesStore', {
  state: () => ({
    activities: [],      // array of activities (raw array format)
    activities_k: {},    // metadata keys
    activities_ctx: [],  // context (pagination etc.)
    raw: {},             // full API response
    loading: false,
    error: null
  }),

  getters: {
    activityCount: (state) => state.activities?.length ?? 0,

    // Get activity by ID
    getActivityById: (state) => (id) => {
      const index = parseInt(state.activities_k?.id?.[0] ?? 0)
      return state.activities.find(activity => activity[index] === id) || null
    },

    // Get activities by case ID
    getActivitiesByCaseId: (state) => (caseId) => {
      const caseIdIndex = parseInt(state.activities_k?.case_id?.[0] ?? -1)
      if (caseIdIndex === -1) return []
      return state.activities.filter(activity => activity[caseIdIndex] === caseId)
    },

    // Get activities by action type
    getActivitiesByAction: (state) => (action) => {
      const actionIndex = parseInt(state.activities_k?.action?.[0] ?? -1)
      if (actionIndex === -1) return []
      return state.activities.filter(activity => activity[actionIndex] === action)
    },

    // Getter to return activities with formatted timestamps
    formattedActivities: (state) => {
      const createdOnIndex = parseInt(state.activities_k?.created_on?.[0] ?? -1)
      if (createdOnIndex === -1) return []

      return state.activities.map(activity => {
        const timestamp = activity[createdOnIndex]
        let readableDate = ''
        if (timestamp) {
          const dateObj = new Date(Number(timestamp) * 1000)
          readableDate = dateObj.toLocaleString()
        }
        return {
          ...activity,
          readableDate
        }
      })
    },

    // Helper to map single activity array to object
    mapActivityToObject: (state) => (activityArray) => {
      const obj = {}
      for (const [fieldName, fieldInfo] of Object.entries(state.activities_k)) {
        const index = fieldInfo[0]
        obj[fieldName] = activityArray[index] || ''
      }
      return obj
    },

    // Get all activities as objects
    activitiesAsObjects: (state) => {
      return state.activities.map(activityArray => {
        const obj = {}
        for (const [fieldName, fieldInfo] of Object.entries(state.activities_k)) {
          const index = fieldInfo[0]
          obj[fieldName] = activityArray[index] || ''
        }
        return obj
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

    // 1. List Activities
    async listActivities(params = {}) {
      this.loading = true
      this.error = null

      try {
        const { data } = await axiosInstance.get('api/activities/', {
          params,
          headers: this.getAuthHeaders()
        })
        
        console.log('API Response:', data)
        this.raw = data
        this.activities = data.activities || []
        this.activities_k = data.activities_k || {}
        this.activities_ctx = data.activities_ctx || []
        
      } catch (err) {
        this.error = err.message || 'Request failed'
      } finally {
        this.loading = false
      }
    },

    // 2. View Activity
    async viewActivity(id) {
      try {
        const { data } = await axiosInstance.get(`api/activities/${id}`, {
          headers: this.getAuthHeaders()
        })
        return data
      } catch (err) {
        throw new Error(err.message || 'Failed to view activity')
      }
    },

    // 3. CSV Download
    async downloadCSV(params = {}) {
      try {
        const response = await axiosInstance.get('api/activities/', {
          params: { ...params, csv: 1 },
          headers: this.getAuthHeaders(),
          responseType: 'blob'
        })
        return response.data
      } catch (err) {
        throw new Error(err.message || 'Failed to download CSV')
      }
    },

    // 4. Pivot Reports
    async getPivotReport(params = {}) {
      try {
        const { data } = await axiosInstance.get('api/activities/rpt', {
          params,
          headers: this.getAuthHeaders()
        })
        return data
      } catch (err) {
        throw new Error(err.message || 'Failed to fetch pivot report')
      }
    },

    // Reset store
    resetStore() {
      this.activities = []
      this.activities_k = {}
      this.activities_ctx = []
      this.raw = {}
      this.loading = false
      this.error = null
    }
  }
})
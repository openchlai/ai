// stores/notifications.js
import { defineStore } from 'pinia'
import { useActivitiesStore } from './activities'
import { useMessagesStore } from './messages'

export const useNotificationsStore = defineStore('notifications', {
    state: () => ({
        callCount: 0,
        atiCount: 0,
        activityCount: 0,
        loading: false
    }),
    getters: {
        totalCount: (state) => state.callCount + state.atiCount + state.activityCount
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
                this.atiCount = messagesStore.paginationInfo.total

                // simulation for callCount for now
                this.callCount = 0

            } catch (err) {
                console.error('Failed to fetch notifications:', err)
            } finally {
                this.loading = false
            }
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
        }
    }
})

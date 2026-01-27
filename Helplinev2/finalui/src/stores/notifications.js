import { defineStore } from 'pinia'
import { useActivitiesStore } from './activities'
import { useMessagesStore } from './messages'
import axiosInstance from '@/utils/axios'

export const useNotificationsStore = defineStore('notifications', {
    state: () => ({
        callCount: 0,
        atiCount: 0,
        activityCount: 0,
        loading: false,
        notifications: [],
        syncCursor: -1,
        isPolling: false,
        pollingInterval: null
    }),
    getters: {
        totalCount: (state) => state.callCount + state.atiCount + state.activityCount,
        allNotifications: (state) => state.notifications
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
            if (this.isPolling) return
            this.isPolling = true
            this.poll()
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
                // Using fetch directly or axios instance if we configured proxy
                // Since we added /ati proxy, we can use /ati/sync
                // We must bypass the default baseURL (/api-proxy) to hit the /ati proxy rule
                const response = await axiosInstance.get(`/ati/sync?c=${this.syncCursor}`, {
                    baseURL: '/'
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
                // Index 27 is the base64 content based on analysis
                const base64Content = row[27]

                if (base64Content && typeof base64Content === 'string' && base64Content.startsWith('ey')) {
                    try {
                        const decodedString = atob(base64Content)
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
    }
})

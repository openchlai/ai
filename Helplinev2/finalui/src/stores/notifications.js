import { defineStore } from 'pinia'
import { useActivitiesStore } from './activities'
import { useMessagesStore } from './messages'
import axiosInstance from '@/utils/axios'
import { useTaxonomyStore } from './taxonomy'

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
    }
})

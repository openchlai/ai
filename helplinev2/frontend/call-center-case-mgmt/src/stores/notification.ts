import { defineStore } from 'pinia'

export const useNotificationStore = defineStore('notification', {
  actions: {
    success(message: string) {
      // Implement notification logic here
      console.log('Success:', message)
    },
    error(message: string) {
      // Implement notification logic here
      console.error('Error:', message)
    }
  }
}) 
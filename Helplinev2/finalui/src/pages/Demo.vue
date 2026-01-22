<template>
  <div class="min-h-screen bg-gray-100 dark:bg-gray-900 flex items-center justify-center p-4">
    <div class="max-w-md w-full bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-6 text-center">
        Password Reset Test
      </h1>

      <!-- User ID Input -->
      <div class="mb-6">
        <label for="userId" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          User ID
        </label>
        <input
          id="userId"
          v-model="userId"
          type="text"
          placeholder="Enter user ID (e.g., 1000031)"
          class="w-full px-4 py-2 border border-transparent dark:border-transparent rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
        />
      </div>

      <!-- Reset Button -->
      <button
        @click="resetPassword"
        :disabled="loading || !userId"
        class="w-full bg-amber-600 hover:bg-amber-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-semibold py-3 px-4 rounded-lg transition-colors duration-200"
      >
        <span v-if="!loading">Reset Password</span>
        <span v-else class="flex items-center justify-center">
          <svg class="animate-spin h-5 w-5 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Resetting...
        </span>
      </button>

      <!-- Response Display -->
      <div v-if="response" class="mt-6">
        <div 
          :class="[
            'p-4 rounded-lg',
            response.success ? 'bg-green-100 dark:bg-green-900 border border-green-400 dark:border-green-600' : 'bg-red-100 dark:bg-red-900 border border-red-400 dark:border-red-600'
          ]"
        >
          <h3 
            :class="[
              'font-semibold mb-2',
              response.success ? 'text-green-800 dark:text-green-200' : 'text-red-800 dark:text-red-200'
            ]"
          >
            {{ response.success ? '✅ Success' : '❌ Error' }}
          </h3>
          <p 
            :class="[
              'text-sm',
              response.success ? 'text-green-700 dark:text-green-300' : 'text-red-700 dark:text-red-300'
            ]"
          >
            {{ response.message }}
          </p>
          
          <!-- Display full response data -->
          <details class="mt-3">
            <summary class="cursor-pointer text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">
              View Full Response
            </summary>
            <pre class="mt-2 p-3 bg-gray-50 dark:bg-gray-950 rounded text-xs overflow-auto max-h-64 text-gray-800 dark:text-gray-200">{{ JSON.stringify(response.data, null, 2) }}</pre>
          </details>
        </div>
      </div>

      <!-- Request Details -->
      <div class="mt-6 p-4 bg-gray-50 dark:bg-gray-900 rounded-lg border border-transparent dark:border-transparent">
        <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
          Endpoint Details
        </h3>
        <div class="text-xs text-gray-600 dark:text-gray-400 space-y-1">
          <p><strong>Method:</strong> POST</p>
          <p><strong>URL:</strong> /api/resetAuth/{{ userId || '{userId}' }}</p>
          <p><strong>Payload:</strong> {{ `{ ".id": "${userId || '{userId}'}" }` }}</p>
          <p><strong>Expected Status:</strong> 202 Accepted</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axiosInstance from '@/utils/axios'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const userId = ref('1000031')
const loading = ref(false)
const response = ref(null)

const resetPassword = async () => {
  if (!userId.value) {
    response.value = {
      success: false,
      message: 'Please enter a user ID',
      data: null
    }
    return
  }

  loading.value = true
  response.value = null

  try {
    console.log('🔄 Resetting password for user:', userId.value)
    console.log('📤 Request URL:', `api/resetAuth/${userId.value}`)
    console.log('📤 Request Payload:', { '.id': userId.value })

    const { data, status } = await axiosInstance.post(
      `api/resetAuth/${userId.value}`,
      { '.id': userId.value },
      {
        headers: {
          'Session-Id': authStore.sessionId,
          'Content-Type': 'application/json'
        }
      }
    )

    console.log('✅ Response Status:', status)
    console.log('✅ Response Data:', data)

    response.value = {
      success: true,
      message: `Password reset successful! Status: ${status}`,
      data: {
        status,
        response: data
      }
    }
  } catch (error) {
    console.error('❌ Password reset failed:', error)
    console.error('❌ Error response:', error.response)

    response.value = {
      success: false,
      message: error.response?.data?.message || error.message || 'Password reset failed',
      data: {
        status: error.response?.status,
        error: error.response?.data || error.message
      }
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* Add any additional styles if needed */
</style>
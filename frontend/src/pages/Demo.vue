<template>
  <div class="flex min-h-screen bg-white">
    <!-- Left Section -->
    <div class="flex-1 flex flex-col justify-center items-center p-10">
      <h1 class="text-4xl font-bold mb-2">Hello,</h1>
      <h2 class="text-4xl font-bold mb-8">Welcome back!</h2>
    </div>

    <!-- Right Section -->
    <div class="flex-1 flex justify-center items-center bg-black">
      <div class="w-80 bg-black p-8 rounded-lg shadow-lg">
        <h2 class="text-white text-3xl font-bold mb-6">Log in</h2>

        <form @submit.prevent="handleLogin">
          <div class="mb-4">
            <label class="text-white block mb-1">Username</label>
            <input
              v-model="username"
              type="text"
              class="w-full p-2 rounded bg-gray-200"
              placeholder="Enter username (ignored)"
            />
          </div>

          <div class="mb-4">
            <label class="text-white block mb-1">Password</label>
            <input
              v-model="password"
              type="password"
              class="w-full p-2 rounded bg-gray-200"
              placeholder="Enter password (ignored)"
            />
          </div>

          <button
            type="submit"
            class="w-full bg-yellow-500 hover:bg-yellow-600 text-black font-semibold py-2 rounded transition"
            :disabled="loading"
          >
            {{ loading ? 'Testing...' : 'Test Login' }}
          </button>

          <p v-if="error" class="text-red-400 text-sm mt-4">{{ error }}</p>
          <p v-if="success" class="text-green-400 text-sm mt-4">{{ success }}</p>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref(null)
const success = ref(null)

// ✅ Configuration identical to your axiosInstance logic
const axiosInstance = axios.create({
  baseURL:
    import.meta.env.MODE === 'development'
      ? '/api-proxy'
      : 'https://demo-openchs.bitz-itc.com/helpline/',
  timeout: 10000,
  auth: {
    username: 'test',
    password: 'p@ssw0rd'
  },
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})


const handleLogin = async () => {
  loading.value = true
  error.value = null
  success.value = null

  try {
    // ✅ Matches the working curl request
    const response = await axiosInstance.post('/api/',  {
      headers: {
        Authorization: 'Basic dGVzdDpwQHNzdzByZA=='
      }
    })

    console.log('✅ Response:', response.data)

    const sessionId = response.data?.ss?.[0]?.[0]
    if (!sessionId) throw new Error('No session ID returned')

    localStorage.setItem('session-id', sessionId)
    success.value = `✅ Login successful! Session ID: ${sessionId}`
  } catch (err) {
    console.error('❌ Error:', err)
    error.value =
      err.response?.data?.errors?.[0]?.[1] ||
      err.message ||
      'Login failed'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
input:focus {
  outline: 2px solid #fbbf24;
}
</style>

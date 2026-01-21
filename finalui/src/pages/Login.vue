<template>
  <div class="flex min-h-screen bg-white">
    <!-- Left Section -->
    <div class="flex-1 flex flex-col justify-center items-center p-10">
      <h1 class="text-4xl font-bold mb-2 text-gray-800">Hello,</h1>
      <h2 class="text-4xl font-bold mb-8 text-gray-800">Welcome back!</h2>
    </div>

    <!-- Right Section -->
    <div class="flex-1 flex justify-center items-center bg-black">
      <div class="w-80 bg-black p-8 rounded-lg shadow-lg">
        <h2 class="text-white text-3xl font-bold mb-6 text-center">
          Log in
        </h2>

        <form @submit.prevent="handleLogin" class="space-y-4">
          <div>
            <label class="text-white block mb-1">Username</label>
            <input
              v-model="username"
              type="text"
              placeholder="Enter username"
              class="w-full p-2 rounded bg-gray-200 focus:outline-none focus:ring-2 focus:ring-yellow-500"
            />
          </div>

          <div>
            <label class="text-white block mb-1">Password</label>
            <input
              v-model="password"
              type="password"
              placeholder="Enter password"
              class="w-full p-2 rounded bg-gray-200 focus:outline-none focus:ring-2 focus:ring-yellow-500"
            />
          </div>

          <button
            type="submit"
            class="w-full bg-yellow-500 hover:bg-yellow-600 text-black font-semibold py-2 rounded transition"
            :disabled="auth.loading"
          >
            {{ auth.loading ? 'Logging in...' : 'Login' }}
          </button>

          <p v-if="auth.error" class="text-red-400 text-sm mt-4 text-center">
            {{ auth.error }}
          </p>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const username = ref('')
const password = ref('')
const router = useRouter()
const auth = useAuthStore()

const handleLogin = async () => {
  const success = await auth.login(username.value, password.value)
  if (success) {
    router.push('/')
  }
}
</script>

<template>
  <div class="flex min-h-screen bg-white">
    <!-- Left Section - Welcome -->
    <div class="flex-1 flex flex-col justify-center items-center p-10 bg-white">
      <!-- Logo -->
      <div class="mb-8">
        <img src="@/assets/images/coat of arms.png" alt="Kenya Coat of Arms" class="w-32 h-32 object-contain" />
      </div>
      
      <h1 class="text-5xl font-bold mb-2 text-gray-800">Hello,</h1>
      <h2 class="text-5xl font-bold mb-12 text-gray-800">Welcome back!</h2>
      
      <!-- Partners Section -->
      <div class="mt-auto pt-8">
        <p class="text-sm text-gray-600 font-semibold mb-4 text-center">Our Partners</p>
        <div class="flex gap-6 items-center justify-center flex-wrap max-w-md">
          <img src="@/assets/images/welcome-helpline.png" alt="Childline Kenya" class="h-10 w-auto object-contain" />
          <img src="@/assets/images/MOH.png" alt="Ministry of Health" class="h-10 w-auto object-contain" />
          <img src="@/assets/images/unicef.png" alt="UNICEF" class="h-10 w-auto object-contain" />
          <img src="@/assets/images/GIZ.png" alt="GIZ" class="h-10 w-auto object-contain" />
          <img src="@/assets/images/UNFPA.png" alt="UNFPA" class="h-10 w-auto object-contain" />
        </div>
      </div>
    </div>

    <!-- Right Section - Login Form -->
    <div class="flex-1 flex justify-center items-center bg-black">
      <div class="w-96 bg-black p-10 rounded-2xl shadow-2xl">
        <h2 class="text-white text-4xl font-bold mb-8 text-center">
          Log in
        </h2>

        <form @submit.prevent="handleLogin" class="space-y-6">
          <div>
            <label class="text-white block mb-2 font-medium">Username</label>
            <input
              v-model="username"
              type="text"
              placeholder="Enter username"
              class="w-full p-3 rounded-xl bg-gray-200 text-gray-800 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-yellow-500 transition"
              :disabled="auth.loading"
              required
            />
          </div>

          <div>
            <label class="text-white block mb-2 font-medium">Password</label>
            <input
              v-model="password"
              type="password"
              placeholder="Enter password"
              class="w-full p-3 rounded-xl bg-gray-200 text-gray-800 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-yellow-500 transition"
              :disabled="auth.loading"
              required
            />
          </div>

          <button
            type="submit"
            class="w-full bg-yellow-500 hover:bg-yellow-600 text-black font-bold py-3 rounded-xl transition transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
            :disabled="auth.loading || !username || !password"
          >
            {{ auth.loading ? 'Logging in...' : 'Login' }}
          </button>

          <p v-if="auth.error" class="text-red-400 text-sm mt-4 text-center bg-red-900/20 p-3 rounded-lg">
            {{ auth.error }}
          </p>
        </form>

        <!-- Additional Links -->
        <div class="mt-6 text-center">
          <a 
            @click.prevent="handleForgotPassword" 
            href="#" 
            class="text-yellow-500 hover:text-yellow-400 text-sm font-medium cursor-pointer"
          >
            Forgot password?
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { useAuthStore } from '@/stores/auth'

const username = ref('')
const password = ref('')
const router = useRouter()
const auth = useAuthStore()

const handleLogin = async () => {
  if (!username.value || !password.value) {
    auth.error = 'Please enter both username and password'
    return
  }

  const success = await auth.login(username.value, password.value)
  if (success) {
    router.push('/')
  }
}

const handleForgotPassword = () => {
  toast.info('Forgot Password feature is not yet available')
}
</script>
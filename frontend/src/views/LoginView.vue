<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { validatePassword } from '@/utils/validation'

const authStore = useAuthStore()
const router = useRouter()

const isLoginMode = ref(true)
const email = ref('')
const password = ref('')
const fullName = ref('')
const isLoading = ref(false)

const handleLogin = async () => {
  if (!email.value || !password.value) return
  
  isLoading.value = true
  const success = await authStore.login(email.value, password.value)
  
  if (success) {
    router.push('/dashboard')
  }
  isLoading.value = false
}

const handleRegister = async () => {
  if (!email.value || !password.value || !fullName.value) return
  
  const passwordValidation = validatePassword(password.value)
  if (!passwordValidation.isValid) {
    authStore.error = passwordValidation.errors[0]
    return
  }
  
  isLoading.value = true
  const success = await authStore.register(email.value, password.value, fullName.value)
  
  if (success) {
    router.push('/dashboard')
  }
  isLoading.value = false
}

const handleSubmit = () => {
  if (isLoginMode.value) {
    handleLogin()
  } else {
    handleRegister()
  }
}

const toggleMode = () => {
  isLoginMode.value = !isLoginMode.value
  email.value = ''
  password.value = ''
  fullName.value = ''
  authStore.error = null
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          {{ isLoginMode ? 'Sign in to your account' : 'Create your account' }}
        </h2>
      </div>
      
      <form class="mt-8 space-y-6" @submit.prevent="handleSubmit">
        <div class="rounded-md shadow-sm -space-y-px">
          <!-- Full Name field (only for registration) -->
          <div v-if="!isLoginMode">
            <label for="full-name" class="sr-only">Full Name</label>
            <input
              id="full-name"
              v-model="fullName"
              name="fullName"
              type="text"
              autocomplete="name"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              placeholder="Full Name"
            />
          </div>
          
          <div>
            <label for="email-address" class="sr-only">Email address</label>
            <input
              id="email-address"
              v-model="email"
              name="email"
              type="email"
              autocomplete="email"
              required
              :class="[
                'appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm',
                isLoginMode ? 'rounded-t-md' : ''
              ]"
              placeholder="Email address"
            />
          </div>
          <div>
            <label for="password" class="sr-only">Password</label>
            <input
              id="password"
              v-model="password"
              name="password"
              type="password"
              :autocomplete="isLoginMode ? 'current-password' : 'new-password'"
              required
              :minlength="isLoginMode ? undefined : 8"
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              :placeholder="isLoginMode ? 'Password' : 'Password (8+ characters, must include number)'"
            />
          </div>
        </div>

        <div v-if="authStore.error" class="text-red-600 text-sm text-center">
          {{ authStore.error }}
        </div>

        <div>
          <button
            type="submit"
            :disabled="isLoading || !email || !password || (!isLoginMode && !fullName)"
            class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="isLoading">
              {{ isLoginMode ? 'Signing in...' : 'Creating account...' }}
            </span>
            <span v-else>
              {{ isLoginMode ? 'Sign in' : 'Create account' }}
            </span>
          </button>
        </div>

        <!-- Toggle between login and register -->
        <div class="text-center">
          <button
            type="button"
            @click="toggleMode"
            class="text-indigo-600 hover:text-indigo-500 text-sm font-medium"
          >
            {{ isLoginMode ? "Don't have an account? Sign up" : "Already have an account? Sign in" }}
          </button>
        </div>

      
      </form>
    </div>
  </div>
</template> 
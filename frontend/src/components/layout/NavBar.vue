<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <nav class="bg-white shadow-sm border-b border-gray-200">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <h1 class="text-xl font-semibold text-gray-900">Task Manager</h1>
          </div>
        </div>
        
        <div class="flex items-center space-x-4">
          <template v-if="authStore.isAuthenticated">
            <!-- Authenticated user menu -->
            <div class="flex items-center space-x-4">
              <span class="text-sm text-gray-700">
                Welcome, {{ authStore.user?.full_name || authStore.user?.email }}
              </span>
              <button
                @click="handleLogout"
                class="bg-red-600 hover:bg-red-700 text-white px-3 py-2 rounded-md text-sm font-medium"
              >
                Logout
              </button>
            </div>
          </template>
          
          <template v-else>
            <!-- Not authenticated -->
            <router-link
              to="/login"
              class="bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-2 rounded-md text-sm font-medium"
            >
              Login
            </router-link>
          </template>
        </div>
      </div>
    </div>
  </nav>
</template> 
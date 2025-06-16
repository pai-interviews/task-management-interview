<script setup lang="ts">
interface Props {
  open: boolean
  title: string
  message: string
  isDeleting?: boolean
}

interface Emits {
  (e: 'close'): void
  (e: 'confirm'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const handleClose = () => {
  if (!props.isDeleting) {
    emit('close')
  }
}

const handleConfirm = () => {
  emit('confirm')
}
</script>

<template>
  <div v-if="open" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
    <div class="bg-white rounded p-6 w-full max-w-sm">
      <h3 class="text-lg font-semibold mb-4 text-red-600">{{ title }}</h3>
      
      <p class="text-gray-700 mb-6">{{ message }}</p>
      
      <div class="flex gap-2">
        <button
          @click="handleConfirm"
          class="flex-1 bg-red-500 text-white px-4 py-2 rounded disabled:opacity-50"
          :disabled="isDeleting"
        >
          {{ isDeleting ? 'Deleting...' : 'Delete' }}
        </button>
        <button
          @click="handleClose"
          class="flex-1 bg-gray-500 text-white px-4 py-2 rounded disabled:opacity-50"
          :disabled="isDeleting"
        >
          Cancel
        </button>
      </div>
    </div>
  </div>
</template> 
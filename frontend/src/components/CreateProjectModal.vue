<script setup lang="ts">
import { ref, watch } from 'vue'
import { useProjectStore } from '@/stores/projects'

interface Props {
  open: boolean
}

interface Emits {
  (e: 'close'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const projectStore = useProjectStore()

const formData = ref({
  name: '',
  description: ''
})

const isSubmitting = ref(false)

// Reset form when modal closes
watch(() => props.open, (newVal) => {
  if (!newVal) {
    resetForm()
  }
})

const resetForm = () => {
  formData.value = {
    name: '',
    description: ''
  }
  isSubmitting.value = false
}

const handleSubmit = async () => {
  if (!formData.value.name.trim()) return
  
  isSubmitting.value = true
  
  try {
    await projectStore.createProject({
      name: formData.value.name.trim(),
      description: formData.value.description.trim() || undefined
    })
    
    emit('close')
    resetForm()
  } catch (error) {
    console.error('Failed to create project:', error)
  } finally {
    isSubmitting.value = false
  }
}

const handleClose = () => {
  if (!isSubmitting.value) {
    emit('close')
  }
}
</script>

<template>
  <div v-if="open" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
    <div class="bg-white rounded p-6 w-full max-w-md">
      <h3 class="text-lg font-semibold mb-4">Create New Project</h3>
      
      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div>
          <label class="block text-sm font-medium mb-1">Project Name *</label>
          <input
            v-model="formData.name"
            type="text"
            class="w-full border rounded px-3 py-2"
            placeholder="Enter project name"
            required
            :disabled="isSubmitting"
          />
        </div>

        <div>
          <label class="block text-sm font-medium mb-1">Description</label>
          <textarea
            v-model="formData.description"
            rows="3"
            class="w-full border rounded px-3 py-2"
            placeholder="Enter project description (optional)"
            :disabled="isSubmitting"
          ></textarea>
        </div>

        <div class="flex gap-2 pt-4">
          <button
            type="submit"
            class="bg-blue-500 text-white px-4 py-2 rounded"
            :disabled="isSubmitting || !formData.name.trim()"
          >
            {{ isSubmitting ? 'Creating...' : 'Create' }}
          </button>
          <button
            type="button"
            @click="handleClose"
            class="bg-gray-300 px-4 py-2 rounded"
            :disabled="isSubmitting"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  </div>
</template> 
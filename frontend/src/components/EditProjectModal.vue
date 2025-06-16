<script setup lang="ts">
import { ref, watch } from 'vue'
import { useProjectStore, type Project } from '@/stores/projects'

interface Props {
  open: boolean
  project: Project | null
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

// Watch for project changes to populate form
watch(() => props.project, (newProject) => {
  if (newProject) {
    formData.value = {
      name: newProject.name,
      description: newProject.description || ''
    }
  }
}, { immediate: true })

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
  if (!formData.value.name.trim() || !props.project) return
  
  isSubmitting.value = true
  
  try {
    await projectStore.updateProject(props.project.id, {
      name: formData.value.name.trim(),
      description: formData.value.description.trim() || undefined
    })
    
    emit('close')
    resetForm()
  } catch (error) {
    console.error('Failed to update project:', error)
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
      <h3 class="text-lg font-semibold mb-4">Edit Project</h3>
      
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

        <div class="flex gap-2">
          <button
            type="submit"
            class="flex-1 bg-blue-500 text-white px-4 py-2 rounded disabled:opacity-50"
            :disabled="isSubmitting"
          >
            {{ isSubmitting ? 'Updating...' : 'Update Project' }}
          </button>
          <button
            type="button"
            @click="handleClose"
            class="flex-1 bg-gray-500 text-white px-4 py-2 rounded disabled:opacity-50"
            :disabled="isSubmitting"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  </div>
</template> 
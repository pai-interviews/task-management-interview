<script setup lang="ts">
import { ref, watch, onMounted, computed } from 'vue'
import { useTaskStore, type Task } from '@/stores/tasks'
import { useProjectStore } from '@/stores/projects'
import apiClient from '@/api/client'

interface Props {
  open: boolean
  task: Task | null
}

interface Emits {
  (e: 'close'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const taskStore = useTaskStore()
const projectStore = useProjectStore()

const formData = ref({
  title: '',
  description: '',
  status: 'todo',
  priority: 1,
  due_date: '',
  project_id: 0,
  assignee_id: null
})

const isSubmitting = ref(false)

const statusOptions = [
  { value: 'todo', label: 'To Do' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'done', label: 'Done' }
]

const priorityOptions = [
  { value: 1, label: 'Low' },
  { value: 2, label: 'Medium' },
  { value: 3, label: 'High' },
  { value: 4, label: 'Critical' }
]

const availableProjects = computed(() => projectStore.projects)
const availableUsers = ref<Array<{id: number, email: string, full_name?: string}>>([])

// Load projects and users when component mounts
onMounted(async () => {
  try {
    if (availableProjects.value.length === 0) {
      await projectStore.fetchProjects()
    }
    
    const response = await apiClient.get('/api/v1/users')
    availableUsers.value = response.data
  } catch (error) {
    console.error('Failed to load data:', error)
  }
})

// Watch for task changes to populate form
watch(() => props.task, (newTask) => {
  if (newTask) {
    formData.value = {
      title: newTask.title,
      description: newTask.description || '',
      status: newTask.status,
      priority: newTask.priority || 1,
      due_date: newTask.due_date ? newTask.due_date.split('T')[0] : '', // Format for date input
      project_id: newTask.project_id,
      assignee_id: newTask.assignee_id
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
    title: '',
    description: '',
    status: 'todo',
    priority: 1,
    due_date: '',
    project_id: 0,
    assignee_id: null
  }
  isSubmitting.value = false
}

const handleSubmit = async () => {
  if (!formData.value.title.trim() || !props.task) return
  
  isSubmitting.value = true
  
  try {
    const taskData = {
      title: formData.value.title.trim(),
      description: formData.value.description.trim() || undefined,
      status: formData.value.status,
      priority: formData.value.priority,
      due_date: formData.value.due_date || undefined,
      project_id: formData.value.project_id,
      assignee_id: formData.value.assignee_id
    }
    
    await taskStore.updateTask(props.task.id, taskData)
    
    emit('close')
    resetForm()
  } catch (error) {
    console.error('Failed to update task:', error)
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
    <div class="bg-white rounded p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
      <h3 class="text-lg font-semibold mb-4">Edit Task</h3>
      
      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div>
          <label class="block text-sm font-medium mb-1">Task Title *</label>
          <input
            v-model="formData.title"
            type="text"
            class="w-full border rounded px-3 py-2"
            placeholder="Enter task title"
            required
            :disabled="isSubmitting"
          />
        </div>

        <div>
          <label class="block text-sm font-medium mb-1">Project *</label>
          <select
            v-model="formData.project_id"
            class="w-full border rounded px-3 py-2"
            required
            :disabled="isSubmitting"
          >
            <option value="0">Select a project</option>
            <option v-for="project in availableProjects" :key="project.id" :value="project.id">
              {{ project.name }}
            </option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium mb-1">Assignee</label>
          <select
            v-model="formData.assignee_id"
            class="w-full border rounded px-3 py-2"
            :disabled="isSubmitting"
          >
            <option :value="null">Unassigned</option>
            <option v-for="user in availableUsers" :key="user.id" :value="user.id">
              {{ user.full_name || user.email }}
            </option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium mb-1">Description</label>
          <textarea
            v-model="formData.description"
            rows="3"
            class="w-full border rounded px-3 py-2"
            placeholder="Enter task description (optional)"
            :disabled="isSubmitting"
          ></textarea>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium mb-1">Status</label>
            <select
              v-model="formData.status"
              class="w-full border rounded px-3 py-2"
              :disabled="isSubmitting"
            >
              <option v-for="status in statusOptions" :key="status.value" :value="status.value">
                {{ status.label }}
              </option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium mb-1">Priority</label>
            <select
              v-model="formData.priority"
              class="w-full border rounded px-3 py-2"
              :disabled="isSubmitting"
            >
              <option v-for="priority in priorityOptions" :key="priority.value" :value="priority.value">
                {{ priority.label }}
              </option>
            </select>
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium mb-1">Due Date</label>
          <input
            v-model="formData.due_date"
            type="date"
            class="w-full border rounded px-3 py-2"
            :disabled="isSubmitting"
          />
        </div>

        <div class="flex gap-2">
          <button
            type="submit"
            class="flex-1 bg-blue-500 text-white px-4 py-2 rounded disabled:opacity-50"
            :disabled="isSubmitting"
          >
            {{ isSubmitting ? 'Updating...' : 'Update Task' }}
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
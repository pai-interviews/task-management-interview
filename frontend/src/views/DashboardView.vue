<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { useProjectStore, type Project } from '@/stores/projects'
import { useTaskStore, type Task } from '@/stores/tasks'
import { onMounted, ref, computed } from 'vue'
import CreateProjectModal from '@/components/CreateProjectModal.vue'
import CreateTaskModal from '@/components/CreateTaskModal.vue'
import EditProjectModal from '@/components/EditProjectModal.vue'
import EditTaskModal from '@/components/EditTaskModal.vue'
import DeleteConfirmModal from '@/components/DeleteConfirmModal.vue'

const projectStore = useProjectStore()
const taskStore = useTaskStore()

const showCreateProjectModal = ref(false)
const showCreateTaskModal = ref(false)
const showEditProjectModal = ref(false)
const showEditTaskModal = ref(false)
const showDeleteModal = ref(false)
const selectedProjectId = ref<number | null>(null)
const editingProject = ref<Project | null>(null)
const editingTask = ref<Task | null>(null)
const deletingItem = ref<{type: 'project' | 'task', id: number, name: string} | null>(null)
const isDeleting = ref(false)

// Computed stats
const totalProjects = computed(() => projectStore.projects.length)
const totalTasks = computed(() => taskStore.tasks.length)
const pendingTasks = computed(() => 
  taskStore.tasks.filter(task => task.status === 'todo' || task.status === 'in_progress').length
)

// Load initial data
onMounted(async () => {
  try {
    await Promise.all([
      projectStore.fetchProjects(),
      taskStore.fetchTasks()
    ])
  } catch (error) {
    console.error('Failed to load dashboard data:', error)
  }
})

const openCreateProjectModal = () => {
  showCreateProjectModal.value = true
}

const openCreateTaskModal = () => {
  showCreateTaskModal.value = true
}

const selectProject = async (projectId: number) => {
  selectedProjectId.value = projectId
  // Fetch tasks for the selected project
  try {
    await taskStore.fetchTasks({ project_id: projectId })
  } catch (error) {
    console.error('Failed to load project tasks:', error)
  }
}

const backToProjects = () => {
  selectedProjectId.value = null
}

// Computed values for selected project
const selectedProject = computed(() => 
  projectStore.projects.find(p => p.id === selectedProjectId.value)
)

const projectTasks = computed(() => 
  selectedProjectId.value 
    ? taskStore.tasks.filter(task => task.project_id === selectedProjectId.value)
    : []
)

// Edit functions
const editProject = (project: Project) => {
  editingProject.value = project
  showEditProjectModal.value = true
}

const editTask = (task: Task) => {
  editingTask.value = task
  showEditTaskModal.value = true
}

// Delete functions
const confirmDeleteProject = (project: Project) => {
  deletingItem.value = { type: 'project', id: project.id, name: project.name }
  showDeleteModal.value = true
}

const confirmDeleteTask = (task: Task) => {
  deletingItem.value = { type: 'task', id: task.id, name: task.title }
  showDeleteModal.value = true
}

const handleDelete = async () => {
  if (!deletingItem.value) return
  
  isDeleting.value = true
  
  try {
    if (deletingItem.value.type === 'project') {
      await projectStore.deleteProject(deletingItem.value.id)
      // If we're viewing this project, go back to projects list
      if (selectedProjectId.value === deletingItem.value.id) {
        selectedProjectId.value = null
      }
    } else {
      await taskStore.deleteTask(deletingItem.value.id)
      // Refresh tasks for the current project
      if (selectedProjectId.value) {
        await taskStore.fetchTasks({ project_id: selectedProjectId.value })
      }
    }
    
    showDeleteModal.value = false
    deletingItem.value = null
  } catch (error: any) {
    console.error('Failed to delete item:', error)
    const itemType = deletingItem.value?.type || 'item'
    const errorMessage = error.response?.data?.detail || error.message || 'Unknown error'
    alert(`Failed to delete ${itemType}: ${errorMessage}`)
  } finally {
    isDeleting.value = false
  }
}

const closeDeleteModal = () => {
  if (!isDeleting.value) {
    showDeleteModal.value = false
    deletingItem.value = null
  }
}
</script>

<template>
  <div class="max-w-4xl mx-auto p-4">
    <h1 class="text-2xl font-bold mb-6">Dashboard</h1>

    <!-- Stats -->
    <div class="grid grid-cols-3 gap-4 mb-6">
      <div class="bg-white border rounded p-4 text-center">
        <div class="text-2xl font-bold">{{ totalProjects }}</div>
        <div class="text-sm text-gray-600">Projects</div>
      </div>
      <div class="bg-white border rounded p-4 text-center">
        <div class="text-2xl font-bold">{{ totalTasks }}</div>
        <div class="text-sm text-gray-600">Tasks</div>
      </div>
      <div class="bg-white border rounded p-4 text-center">
        <div class="text-2xl font-bold">{{ pendingTasks }}</div>
        <div class="text-sm text-gray-600">Pending</div>
      </div>
    </div>

    <!-- Actions -->
    <div class="mb-6">
      <button 
        @click="openCreateProjectModal"
        class="bg-blue-500 text-white px-4 py-2 rounded mr-2"
      >
        Create Project
      </button>
      <button 
        @click="openCreateTaskModal"
        class="bg-green-500 text-white px-4 py-2 rounded"
      >
        Create Task
      </button>
    </div>

    <!-- Projects List -->
    <div v-if="!selectedProjectId" class="bg-white border rounded p-4">
      <h2 class="text-lg font-semibold mb-4">Projects</h2>
      <div v-if="projectStore.projects.length === 0" class="text-gray-500">
        No projects yet. Create your first project above.
      </div>
      <div v-else class="space-y-2">
        <div 
          v-for="project in projectStore.projects" 
          :key="project.id"
          class="border-l-4 border-blue-400 pl-4 py-2 hover:bg-gray-50 transition-colors"
        >
          <div class="flex items-center justify-between">
            <div 
              @click="selectProject(project.id)"
              class="flex-1 cursor-pointer"
            >
              <div class="font-medium">{{ project.name }}</div>
              <div v-if="project.description" class="text-sm text-gray-600">{{ project.description }}</div>
              <div class="text-xs text-gray-500 mt-1">Click to view tasks →</div>
            </div>
            <div class="flex items-center space-x-2 ml-4">
              <button
                @click.stop="editProject(project)"
                class="text-blue-500 hover:text-blue-700 text-sm px-2 py-1"
                title="Edit project"
              >
                Edit
              </button>
              <button
                @click.stop="confirmDeleteProject(project)"
                class="text-red-500 hover:text-red-700 text-sm px-2 py-1"
                title="Delete project"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Project Tasks View -->
    <div v-if="selectedProjectId" class="bg-white border rounded p-4">
      <div class="flex items-center justify-between mb-4">
        <div>
          <button 
            @click="backToProjects"
            class="text-blue-500 hover:text-blue-700 text-sm mb-2"
          >
            ← Back to Projects
          </button>
          <h2 class="text-lg font-semibold">{{ selectedProject?.name }}</h2>
          <p v-if="selectedProject?.description" class="text-sm text-gray-600">{{ selectedProject.description }}</p>
        </div>
        <button 
          @click="openCreateTaskModal"
          class="bg-green-500 text-white px-3 py-1 rounded text-sm"
        >
          Add Task
        </button>
      </div>

      <div v-if="projectTasks.length === 0" class="text-gray-500 text-center py-8">
        No tasks in this project yet.
      </div>
      <div v-else class="space-y-3">
                 <div 
           v-for="task in projectTasks" 
           :key="task.id"
           class="border rounded p-3"
         >
           <div class="flex items-center justify-between">
             <div class="flex-1">
               <div class="font-medium">{{ task.title }}</div>
               <div v-if="task.description" class="text-sm text-gray-600 mt-1">{{ task.description }}</div>
               <div class="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                 <span 
                   class="px-2 py-1 rounded text-white text-xs"
                   :class="{
                     'bg-gray-500': task.status === 'todo',
                     'bg-blue-500': task.status === 'in_progress',
                     'bg-green-500': task.status === 'done'
                   }"
                 >
                   {{ task.status.replace('_', ' ').toUpperCase() }}
                 </span>
                 <span v-if="task.due_date">Due: {{ new Date(task.due_date).toLocaleDateString() }}</span>
                 <span v-if="task.priority">Priority: {{ task.priority }}</span>
               </div>
             </div>
             <div class="flex items-center space-x-2 ml-4">
               <button
                 @click="editTask(task)"
                 class="text-blue-500 hover:text-blue-700 text-sm px-2 py-1"
                 title="Edit task"
               >
                 Edit
               </button>
               <button
                 @click="confirmDeleteTask(task)"
                 class="text-red-500 hover:text-red-700 text-sm px-2 py-1"
                 title="Delete task"
               >
                 Delete
               </button>
             </div>
           </div>
         </div>
      </div>
    </div>

    <!-- Modals -->
    <CreateProjectModal 
      :open="showCreateProjectModal" 
      @close="showCreateProjectModal = false"
    />
    
    <CreateTaskModal 
      :open="showCreateTaskModal" 
      :default-project-id="selectedProjectId || undefined"
      @close="showCreateTaskModal = false; if (selectedProjectId) taskStore.fetchTasks({ project_id: selectedProjectId })"
    />

    <EditProjectModal 
      :open="showEditProjectModal" 
      :project="editingProject"
      @close="showEditProjectModal = false"
    />
    
    <EditTaskModal 
      :open="showEditTaskModal" 
      :task="editingTask"
      @close="showEditTaskModal = false; if (selectedProjectId) taskStore.fetchTasks({ project_id: selectedProjectId })"
    />

    <DeleteConfirmModal 
      :open="showDeleteModal"
      :title="`Delete ${deletingItem?.type || 'Item'}`"
      :message="`Are you sure you want to delete '${deletingItem?.name}'? This action cannot be undone.`"
      :is-deleting="isDeleting"
      @close="closeDeleteModal"
      @confirm="handleDelete"
    />
  </div>
</template> 
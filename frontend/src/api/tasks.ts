import { apiClient } from './client'

export interface Task {
  id: number
  title: string
  description: string
  user_id: number
  priority: 'low' | 'medium' | 'high' | 'urgent'
  status: 'todo' | 'in_progress' | 'review' | 'done' | 'cancelled'
  due_date: string | null
  created_at: string
  updated_at: string
  completed_at: string | null
}

export interface CreateTaskRequest {
  title: string
  description?: string
  priority?: 'low' | 'medium' | 'high' | 'urgent'
  status?: 'todo' | 'in_progress' | 'review' | 'done' | 'cancelled'
  due_date?: string
}

export interface UpdateTaskRequest {
  title?: string
  description?: string
  priority?: 'low' | 'medium' | 'high' | 'urgent'
  status?: 'todo' | 'in_progress' | 'review' | 'done' | 'cancelled'
  due_date?: string
}

export interface TaskFilters {
  status?: string
  priority?: string
  search?: string
  ordering?: string
}

export interface TaskStats {
  total_tasks: number
  todo_tasks: number
  in_progress_tasks: number
  done_tasks: number
  overdue_tasks: number
}

export const tasksApi = {
  getTasks: async (filters?: TaskFilters): Promise<{
    results: Task[]
    count: number
    next: string | null
    previous: string | null
  }> => {
    const response = await apiClient.get('/api/tasks/', { params: filters })
    return response.data
  },

  getTask: async (id: number): Promise<Task> => {
    const response = await apiClient.get(`/api/tasks/${id}/`)
    return response.data
  },

  createTask: async (data: CreateTaskRequest): Promise<Task> => {
    const response = await apiClient.post('/api/tasks/', data)
    return response.data
  },

  updateTask: async (id: number, data: UpdateTaskRequest): Promise<Task> => {
    const response = await apiClient.patch(`/api/tasks/${id}/`, data)
    return response.data
  },

  deleteTask: async (id: number): Promise<void> => {
    await apiClient.delete(`/api/tasks/${id}/`)
  },

  getTaskStats: async (): Promise<TaskStats> => {
    const response = await apiClient.get('/api/tasks/stats/')
    return response.data
  },

  bulkUpdateTasks: async (taskIds: number[], updates: UpdateTaskRequest): Promise<{
    message: string
    updated_count: number
  }> => {
    const response = await apiClient.post('/api/tasks/bulk-update/', {
      task_ids: taskIds,
      updates,
    })
    return response.data
  },
}

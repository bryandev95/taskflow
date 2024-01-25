import { useParams, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { ArrowLeft, Edit, Trash2, Calendar, User, Flag } from 'lucide-react'
import { tasksApi, Task } from '../api/tasks'
import { format } from 'date-fns'
import toast from 'react-hot-toast'

export const TaskDetail = () => {
  const { id } = useParams<{ id: string }>()
  const queryClient = useQueryClient()

  const { data: task, isLoading } = useQuery(
    ['task', id],
    () => tasksApi.getTask(Number(id)),
    {
      enabled: !!id,
    }
  )

  const updateTaskMutation = useMutation(
    (data: Partial<Task>) => tasksApi.updateTask(Number(id), data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['task', id])
        queryClient.invalidateQueries(['tasks'])
        toast.success('Task updated successfully!')
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to update task')
      },
    }
  )

  const deleteTaskMutation = useMutation(
    () => tasksApi.deleteTask(Number(id)),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['tasks'])
        toast.success('Task deleted successfully!')
        // Redirect to dashboard
        window.location.href = '/dashboard'
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.detail || 'Failed to delete task')
      },
    }
  )

  const handleStatusChange = (status: Task['status']) => {
    updateTaskMutation.mutate({ status })
  }

  const handlePriorityChange = (priority: Task['priority']) => {
    updateTaskMutation.mutate({ priority })
  }

  const handleDelete = () => {
    if (window.confirm('Are you sure you want to delete this task?')) {
      deleteTaskMutation.mutate()
    }
  }

  const getPriorityColor = (priority: Task['priority']) => {
    switch (priority) {
      case 'low':
        return 'bg-green-100 text-green-800'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800'
      case 'high':
        return 'bg-orange-100 text-orange-800'
      case 'urgent':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusColor = (status: Task['status']) => {
    switch (status) {
      case 'todo':
        return 'bg-gray-100 text-gray-800'
      case 'in_progress':
        return 'bg-blue-100 text-blue-800'
      case 'review':
        return 'bg-purple-100 text-purple-800'
      case 'done':
        return 'bg-green-100 text-green-800'
      case 'cancelled':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      </div>
    )
  }

  if (!task) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center py-12">
          <h3 className="text-lg font-medium text-gray-900 mb-2">Task not found</h3>
          <p className="text-gray-500 mb-4">The task you're looking for doesn't exist.</p>
          <Link to="/dashboard" className="btn btn-primary btn-md">
            Back to Dashboard
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-4 mb-4">
          <Link
            to="/dashboard"
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Dashboard
          </Link>
        </div>
        
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">{task.title}</h1>
            <div className="flex items-center gap-4 text-sm text-gray-500">
              <span className="flex items-center gap-1">
                <Calendar className="h-4 w-4" />
                Created {format(new Date(task.created_at), 'MMM d, yyyy')}
              </span>
              {task.due_date && (
                <span className="flex items-center gap-1">
                  <Calendar className="h-4 w-4" />
                  Due {format(new Date(task.due_date), 'MMM d, yyyy')}
                </span>
              )}
            </div>
          </div>
          
          <div className="flex gap-2">
            <Link
              to={`/tasks/${task.id}/edit`}
              className="btn btn-outline btn-md flex items-center gap-2"
            >
              <Edit className="h-4 w-4" />
              Edit
            </Link>
            <button
              onClick={handleDelete}
              className="btn btn-outline btn-md flex items-center gap-2 text-red-600 hover:text-red-700 hover:border-red-300"
            >
              <Trash2 className="h-4 w-4" />
              Delete
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Description */}
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold">Description</h3>
            </div>
            <div className="card-content">
              <p className="text-gray-700 whitespace-pre-wrap">
                {task.description || 'No description provided.'}
              </p>
            </div>
          </div>

          {/* Comments */}
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold">Comments</h3>
            </div>
            <div className="card-content">
              <p className="text-gray-500">No comments yet.</p>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Status */}
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold">Status</h3>
            </div>
            <div className="card-content">
              <select
                className="input w-full"
                value={task.status}
                onChange={(e) => handleStatusChange(e.target.value as Task['status'])}
              >
                <option value="todo">To Do</option>
                <option value="in_progress">In Progress</option>
                <option value="review">Review</option>
                <option value="done">Done</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>
          </div>

          {/* Priority */}
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold">Priority</h3>
            </div>
            <div className="card-content">
              <select
                className="input w-full"
                value={task.priority}
                onChange={(e) => handlePriorityChange(e.target.value as Task['priority'])}
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="urgent">Urgent</option>
              </select>
            </div>
          </div>

          {/* Task Info */}
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold">Task Information</h3>
            </div>
            <div className="card-content space-y-4">
              <div>
                <label className="text-sm font-medium text-gray-500">Status</label>
                <div className="mt-1">
                  <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(task.status)}`}>
                    {task.status.replace('_', ' ').toUpperCase()}
                  </span>
                </div>
              </div>
              
              <div>
                <label className="text-sm font-medium text-gray-500">Priority</label>
                <div className="mt-1">
                  <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getPriorityColor(task.priority)}`}>
                    {task.priority.toUpperCase()}
                  </span>
                </div>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-500">Created</label>
                <p className="mt-1 text-sm text-gray-900">
                  {format(new Date(task.created_at), 'MMM d, yyyy \'at\' h:mm a')}
                </p>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-500">Last Updated</label>
                <p className="mt-1 text-sm text-gray-900">
                  {format(new Date(task.updated_at), 'MMM d, yyyy \'at\' h:mm a')}
                </p>
              </div>

              {task.completed_at && (
                <div>
                  <label className="text-sm font-medium text-gray-500">Completed</label>
                  <p className="mt-1 text-sm text-gray-900">
                    {format(new Date(task.completed_at), 'MMM d, yyyy \'at\' h:mm a')}
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

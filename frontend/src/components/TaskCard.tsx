import { Link } from 'react-router-dom'
import { Calendar, Flag, Clock } from 'lucide-react'
import { Task } from '../api/tasks'
import { format, isAfter, isBefore, addDays } from 'date-fns'

interface TaskCardProps {
  task: Task
}

export const TaskCard = ({ task }: TaskCardProps) => {
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

  const isOverdue = task.due_date && isBefore(new Date(task.due_date), new Date())
  const isDueSoon = task.due_date && isBefore(new Date(task.due_date), addDays(new Date(), 3)) && !isOverdue

  return (
    <Link to={`/tasks/${task.id}`} className="block">
      <div className="card hover:shadow-md transition-shadow duration-200">
        <div className="card-content">
          <div className="flex items-start justify-between">
            <div className="flex-1 min-w-0">
              <h3 className="text-lg font-semibold text-gray-900 truncate">
                {task.title}
              </h3>
              {task.description && (
                <p className="mt-1 text-sm text-gray-600 line-clamp-2">
                  {task.description}
                </p>
              )}
            </div>
            
            <div className="flex items-center gap-2 ml-4">
              <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getPriorityColor(task.priority)}`}>
                <Flag className="h-3 w-3 mr-1" />
                {task.priority.toUpperCase()}
              </span>
              <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(task.status)}`}>
                {task.status.replace('_', ' ').toUpperCase()}
              </span>
            </div>
          </div>

          <div className="mt-4 flex items-center justify-between text-sm text-gray-500">
            <div className="flex items-center gap-4">
              {task.due_date && (
                <div className={`flex items-center gap-1 ${isOverdue ? 'text-red-600' : isDueSoon ? 'text-yellow-600' : ''}`}>
                  <Calendar className="h-4 w-4" />
                  <span>
                    {isOverdue ? 'Overdue' : isDueSoon ? 'Due soon' : 'Due'} {format(new Date(task.due_date), 'MMM d')}
                  </span>
                </div>
              )}
              <div className="flex items-center gap-1">
                <Clock className="h-4 w-4" />
                <span>Created {format(new Date(task.created_at), 'MMM d')}</span>
              </div>
            </div>
            
            {task.completed_at && (
              <div className="text-green-600 font-medium">
                Completed {format(new Date(task.completed_at), 'MMM d')}
              </div>
            )}
          </div>
        </div>
      </div>
    </Link>
  )
}

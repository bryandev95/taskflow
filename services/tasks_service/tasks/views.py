from rest_framework import generics, status, filters
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Task, TaskComment, TaskAttachment
from .serializers import (
    TaskSerializer, TaskCreateSerializer, TaskUpdateSerializer,
    TaskCommentSerializer, TaskAttachmentSerializer, TaskDetailSerializer
)


class TaskListCreateView(generics.ListCreateAPIView):
    """List and create tasks."""
    
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'due_date', 'priority']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TaskCreateSerializer
        return TaskSerializer
    
    def get_queryset(self):
        user_id = self.request.user_id
        return Task.objects.filter(user_id=user_id)
    
    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user_id)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a task."""
    
    serializer_class = TaskDetailSerializer
    
    def get_queryset(self):
        user_id = self.request.user_id
        return Task.objects.filter(user_id=user_id)
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return TaskUpdateSerializer
        return TaskDetailSerializer


class TaskCommentListCreateView(generics.ListCreateAPIView):
    """List and create task comments."""
    
    serializer_class = TaskCommentSerializer
    
    def get_queryset(self):
        task_id = self.kwargs['task_id']
        return TaskComment.objects.filter(task_id=task_id)
    
    def perform_create(self, serializer):
        task_id = self.kwargs['task_id']
        task = Task.objects.get(id=task_id, user_id=self.request.user_id)
        serializer.save(task=task, user_id=self.request.user_id)


class TaskAttachmentListCreateView(generics.ListCreateAPIView):
    """List and create task attachments."""
    
    serializer_class = TaskAttachmentSerializer
    
    def get_queryset(self):
        task_id = self.kwargs['task_id']
        return TaskAttachment.objects.filter(task_id=task_id)
    
    def perform_create(self, serializer):
        task_id = self.kwargs['task_id']
        task = Task.objects.get(id=task_id, user_id=self.request.user_id)
        serializer.save(task=task, user_id=self.request.user_id)


@api_view(['GET'])
def task_stats(request):
    """Get task statistics for the user."""
    user_id = request.user_id
    
    # Use database aggregation for better performance
    from django.db.models import Count, Q
    from django.utils import timezone
    
    now = timezone.now()
    stats = {
        'total_tasks': Task.objects.filter(user_id=user_id).count(),
        'todo_tasks': Task.objects.filter(user_id=user_id, status='todo').count(),
        'in_progress_tasks': Task.objects.filter(user_id=user_id, status='in_progress').count(),
        'done_tasks': Task.objects.filter(user_id=user_id, status='done').count(),
        'overdue_tasks': Task.objects.filter(
            user_id=user_id,
            due_date__lt=now,
            status__in=['todo', 'in_progress', 'review']
        ).count(),
    }
    
    return Response(stats)


@api_view(['POST'])
def bulk_update_tasks(request):
    """Bulk update multiple tasks."""
    task_ids = request.data.get('task_ids', [])
    updates = request.data.get('updates', {})
    
    if not task_ids or not updates:
        return Response(
            {'error': 'task_ids and updates are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user_id = request.user_id
    tasks = Task.objects.filter(id__in=task_ids, user_id=user_id)
    
    if not tasks.exists():
        return Response(
            {'error': 'No tasks found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    updated_count = tasks.update(**updates)
    
    return Response({
        'message': f'Updated {updated_count} tasks',
        'updated_count': updated_count
    })

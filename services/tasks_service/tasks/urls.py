from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.TaskListCreateView.as_view(), name='task-list-create'),
    path('<int:pk>/', views.TaskDetailView.as_view(), name='task-detail'),
    path('stats/', views.task_stats, name='task-stats'),
    path('bulk-update/', views.bulk_update_tasks, name='bulk-update-tasks'),
    path('<int:task_id>/comments/', views.TaskCommentListCreateView.as_view(), name='task-comments'),
    path('<int:task_id>/attachments/', views.TaskAttachmentListCreateView.as_view(), name='task-attachments'),
]

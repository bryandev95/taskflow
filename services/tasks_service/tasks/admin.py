from django.contrib import admin
from .models import Task, TaskComment, TaskAttachment


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin configuration for Task model."""
    
    list_display = ['title', 'user_id', 'priority', 'status', 'due_date', 'created_at']
    list_filter = ['priority', 'status', 'created_at', 'due_date']
    search_fields = ['title', 'description']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'completed_at']
    
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'user_id')
        }),
        ('Status & Priority', {
            'fields': ('priority', 'status', 'due_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    """Admin configuration for TaskComment model."""
    
    list_display = ['task', 'user_id', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content', 'task__title']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TaskAttachment)
class TaskAttachmentAdmin(admin.ModelAdmin):
    """Admin configuration for TaskAttachment model."""
    
    list_display = ['file_name', 'task', 'user_id', 'file_size', 'created_at']
    list_filter = ['mime_type', 'created_at']
    search_fields = ['file_name', 'task__title']
    ordering = ['-created_at']
    readonly_fields = ['created_at']

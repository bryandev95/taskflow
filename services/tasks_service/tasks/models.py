from django.db import models
from django.contrib.auth.models import User


class Task(models.Model):
    """Task model for task management."""
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('review', 'Review'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    user_id = models.IntegerField()  # Reference to user in auth service
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='todo')
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'tasks'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['due_date']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Set completed_at when status changes to 'done'
        if self.status == 'done' and not self.completed_at:
            from django.utils import timezone
            self.completed_at = timezone.now()
        elif self.status != 'done' and self.completed_at:
            self.completed_at = None
        
        # Update updated_at timestamp
        from django.utils import timezone
        self.updated_at = timezone.now()
        
        super().save(*args, **kwargs)


class TaskComment(models.Model):
    """Task comment model for task discussions."""
    
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    user_id = models.IntegerField()  # Reference to user in auth service
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'task_comments'
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment on {self.task.title} by user {self.user_id}"


class TaskAttachment(models.Model):
    """Task attachment model for file uploads."""
    
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='attachments')
    user_id = models.IntegerField()  # Reference to user in auth service
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    file_size = models.IntegerField()
    mime_type = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'task_attachments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Attachment: {self.file_name}"

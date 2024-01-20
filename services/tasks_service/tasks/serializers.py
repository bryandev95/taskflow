from rest_framework import serializers
from .models import Task, TaskComment, TaskAttachment


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for Task model."""
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'user_id', 'priority', 'status',
            'due_date', 'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'completed_at']


class TaskCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating tasks."""
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'priority', 'status', 'due_date']
    
    def create(self, validated_data):
        validated_data['user_id'] = self.context['request'].user_id
        return super().create(validated_data)


class TaskUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating tasks."""
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'priority', 'status', 'due_date']


class TaskCommentSerializer(serializers.ModelSerializer):
    """Serializer for TaskComment model."""
    
    class Meta:
        model = TaskComment
        fields = ['id', 'content', 'user_id', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user_id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['user_id'] = self.context['request'].user_id
        return super().create(validated_data)


class TaskAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for TaskAttachment model."""
    
    class Meta:
        model = TaskAttachment
        fields = [
            'id', 'file_name', 'file_path', 'file_size', 'mime_type', 'user_id', 'created_at'
        ]
        read_only_fields = ['id', 'user_id', 'created_at']
    
    def create(self, validated_data):
        validated_data['user_id'] = self.context['request'].user_id
        return super().create(validated_data)


class TaskDetailSerializer(TaskSerializer):
    """Detailed serializer for Task model with related objects."""
    
    comments = TaskCommentSerializer(many=True, read_only=True)
    attachments = TaskAttachmentSerializer(many=True, read_only=True)
    
    class Meta(TaskSerializer.Meta):
        fields = TaskSerializer.Meta.fields + ['comments', 'attachments']

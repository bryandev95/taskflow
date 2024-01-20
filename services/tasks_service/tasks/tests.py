from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import Task, TaskComment, TaskAttachment


class TaskModelTest(TestCase):
    """Test cases for Task model."""
    
    def setUp(self):
        self.task_data = {
            'title': 'Test Task',
            'description': 'Test Description',
            'user_id': 1,
            'priority': 'medium',
            'status': 'todo'
        }
    
    def test_create_task(self):
        """Test task creation."""
        task = Task.objects.create(**self.task_data)
        self.assertEqual(task.title, self.task_data['title'])
        self.assertEqual(task.user_id, self.task_data['user_id'])
        self.assertEqual(task.priority, self.task_data['priority'])
        self.assertEqual(task.status, self.task_data['status'])
    
    def test_task_str_representation(self):
        """Test task string representation."""
        task = Task.objects.create(**self.task_data)
        self.assertEqual(str(task), self.task_data['title'])


class TaskAPITest(APITestCase):
    """Test cases for Task API endpoints."""
    
    def setUp(self):
        self.task_list_url = reverse('task-list-create')
        self.task_data = {
            'title': 'Test Task',
            'description': 'Test Description',
            'priority': 'medium',
            'status': 'todo'
        }
        self.user_id = 1
    
    def test_create_task(self):
        """Test task creation via API."""
        # Mock user_id in request
        self.client.force_authenticate(user=None)
        self.client.user_id = self.user_id
        
        response = self.client.post(self.task_list_url, self.task_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Task.objects.filter(title=self.task_data['title']).exists())
    
    def test_list_tasks(self):
        """Test task listing via API."""
        # Create a task first
        Task.objects.create(user_id=self.user_id, **self.task_data)
        
        # Mock user_id in request
        self.client.force_authenticate(user=None)
        self.client.user_id = self.user_id
        
        response = self.client.get(self.task_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

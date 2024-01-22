"""
Notification worker for processing events and sending notifications.
"""

import json
import time
import threading
from datetime import datetime
from typing import Dict, Any
import pika
import redis
from decouple import config


class NotificationWorker:
    """Worker class for processing notifications."""
    
    def __init__(self, redis_client: redis.Redis, rabbitmq_connection: pika.BlockingConnection):
        self.redis_client = redis_client
        self.rabbitmq_connection = rabbitmq_connection
        self.channel = None
        self.running = False
        self.thread = None
        
        # Notification templates
        self.templates = {
            'task_created': {
                'title': 'New Task Created',
                'message': 'A new task "{task_title}" has been created.',
                'type': 'info'
            },
            'task_updated': {
                'title': 'Task Updated',
                'message': 'Task "{task_title}" has been updated.',
                'type': 'info'
            },
            'task_completed': {
                'title': 'Task Completed',
                'message': 'Task "{task_title}" has been completed!',
                'type': 'success'
            },
            'task_due_soon': {
                'title': 'Task Due Soon',
                'message': 'Task "{task_title}" is due soon.',
                'type': 'warning'
            },
            'task_overdue': {
                'title': 'Task Overdue',
                'message': 'Task "{task_title}" is overdue.',
                'type': 'error'
            },
            'comment_added': {
                'title': 'New Comment',
                'message': 'A new comment was added to task "{task_title}".',
                'type': 'info'
            }
        }
    
    def start(self):
        """Start the notification worker."""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()
        print("Notification worker started")
    
    def stop(self):
        """Stop the notification worker."""
        self.running = False
        if self.thread:
            self.thread.join()
        if self.channel and not self.channel.is_closed:
            self.channel.close()
        print("Notification worker stopped")
    
    def _run(self):
        """Main worker loop."""
        try:
            self.channel = self.rabbitmq_connection.channel()
            
            # Declare queues
            self.channel.queue_declare(queue='task_events', durable=True)
            self.channel.queue_declare(queue='notification_events', durable=True)
            
            # Set up consumers
            self.channel.basic_consume(
                queue='task_events',
                on_message_callback=self._process_task_event,
                auto_ack=True
            )
            
            self.channel.basic_consume(
                queue='notification_events',
                on_message_callback=self._process_notification_event,
                auto_ack=True
            )
            
            print("Waiting for messages. To exit press CTRL+C")
            self.channel.start_consuming()
            
        except Exception as e:
            print(f"Error in notification worker: {e}")
            if self.running:
                # Retry after a delay
                time.sleep(5)
                self._run()
    
    def _process_task_event(self, channel, method, properties, body):
        """Process task-related events."""
        try:
            event_data = json.loads(body)
            event_type = event_data.get('type')
            task_data = event_data.get('data', {})
            user_id = task_data.get('user_id')
            
            if not user_id:
                print(f"No user_id in event: {event_data}")
                return
            
            # Generate notification based on event type
            notification = self._create_notification(event_type, task_data)
            if notification:
                self._store_notification(user_id, notification)
                print(f"Processed task event: {event_type} for user {user_id}")
            
        except Exception as e:
            print(f"Error processing task event: {e}")
    
    def _process_notification_event(self, channel, method, properties, body):
        """Process direct notification events."""
        try:
            event_data = json.loads(body)
            user_id = event_data.get('user_id')
            notification_data = event_data.get('notification', {})
            
            if not user_id or not notification_data:
                print(f"Invalid notification event: {event_data}")
                return
            
            # Store the notification
            self._store_notification(user_id, notification_data)
            print(f"Processed notification event for user {user_id}")
            
        except Exception as e:
            print(f"Error processing notification event: {e}")
    
    def _create_notification(self, event_type: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a notification from an event."""
        template = self.templates.get(event_type)
        if not template:
            return None
        
        # Format the message with task data, handle missing keys gracefully
        try:
            message = template['message'].format(**task_data)
        except KeyError as e:
            # Fallback message if task data is missing required fields
            message = f"Task {task_data.get('title', 'Unknown')} - {template['title']}"
        
        return {
            'id': f"{event_type}_{task_data.get('id', 'unknown')}_{int(time.time())}",
            'title': template['title'],
            'message': message,
            'type': template['type'],
            'event_type': event_type,
            'task_id': task_data.get('id'),
            'created_at': datetime.utcnow().isoformat(),
            'read': False
        }
    
    def _store_notification(self, user_id: int, notification: Dict[str, Any]):
        """Store notification in Redis."""
        try:
            notifications_key = f"notifications:user:{user_id}"
            
            # Store notification
            notification_json = json.dumps(notification)
            self.redis_client.lpush(notifications_key, notification_json)
            
            # Keep only last 100 notifications per user
            self.redis_client.ltrim(notifications_key, 0, 99)
            
            # Set expiration (30 days)
            self.redis_client.expire(notifications_key, 86400 * 30)
            
        except Exception as e:
            print(f"Error storing notification: {e}")
    
    def send_notification(self, user_id: int, title: str, message: str, notification_type: str = 'info'):
        """Send a direct notification to a user."""
        notification = {
            'id': f"direct_{int(time.time())}",
            'title': title,
            'message': message,
            'type': notification_type,
            'event_type': 'direct',
            'created_at': datetime.utcnow().isoformat(),
            'read': False
        }
        
        self._store_notification(user_id, notification)
        print(f"Sent direct notification to user {user_id}: {title}")

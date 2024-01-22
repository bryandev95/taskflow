"""
FastAPI application for notifications service.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import redis
import pika
import json
from decouple import config
from worker import NotificationWorker

# Configuration
REDIS_URL = config('REDIS_URL', default='redis://localhost:6379')
RABBITMQ_URL = config('RABBITMQ_URL', default='amqp://localhost:5672')

# Global variables for connections
redis_client = None
rabbitmq_connection = None
notification_worker = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global redis_client, rabbitmq_connection, notification_worker
    
    # Startup
    try:
        # Initialize Redis connection
        redis_client = redis.from_url(REDIS_URL)
        redis_client.ping()  # Test connection
        
        # Initialize RabbitMQ connection
        rabbitmq_connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
        
        # Start notification worker
        notification_worker = NotificationWorker(redis_client, rabbitmq_connection)
        notification_worker.start()
        
        print("Notifications service started successfully")
        
    except Exception as e:
        print(f"Failed to start notifications service: {e}")
        raise
    
    yield
    
    # Shutdown
    try:
        if notification_worker:
            notification_worker.stop()
        if rabbitmq_connection and not rabbitmq_connection.is_closed:
            rabbitmq_connection.close()
        if redis_client:
            redis_client.close()
        print("Notifications service stopped")
    except Exception as e:
        print(f"Error during shutdown: {e}")


# Create FastAPI app
app = FastAPI(
    title="TaskFlow Notifications Service",
    description="Microservice for handling notifications and events",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_redis():
    """Dependency to get Redis client."""
    if not redis_client:
        raise HTTPException(status_code=503, detail="Redis not available")
    return redis_client


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "TaskFlow Notifications Service", "status": "running"}


@app.get("/health")
async def health_check(redis: redis.Redis = Depends(get_redis)):
    """Health check endpoint."""
    try:
        # Check Redis connection
        redis.ping()
        return {"status": "healthy", "redis": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {e}")


@app.get("/notifications/{user_id}")
async def get_user_notifications(
    user_id: int,
    limit: int = 20,
    offset: int = 0,
    redis: redis.Redis = Depends(get_redis)
):
    """Get notifications for a specific user."""
    try:
        # Get notifications from Redis
        notifications_key = f"notifications:user:{user_id}"
        notifications = redis.lrange(notifications_key, offset, offset + limit - 1)
        
        # Parse notifications
        parsed_notifications = []
        for notification in notifications:
            try:
                parsed_notifications.append(json.loads(notification))
            except json.JSONDecodeError:
                continue
        
        return {
            "notifications": parsed_notifications,
            "total": redis.llen(notifications_key),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get notifications: {e}")


@app.post("/notifications/{user_id}/mark-read")
async def mark_notifications_read(
    user_id: int,
    notification_ids: list[str],
    redis: redis.Redis = Depends(get_redis)
):
    """Mark notifications as read."""
    try:
        # Mark notifications as read in Redis
        for notification_id in notification_ids:
            read_key = f"notifications:read:{user_id}:{notification_id}"
            redis.set(read_key, "true", ex=86400 * 30)  # Expire in 30 days
        
        return {"message": "Notifications marked as read"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mark notifications as read: {e}")


@app.delete("/notifications/{user_id}")
async def clear_user_notifications(
    user_id: int,
    redis: redis.Redis = Depends(get_redis)
):
    """Clear all notifications for a user."""
    try:
        notifications_key = f"notifications:user:{user_id}"
        redis.delete(notifications_key)
        return {"message": "Notifications cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear notifications: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

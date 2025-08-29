"""
Celery Application Configuration for WAR KRS
Implementation following existing code style and patterns
"""

import os
from celery import Celery
from kombu import Queue

# Create Celery app instance
celery_app = Celery('warkrs_celery')

# Configuration
celery_app.conf.update(
    # Broker configuration (Redis)
    broker_url=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    result_backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
    
    # Task configuration
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Jakarta',
    enable_utc=True,
    
    # Worker configuration for VPS 1GB
    worker_concurrency=2,  # Max 2 concurrent tasks per worker
    worker_prefetch_multiplier=1,  # One task at a time per worker
    task_acks_late=True,  # Acknowledge task after completion
    worker_disable_rate_limits=False,
    
    # Task routing
    task_routes={
        'tasks.war_tasks.run_war_task': {'queue': 'war_queue'},
        'tasks.war_tasks.stop_war_task': {'queue': 'control_queue'},
    },
    
    # Queue configuration
    task_default_queue='default',
    task_queues=(
        Queue('war_queue', routing_key='war_queue'),
        Queue('control_queue', routing_key='control_queue'),
        Queue('default', routing_key='default'),
    ),
    
    # Task annotations for resource management
    task_annotations={
        'tasks.war_tasks.run_war_task': {
            'rate_limit': '50/m',  # Max 50 new tasks per minute
            'time_limit': 7200,    # 2 hours max (safety)
            'soft_time_limit': 6900,  # Warning at 1h 55m
        }
    },
    
    # Result expiration
    result_expires=3600,  # Results expire after 1 hour
    
    # Error handling
    task_reject_on_worker_lost=True,
    task_ignore_result=False,
)

# Auto-discover tasks
celery_app.autodiscover_tasks(['tasks'])

# Import tasks manually to ensure they're loaded
try:
    from tasks import war_tasks
    print("✅ WAR tasks imported successfully")
except ImportError as e:
    print(f"⚠️  Warning: Could not import WAR tasks: {e}")

if __name__ == '__main__':
    celery_app.start()

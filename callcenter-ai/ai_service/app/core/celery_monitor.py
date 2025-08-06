# app/core/celery_monitor.py
import threading
import logging
import time
from typing import Dict, Any
from datetime import datetime
from celery.events import EventReceiver
from ..celery_app import celery_app

logger = logging.getLogger(__name__)

class CeleryEventMonitor:
    def __init__(self):
        self.active_tasks = {}
        self.worker_stats = {}
        self.monitoring_thread = None
        self.is_monitoring = False
        
    def start_monitoring(self):
        """Start monitoring in background thread with resilient reconnection"""
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            logger.info("Event monitoring already running")
            return
            
        def monitor_worker():
            retry_interval = 5  # Start with 5 seconds
            max_retry_interval = 60  # Max 1 minute between retries
            
            while True:
                try:
                    logger.info("🔄 Attempting to connect to Celery events...")
                    
                    def on_task_started(event):
                        self.active_tasks[event['uuid']] = {
                            'task_id': event['uuid'],
                            'name': event.get('name', 'unknown'),
                            'worker': event.get('hostname', 'unknown'),
                            'started': datetime.fromtimestamp(event['timestamp']).isoformat(),
                            'args': event.get('args', [])
                        }
                        logger.info(f"📋 Task started: {event.get('name', 'unknown')} ({event['uuid'][:8]})")
                    
                    def on_task_succeeded(event):
                        task_info = self.active_tasks.pop(event['uuid'], {})
                        logger.info(f"✅ Task completed: {task_info.get('name', 'unknown')} ({event['uuid'][:8]})")
                    
                    def on_task_failed(event):
                        task_info = self.active_tasks.pop(event['uuid'], {})
                        logger.warning(f"❌ Task failed: {task_info.get('name', 'unknown')} ({event['uuid'][:8]})")
                    
                    def on_worker_heartbeat(event):
                        self.worker_stats[event['hostname']] = {
                            'last_heartbeat': datetime.fromtimestamp(event['timestamp']).isoformat(),
                            'status': 'online'
                        }
                    
                    # Attempt connection
                    with celery_app.connection() as connection:
                        receiver = EventReceiver(
                            connection,
                            handlers={
                                'task-started': on_task_started,
                                'task-succeeded': on_task_succeeded,
                                'task-failed': on_task_failed,
                                'worker-heartbeat': on_worker_heartbeat,
                            }
                        )
                        
                        logger.info("✅ Connected to Celery events - monitoring active")
                        self.is_monitoring = True
                        retry_interval = 5  # Reset retry interval on success
                        
                        # This blocks until connection fails
                        receiver.capture(limit=None, timeout=None, wakeup=True)
                        
                except (KeyboardInterrupt, SystemExit):
                    logger.info("🛑 Event monitoring stopped by user")
                    self.is_monitoring = False
                    break
                    
                except Exception as e:
                    self.is_monitoring = False
                    logger.warning(f"⚠️ Celery event connection failed: {e}")
                    logger.info(f"🔄 Retrying in {retry_interval} seconds... (make sure Celery worker is running)")
                    
                    time.sleep(retry_interval)
                    
                    # Exponential backoff with max limit
                    retry_interval = min(retry_interval * 1.5, max_retry_interval)
        
        self.monitoring_thread = threading.Thread(target=monitor_worker, daemon=True)
        self.monitoring_thread.start()
        logger.info("🔄 Celery event monitoring thread started (will connect when worker available)")
    
    def get_active_tasks(self) -> Dict[str, Any]:
        """Get currently active tasks"""
        return {
            "active_tasks": list(self.active_tasks.values()),
            "total_active": len(self.active_tasks),
            "data_source": "celery_events",
            "monitoring_status": "connected" if self.is_monitoring else "waiting_for_worker"
        }
    
    def get_worker_stats(self) -> Dict[str, Any]:
        """Get worker statistics"""
        return {
            "workers": self.worker_stats,
            "total_workers": len(self.worker_stats),
            "monitoring_status": "connected" if self.is_monitoring else "waiting_for_worker"
        }
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get monitoring connection status"""
        return {
            "is_monitoring": self.is_monitoring,
            "thread_alive": self.monitoring_thread.is_alive() if self.monitoring_thread else False,
            "active_tasks_count": len(self.active_tasks),
            "workers_seen": len(self.worker_stats),
            "status": "connected" if self.is_monitoring else "waiting_for_celery_worker"
        }

# Global instance
celery_monitor = CeleryEventMonitor()
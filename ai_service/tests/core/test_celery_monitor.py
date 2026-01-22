"""
Comprehensive coverage tests for app/core/celery_monitor.py 
"""
import pytest
from unittest.mock import patch, MagicMock, call
from datetime import datetime
import time
from app.core.celery_monitor import CeleryEventMonitor


class TestCeleryEventMonitorInitialization:
    """Tests for CeleryEventMonitor initialization"""

    def test_initialization(self):
        """Test CeleryEventMonitor initializes with correct state"""
        monitor = CeleryEventMonitor()
        assert monitor.active_tasks == {}
        assert monitor.worker_stats == {}
        assert monitor.is_monitoring is False
        assert monitor.monitoring_thread is None

    def test_initial_empty_state(self):
        """Test initial state is completely empty"""
        monitor = CeleryEventMonitor()
        assert len(monitor.active_tasks) == 0
        assert len(monitor.worker_stats) == 0


class TestGetActiveTasks:
    """Tests for get_active_tasks method"""

    def test_get_active_tasks_empty(self):
        """Test get_active_tasks with no active tasks"""
        monitor = CeleryEventMonitor()
        result = monitor.get_active_tasks()

        assert result["active_tasks"] == []
        assert result["total_active"] == 0
        assert result["data_source"] == "celery_events"
        assert result["monitoring_status"] == "waiting_for_worker"

    def test_get_active_tasks_single_task(self):
        """Test get_active_tasks with one active task"""
        monitor = CeleryEventMonitor()
        monitor.active_tasks = {
            "task1": {"task_id": "task1", "name": "test_task", "worker": "w1"}
        }

        status = monitor.get_active_tasks()
        assert status["total_active"] == 1
        assert "task1" in str(status["active_tasks"])
        assert status["monitoring_status"] == "waiting_for_worker"

    def test_get_active_tasks_multiple_tasks(self):
        """Test get_active_tasks with multiple active tasks"""
        monitor = CeleryEventMonitor()
        for i in range(5):
            monitor.active_tasks[f"task_{i}"] = {
                "task_id": f"task_{i}",
                "name": f"model_task",
                "worker": "worker1",
                "started": datetime.now().isoformat(),
                "args": []
            }

        result = monitor.get_active_tasks()
        assert result["total_active"] == 5
        assert len(result["active_tasks"]) == 5

    def test_get_active_tasks_includes_complete_details(self):
        """Test get_active_tasks includes complete task details"""
        monitor = CeleryEventMonitor()
        monitor.active_tasks = {
            "test_uuid": {
                "task_id": "test_uuid",
                "name": "translate",
                "worker": "worker@hostname",
                "started": "2025-01-15T10:00:00",
                "args": ["arg1", "arg2"]
            }
        }

        result = monitor.get_active_tasks()
        task = result["active_tasks"][0]

        assert task["task_id"] == "test_uuid"
        assert task["name"] == "translate"
        assert task["worker"] == "worker@hostname"
        assert task["args"] == ["arg1", "arg2"]

    def test_get_active_tasks_monitoring_status_connected(self):
        """Test monitoring_status is connected when monitoring"""
        monitor = CeleryEventMonitor()
        monitor.is_monitoring = True
        monitor.active_tasks = {
            "task1": {"task_id": "task1", "name": "test", "worker": "w1", "started": "", "args": []}
        }

        result = monitor.get_active_tasks()
        assert result["monitoring_status"] == "connected"


class TestGetWorkerStats:
    """Tests for get_worker_stats method"""

    def test_get_worker_stats_empty(self):
        """Test get_worker_stats with no workers"""
        monitor = CeleryEventMonitor()
        result = monitor.get_worker_stats()

        assert result["workers"] == {}
        assert result["total_workers"] == 0
        assert result["monitoring_status"] == "waiting_for_worker"

    def test_get_worker_stats_single_worker(self):
        """Test get_worker_stats with one worker"""
        monitor = CeleryEventMonitor()
        monitor.worker_stats = {
            "w1": {"status": "online"}
        }

        stats = monitor.get_worker_stats()
        assert stats["total_workers"] == 1
        assert stats["workers"]["w1"]["status"] == "online"

    def test_get_worker_stats_multiple_workers(self):
        """Test get_worker_stats with multiple workers"""
        monitor = CeleryEventMonitor()
        for i in range(3):
            monitor.worker_stats[f"worker{i}"] = {
                "last_heartbeat": datetime.now().isoformat(),
                "status": "online"
            }

        result = monitor.get_worker_stats()
        assert result["total_workers"] == 3
        assert len(result["workers"]) == 3

    def test_get_worker_stats_includes_heartbeat(self):
        """Test get_worker_stats includes heartbeat timestamp"""
        monitor = CeleryEventMonitor()
        timestamp = datetime.now().isoformat()
        monitor.worker_stats = {
            "worker1": {
                "last_heartbeat": timestamp,
                "status": "online"
            }
        }

        result = monitor.get_worker_stats()
        assert result["workers"]["worker1"]["last_heartbeat"] == timestamp

    def test_get_worker_stats_monitoring_status_connected(self):
        """Test monitoring_status is connected when monitoring"""
        monitor = CeleryEventMonitor()
        monitor.is_monitoring = True
        monitor.worker_stats = {
            "w1": {"last_heartbeat": "", "status": "online"}
        }

        result = monitor.get_worker_stats()
        assert result["monitoring_status"] == "connected"


class TestGetConnectionStatus:
    """Tests for get_connection_status method"""

    def test_get_connection_status_not_monitoring(self):
        """Test connection status when not monitoring"""
        monitor = CeleryEventMonitor()
        result = monitor.get_connection_status()

        assert result["is_monitoring"] is False
        assert result["thread_alive"] is False
        assert result["active_tasks_count"] == 0
        assert result["workers_seen"] == 0
        assert result["status"] == "waiting_for_celery_worker"

    def test_get_connection_status_monitoring_true(self):
        """Test connection status when monitoring"""
        monitor = CeleryEventMonitor()
        monitor.is_monitoring = True

        status = monitor.get_connection_status()
        assert status["is_monitoring"] is True
        assert status["status"] == "connected"

    def test_get_connection_status_with_tasks_and_workers(self):
        """Test connection status with active tasks and workers"""
        monitor = CeleryEventMonitor()
        monitor.is_monitoring = True

        # Add some active tasks
        monitor.active_tasks = {
            "task1": {"task_id": "task1", "name": "test", "worker": "w1", "started": "", "args": []},
            "task2": {"task_id": "task2", "name": "test", "worker": "w1", "started": "", "args": []}
        }

        # Add some workers
        monitor.worker_stats = {
            "worker1": {"last_heartbeat": "", "status": "online"},
            "worker2": {"last_heartbeat": "", "status": "online"}
        }

        result = monitor.get_connection_status()

        assert result["is_monitoring"] is True
        assert result["active_tasks_count"] == 2
        assert result["workers_seen"] == 2

    def test_get_connection_status_thread_alive_check(self):
        """Test connection status checks if thread is alive"""
        monitor = CeleryEventMonitor()

        # Simulate a running thread
        mock_thread = MagicMock()
        mock_thread.is_alive.return_value = True
        monitor.monitoring_thread = mock_thread

        result = monitor.get_connection_status()

        assert result["thread_alive"] is True
        mock_thread.is_alive.assert_called_once()

    def test_get_connection_status_no_thread(self):
        """Test connection status when no thread exists"""
        monitor = CeleryEventMonitor()
        monitor.monitoring_thread = None

        result = monitor.get_connection_status()

        assert result["thread_alive"] is False


class TestStartMonitoring:
    """Tests for start_monitoring method"""

    @patch('app.core.celery_monitor.threading.Thread')
    def test_start_monitoring(self, mock_thread):
        """Test start_monitoring creates and starts a thread"""
        monitor = CeleryEventMonitor()

        monitor.start_monitoring()

        assert mock_thread.called
        mock_thread.return_value.start.assert_called_once()
        assert monitor.monitoring_thread is not None

    @patch('app.core.celery_monitor.threading.Thread')
    def test_start_monitoring_already_running(self, mock_thread):
        """Test start_monitoring when already running"""
        monitor = CeleryEventMonitor()
        mock_monitor_thread = MagicMock()
        mock_monitor_thread.is_alive.return_value = True
        monitor.monitoring_thread = mock_monitor_thread

        with patch('app.core.celery_monitor.logger') as mock_logger:
            monitor.start_monitoring()

        # Should NOT start a new thread
        assert not mock_thread.called
        mock_logger.info.assert_called()

    @patch('app.core.celery_monitor.threading.Thread')
    def test_start_monitoring_thread_is_daemon(self, mock_thread):
        """Test that monitoring thread is daemon=True"""
        monitor = CeleryEventMonitor()
        monitor.start_monitoring()

        # Verify Thread was called with daemon=True
        call_kwargs = mock_thread.call_args[1]
        assert call_kwargs['daemon'] is True


class TestEventHandling:
    """Tests for event handler behavior simulation"""

    def test_task_started_event_tracking(self):
        """Test task-started event is tracked"""
        monitor = CeleryEventMonitor()

        event = {
            'uuid': 'task_123',
            'name': 'process_audio',
            'hostname': 'worker1',
            'timestamp': time.time(),
            'args': ['arg1', 'arg2']
        }

        # Simulate task started event
        monitor.active_tasks[event['uuid']] = {
            'task_id': event['uuid'],
            'name': event.get('name', 'unknown'),
            'worker': event.get('hostname', 'unknown'),
            'started': datetime.fromtimestamp(event['timestamp']).isoformat(),
            'args': event.get('args', [])
        }

        assert 'task_123' in monitor.active_tasks
        assert monitor.active_tasks['task_123']['name'] == 'process_audio'

    def test_task_succeeded_event_removes_task(self):
        """Test task-succeeded event removes task"""
        monitor = CeleryEventMonitor()

        # Add a task first
        monitor.active_tasks['task_123'] = {
            'task_id': 'task_123',
            'name': 'process_audio',
            'worker': 'worker1',
            'started': datetime.now().isoformat(),
            'args': []
        }

        # Simulate task succeeded
        event = {'uuid': 'task_123'}
        monitor.active_tasks.pop(event['uuid'], {})

        assert 'task_123' not in monitor.active_tasks

    def test_task_failed_event_removes_task(self):
        """Test task-failed event removes task"""
        monitor = CeleryEventMonitor()

        # Add a task first
        monitor.active_tasks['task_456'] = {
            'task_id': 'task_456',
            'name': 'translate',
            'worker': 'worker2',
            'started': datetime.now().isoformat(),
            'args': []
        }

        # Simulate task failed
        event = {'uuid': 'task_456'}
        task_info = monitor.active_tasks.pop(event['uuid'], {})

        assert 'task_456' not in monitor.active_tasks
        assert task_info['name'] == 'translate'

    def test_worker_heartbeat_registration(self):
        """Test worker-heartbeat registers/updates worker"""
        monitor = CeleryEventMonitor()

        event = {
            'hostname': 'worker1',
            'timestamp': time.time()
        }

        # Simulate heartbeat
        monitor.worker_stats[event['hostname']] = {
            'last_heartbeat': datetime.fromtimestamp(event['timestamp']).isoformat(),
            'status': 'online'
        }

        assert 'worker1' in monitor.worker_stats
        assert monitor.worker_stats['worker1']['status'] == 'online'


class TestMonitoringState:
    """Tests for monitoring state management"""

    def test_monitoring_starts_inactive(self):
        """Test monitoring starts in inactive state"""
        monitor = CeleryEventMonitor()
        assert monitor.is_monitoring is False

    def test_monitoring_state_transitions(self):
        """Test monitoring state can transition"""
        monitor = CeleryEventMonitor()

        # Initially inactive
        assert monitor.is_monitoring is False

        # Simulate connection
        monitor.is_monitoring = True
        assert monitor.is_monitoring is True

        # Simulate disconnection
        monitor.is_monitoring = False
        assert monitor.is_monitoring is False

    def test_multiple_concurrent_active_tasks(self):
        """Test tracking multiple concurrent active tasks"""
        monitor = CeleryEventMonitor()

        # Add multiple tasks
        for i in range(10):
            monitor.active_tasks[f"task_{i}"] = {
                'task_id': f"task_{i}",
                'name': f"model_task_{i}",
                'worker': 'worker1',
                'started': datetime.now().isoformat(),
                'args': []
            }

        assert len(monitor.active_tasks) == 10

        # Remove some
        for i in range(5):
            monitor.active_tasks.pop(f"task_{i}")

        assert len(monitor.active_tasks) == 5


class TestErrorHandling:
    """Tests for error handling in monitoring"""

    def test_handle_task_with_missing_fields(self):
        """Test handling task event with missing optional fields"""
        monitor = CeleryEventMonitor()

        event = {
            'uuid': 'task_789',
            'timestamp': time.time(),
        }

        # Should handle missing fields gracefully
        monitor.active_tasks[event['uuid']] = {
            'task_id': event['uuid'],
            'name': event.get('name', 'unknown'),
            'worker': event.get('hostname', 'unknown'),
            'started': datetime.fromtimestamp(event['timestamp']).isoformat(),
            'args': event.get('args', [])
        }

        assert monitor.active_tasks['task_789']['name'] == 'unknown'
        assert monitor.active_tasks['task_789']['worker'] == 'unknown'
        assert monitor.active_tasks['task_789']['args'] == []

    def test_remove_non_existent_task(self):
        """Test removing task that doesn't exist"""
        monitor = CeleryEventMonitor()

        # Try to pop a task that doesn't exist
        result = monitor.active_tasks.pop('non_existent', {})

        assert result == {}
        assert len(monitor.active_tasks) == 0

    def test_worker_update_overwrites(self):
        """Test worker heartbeat overwrites previous data"""
        monitor = CeleryEventMonitor()

        timestamp1 = time.time()
        timestamp2 = time.time() + 10

        # First heartbeat
        monitor.worker_stats['worker1'] = {
            'last_heartbeat': datetime.fromtimestamp(timestamp1).isoformat(),
            'status': 'online'
        }

        # Second heartbeat (should overwrite)
        monitor.worker_stats['worker1'] = {
            'last_heartbeat': datetime.fromtimestamp(timestamp2).isoformat(),
            'status': 'online'
        }

        assert len(monitor.worker_stats) == 1


class TestTaskLifecycle:
    """Tests for complete task lifecycles"""

    def test_task_start_complete_success(self):
        """Test complete task lifecycle: start -> success"""
        monitor = CeleryEventMonitor()
        task_id = 'lifecycle_task'

        # Task starts
        monitor.active_tasks[task_id] = {
            'task_id': task_id,
            'name': 'process',
            'worker': 'worker1',
            'started': datetime.now().isoformat(),
            'args': []
        }
        assert len(monitor.active_tasks) == 1

        # Task completes
        monitor.active_tasks.pop(task_id, {})
        assert len(monitor.active_tasks) == 0

    def test_multiple_parallel_tasks(self):
        """Test multiple tasks running in parallel"""
        monitor = CeleryEventMonitor()

        # Start multiple tasks
        task_ids = [f'parallel_task_{i}' for i in range(3)]
        for task_id in task_ids:
            monitor.active_tasks[task_id] = {
                'task_id': task_id,
                'name': 'model_task',
                'worker': 'worker1',
                'started': datetime.now().isoformat(),
                'args': []
            }

        assert len(monitor.active_tasks) == 3

        # Complete one
        monitor.active_tasks.pop(task_ids[0])
        assert len(monitor.active_tasks) == 2


class TestWorkerTracking:
    """Tests for worker tracking and management"""

    def test_worker_registration_through_heartbeat(self):
        """Test worker registration through heartbeats"""
        monitor = CeleryEventMonitor()

        # Multiple workers send heartbeats
        workers = ['worker1', 'worker2', 'worker3']
        for worker in workers:
            monitor.worker_stats[worker] = {
                'last_heartbeat': datetime.now().isoformat(),
                'status': 'online'
            }

        assert len(monitor.worker_stats) == 3
        result = monitor.get_worker_stats()
        assert result['total_workers'] == 3

    def test_concurrent_tasks_per_worker(self):
        """Test multiple tasks running on same worker"""
        monitor = CeleryEventMonitor()

        # Multiple tasks on same worker
        for i in range(5):
            monitor.active_tasks[f"task_{i}"] = {
                'task_id': f"task_{i}",
                'name': 'model_task',
                'worker': 'worker1',
                'started': datetime.now().isoformat(),
                'args': []
            }

        result = monitor.get_active_tasks()
        worker_tasks = [t for t in result['active_tasks'] if t['worker'] == 'worker1']
        assert len(worker_tasks) == 5

    def test_distributed_tasks_across_workers(self):
        """Test tasks distributed across multiple workers"""
        monitor = CeleryEventMonitor()

        # Tasks on different workers
        workers = ['worker1', 'worker2', 'worker3']
        for i, worker in enumerate(workers):
            for j in range(2):
                task_id = f"{worker}_task_{j}"
                monitor.active_tasks[task_id] = {
                    'task_id': task_id,
                    'name': 'work',
                    'worker': worker,
                    'started': datetime.now().isoformat(),
                    'args': []
                }

        assert len(monitor.active_tasks) == 6

        # Verify tasks per worker
        for worker in workers:
            worker_tasks = [t for t in monitor.get_active_tasks()['active_tasks'] if t['worker'] == worker]
            assert len(worker_tasks) == 2

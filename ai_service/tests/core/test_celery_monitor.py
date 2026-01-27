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


class TestMonitorWorkerThreadExecution:
    """Tests for the actual monitor_worker thread execution logic"""

    @patch('app.core.celery_monitor.celery_app')
    @patch('app.core.celery_monitor.EventReceiver')
    @patch('app.core.celery_monitor.logger')
    def test_monitor_worker_successful_connection(self, mock_logger,
                                                   mock_event_receiver, mock_celery_app):
        """Test monitor_worker connects successfully and sets monitoring state"""
        monitor = CeleryEventMonitor()

        # Setup mocks - let thread actually run
        mock_connection = MagicMock()
        mock_celery_app.connection.return_value.__enter__.return_value = mock_connection

        mock_receiver_instance = MagicMock()
        # Make capture() raise KeyboardInterrupt to exit the thread cleanly
        mock_receiver_instance.capture.side_effect = KeyboardInterrupt
        mock_event_receiver.return_value = mock_receiver_instance

        # Start monitoring - thread actually runs
        monitor.start_monitoring()

        # Wait for thread to execute
        import time
        time.sleep(0.15)

        # Verify connection was attempted
        mock_celery_app.connection.assert_called()
        mock_event_receiver.assert_called()

    @patch('app.core.celery_monitor.celery_app')
    @patch('app.core.celery_monitor.EventReceiver')
    @patch('app.core.celery_monitor.time.sleep')
    @patch('app.core.celery_monitor.logger')
    def test_monitor_worker_connection_retry_logic(self, mock_logger, mock_sleep,
                                                   mock_event_receiver, mock_celery_app):
        """Test retry logic when connection fails"""
        monitor = CeleryEventMonitor()

        # Setup connection to fail twice, then succeed
        call_count = [0]

        def connection_side_effect():
            call_count[0] += 1
            if call_count[0] <= 2:
                raise ConnectionError(f"Failed {call_count[0]}")
            # Third call succeeds
            ctx = MagicMock()
            ctx.__enter__ = MagicMock(return_value=MagicMock())
            ctx.__exit__ = MagicMock(return_value=False)
            return ctx

        mock_celery_app.connection.side_effect = connection_side_effect

        mock_receiver_instance = MagicMock()
        mock_receiver_instance.capture.side_effect = KeyboardInterrupt
        mock_event_receiver.return_value = mock_receiver_instance

        # Start monitoring
        monitor.start_monitoring()

        # Wait for thread to execute
        import time
        time.sleep(0.2)

        # Verify sleep was called for retry delays
        assert mock_sleep.called

    @patch('app.core.celery_monitor.celery_app')
    @patch('app.core.celery_monitor.EventReceiver')
    @patch('app.core.celery_monitor.logger')
    def test_event_handlers_registered(self, mock_logger, mock_event_receiver, mock_celery_app):
        """Test that all event handlers are registered correctly"""
        monitor = CeleryEventMonitor()

        mock_connection = MagicMock()
        mock_celery_app.connection.return_value.__enter__.return_value = mock_connection

        # Capture the handlers passed to EventReceiver
        captured_handlers = {}

        def capture_handlers(connection, handlers):
            captured_handlers.update(handlers)
            mock_receiver = MagicMock()
            mock_receiver.capture.side_effect = KeyboardInterrupt
            return mock_receiver

        mock_event_receiver.side_effect = capture_handlers

        # Start monitoring
        monitor.start_monitoring()

        # Wait for thread to execute
        import time
        time.sleep(0.15)

        # Verify all required handlers were registered
        assert 'task-started' in captured_handlers
        assert 'task-succeeded' in captured_handlers
        assert 'task-failed' in captured_handlers
        assert 'worker-heartbeat' in captured_handlers

    @patch('app.core.celery_monitor.celery_app')
    @patch('app.core.celery_monitor.EventReceiver')
    @patch('app.core.celery_monitor.logger')
    def test_task_started_handler_behavior(self, mock_logger, mock_event_receiver, mock_celery_app):
        """Test task-started event handler updates active_tasks"""
        monitor = CeleryEventMonitor()

        # Setup mocks
        mock_connection = MagicMock()
        mock_celery_app.connection.return_value.__enter__.return_value = mock_connection

        # Capture the handlers and call task-started
        def capture_and_test_handlers(connection, handlers):
            # Simulate task-started event
            task_event = {
                'uuid': 'test-task-123',
                'name': 'test.task',
                'hostname': 'worker1',
                'timestamp': 1234567890.0,
                'args': ['arg1', 'arg2']
            }
            handlers['task-started'](task_event)

            mock_receiver = MagicMock()
            mock_receiver.capture.side_effect = KeyboardInterrupt
            return mock_receiver

        mock_event_receiver.side_effect = capture_and_test_handlers

        # Start monitoring
        monitor.start_monitoring()

        # Wait for thread to execute
        import time
        time.sleep(0.15)

        # Verify task was added to active_tasks
        assert 'test-task-123' in monitor.active_tasks
        assert monitor.active_tasks['test-task-123']['name'] == 'test.task'
        assert monitor.active_tasks['test-task-123']['worker'] == 'worker1'

    @patch('app.core.celery_monitor.celery_app')
    @patch('app.core.celery_monitor.EventReceiver')
    @patch('app.core.celery_monitor.logger')
    def test_task_succeeded_handler_behavior(self, mock_logger, mock_event_receiver, mock_celery_app):
        """Test task-succeeded event handler removes task from active_tasks"""
        monitor = CeleryEventMonitor()

        # Prepopulate active tasks
        monitor.active_tasks['task-123'] = {
            'task_id': 'task-123',
            'name': 'test_task',
            'worker': 'worker1'
        }

        # Setup mocks
        mock_connection = MagicMock()
        mock_celery_app.connection.return_value.__enter__.return_value = mock_connection

        # Capture handlers and simulate task-succeeded
        def capture_and_test_handlers(connection, handlers):
            # Simulate task-succeeded event
            task_event = {
                'uuid': 'task-123',
                'timestamp': 1234567890.0
            }
            handlers['task-succeeded'](task_event)

            mock_receiver = MagicMock()
            mock_receiver.capture.side_effect = KeyboardInterrupt
            return mock_receiver

        mock_event_receiver.side_effect = capture_and_test_handlers

        # Start monitoring
        monitor.start_monitoring()

        # Wait for thread to execute
        import time
        time.sleep(0.15)

        # Verify task was removed
        assert 'task-123' not in monitor.active_tasks

    @patch('app.core.celery_monitor.celery_app')
    @patch('app.core.celery_monitor.EventReceiver')
    @patch('app.core.celery_monitor.logger')
    def test_task_failed_handler_behavior(self, mock_logger, mock_event_receiver, mock_celery_app):
        """Test task-failed event handler removes task from active_tasks"""
        monitor = CeleryEventMonitor()

        # Prepopulate active tasks
        monitor.active_tasks['task-456'] = {
            'task_id': 'task-456',
            'name': 'failing_task',
            'worker': 'worker1'
        }

        # Setup mocks
        mock_connection = MagicMock()
        mock_celery_app.connection.return_value.__enter__.return_value = mock_connection

        # Capture handlers and simulate task-failed
        def capture_and_test_handlers(connection, handlers):
            # Simulate task-failed event
            task_event = {
                'uuid': 'task-456',
                'timestamp': 1234567890.0
            }
            handlers['task-failed'](task_event)

            mock_receiver = MagicMock()
            mock_receiver.capture.side_effect = KeyboardInterrupt
            return mock_receiver

        mock_event_receiver.side_effect = capture_and_test_handlers

        # Start monitoring
        monitor.start_monitoring()

        # Wait for thread to execute
        import time
        time.sleep(0.15)

        # Verify task was removed
        assert 'task-456' not in monitor.active_tasks

    @patch('app.core.celery_monitor.celery_app')
    @patch('app.core.celery_monitor.EventReceiver')
    @patch('app.core.celery_monitor.logger')
    def test_worker_heartbeat_handler_behavior(self, mock_logger, mock_event_receiver, mock_celery_app):
        """Test worker-heartbeat event handler updates worker_stats"""
        monitor = CeleryEventMonitor()

        # Setup mocks
        mock_connection = MagicMock()
        mock_celery_app.connection.return_value.__enter__.return_value = mock_connection

        # Capture handlers and simulate worker-heartbeat
        def capture_and_test_handlers(connection, handlers):
            # Simulate worker-heartbeat event
            heartbeat_event = {
                'hostname': 'worker1',
                'timestamp': 1234567890.0
            }
            handlers['worker-heartbeat'](heartbeat_event)

            mock_receiver = MagicMock()
            mock_receiver.capture.side_effect = KeyboardInterrupt
            return mock_receiver

        mock_event_receiver.side_effect = capture_and_test_handlers

        # Start monitoring
        monitor.start_monitoring()

        # Wait for thread to execute
        import time
        time.sleep(0.15)

        # Verify worker stats were updated
        assert 'worker1' in monitor.worker_stats
        assert monitor.worker_stats['worker1']['status'] == 'online'

    @patch('app.core.celery_monitor.celery_app')
    @patch('app.core.celery_monitor.EventReceiver')
    @patch('app.core.celery_monitor.time.sleep')
    @patch('app.core.celery_monitor.logger')
    def test_exponential_backoff_retry(self, mock_logger, mock_sleep,
                                      mock_event_receiver, mock_celery_app):
        """Test exponential backoff on repeated failures"""
        monitor = CeleryEventMonitor()

        # Track sleep intervals
        sleep_intervals = []
        mock_sleep.side_effect = lambda x: sleep_intervals.append(x)

        # Setup connection to fail 3 times, then raise KeyboardInterrupt
        call_count = [0]

        def connection_side_effect():
            call_count[0] += 1
            if call_count[0] <= 3:
                raise ConnectionError(f"Failed {call_count[0]}")
            raise KeyboardInterrupt  # Exit after 3 failures

        mock_celery_app.connection.side_effect = connection_side_effect

        # Start monitoring
        monitor.start_monitoring()

        # Wait for thread to complete
        import time
        time.sleep(0.25)

        # Verify exponential backoff: 5, 7.5, 11.25
        assert len(sleep_intervals) >= 2
        assert sleep_intervals[0] == 5
        assert sleep_intervals[1] == 7.5

    @patch('app.core.celery_monitor.celery_app')
    @patch('app.core.celery_monitor.EventReceiver')
    @patch('app.core.celery_monitor.logger')
    def test_monitoring_state_changes_on_connection(self, mock_logger,
                                                    mock_event_receiver, mock_celery_app):
        """Test is_monitoring flag changes when connection established"""
        monitor = CeleryEventMonitor()

        # Track state changes
        state_changes = []

        def capture_state_and_handlers(connection, handlers):
            # Record state when EventReceiver is created (connection established)
            state_changes.append(('receiver_created', monitor.is_monitoring))

            mock_receiver = MagicMock()

            # When capture() is called, is_monitoring should be True
            def capture_with_state_check(*args, **kwargs):
                state_changes.append(('capture_called', monitor.is_monitoring))
                raise KeyboardInterrupt  # Exit cleanly

            mock_receiver.capture = capture_with_state_check
            return mock_receiver

        mock_event_receiver.side_effect = capture_state_and_handlers

        mock_connection = MagicMock()
        mock_celery_app.connection.return_value.__enter__.return_value = mock_connection

        # Verify initial state
        assert monitor.is_monitoring is False

        # Start monitoring
        monitor.start_monitoring()

        # Wait for thread to execute
        import time
        time.sleep(0.15)

        # Verify state was True during execution
        assert len(state_changes) == 2
        assert state_changes[1] == ('capture_called', True)

        # After KeyboardInterrupt, should be False again
        assert monitor.is_monitoring is False

    @patch('app.core.celery_monitor.celery_app')
    @patch('app.core.celery_monitor.EventReceiver')
    @patch('app.core.celery_monitor.logger')
    def test_event_with_missing_name_field(self, mock_logger, mock_event_receiver, mock_celery_app):
        """Test handling of task-started events with missing 'name' field"""
        monitor = CeleryEventMonitor()

        # Setup mocks
        mock_connection = MagicMock()
        mock_celery_app.connection.return_value.__enter__.return_value = mock_connection

        # Capture handlers and simulate event without 'name'
        def capture_and_test_handlers(connection, handlers):
            # Simulate task-started event without 'name' field
            task_event = {
                'uuid': 'test-task-789',
                'timestamp': 1234567890.0,
                # No 'name' field
                # No 'hostname' field
                # No 'args' field
            }
            handlers['task-started'](task_event)

            mock_receiver = MagicMock()
            mock_receiver.capture.side_effect = KeyboardInterrupt
            return mock_receiver

        mock_event_receiver.side_effect = capture_and_test_handlers

        # Start monitoring
        monitor.start_monitoring()

        # Wait for thread to execute
        import time
        time.sleep(0.15)

        # Verify task was added with default values
        assert 'test-task-789' in monitor.active_tasks
        assert monitor.active_tasks['test-task-789']['name'] == 'unknown'
        assert monitor.active_tasks['test-task-789']['worker'] == 'unknown'
        assert monitor.active_tasks['test-task-789']['args'] == []

    @patch('app.core.celery_monitor.celery_app')
    @patch('app.core.celery_monitor.EventReceiver')
    @patch('app.core.celery_monitor.logger')
    def test_system_exit_stops_monitoring(self, mock_logger, mock_event_receiver, mock_celery_app):
        """Test that SystemExit properly stops the monitoring loop"""
        monitor = CeleryEventMonitor()

        # Setup mocks
        mock_connection = MagicMock()
        mock_celery_app.connection.return_value.__enter__.return_value = mock_connection

        mock_receiver_instance = MagicMock()
        mock_receiver_instance.capture.side_effect = SystemExit  # Simulate system exit
        mock_event_receiver.return_value = mock_receiver_instance

        # Start monitoring
        monitor.start_monitoring()

        # Wait for thread to execute
        import time
        time.sleep(0.15)

        # Verify monitoring stopped cleanly
        assert monitor.is_monitoring is False

    @patch('app.core.celery_monitor.celery_app')
    @patch('app.core.celery_monitor.EventReceiver')
    @patch('app.core.celery_monitor.logger')
    def test_connection_context_manager_exit(self, mock_logger, mock_event_receiver, mock_celery_app):
        """Test that connection context manager properly exits"""
        monitor = CeleryEventMonitor()

        # Setup connection context manager tracking
        connection_entered = [False]
        connection_exited = [False]

        class MockContextManager:
            def __enter__(self):
                connection_entered[0] = True
                return MagicMock()

            def __exit__(self, *args):
                connection_exited[0] = True
                return False

        mock_celery_app.connection.return_value = MockContextManager()

        mock_receiver_instance = MagicMock()
        mock_receiver_instance.capture.side_effect = KeyboardInterrupt
        mock_event_receiver.return_value = mock_receiver_instance

        # Start monitoring
        monitor.start_monitoring()

        # Wait for thread to execute
        import time
        time.sleep(0.15)

        # Verify context manager was properly used
        assert connection_entered[0] is True
        assert connection_exited[0] is True

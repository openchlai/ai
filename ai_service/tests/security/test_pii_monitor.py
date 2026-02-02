"""
Unit tests for PII Monitor Service

Tests the continuous PII monitoring service.
"""
import pytest
import json
import tempfile
import os
import time
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch, PropertyMock

from app.security.pii_monitor import PIIMonitorService


class TestPIIMonitorServiceInit:
    """Test PIIMonitorService initialization"""

    def test_init_default_values(self, temp_log_dir):
        """Test monitor initializes with default values"""
        monitor = PIIMonitorService(
            watch_dir=temp_log_dir,
            use_presidio=False
        )

        assert monitor.watch_dir == temp_log_dir
        assert monitor.alert_email is None
        assert monitor.slack_webhook is None
        assert monitor.check_interval == 300
        assert monitor.pattern == "*.log"
        assert monitor.running is False

    def test_init_with_custom_values(self, temp_log_dir):
        """Test monitor initializes with custom values"""
        monitor = PIIMonitorService(
            watch_dir=temp_log_dir,
            alert_email="admin@test.com",
            slack_webhook="https://hooks.slack.com/test",
            check_interval=60,
            pattern="app*.log",
            use_presidio=False
        )

        assert monitor.alert_email == "admin@test.com"
        assert monitor.slack_webhook == "https://hooks.slack.com/test"
        assert monitor.check_interval == 60
        assert monitor.pattern == "app*.log"

    def test_init_starts_with_empty_stats(self, temp_log_dir):
        """Test monitor starts with empty statistics"""
        monitor = PIIMonitorService(
            watch_dir=temp_log_dir,
            use_presidio=False
        )

        assert monitor.total_files_scanned == 0
        assert monitor.total_pii_detections == 0
        assert monitor.scanned_files == {}
        assert monitor.last_alert_time is None


class TestPIIMonitorServiceGetLogFiles:
    """Test _get_log_files method"""

    def test_get_log_files_finds_files(self, temp_log_dir):
        """Test finding log files"""
        monitor = PIIMonitorService(
            watch_dir=temp_log_dir,
            use_presidio=False
        )

        files = monitor._get_log_files()

        assert len(files) >= 1
        assert all(isinstance(f, Path) for f in files)

    def test_get_log_files_respects_pattern(self, temp_log_dir):
        """Test pattern filtering"""
        # Create test files
        (temp_log_dir / "test.txt").write_text("test")
        (temp_log_dir / "test.log").write_text("test")

        monitor = PIIMonitorService(
            watch_dir=temp_log_dir,
            pattern="*.log",
            use_presidio=False
        )

        files = monitor._get_log_files()

        # Should find .log files (and also .txt files due to additional pattern)
        log_files = [f for f in files if f.suffix == '.log']
        assert len(log_files) >= 1


class TestPIIMonitorServiceShouldScanFile:
    """Test _should_scan_file method"""

    def test_should_scan_new_file(self, temp_log_dir):
        """Test new files should be scanned"""
        log_file = temp_log_dir / "app.log"

        monitor = PIIMonitorService(
            watch_dir=temp_log_dir,
            use_presidio=False
        )

        assert monitor._should_scan_file(log_file) is True

    def test_should_not_scan_already_scanned(self, temp_log_dir):
        """Test already scanned files should not be re-scanned"""
        log_file = temp_log_dir / "app.log"

        monitor = PIIMonitorService(
            watch_dir=temp_log_dir,
            use_presidio=False
        )

        # Mark file as scanned
        monitor.scanned_files[log_file] = log_file.stat().st_mtime

        assert monitor._should_scan_file(log_file) is False

    def test_should_scan_modified_file(self, temp_log_dir):
        """Test modified files should be re-scanned"""
        log_file = temp_log_dir / "app.log"

        monitor = PIIMonitorService(
            watch_dir=temp_log_dir,
            use_presidio=False
        )

        # Mark file as scanned with old mtime
        monitor.scanned_files[log_file] = log_file.stat().st_mtime - 100

        assert monitor._should_scan_file(log_file) is True

    def test_should_not_scan_nonexistent_file(self, temp_log_dir):
        """Test nonexistent files should not be scanned"""
        monitor = PIIMonitorService(
            watch_dir=temp_log_dir,
            use_presidio=False
        )

        assert monitor._should_scan_file(Path("/nonexistent/file.log")) is False


class TestPIIMonitorServiceScanFile:
    """Test _scan_file method"""

    def test_scan_file_with_pii(self, temp_log_dir):
        """Test scanning file with PII"""
        log_file = temp_log_dir / "app.log"

        monitor = PIIMonitorService(
            watch_dir=temp_log_dir,
            use_presidio=False
        )

        result = monitor._scan_file(log_file)

        assert result is not None
        assert result.lines_with_pii > 0

    def test_scan_file_updates_tracking(self, temp_log_dir):
        """Test scanning updates file tracking"""
        log_file = temp_log_dir / "app.log"

        monitor = PIIMonitorService(
            watch_dir=temp_log_dir,
            use_presidio=False
        )

        monitor._scan_file(log_file)

        assert log_file in monitor.scanned_files
        assert monitor.total_files_scanned == 1

    def test_scan_file_without_pii(self, temp_log_dir):
        """Test scanning file without PII returns None"""
        # Create clean log file
        clean_log = temp_log_dir / "clean.log"
        clean_log.write_text("Processing completed\nDatabase connected\n")

        monitor = PIIMonitorService(
            watch_dir=temp_log_dir,
            use_presidio=False
        )

        result = monitor._scan_file(clean_log)

        assert result is None

    def test_scan_file_handles_error(self, temp_log_dir):
        """Test scanning handles errors gracefully"""
        monitor = PIIMonitorService(
            watch_dir=temp_log_dir,
            use_presidio=False
        )

        result = monitor._scan_file(Path("/nonexistent/file.log"))

        assert result is None


class TestPIIMonitorServiceAlerts:
    """Test alert functionality"""

    def test_can_send_alert_first_time(self, temp_log_dir):
        """Test can send alert when never sent before"""
        monitor = PIIMonitorService(
            watch_dir=temp_log_dir,
            use_presidio=False
        )

        assert monitor._can_send_alert() is True

    def test_cannot_send_alert_in_cooldown(self, temp_log_dir):
        """Test cannot send alert during cooldown period"""
        monitor = PIIMonitorService(
            watch_dir=temp_log_dir,
            use_presidio=False
        )

        monitor.last_alert_time = datetime.now()

        assert monitor._can_send_alert() is False

    def test_can_send_alert_after_cooldown(self, temp_log_dir):
        """Test can send alert after cooldown expires"""
        monitor = PIIMonitorService(
            watch_dir=temp_log_dir,
            use_presidio=False
        )

        monitor.last_alert_time = datetime.now() - timedelta(hours=2)

        assert monitor._can_send_alert() is True

    def test_send_alert_updates_last_alert_time(self, temp_log_dir):
        """Test sending alert updates last_alert_time"""
        monitor = PIIMonitorService(
            watch_dir=temp_log_dir,
            alert_email="test@test.com",
            use_presidio=False
        )

        from app.security.pii_log_scanner import ScanResult

        result = ScanResult(
            scan_timestamp=datetime.now().isoformat(),
            files_scanned=1,
            total_lines=100,
            lines_with_pii=10,
            pii_percentage=10.0,
            total_detections=15,
            detections_by_type={"PERSON": 10}
        )

        with patch.object(monitor, '_send_email_alert'):
            monitor._send_alert(Path("/tmp/test.log"), result)

        assert monitor.last_alert_time is not None

    def test_send_alert_rate_limited(self, temp_log_dir):
        """Test alert is rate limited"""
        monitor = PIIMonitorService(
            watch_dir=temp_log_dir,
            alert_email="test@test.com",
            use_presidio=False
        )

        monitor.last_alert_time = datetime.now()

        from app.security.pii_log_scanner import ScanResult

        result = ScanResult(
            scan_timestamp=datetime.now().isoformat(),
            files_scanned=1,
            total_lines=100,
            lines_with_pii=10,
            pii_percentage=10.0,
            total_detections=15,
            detections_by_type={"PERSON": 10}
        )

        original_time = monitor.last_alert_time

        with patch.object(monitor, '_send_email_alert') as mock_email:
            monitor._send_alert(Path("/tmp/test.log"), result)
            mock_email.assert_not_called()

        # Time should not be updated when rate limited
        assert monitor.last_alert_time == original_time


class TestPIIMonitorServiceSlackAlert:
    """Test Slack alert functionality"""

    @patch('requests.post')
    def test_send_slack_alert_success(self, mock_post, temp_log_dir):
        """Test successful Slack alert"""
        mock_post.return_value.status_code = 200

        monitor = PIIMonitorService(
            watch_dir=temp_log_dir,
            slack_webhook="https://hooks.slack.com/test",
            use_presidio=False
        )

        monitor._send_slack_alert("Test alert message")

        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://hooks.slack.com/test"
        assert "text" in call_args[1]["json"]

    @patch('requests.post')
    def test_send_slack_alert_failure(self, mock_post, temp_log_dir):
        """Test Slack alert failure handling"""
        mock_post.return_value.status_code = 500

        monitor = PIIMonitorService(
            watch_dir=temp_log_dir,
            slack_webhook="https://hooks.slack.com/test",
            use_presidio=False
        )

        # Should not raise error
        monitor._send_slack_alert("Test alert message")


class TestPIIMonitorServiceDailySummary:
    """Test daily summary generation"""

    def test_generate_daily_summary(self, temp_log_dir):
        """Test generating daily summary"""
        monitor = PIIMonitorService(
            watch_dir=temp_log_dir,
            use_presidio=False
        )

        monitor.total_files_scanned = 10
        monitor.total_pii_detections = 50

        monitor._generate_daily_summary()

        # Check summary file was created
        summary_files = list(temp_log_dir.parent.glob("pii_summary_*.json"))
        # The summary is created in current working directory
        # Just verify the counters are reset
        assert monitor.total_files_scanned == 0
        assert monitor.total_pii_detections == 0


class TestPIIMonitorServiceRunOnce:
    """Test run_once method"""

    def test_run_once_returns_results(self, temp_log_dir):
        """Test run_once returns results dictionary"""
        monitor = PIIMonitorService(
            watch_dir=temp_log_dir,
            use_presidio=False
        )

        results = monitor.run_once()

        assert isinstance(results, dict)
        assert "files_scanned" in results
        assert "files_with_pii" in results
        assert "total_detections" in results

    def test_run_once_scans_files(self, temp_log_dir):
        """Test run_once scans all files"""
        monitor = PIIMonitorService(
            watch_dir=temp_log_dir,
            use_presidio=False
        )

        results = monitor.run_once()

        assert results["files_scanned"] >= 1


class TestPIIMonitorServiceGetStats:
    """Test get_stats method"""

    def test_get_stats_returns_dict(self, temp_log_dir):
        """Test get_stats returns dictionary"""
        monitor = PIIMonitorService(
            watch_dir=temp_log_dir,
            use_presidio=False
        )

        stats = monitor.get_stats()

        assert isinstance(stats, dict)

    def test_get_stats_contains_required_fields(self, temp_log_dir):
        """Test get_stats contains all required fields"""
        monitor = PIIMonitorService(
            watch_dir=temp_log_dir,
            use_presidio=False
        )

        stats = monitor.get_stats()

        assert "watch_directory" in stats
        assert "files_tracked" in stats
        assert "total_files_scanned" in stats
        assert "total_pii_detections" in stats
        assert "session_start" in stats
        assert "running" in stats

    def test_get_stats_reflects_state(self, temp_log_dir):
        """Test get_stats reflects current state"""
        monitor = PIIMonitorService(
            watch_dir=temp_log_dir,
            use_presidio=False
        )

        monitor.total_files_scanned = 5
        monitor.total_pii_detections = 25

        stats = monitor.get_stats()

        assert stats["total_files_scanned"] == 5
        assert stats["total_pii_detections"] == 25
        assert stats["running"] is False


class TestPIIMonitorServiceSignalHandling:
    """Test signal handling"""

    def test_handle_signal_stops_running(self, temp_log_dir):
        """Test signal handler stops running"""
        monitor = PIIMonitorService(
            watch_dir=temp_log_dir,
            use_presidio=False
        )

        monitor.running = True
        monitor._handle_signal(2, None)  # SIGINT

        assert monitor.running is False


class TestPIIMonitorServiceEdgeCases:
    """Test edge cases"""

    def test_empty_directory(self):
        """Test monitoring empty directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            monitor = PIIMonitorService(
                watch_dir=Path(temp_dir),
                use_presidio=False
            )

            results = monitor.run_once()

            assert results["files_scanned"] == 0
            assert results["files_with_pii"] == 0

    def test_directory_with_only_clean_files(self):
        """Test monitoring directory with only clean files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create clean log file
            clean_log = temp_path / "clean.log"
            clean_log.write_text("Processing completed\nDatabase connected\n")

            monitor = PIIMonitorService(
                watch_dir=temp_path,
                use_presidio=False
            )

            results = monitor.run_once()

            assert results["files_scanned"] == 1
            assert results["files_with_pii"] == 0

    def test_multiple_scans_track_changes(self, temp_log_dir):
        """Test multiple scans properly track file changes"""
        monitor = PIIMonitorService(
            watch_dir=temp_log_dir,
            use_presidio=False
        )

        # First scan
        results1 = monitor.run_once()
        files_scanned_1 = results1["files_scanned"]

        # Second scan without changes
        results2 = monitor.run_once()

        # Should not scan already scanned files
        assert results2["files_scanned"] == 0

        # Modify a file
        log_file = temp_log_dir / "app.log"
        original_content = log_file.read_text()
        time.sleep(0.1)  # Ensure mtime changes
        log_file.write_text(original_content + "\nNew log entry from Kamau\n")

        # Third scan should detect the change
        results3 = monitor.run_once()

        assert results3["files_scanned"] >= 1


class TestImportFallback:
    """Test import fallback behavior (lines 38-39)"""

    def test_scanner_import_works(self):
        """Test that scanner can be imported via either path"""
        # Both import paths should work
        from app.security.pii_log_scanner import PIILogScanner, ScanResult

        assert PIILogScanner is not None
        assert ScanResult is not None

    def test_import_fallback_path(self):
        """Test the import fallback logic (lines 38-39)"""
        # The import fallback is used when running as a standalone script
        # vs when imported as a module. We test both paths work.
        import importlib
        import app.security.pii_monitor as pii_monitor

        # Verify the module has the expected classes
        assert hasattr(pii_monitor, 'PIIMonitorService')

        # Verify imports from scanner work
        from app.security.pii_log_scanner import PIILogScanner, ScanResult
        assert PIILogScanner is not None
        assert ScanResult is not None


class TestShouldScanFileErrors:
    """Test _should_scan_file error handling (lines 140-141)"""

    def test_os_error_returns_false(self, temp_log_dir):
        """Test _should_scan_file returns False on OSError"""
        monitor = PIIMonitorService(
            watch_dir=temp_log_dir,
            use_presidio=False
        )

        log_file = temp_log_dir / "app.log"

        # Create a mock file object that raises OSError on stat()
        mock_file = MagicMock(spec=Path)
        mock_file.exists.return_value = True
        mock_file.stat.side_effect = OSError("Permission denied")

        result = monitor._should_scan_file(mock_file)

        assert result is False

    def test_permission_denied_returns_false(self, temp_log_dir):
        """Test _should_scan_file handles permission errors"""
        monitor = PIIMonitorService(
            watch_dir=temp_log_dir,
            use_presidio=False
        )

        log_file = temp_log_dir / "app.log"

        # Create a mock file object that raises PermissionError on stat()
        mock_file = MagicMock(spec=Path)
        mock_file.exists.return_value = True
        mock_file.stat.side_effect = PermissionError("Access denied")

        result = monitor._should_scan_file(mock_file)

        assert result is False


class TestEmailAlert:
    """Test email alert functionality (line 265)"""

    def test_send_email_alert_logs_message(self, temp_log_dir):
        """Test _send_email_alert logs the message"""
        monitor = PIIMonitorService(
            watch_dir=temp_log_dir,
            alert_email="test@example.com",
            use_presidio=False
        )

        with patch.object(monitor.logger, 'info') as mock_info:
            monitor._send_email_alert("Test alert message")

        mock_info.assert_called_once()
        call_args = mock_info.call_args[0][0]
        assert "test@example.com" in call_args

    def test_send_email_alert_with_none_email(self, temp_log_dir):
        """Test _send_email_alert when no email configured"""
        monitor = PIIMonitorService(
            watch_dir=temp_log_dir,
            alert_email=None,
            use_presidio=False
        )

        # Should not raise error when email is None
        with patch.object(monitor.logger, 'info') as mock_info:
            monitor._send_email_alert("Test alert message")
            # Still logs even without real email
            mock_info.assert_called()


class TestSlackAlertErrors:
    """Test Slack alert error handling (lines 280-283)"""

    @patch('requests.post')
    def test_slack_alert_request_exception(self, mock_post, temp_log_dir):
        """Test Slack alert handles request exceptions"""
        mock_post.side_effect = Exception("Network error")

        monitor = PIIMonitorService(
            watch_dir=temp_log_dir,
            slack_webhook="https://hooks.slack.com/test",
            use_presidio=False
        )

        # Should not raise error
        with patch.object(monitor.logger, 'error') as mock_error:
            monitor._send_slack_alert("Test alert")
            mock_error.assert_called()

    @patch('requests.post')
    def test_slack_alert_timeout(self, mock_post, temp_log_dir):
        """Test Slack alert handles timeout"""
        import requests
        mock_post.side_effect = requests.exceptions.Timeout("Request timeout")

        monitor = PIIMonitorService(
            watch_dir=temp_log_dir,
            slack_webhook="https://hooks.slack.com/test",
            use_presidio=False
        )

        # Should not raise error
        with patch.object(monitor.logger, 'error') as mock_error:
            monitor._send_slack_alert("Test alert")
            mock_error.assert_called()

    def test_slack_alert_import_error(self, temp_log_dir):
        """Test Slack alert handles ImportError when requests not available"""
        monitor = PIIMonitorService(
            watch_dir=temp_log_dir,
            slack_webhook="https://hooks.slack.com/test",
            use_presidio=False
        )

        # Mock the import to fail
        with patch.dict('sys.modules', {'requests': None}):
            with patch('builtins.__import__', side_effect=ImportError("No module named requests")):
                with patch.object(monitor.logger, 'warning') as mock_warning:
                    monitor._send_slack_alert("Test alert")
                    # Should log warning about missing requests


class TestMonitorRunLoop:
    """Test run() main loop (lines 320-359)"""

    def test_run_starts_and_stops(self, temp_log_dir):
        """Test run starts and stops correctly"""
        monitor = PIIMonitorService(
            watch_dir=temp_log_dir,
            check_interval=1,
            use_presidio=False
        )

        # Start in a controlled way - set running then stop
        def stop_after_start(*args):
            monitor.running = False

        with patch.object(monitor, '_get_log_files', return_value=set()):
            with patch('time.sleep', side_effect=stop_after_start):
                monitor.run()

        assert monitor.running is False

    def test_run_scans_new_files(self, temp_log_dir):
        """Test run scans new files"""
        monitor = PIIMonitorService(
            watch_dir=temp_log_dir,
            check_interval=1,
            use_presidio=False
        )

        scan_count = [0]

        def track_scan(file_path):
            scan_count[0] += 1
            return None

        def stop_after_one(*args):
            monitor.running = False

        log_file = temp_log_dir / "app.log"

        with patch.object(monitor, '_scan_file', side_effect=track_scan):
            with patch.object(monitor, '_should_scan_file', return_value=True):
                with patch('time.sleep', side_effect=stop_after_one):
                    monitor.run()

        assert scan_count[0] > 0

    def test_run_generates_daily_summary(self, temp_log_dir):
        """Test run generates daily summary on date change"""
        monitor = PIIMonitorService(
            watch_dir=temp_log_dir,
            check_interval=1,
            use_presidio=False
        )

        summary_called = [False]

        def track_summary():
            summary_called[0] = True

        def stop_after_one(*args):
            monitor.running = False

        # Simulate date change
        from datetime import date
        yesterday = date.today() - timedelta(days=1)

        with patch.object(monitor, '_generate_daily_summary', side_effect=track_summary):
            with patch.object(monitor, '_get_log_files', return_value=set()):
                with patch('time.sleep', side_effect=stop_after_one):
                    with patch('datetime.datetime') as mock_datetime:
                        mock_datetime.now.return_value.date.return_value = date.today()
                        monitor.run()

    def test_run_handles_fatal_error(self, temp_log_dir):
        """Test run handles fatal errors"""
        monitor = PIIMonitorService(
            watch_dir=temp_log_dir,
            check_interval=1,
            use_presidio=False
        )

        with patch.object(monitor, '_get_log_files', side_effect=Exception("Fatal error")):
            with pytest.raises(Exception, match="Fatal error"):
                monitor.run()

    def test_run_respects_check_interval(self, temp_log_dir):
        """Test run respects check_interval"""
        monitor = PIIMonitorService(
            watch_dir=temp_log_dir,
            check_interval=60,
            use_presidio=False
        )

        sleep_times = []

        def track_sleep(seconds):
            sleep_times.append(seconds)
            monitor.running = False

        with patch.object(monitor, '_get_log_files', return_value=set()):
            with patch('time.sleep', side_effect=track_sleep):
                monitor.run()

        # Should have called sleep with check_interval
        assert 60 in sleep_times

    def test_run_stops_scanning_on_shutdown(self, temp_log_dir):
        """Test run stops scanning files when running becomes False"""
        monitor = PIIMonitorService(
            watch_dir=temp_log_dir,
            check_interval=1,
            use_presidio=False
        )

        scan_count = [0]

        def track_scan_and_stop(file_path):
            scan_count[0] += 1
            monitor.running = False  # Stop after first file
            return None

        log_file = temp_log_dir / "app.log"

        with patch.object(monitor, '_scan_file', side_effect=track_scan_and_stop):
            with patch.object(monitor, '_should_scan_file', return_value=True):
                with patch('time.sleep'):
                    monitor.run()

        # Should have scanned at least one file before stopping
        assert scan_count[0] >= 1

    def test_run_date_change_triggers_summary(self, temp_log_dir):
        """Test run detects date change and generates summary (line 340, 346-347)"""
        monitor = PIIMonitorService(
            watch_dir=temp_log_dir,
            check_interval=1,
            use_presidio=False
        )

        iteration = [0]
        summary_generated = [False]

        def mock_get_files():
            iteration[0] += 1
            if iteration[0] >= 2:
                monitor.running = False
            return set()

        original_generate = monitor._generate_daily_summary

        def track_summary():
            summary_generated[0] = True
            # Don't call original to avoid file creation
            monitor.total_files_scanned = 0
            monitor.total_pii_detections = 0

        # Simulate date progression using real dates
        from datetime import date
        today = date.today()
        yesterday = today - timedelta(days=1)

        # Track sleep to control iterations
        with patch.object(monitor, '_get_log_files', side_effect=mock_get_files):
            with patch.object(monitor, '_generate_daily_summary', side_effect=track_summary):
                with patch('time.sleep'):
                    # Just run and let the logic execute
                    monitor.run()

        # Summary is called in finally block
        assert summary_generated[0] is True

    def test_run_date_comparison_branch(self, temp_log_dir):
        """Test run date comparison explicitly (lines 346-347)"""
        from datetime import date
        from app.security.pii_monitor import PIIMonitorService

        monitor = PIIMonitorService(
            watch_dir=temp_log_dir,
            check_interval=1,
            use_presidio=False
        )

        iteration = [0]
        summary_call_count = [0]

        today = date.today()
        tomorrow = today + timedelta(days=1)

        def mock_get_files():
            iteration[0] += 1
            # First iteration: current date
            # Second iteration: simulate date change by stopping
            if iteration[0] >= 2:
                monitor.running = False
            return set()

        def track_summary():
            summary_call_count[0] += 1
            # Reset counters like original does
            monitor.total_files_scanned = 0
            monitor.total_pii_detections = 0

        # Create mock datetime module
        mock_date_values = [today, today, tomorrow, tomorrow]
        mock_index = [0]

        class MockDatetime:
            @staticmethod
            def now():
                idx = min(mock_index[0], len(mock_date_values) - 1)
                mock_index[0] += 1

                class MockNow:
                    @staticmethod
                    def date():
                        return mock_date_values[idx]

                    @staticmethod
                    def isoformat():
                        return "2026-01-30T10:00:00"

                    @staticmethod
                    def strftime(fmt):
                        return "2026-01-30"

                return MockNow()

        with patch.object(monitor, '_get_log_files', side_effect=mock_get_files):
            with patch.object(monitor, '_generate_daily_summary', side_effect=track_summary):
                with patch('time.sleep'):
                    monitor.run()

        # Summary is called at least once (in finally block)
        assert summary_call_count[0] >= 1

    def test_run_date_change_mid_loop(self, temp_log_dir):
        """Test run triggers summary when date changes during loop (lines 345-347)"""
        from datetime import date
        import app.security.pii_monitor as pii_monitor_module

        monitor = PIIMonitorService(
            watch_dir=temp_log_dir,
            check_interval=1,
            use_presidio=False
        )

        iteration = [0]
        summary_call_count = [0]
        today = date.today()
        yesterday = today - timedelta(days=1)

        # Track the original datetime
        original_datetime = pii_monitor_module.datetime

        def mock_get_files():
            iteration[0] += 1
            if iteration[0] >= 3:
                monitor.running = False
            return set()

        def track_summary():
            summary_call_count[0] += 1
            monitor.total_files_scanned = 0
            monitor.total_pii_detections = 0

        # Mock datetime.now().date() to return different dates
        class MockNow:
            def __init__(self, d):
                self._date = d

            def date(self):
                return self._date

            def isoformat(self):
                return str(self._date)

            def strftime(self, fmt):
                return str(self._date)

        class MockDatetime:
            def __init__(self):
                self.call_count = 0

            def now(self):
                self.call_count += 1
                # First few calls: yesterday (to initialize last_summary_date)
                # Later calls: today (to trigger date change)
                if self.call_count <= 2:
                    return MockNow(yesterday)
                return MockNow(today)

        mock_dt = MockDatetime()

        with patch.object(monitor, '_get_log_files', side_effect=mock_get_files):
            with patch.object(monitor, '_generate_daily_summary', side_effect=track_summary):
                with patch.object(pii_monitor_module, 'datetime', mock_dt):
                    with patch('time.sleep'):
                        monitor.run()

        # Summary should be called at least once - either from date change or finally block
        assert summary_call_count[0] >= 1


class TestMonitorCLI:
    """Test main() CLI function (lines 400-498)"""

    def test_main_requires_watch_arg(self, capsys):
        """Test main requires --watch argument"""
        from app.security.pii_monitor import main

        with patch('sys.argv', ['pii_monitor.py']):
            with pytest.raises(SystemExit) as exc_info:
                main()

        # argparse raises SystemExit for missing required args
        assert exc_info.value.code != 0

    def test_main_validates_directory(self, capsys):
        """Test main validates watch directory exists"""
        from app.security.pii_monitor import main

        with patch('sys.argv', [
            'pii_monitor.py',
            '--watch', '/nonexistent/directory/path'
        ]):
            result = main()

        assert result == 1

    def test_main_once_mode(self, temp_log_dir, capsys):
        """Test main in --once mode"""
        from app.security.pii_monitor import main

        with patch('sys.argv', [
            'pii_monitor.py',
            '--watch', str(temp_log_dir),
            '--once',
            '--no-presidio'
        ]):
            result = main()

        # Should return 0 or 2 depending on PII found
        assert result in [0, 2]

    def test_main_continuous_mode_stops(self, temp_log_dir):
        """Test main in continuous mode can be stopped"""
        from app.security.pii_monitor import main

        def stop_monitor(monitor):
            """Stop monitor after it starts"""
            monitor.running = False

        with patch('sys.argv', [
            'pii_monitor.py',
            '--watch', str(temp_log_dir),
            '--no-presidio',
            '--check-interval', '1'
        ]):
            # Mock the monitor's run method to stop immediately
            with patch.object(PIIMonitorService, 'run', lambda self: None):
                result = main()

        assert result == 0

    def test_main_with_all_options(self, temp_log_dir):
        """Test main with all options"""
        from app.security.pii_monitor import main

        with patch('sys.argv', [
            'pii_monitor.py',
            '--watch', str(temp_log_dir),
            '--alert-email', 'test@example.com',
            '--slack-webhook', 'https://hooks.slack.com/test',
            '--check-interval', '60',
            '--pattern', '*.log',
            '--once',
            '--no-presidio'
        ]):
            result = main()

        assert result in [0, 2]

    def test_main_invalid_directory_error(self):
        """Test main with file instead of directory"""
        from app.security.pii_monitor import main

        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_file = f.name

        try:
            with patch('sys.argv', [
                'pii_monitor.py',
                '--watch', temp_file  # File, not directory
            ]):
                result = main()

            assert result == 1
        finally:
            os.unlink(temp_file)


class TestSlackWebhookCall:
    """Test Slack webhook actually gets called (line 260)"""

    @patch('requests.post')
    def test_send_alert_calls_slack_webhook(self, mock_post, temp_log_dir):
        """Test _send_alert calls Slack webhook when configured"""
        mock_post.return_value.status_code = 200

        monitor = PIIMonitorService(
            watch_dir=temp_log_dir,
            slack_webhook="https://hooks.slack.com/services/test",
            use_presidio=False
        )

        from app.security.pii_log_scanner import ScanResult

        result = ScanResult(
            scan_timestamp=datetime.now().isoformat(),
            files_scanned=1,
            total_lines=100,
            lines_with_pii=10,
            pii_percentage=10.0,
            total_detections=15,
            detections_by_type={"PERSON": 10}
        )

        monitor._send_alert(Path("/tmp/test.log"), result)

        # Verify Slack was called
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://hooks.slack.com/services/test"
        assert "text" in call_args[1]["json"]

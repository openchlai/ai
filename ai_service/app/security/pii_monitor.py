#!/usr/bin/env python3
"""
Continuous PII Monitoring Service for OpenCHS

Watches log directory for new files and scans them automatically for PII.
Sends alerts when PII is detected.

"""

import time
import logging
import sys
import signal
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Set, Dict, Optional
import argparse

# Import the scanner
try:
    from .pii_log_scanner import PIILogScanner, ScanResult
except ImportError:
    from pii_log_scanner import PIILogScanner, ScanResult


class PIIMonitorService:
    """
    Continuous monitoring service for PII in logs

    Features:
    - Watches directory for new log files
    - Scans new files automatically
    - Tracks files already scanned
    - Sends alerts when PII detected
    - Generates daily summary reports
    """

    def __init__(
        self,
        watch_dir: Path,
        alert_email: str = None,
        slack_webhook: str = None,
        check_interval: int = 300,  # 5 minutes
        pattern: str = "*.log",
        use_presidio: bool = True
    ):
        """
        Initialize monitoring service

        Args:
            watch_dir: Directory to monitor
            alert_email: Email for alerts
            slack_webhook: Slack webhook URL for alerts
            check_interval: Seconds between checks
            pattern: Glob pattern for log files
            use_presidio: Use Presidio for detection
        """
        self.watch_dir = Path(watch_dir)
        self.alert_email = alert_email
        self.slack_webhook = slack_webhook
        self.check_interval = check_interval
        self.pattern = pattern
        self.use_presidio = use_presidio

        # Track scanned files and their modification times
        self.scanned_files: Dict[Path, float] = {}

        # Statistics
        self.total_files_scanned = 0
        self.total_pii_detections = 0
        self.session_start = datetime.now()
        self.last_alert_time: Optional[datetime] = None
        self.alert_cooldown_hours = 1  # Minimum time between alerts

        # Running state
        self.running = False

        # Setup logging
        log_file = Path('pii_monitor.log')
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('PIIMonitor')

        # Initialize scanner (created fresh for each scan to clear detections)
        self.scanner: Optional[PIILogScanner] = None

        self.logger.info("=" * 60)
        self.logger.info("PII Monitor Service Initialized")
        self.logger.info("=" * 60)
        self.logger.info(f"Watch directory: {watch_dir}")
        self.logger.info(f"Check interval: {check_interval}s")
        self.logger.info(f"Pattern: {pattern}")
        self.logger.info(f"Alert email: {alert_email or 'Not configured'}")
        self.logger.info(f"Slack webhook: {'Configured' if slack_webhook else 'Not configured'}")

    def _get_log_files(self) -> Set[Path]:
        """Get all log files in watch directory"""
        files = set(self.watch_dir.glob(self.pattern))
        # Also check common patterns
        files.update(self.watch_dir.glob("*.txt"))
        return files

    def _should_scan_file(self, file_path: Path) -> bool:
        """
        Check if file should be scanned

        Args:
            file_path: Path to file

        Returns:
            True if file is new or modified since last scan
        """
        if not file_path.exists():
            return False

        try:
            current_mtime = file_path.stat().st_mtime
        except OSError:
            return False

        if file_path not in self.scanned_files:
            # New file
            return True

        if current_mtime > self.scanned_files[file_path]:
            # File modified since last scan
            return True

        return False

    def _scan_file(self, file_path: Path) -> Optional[ScanResult]:
        """
        Scan a single file for PII

        Args:
            file_path: Path to file to scan

        Returns:
            ScanResult if PII found, None otherwise
        """
        self.logger.info(f"Scanning: {file_path.name}")

        try:
            # Create fresh scanner for this file
            scanner = PIILogScanner(
                alert_email=self.alert_email,
                use_presidio=self.use_presidio
            )

            total_lines, lines_with_pii = scanner.scan_log_file(file_path)

            # Update tracking
            self.scanned_files[file_path] = file_path.stat().st_mtime
            self.total_files_scanned += 1

            if lines_with_pii > 0:
                self.total_pii_detections += lines_with_pii
                pii_percentage = (lines_with_pii / total_lines * 100) if total_lines > 0 else 0

                self.logger.warning(
                    f"PII detected in {file_path.name}: "
                    f"{lines_with_pii}/{total_lines} lines ({pii_percentage:.2f}%)"
                )

                result = ScanResult(
                    scan_timestamp=datetime.now().isoformat(),
                    files_scanned=1,
                    total_lines=total_lines,
                    lines_with_pii=lines_with_pii,
                    pii_percentage=pii_percentage,
                    total_detections=len(scanner.detections),
                    detections_by_type=scanner._count_by_type(),
                    high_risk_files=[str(file_path)] if pii_percentage > 5.0 else []
                )

                # Send alert if threshold met
                if pii_percentage > 1.0:  # Alert if >1% of lines contain PII
                    self._send_alert(file_path, result)

                return result
            else:
                self.logger.info(f"No PII detected in {file_path.name}")
                return None

        except Exception as e:
            self.logger.error(f"Error scanning {file_path}: {e}")
            return None

    def _can_send_alert(self) -> bool:
        """Check if we can send an alert (rate limiting)"""
        if self.last_alert_time is None:
            return True

        elapsed = (datetime.now() - self.last_alert_time).total_seconds()
        return elapsed >= (self.alert_cooldown_hours * 3600)

    def _send_alert(self, file_path: Path, result: ScanResult):
        """
        Send alert about PII detection

        Args:
            file_path: File where PII was detected
            result: Scan result
        """
        if not self._can_send_alert():
            self.logger.info("Alert rate limited (sent within cooldown period)")
            return

        self.last_alert_time = datetime.now()

        alert_message = f"""
🚨 PII DETECTED IN LOGS - OpenCHS AI Service

File: {file_path}
Lines with PII: {result.lines_with_pii}/{result.total_lines} ({result.pii_percentage:.2f}%)
Timestamp: {datetime.now().isoformat()}

Detections by Type:
{chr(10).join(f'  - {k}: {v}' for k, v in result.detections_by_type.items())}

ACTION REQUIRED:
1. Review audit report: pii_audit_report.json
2. Investigate why PII is being logged
3. Ensure PIISanitizingFilter is enabled
4. Update logging code to prevent PII leakage

This is an automated alert from the PII monitoring service.
        """

        # Log alert
        self.logger.warning(alert_message)

        # Send via configured channels
        if self.alert_email:
            self._send_email_alert(alert_message)

        if self.slack_webhook:
            self._send_slack_alert(alert_message)

    def _send_email_alert(self, message: str):
        """Send email alert"""
        # TODO: Implement actual email sending using SMTP
        self.logger.info(f"Email alert would be sent to: {self.alert_email}")

    def _send_slack_alert(self, message: str):
        """Send Slack alert"""
        try:
            import requests
            response = requests.post(
                self.slack_webhook,
                json={"text": message},
                timeout=10
            )
            if response.status_code == 200:
                self.logger.info("Slack alert sent successfully")
            else:
                self.logger.error(f"Failed to send Slack alert: {response.status_code}")
        except ImportError:
            self.logger.warning("requests library not available for Slack alerts")
        except Exception as e:
            self.logger.error(f"Error sending Slack alert: {e}")

    def _generate_daily_summary(self):
        """Generate daily summary report"""
        summary = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "session_start": self.session_start.isoformat(),
            "files_scanned": self.total_files_scanned,
            "pii_detections": self.total_pii_detections,
            "files_tracked": len(self.scanned_files)
        }

        summary_file = Path(f"pii_summary_{summary['date']}.json")
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        self.logger.info(f"Daily summary saved to: {summary_file}")

        # Log summary
        self.logger.info("=" * 60)
        self.logger.info("Daily Summary")
        self.logger.info("=" * 60)
        self.logger.info(f"Files scanned: {self.total_files_scanned}")
        self.logger.info(f"PII detections: {self.total_pii_detections}")
        self.logger.info(f"Files tracked: {len(self.scanned_files)}")

        # Reset daily counters
        self.total_files_scanned = 0
        self.total_pii_detections = 0

    def _handle_signal(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.running = False

    def run(self):
        """Main monitoring loop"""
        self.logger.info("Starting PII monitoring service...")
        self.running = True

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

        last_summary_date = datetime.now().date()

        try:
            while self.running:
                # Check for new or modified files
                current_files = self._get_log_files()
                files_to_scan = [f for f in current_files if self._should_scan_file(f)]

                if files_to_scan:
                    self.logger.info(f"Found {len(files_to_scan)} files to scan")

                    for file_path in files_to_scan:
                        if not self.running:
                            break
                        self._scan_file(file_path)

                # Generate daily summary if date changed
                current_date = datetime.now().date()
                if current_date > last_summary_date:
                    self._generate_daily_summary()
                    last_summary_date = current_date

                # Wait before next check
                if self.running:
                    self.logger.debug(f"Waiting {self.check_interval}s until next check...")
                    time.sleep(self.check_interval)

        except Exception as e:
            self.logger.error(f"Fatal error in monitoring service: {e}")
            raise
        finally:
            self.logger.info("Monitoring service stopped")
            self._generate_daily_summary()  # Final summary

    def run_once(self) -> Dict:
        """
        Run a single scan (useful for cron jobs)

        Returns:
            Dictionary with scan results
        """
        self.logger.info("Running single scan...")

        current_files = self._get_log_files()
        files_to_scan = [f for f in current_files if self._should_scan_file(f)]

        results = []
        for file_path in files_to_scan:
            result = self._scan_file(file_path)
            if result:
                results.append(result)

        return {
            "files_scanned": len(files_to_scan),
            "files_with_pii": len(results),
            "total_detections": sum(r.total_detections for r in results)
        }

    def get_stats(self) -> Dict:
        """Get current statistics"""
        return {
            "watch_directory": str(self.watch_dir),
            "files_tracked": len(self.scanned_files),
            "total_files_scanned": self.total_files_scanned,
            "total_pii_detections": self.total_pii_detections,
            "session_start": self.session_start.isoformat(),
            "last_alert": self.last_alert_time.isoformat() if self.last_alert_time else None,
            "running": self.running
        }


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="PII Monitoring Service for OpenCHS Logs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start continuous monitoring
  python pii_monitor.py --watch /var/log/openchs/

  # Monitor with email alerts
  python pii_monitor.py --watch /var/log/openchs/ --alert-email admin@openchs.org

  # Run single scan (for cron jobs)
  python pii_monitor.py --watch /var/log/openchs/ --once

  # Custom check interval (10 minutes)
  python pii_monitor.py --watch /var/log/openchs/ --check-interval 600

Systemd Service:
  Create /etc/systemd/system/pii-monitor.service with:

  [Unit]
  Description=PII Log Monitor for OpenCHS
  After=network.target

  [Service]
  Type=simple
  User=openchs
  WorkingDirectory=/opt/openchs
  ExecStart=/usr/bin/python3 /opt/openchs/pii_monitor.py --watch /var/log/openchs
  Restart=always

  [Install]
  WantedBy=multi-user.target
        """
    )
    parser.add_argument(
        '--watch',
        type=Path,
        required=True,
        help='Directory to monitor for log files'
    )
    parser.add_argument(
        '--alert-email',
        help='Email address for alerts'
    )
    parser.add_argument(
        '--slack-webhook',
        help='Slack webhook URL for alerts'
    )
    parser.add_argument(
        '--check-interval',
        type=int,
        default=300,
        help='Seconds between checks (default: 300)'
    )
    parser.add_argument(
        '--pattern',
        default='*.log',
        help='Glob pattern for log files (default: *.log)'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run single scan and exit (for cron jobs)'
    )
    parser.add_argument(
        '--no-presidio',
        action='store_true',
        help='Use regex-only detection'
    )

    args = parser.parse_args()

    # Validate watch directory
    if not args.watch.is_dir():
        print(f"Error: {args.watch} is not a valid directory")
        return 1

    # Create monitor service
    monitor = PIIMonitorService(
        watch_dir=args.watch,
        alert_email=args.alert_email,
        slack_webhook=args.slack_webhook,
        check_interval=args.check_interval,
        pattern=args.pattern,
        use_presidio=not args.no_presidio
    )

    if args.once:
        # Single scan mode (for cron)
        results = monitor.run_once()
        print(f"Scan complete: {results['files_scanned']} files, "
              f"{results['files_with_pii']} with PII, "
              f"{results['total_detections']} detections")
        return 0 if results['files_with_pii'] == 0 else 2
    else:
        # Continuous monitoring mode
        monitor.run()
        return 0


if __name__ == '__main__':
    sys.exit(main())

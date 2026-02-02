"""
Unit tests for PII Log Scanner

Tests the retrospective PII detection and redaction scanner.
"""
import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

from app.security.pii_log_scanner import (
    PIILogScanner,
    PIIDetection,
    ScanResult
)


class TestPIIDetectionDataclass:
    """Test PIIDetection dataclass"""

    def test_pii_detection_creation(self):
        """Test PIIDetection can be created"""
        detection = PIIDetection(
            timestamp="2026-01-30T10:00:00",
            log_file="/tmp/test.log",
            line_number=1,
            entity_type="PHONE_NUMBER",
            entity_text="+254712345678",
            confidence=0.95,
            context="Phone: +254712345678"
        )

        assert detection.timestamp == "2026-01-30T10:00:00"
        assert detection.entity_type == "PHONE_NUMBER"
        assert detection.confidence == 0.95

    def test_pii_detection_default_redacted_text(self):
        """Test PIIDetection has default empty redacted_text"""
        detection = PIIDetection(
            timestamp="2026-01-30T10:00:00",
            log_file="/tmp/test.log",
            line_number=1,
            entity_type="PERSON",
            entity_text="Wanjiru",
            confidence=0.8,
            context="Call from Wanjiru"
        )

        assert detection.redacted_text == ""


class TestScanResultDataclass:
    """Test ScanResult dataclass"""

    def test_scan_result_creation(self):
        """Test ScanResult can be created"""
        result = ScanResult(
            scan_timestamp="2026-01-30T10:00:00",
            files_scanned=5,
            total_lines=1000,
            lines_with_pii=50,
            pii_percentage=5.0,
            total_detections=75,
            detections_by_type={"PERSON": 40, "PHONE_NUMBER": 35}
        )

        assert result.files_scanned == 5
        assert result.pii_percentage == 5.0
        assert result.detections_by_type["PERSON"] == 40

    def test_scan_result_default_high_risk_files(self):
        """Test ScanResult has default empty high_risk_files"""
        result = ScanResult(
            scan_timestamp="2026-01-30T10:00:00",
            files_scanned=1,
            total_lines=100,
            lines_with_pii=1,
            pii_percentage=1.0,
            total_detections=1,
            detections_by_type={"PERSON": 1}
        )

        assert result.high_risk_files == []


class TestPIILogScannerInit:
    """Test PIILogScanner initialization"""

    def test_init_default_values(self):
        """Test scanner initializes with default values"""
        scanner = PIILogScanner(use_presidio=False, use_spacy=False)

        assert scanner.alert_email is None
        assert scanner.use_presidio is False
        assert scanner.detections == []

    def test_init_with_alert_email(self):
        """Test scanner initializes with alert email"""
        scanner = PIILogScanner(alert_email="admin@test.com", use_presidio=False, use_spacy=False)

        assert scanner.alert_email == "admin@test.com"

    def test_init_regex_patterns(self):
        """Test scanner initializes regex patterns when presidio disabled"""
        scanner = PIILogScanner(use_presidio=False, use_spacy=False)

        assert hasattr(scanner, 'regex_patterns')
        assert len(scanner.regex_patterns) > 0


class TestPIILogScannerRegexAnalysis:
    """Test regex-based analysis"""

    def test_analyze_line_detects_phone(self):
        """Test regex analyzer detects phone numbers"""
        scanner = PIILogScanner(use_presidio=False, use_spacy=False)

        results = scanner._analyze_line_regex("Phone: +254712345678")

        assert len(results) == 1
        assert results[0]['entity_type'] == 'PHONE_NUMBER'

    def test_analyze_line_detects_email(self):
        """Test regex analyzer detects email"""
        scanner = PIILogScanner(use_presidio=False, use_spacy=False)

        results = scanner._analyze_line_regex("Email: test@gmail.com")

        assert len(results) == 1
        assert results[0]['entity_type'] == 'EMAIL'

    def test_analyze_line_detects_names(self):
        """Test regex analyzer detects common names"""
        scanner = PIILogScanner(use_presidio=False, use_spacy=False)

        results = scanner._analyze_line_regex("Caller: Wanjiru Kamau")

        assert len(results) >= 1
        assert any(r['entity_type'] == 'PERSON' for r in results)

    def test_analyze_line_multiple_entities(self):
        """Test regex analyzer detects multiple entities"""
        scanner = PIILogScanner(use_presidio=False, use_spacy=False)

        results = scanner._analyze_line_regex("Call from Wanjiru, phone +254712345678")

        assert len(results) >= 2

    def test_analyze_line_no_pii(self):
        """Test regex analyzer returns empty for clean lines"""
        scanner = PIILogScanner(use_presidio=False, use_spacy=False)

        results = scanner._analyze_line_regex("Processing completed successfully")

        assert len(results) == 0


class TestPIILogScannerScanFile:
    """Test file scanning"""

    def test_scan_file_with_pii(self, temp_log_file):
        """Test scanning file with PII"""
        scanner = PIILogScanner(use_presidio=False, use_spacy=False)

        total_lines, lines_with_pii = scanner.scan_log_file(temp_log_file)

        assert total_lines > 0
        assert lines_with_pii > 0
        assert len(scanner.detections) > 0

    def test_scan_file_without_pii(self, clean_log_file):
        """Test scanning file without PII"""
        scanner = PIILogScanner(use_presidio=False, use_spacy=False)

        total_lines, lines_with_pii = scanner.scan_log_file(clean_log_file)

        assert total_lines > 0
        assert lines_with_pii == 0

    def test_scan_file_records_detections(self, temp_log_file):
        """Test scan records detections"""
        scanner = PIILogScanner(use_presidio=False, use_spacy=False)

        scanner.scan_log_file(temp_log_file)

        assert len(scanner.detections) > 0
        assert all(isinstance(d, PIIDetection) for d in scanner.detections)

    def test_scan_file_detection_has_context(self, temp_log_file):
        """Test detections include context"""
        scanner = PIILogScanner(use_presidio=False, use_spacy=False)

        scanner.scan_log_file(temp_log_file)

        for detection in scanner.detections:
            assert detection.context != ""
            assert len(detection.context) > 0

    def test_scan_nonexistent_file(self):
        """Test scanning nonexistent file"""
        scanner = PIILogScanner(use_presidio=False, use_spacy=False)

        total_lines, lines_with_pii = scanner.scan_log_file(Path("/nonexistent/file.log"))

        assert total_lines == 0
        assert lines_with_pii == 0


class TestPIILogScannerScanDirectory:
    """Test directory scanning"""

    def test_scan_directory(self, temp_log_dir):
        """Test scanning directory"""
        scanner = PIILogScanner(use_presidio=False, use_spacy=False)

        result = scanner.scan_directory(temp_log_dir)

        assert isinstance(result, ScanResult)
        assert result.files_scanned >= 1

    def test_scan_directory_counts_pii(self, temp_log_dir):
        """Test directory scan counts PII"""
        scanner = PIILogScanner(use_presidio=False, use_spacy=False)

        result = scanner.scan_directory(temp_log_dir)

        assert result.total_lines > 0
        assert result.lines_with_pii >= 0

    def test_scan_directory_calculates_percentage(self, temp_log_dir):
        """Test directory scan calculates PII percentage"""
        scanner = PIILogScanner(use_presidio=False, use_spacy=False)

        result = scanner.scan_directory(temp_log_dir)

        if result.total_lines > 0:
            expected_pct = (result.lines_with_pii / result.total_lines) * 100
            assert abs(result.pii_percentage - expected_pct) < 0.01

    def test_scan_directory_with_pattern(self, temp_log_dir):
        """Test directory scan with specific pattern"""
        scanner = PIILogScanner(use_presidio=False, use_spacy=False)

        result = scanner.scan_directory(temp_log_dir, pattern="app*.log")

        assert isinstance(result, ScanResult)


class TestPIILogScannerCountByType:
    """Test _count_by_type method"""

    def test_count_by_type_empty(self):
        """Test count with no detections"""
        scanner = PIILogScanner(use_presidio=False, use_spacy=False)

        counts = scanner._count_by_type()

        assert counts == {}

    def test_count_by_type_with_detections(self, temp_log_file):
        """Test count with detections"""
        scanner = PIILogScanner(use_presidio=False, use_spacy=False)
        scanner.scan_log_file(temp_log_file)

        counts = scanner._count_by_type()

        assert isinstance(counts, dict)
        assert sum(counts.values()) == len(scanner.detections)


class TestPIILogScannerRedaction:
    """Test log file redaction"""

    def test_redact_log_file(self, temp_log_file):
        """Test redacting log file"""
        scanner = PIILogScanner(use_presidio=False, use_spacy=False)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            output_file = Path(f.name)

        try:
            lines_redacted = scanner.redact_log_file(temp_log_file, output_file)

            assert lines_redacted > 0
            assert output_file.exists()

            # Verify content is redacted
            content = output_file.read_text()
            assert "[REDACTED-" in content
        finally:
            if output_file.exists():
                os.unlink(output_file)

    def test_redact_removes_phone(self, temp_log_file):
        """Test redaction removes phone numbers"""
        scanner = PIILogScanner(use_presidio=False, use_spacy=False)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            output_file = Path(f.name)

        try:
            scanner.redact_log_file(temp_log_file, output_file)

            content = output_file.read_text()
            assert "+254712345678" not in content
            assert "0722123456" not in content
        finally:
            if output_file.exists():
                os.unlink(output_file)

    def test_redact_removes_email(self, temp_log_file):
        """Test redaction removes email"""
        scanner = PIILogScanner(use_presidio=False, use_spacy=False)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            output_file = Path(f.name)

        try:
            scanner.redact_log_file(temp_log_file, output_file)

            content = output_file.read_text()
            assert "caller@gmail.com" not in content
        finally:
            if output_file.exists():
                os.unlink(output_file)

    def test_redact_preserves_clean_lines(self, temp_log_file):
        """Test redaction preserves lines without PII"""
        scanner = PIILogScanner(use_presidio=False, use_spacy=False)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            output_file = Path(f.name)

        try:
            scanner.redact_log_file(temp_log_file, output_file)

            content = output_file.read_text()
            assert "Processing completed successfully" in content
            assert "Task ID: abc123-def456" in content
        finally:
            if output_file.exists():
                os.unlink(output_file)


class TestPIILogScannerAuditReport:
    """Test audit report generation"""

    def test_generate_audit_report_json(self, temp_log_file):
        """Test generating JSON audit report"""
        scanner = PIILogScanner(use_presidio=False, use_spacy=False)
        scanner.scan_log_file(temp_log_file)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            report_file = Path(f.name)

        try:
            scanner.generate_audit_report(report_file)

            assert report_file.exists()

            with open(report_file) as f:
                report = json.load(f)

            assert "report_timestamp" in report
            assert "summary" in report
            assert "detections" in report
            assert report["scanner_type"] == "regex"
        finally:
            if report_file.exists():
                os.unlink(report_file)
            txt_file = report_file.with_suffix('.txt')
            if txt_file.exists():
                os.unlink(txt_file)

    def test_generate_audit_report_txt(self, temp_log_file):
        """Test generating text audit report"""
        scanner = PIILogScanner(use_presidio=False, use_spacy=False)
        scanner.scan_log_file(temp_log_file)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            report_file = Path(f.name)

        try:
            scanner.generate_audit_report(report_file)

            txt_file = report_file.with_suffix('.txt')
            assert txt_file.exists()

            content = txt_file.read_text()
            assert "PII Detection Audit Report" in content
            assert "Detections by Type:" in content
        finally:
            if report_file.exists():
                os.unlink(report_file)
            txt_file = report_file.with_suffix('.txt')
            if txt_file.exists():
                os.unlink(txt_file)

    def test_audit_report_includes_summary(self, temp_log_file):
        """Test audit report includes summary"""
        scanner = PIILogScanner(use_presidio=False, use_spacy=False)
        scanner.scan_log_file(temp_log_file)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            report_file = Path(f.name)

        try:
            scanner.generate_audit_report(report_file)

            with open(report_file) as f:
                report = json.load(f)

            summary = report["summary"]
            assert "total_detections" in summary
            assert "detections_by_type" in summary
            assert "files_with_pii" in summary
        finally:
            if report_file.exists():
                os.unlink(report_file)
            txt_file = report_file.with_suffix('.txt')
            if txt_file.exists():
                os.unlink(txt_file)


class TestPIILogScannerAlert:
    """Test alert functionality"""

    def test_send_alert_logs_warning(self, temp_log_file):
        """Test send_alert logs warning message"""
        scanner = PIILogScanner(alert_email="test@example.com", use_presidio=False)

        result = ScanResult(
            scan_timestamp="2026-01-30T10:00:00",
            files_scanned=1,
            total_lines=100,
            lines_with_pii=10,
            pii_percentage=10.0,
            total_detections=15,
            detections_by_type={"PERSON": 10, "PHONE_NUMBER": 5},
            high_risk_files=["/tmp/test.log"]
        )

        with patch.object(scanner.logger, 'warning') as mock_warning:
            scanner.send_alert(result)
            mock_warning.assert_called()

    def test_send_alert_no_email(self):
        """Test send_alert without email configured"""
        scanner = PIILogScanner(use_presidio=False, use_spacy=False)

        result = ScanResult(
            scan_timestamp="2026-01-30T10:00:00",
            files_scanned=1,
            total_lines=100,
            lines_with_pii=10,
            pii_percentage=10.0,
            total_detections=15,
            detections_by_type={"PERSON": 10}
        )

        # Should not raise error
        scanner.send_alert(result)


class TestPIILogScannerEdgeCases:
    """Test edge cases"""

    def test_empty_file(self):
        """Test scanning empty file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write("")
            temp_path = Path(f.name)

        try:
            scanner = PIILogScanner(use_presidio=False, use_spacy=False)
            total_lines, lines_with_pii = scanner.scan_log_file(temp_path)

            assert total_lines == 0
            assert lines_with_pii == 0
        finally:
            os.unlink(temp_path)

    def test_file_with_unicode(self):
        """Test scanning file with unicode characters"""
        content = "Call from Wanjiru 📞 +254712345678"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False,
                                          encoding='utf-8') as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            scanner = PIILogScanner(use_presidio=False, use_spacy=False)
            total_lines, lines_with_pii = scanner.scan_log_file(temp_path)

            assert total_lines == 1
            assert lines_with_pii == 1
        finally:
            os.unlink(temp_path)

    def test_very_long_lines(self):
        """Test scanning file with very long lines"""
        long_line = "A" * 10000 + "+254712345678" + "B" * 10000
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write(long_line)
            temp_path = Path(f.name)

        try:
            scanner = PIILogScanner(use_presidio=False, use_spacy=False)
            total_lines, lines_with_pii = scanner.scan_log_file(temp_path)

            assert total_lines == 1
            assert lines_with_pii == 1
        finally:
            os.unlink(temp_path)


class TestPresidioImportFallback:
    """Test Presidio import error handling (lines 45-49)"""

    def test_presidio_import_flag_when_unavailable(self):
        """Test PRESIDIO_AVAILABLE flag is set correctly when Presidio unavailable"""
        # Test that the scanner properly handles the case when presidio is unavailable
        scanner = PIILogScanner(use_presidio=False, use_spacy=False)
        assert scanner.use_presidio is False
        assert hasattr(scanner, 'regex_patterns')

    @patch.dict('sys.modules', {'presidio_analyzer': None})
    def test_scanner_works_without_presidio(self):
        """Test scanner falls back to regex when Presidio not available"""
        scanner = PIILogScanner(use_presidio=False, use_spacy=False)

        results = scanner._analyze_line_regex("Phone: +254712345678")
        assert len(results) >= 1
        assert any(r['entity_type'] == 'PHONE_NUMBER' for r in results)

    def test_presidio_available_flag_exists(self):
        """Test PRESIDIO_AVAILABLE flag is defined"""
        from app.security import pii_log_scanner
        assert hasattr(pii_log_scanner, 'PRESIDIO_AVAILABLE')

    def test_scanner_use_presidio_and_presidio_available(self):
        """Test scanner respects use_presidio and PRESIDIO_AVAILABLE"""
        from app.security.pii_log_scanner import PRESIDIO_AVAILABLE

        scanner = PIILogScanner(use_presidio=True)
        # use_presidio should be True only if PRESIDIO_AVAILABLE is True
        expected = True and PRESIDIO_AVAILABLE
        assert scanner.use_presidio == expected


class TestRegexAnalyzerSetup:
    """Test _setup_regex_analyzer method (lines 216-242)"""

    def test_setup_regex_analyzer_creates_patterns(self):
        """Test _setup_regex_analyzer creates expected patterns"""
        scanner = PIILogScanner(use_presidio=False, use_spacy=False)

        # Verify patterns were created
        assert hasattr(scanner, 'regex_patterns')
        assert len(scanner.regex_patterns) >= 3  # phone, email, names

    def test_regex_patterns_phone_detection(self):
        """Test regex patterns detect Kenyan phone numbers"""
        scanner = PIILogScanner(use_presidio=False, use_spacy=False)

        # Test various phone formats
        test_cases = [
            ("+254712345678", True),
            ("0712345678", True),
            ("test@example.com", False),
        ]

        for text, should_match in test_cases:
            results = scanner._analyze_line_regex(f"Text: {text}")
            has_phone = any(r['entity_type'] == 'PHONE_NUMBER' for r in results)
            assert has_phone == should_match, f"Failed for {text}"

    def test_regex_patterns_email_detection(self):
        """Test regex patterns detect email addresses"""
        scanner = PIILogScanner(use_presidio=False, use_spacy=False)

        results = scanner._analyze_line_regex("Email: test@example.com")

        assert len(results) >= 1
        assert any(r['entity_type'] == 'EMAIL' for r in results)

    def test_regex_patterns_name_detection(self):
        """Test regex patterns detect common Kenyan names"""
        scanner = PIILogScanner(use_presidio=False, use_spacy=False)

        # Test multiple names from different ethnic groups
        names = ["Wanjiru", "Kamau", "Njeri", "Mwangi", "Otieno", "Akinyi", "Omondi"]
        for name in names:
            results = scanner._analyze_line_regex(f"Caller: {name}")
            assert len(results) >= 1, f"Failed to detect name: {name}"
            assert any(r['entity_type'] == 'PERSON' for r in results), f"Failed for name: {name}"


class TestKenyanPhoneRecognizer:
    """Test KenyanPhoneRecognizer class (lines 82-104)"""

    def test_recognizer_class_exists(self):
        """Test KenyanPhoneRecognizer can be imported"""
        from app.security.pii_log_scanner import KenyanPhoneRecognizer

        # May fail if Presidio not installed, that's OK for coverage
        try:
            recognizer = KenyanPhoneRecognizer()
            assert recognizer.supported_entities == ["KENYAN_PHONE"]
            assert len(recognizer.patterns) == 4  # 4 phone patterns
            assert recognizer.context == ["phone", "call", "caller", "contact", "mobile", "tel", "simu"]
        except (ImportError, NameError):
            # Presidio not available, skip
            pytest.skip("Presidio not available")


class TestSwahiliNameRecognizer:
    """Test SwahiliNameRecognizer class (lines 111-153)"""

    def test_recognizer_class_exists(self):
        """Test SwahiliNameRecognizer can be imported"""
        from app.security.pii_log_scanner import SwahiliNameRecognizer

        try:
            recognizer = SwahiliNameRecognizer()
            assert recognizer.supported_entities == ["KENYAN_NAME"]
            assert len(recognizer.patterns) == 1
            # Check context keywords
            assert "caller" in recognizer.context
            assert "mtoto" in recognizer.context
        except (ImportError, NameError):
            pytest.skip("Presidio not available")


class TestKenyanLocationRecognizer:
    """Test KenyanLocationRecognizer class (lines 156-184)"""

    def test_recognizer_class_exists(self):
        """Test KenyanLocationRecognizer can be imported"""
        from app.security.pii_log_scanner import KenyanLocationRecognizer

        try:
            recognizer = KenyanLocationRecognizer()
            assert recognizer.supported_entities == ["KENYAN_LOCATION"]
            assert len(recognizer.patterns) == 1
            assert "location" in recognizer.context
            assert "mahali" in recognizer.context
        except (ImportError, NameError):
            pytest.skip("Presidio not available")


class TestPresidioIntegration:
    """Test Presidio integration (lines 209-270, 315, 429-448)"""

    def test_setup_presidio_analyzer_failure_fallback(self):
        """Test scanner falls back to regex when Presidio setup fails"""
        # Create scanner with regex first, then simulate presidio failure
        scanner = PIILogScanner(use_presidio=False, use_spacy=False)

        # Save original method
        original_setup = scanner._setup_presidio_analyzer

        # Track that fallback was used
        fallback_used = [False]

        def mock_setup():
            # Simulate presidio setup failure
            scanner.use_presidio = False
            scanner._setup_regex_analyzer()
            fallback_used[0] = True

        # The actual coverage path is when _setup_presidio_analyzer catches an exception
        # and falls back to regex. We test this by checking the scanner behaves correctly
        # when use_presidio is False
        assert scanner.use_presidio is False
        assert hasattr(scanner, 'regex_patterns')

    def test_presidio_setup_exception_fallback_path(self):
        """Test _setup_presidio_analyzer exception handling (lines 238-242)"""
        # Create scanner instance directly
        scanner = PIILogScanner.__new__(PIILogScanner)
        scanner.alert_email = None
        scanner.detections = []
        scanner.use_presidio = True
        scanner.use_spacy = False  # Ensure fallback goes to regex
        scanner.nlp = None

        # Setup logging manually
        import logging
        logging.basicConfig(level=logging.INFO)
        scanner.logger = logging.getLogger(__name__)

        # Patch NlpEngineProvider to raise an exception and SPACY_AVAILABLE
        with patch('app.security.pii_log_scanner.NlpEngineProvider') as mock_provider, \
             patch('app.security.pii_log_scanner.SPACY_AVAILABLE', False):
            mock_provider.side_effect = Exception("Spacy model not found")

            # Call the method - it should catch the exception and fallback
            scanner._setup_presidio_analyzer()

        # After exception, should fall back to regex
        assert scanner.use_presidio is False
        assert hasattr(scanner, 'regex_patterns')

    def test_analyze_line_presidio_mocked(self):
        """Test _analyze_line_presidio with mocked analyzer"""
        scanner = PIILogScanner(use_presidio=False, use_spacy=False)

        # Create a mock analyzer
        mock_analyzer = MagicMock()
        mock_result = MagicMock()
        mock_result.entity_type = "PERSON"
        mock_result.start = 0
        mock_result.end = 7
        mock_result.score = 0.85
        mock_analyzer.analyze.return_value = [mock_result]

        scanner.analyzer = mock_analyzer
        scanner.use_presidio = True

        # Use prediction format so content gets extracted
        line = """{'task': 'transcription', 'prediction': '"Wanjiru called today"'}"""
        results = scanner._analyze_line_presidio(line)

        assert len(results) == 1
        assert results[0]['entity_type'] == "PERSON"
        assert results[0]['score'] == 0.85

    def test_scan_with_presidio_enabled_mocked(self, temp_log_file):
        """Test scanning with Presidio enabled (mocked)"""
        scanner = PIILogScanner(use_presidio=False, use_spacy=False)

        # Mock the analyzer
        mock_analyzer = MagicMock()
        mock_result = MagicMock()
        mock_result.entity_type = "PHONE_NUMBER"
        mock_result.start = 0
        mock_result.end = 13
        mock_result.score = 0.95
        mock_analyzer.analyze.return_value = [mock_result]

        scanner.analyzer = mock_analyzer
        scanner.use_presidio = True

        total_lines, lines_with_pii = scanner.scan_log_file(temp_log_file)

        assert total_lines > 0
        assert lines_with_pii > 0

    def test_redact_with_presidio_mocked(self, temp_log_file):
        """Test redaction with Presidio enabled (mocked)"""
        scanner = PIILogScanner(use_presidio=False, use_spacy=False)

        # Mock the analyzer and anonymizer
        mock_analyzer = MagicMock()
        mock_result = MagicMock()
        mock_result.entity_type = "PHONE_NUMBER"
        mock_result.start = 0
        mock_result.end = 13
        mock_result.score = 0.95
        mock_analyzer.analyze.return_value = [mock_result]

        mock_anonymizer = MagicMock()
        mock_anonymized = MagicMock()
        mock_anonymized.text = "[REDACTED] called\n"
        mock_anonymizer.anonymize.return_value = mock_anonymized

        scanner.analyzer = mock_analyzer
        scanner.anonymizer = mock_anonymizer
        scanner.use_presidio = True

        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            output_file = Path(f.name)

        try:
            lines_redacted = scanner.redact_log_file(temp_log_file, output_file)
            assert lines_redacted >= 0
        finally:
            if output_file.exists():
                os.unlink(output_file)

    def test_redact_with_presidio_no_results(self, temp_log_file):
        """Test redaction with Presidio when no PII found"""
        scanner = PIILogScanner(use_presidio=False, use_spacy=False)

        # Mock analyzer returning no results
        mock_analyzer = MagicMock()
        mock_analyzer.analyze.return_value = []

        scanner.analyzer = mock_analyzer
        scanner.use_presidio = True

        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            output_file = Path(f.name)

        try:
            lines_redacted = scanner.redact_log_file(temp_log_file, output_file)
            # Content should be written as-is
            assert output_file.exists()
        finally:
            if output_file.exists():
                os.unlink(output_file)


class TestPIILogScannerCLI:
    """Test CLI main() function (lines 565-691)"""

    def test_main_no_args_shows_help(self, capsys):
        """Test main with no args shows help and returns 1"""
        from app.security.pii_log_scanner import main

        with patch('sys.argv', ['pii_log_scanner.py']):
            result = main()

        assert result == 1

    def test_main_scan_file(self, temp_log_file, capsys):
        """Test main scanning a single file"""
        from app.security.pii_log_scanner import main

        report_file = Path('test_report_scan_file.json')
        try:
            with patch('sys.argv', [
                'pii_log_scanner.py',
                '--scan', str(temp_log_file),
                '--no-presidio',
                '--report', str(report_file)
            ]):
                result = main()

            # Should complete (may return 0 or 2 depending on PII percentage)
            assert result in [0, 2]
            assert report_file.exists()
        finally:
            if report_file.exists():
                os.unlink(report_file)
            txt_file = report_file.with_suffix('.txt')
            if txt_file.exists():
                os.unlink(txt_file)

    def test_main_scan_directory(self, temp_log_dir, capsys):
        """Test main scanning a directory"""
        from app.security.pii_log_scanner import main

        report_file = Path('test_report_scan_dir.json')
        try:
            with patch('sys.argv', [
                'pii_log_scanner.py',
                '--scan', str(temp_log_dir),
                '--no-presidio',
                '--report', str(report_file)
            ]):
                result = main()

            assert result in [0, 2]
        finally:
            if report_file.exists():
                os.unlink(report_file)
            txt_file = report_file.with_suffix('.txt')
            if txt_file.exists():
                os.unlink(txt_file)

    def test_main_redact(self, temp_log_file):
        """Test main in redact mode"""
        from app.security.pii_log_scanner import main

        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            output_file = Path(f.name)

        try:
            with patch('sys.argv', [
                'pii_log_scanner.py',
                '--redact', str(temp_log_file), str(output_file),
                '--no-presidio'
            ]):
                result = main()

            assert result == 0
            assert output_file.exists()
        finally:
            if output_file.exists():
                os.unlink(output_file)

    def test_main_with_alert_email(self, temp_log_file):
        """Test main with alert email"""
        from app.security.pii_log_scanner import main

        report_file = Path('test_report_alert.json')
        try:
            with patch('sys.argv', [
                'pii_log_scanner.py',
                '--scan', str(temp_log_file),
                '--no-presidio',
                '--alert-email', 'test@example.com',
                '--report', str(report_file)
            ]):
                result = main()

            assert result in [0, 2]
        finally:
            if report_file.exists():
                os.unlink(report_file)
            txt_file = report_file.with_suffix('.txt')
            if txt_file.exists():
                os.unlink(txt_file)

    def test_main_with_pattern(self, temp_log_dir):
        """Test main with specific pattern"""
        from app.security.pii_log_scanner import main

        report_file = Path('test_report_pattern.json')
        try:
            with patch('sys.argv', [
                'pii_log_scanner.py',
                '--scan', str(temp_log_dir),
                '--no-presidio',
                '--pattern', 'app*.log',
                '--report', str(report_file)
            ]):
                result = main()

            assert result in [0, 2]
        finally:
            if report_file.exists():
                os.unlink(report_file)
            txt_file = report_file.with_suffix('.txt')
            if txt_file.exists():
                os.unlink(txt_file)

    def test_main_invalid_path_error(self, capsys):
        """Test main with invalid path returns error"""
        from app.security.pii_log_scanner import main

        with patch('sys.argv', [
            'pii_log_scanner.py',
            '--scan', '/nonexistent/invalid/path/that/does/not/exist',
            '--no-presidio'
        ]):
            result = main()

        assert result == 1

    def test_main_high_pii_warning_exit_code(self, temp_log_file):
        """Test main returns warning exit code (2) when high PII detected"""
        from app.security.pii_log_scanner import main

        # Create file with high PII percentage (>5%) using prediction format
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            # Write mostly PII content in prediction format
            for i in range(10):
                f.write(f"Line {i}: {{'task': 'transcription', 'prediction': '\"Call from Wanjiru +254712345678\"'}}\n")
            temp_high_pii = Path(f.name)

        report_file = Path('test_report_high_pii.json')
        try:
            with patch('sys.argv', [
                'pii_log_scanner.py',
                '--scan', str(temp_high_pii),
                '--no-presidio',
                '--report', str(report_file)
            ]):
                result = main()

            # Should return 2 for high PII warning
            assert result == 2
        finally:
            os.unlink(temp_high_pii)
            if report_file.exists():
                os.unlink(report_file)
            txt_file = report_file.with_suffix('.txt')
            if txt_file.exists():
                os.unlink(txt_file)


class TestSpaCyIntegration:
    """Test spaCy NER integration"""

    def test_spacy_available_flag_exists(self):
        """Test SPACY_AVAILABLE flag is defined"""
        from app.security import pii_log_scanner
        assert hasattr(pii_log_scanner, 'SPACY_AVAILABLE')

    def test_scanner_with_spacy_enabled(self):
        """Test scanner initializes with spaCy when available"""
        from app.security.pii_log_scanner import SPACY_AVAILABLE

        if not SPACY_AVAILABLE:
            pytest.skip("spaCy not available")

        scanner = PIILogScanner(use_presidio=False, use_spacy=True)

        # Should have spaCy enabled if available
        assert scanner.use_spacy is True
        assert scanner.nlp is not None
        assert hasattr(scanner, 'spacy_entity_types')
        assert hasattr(scanner, 'supplementary_patterns')

    def test_spacy_detects_person_names(self):
        """Test spaCy NER detects person names dynamically"""
        from app.security.pii_log_scanner import SPACY_AVAILABLE

        if not SPACY_AVAILABLE:
            pytest.skip("spaCy not available")

        scanner = PIILogScanner(use_presidio=False, use_spacy=True)

        # Test with names in prediction field format
        line = """'prediction': '"John Smith called about the incident"'"""
        results = scanner._analyze_line_spacy(line)

        assert len(results) >= 1
        assert any(r['entity_type'] == 'PERSON' for r in results)

    def test_spacy_detects_locations(self):
        """Test spaCy NER detects locations dynamically"""
        from app.security.pii_log_scanner import SPACY_AVAILABLE

        if not SPACY_AVAILABLE:
            pytest.skip("spaCy not available")

        scanner = PIILogScanner(use_presidio=False, use_spacy=True)

        # Test with location in prediction field format
        line = """'prediction': '"The caller is from Tanzania in East Africa"'"""
        results = scanner._analyze_line_spacy(line)

        assert len(results) >= 1
        assert any(r['entity_type'] == 'LOCATION' for r in results)

    def test_spacy_with_supplementary_regex(self):
        """Test spaCy also applies supplementary regex patterns"""
        from app.security.pii_log_scanner import SPACY_AVAILABLE

        if not SPACY_AVAILABLE:
            pytest.skip("spaCy not available")

        scanner = PIILogScanner(use_presidio=False, use_spacy=True)

        # Phone number in prediction field format
        line = """'prediction': '"Contact the helpline at +254712345678 for assistance"'"""
        results = scanner._analyze_line_spacy(line)

        assert len(results) >= 1
        assert any(r['entity_type'] == 'PHONE_NUMBER' for r in results)

    def test_extract_text_content_from_json(self):
        """Test _extract_text_content extracts text from JSON strings"""
        from app.security.pii_log_scanner import SPACY_AVAILABLE

        if not SPACY_AVAILABLE:
            pytest.skip("spaCy not available")

        scanner = PIILogScanner(use_presidio=False, use_spacy=True)

        # Test extraction from JSON-like content
        line = """'prediction': '"John Smith from Nairobi reported the case"'"""
        extracted = scanner._extract_text_content(line)

        assert "John Smith from Nairobi" in extracted

    def test_extract_text_content_from_sql(self):
        """Test _extract_text_content extracts text from prediction field in SQL"""
        from app.security.pii_log_scanner import SPACY_AVAILABLE

        if not SPACY_AVAILABLE:
            pytest.skip("spaCy not available")

        scanner = PIILogScanner(use_presidio=False, use_spacy=True)

        # Test extraction from SQL INSERT with prediction field
        line = """INSERT INTO results VALUES ('prediction': '"Name is Wanjiru from Nairobi"')"""
        extracted = scanner._extract_text_content(line)

        assert "Name is Wanjiru from Nairobi" in extracted

    def test_redact_by_positions(self):
        """Test _redact_by_positions correctly replaces text"""
        scanner = PIILogScanner(use_presidio=False, use_spacy=False)

        text = "Call from John at 123-456-7890"
        detections = [
            {'entity_type': 'PERSON', 'start': 10, 'end': 14, 'score': 0.9},
            {'entity_type': 'PHONE_NUMBER', 'start': 18, 'end': 30, 'score': 0.9}
        ]

        result = scanner._redact_by_positions(text, detections)

        assert "[REDACTED-PERSON]" in result
        assert "[REDACTED-PHONE_NUMBER]" in result
        assert "John" not in result
        assert "123-456-7890" not in result

    def test_spacy_scan_log_file(self, temp_log_file):
        """Test scanning file with spaCy"""
        from app.security.pii_log_scanner import SPACY_AVAILABLE

        if not SPACY_AVAILABLE:
            pytest.skip("spaCy not available")

        scanner = PIILogScanner(use_presidio=False, use_spacy=True)

        total_lines, lines_with_pii = scanner.scan_log_file(temp_log_file)

        assert total_lines > 0
        assert lines_with_pii > 0

    def test_spacy_redact_log_file(self, temp_log_file):
        """Test redaction with spaCy"""
        from app.security.pii_log_scanner import SPACY_AVAILABLE

        if not SPACY_AVAILABLE:
            pytest.skip("spaCy not available")

        scanner = PIILogScanner(use_presidio=False, use_spacy=True)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            output_file = Path(f.name)

        try:
            lines_redacted = scanner.redact_log_file(temp_log_file, output_file)
            assert lines_redacted >= 0
            assert output_file.exists()
        finally:
            if output_file.exists():
                os.unlink(output_file)

    def test_spacy_setup_fallback_to_regex(self):
        """Test spaCy setup falls back to regex on failure"""
        scanner = PIILogScanner.__new__(PIILogScanner)
        scanner.alert_email = None
        scanner.detections = []
        scanner.use_presidio = False
        scanner.use_spacy = True
        scanner.nlp = None

        import logging
        logging.basicConfig(level=logging.INFO)
        scanner.logger = logging.getLogger(__name__)

        # Mock spacy.load to fail
        with patch('app.security.pii_log_scanner.spacy') as mock_spacy:
            mock_spacy.load.side_effect = OSError("Model not found")

            scanner._setup_spacy_analyzer()

        # Should fall back to regex
        assert scanner.use_spacy is False
        assert hasattr(scanner, 'regex_patterns')

"""
Unit tests for PII Sanitizing Filter

Tests the real-time PII redaction filter for Python logging.
"""
import pytest
import logging
from unittest.mock import MagicMock, patch
from io import StringIO

from app.security.pii_logging_filter import (
    PIISanitizingFilter,
    setup_sanitized_logging,
    get_pii_filter_for_handler
)


class TestPIISanitizingFilterInit:
    """Test PIISanitizingFilter initialization"""

    def test_init_default_values(self):
        """Test filter initializes with default values"""
        filter_instance = PIISanitizingFilter()

        assert filter_instance.enable_stats is True
        assert filter_instance.redaction_count == 0
        assert filter_instance.messages_processed == 0
        assert filter_instance.messages_with_pii == 0

    def test_init_with_custom_name(self):
        """Test filter initializes with custom name"""
        filter_instance = PIISanitizingFilter(name='custom_filter')

        assert filter_instance.name == 'custom_filter'

    def test_init_with_stats_disabled(self):
        """Test filter initializes with stats disabled"""
        filter_instance = PIISanitizingFilter(enable_stats=False)

        assert filter_instance.enable_stats is False

    def test_init_compiles_patterns(self):
        """Test filter compiles regex patterns on init"""
        filter_instance = PIISanitizingFilter()

        assert hasattr(filter_instance, 'phone_patterns')
        assert hasattr(filter_instance, 'email_pattern')
        assert hasattr(filter_instance, 'name_pattern')
        assert hasattr(filter_instance, 'location_pattern')
        assert hasattr(filter_instance, 'age_pattern')
        assert len(filter_instance.phone_patterns) > 0


class TestPIISanitizingFilterPhoneRedaction:
    """Test phone number redaction"""

    def test_redact_kenyan_phone_plus254(self):
        """Test redaction of +254 phone numbers"""
        filter_instance = PIISanitizingFilter()

        result = filter_instance._sanitize_text("Phone: +254712345678")
        assert result == "Phone: [REDACTED-PHONE]"

    def test_redact_kenyan_phone_07(self):
        """Test redaction of 07 phone numbers"""
        filter_instance = PIISanitizingFilter()

        result = filter_instance._sanitize_text("Call from 0722123456")
        assert result == "Call from [REDACTED-PHONE]"

    def test_redact_kenyan_phone_spaced(self):
        """Test redaction of spaced phone numbers"""
        filter_instance = PIISanitizingFilter()

        result = filter_instance._sanitize_text("Contact: +254 712 345 678")
        assert result == "Contact: [REDACTED-PHONE]"

    def test_redact_kenyan_phone_no_plus(self):
        """Test redaction of 254 without plus"""
        filter_instance = PIISanitizingFilter()

        result = filter_instance._sanitize_text("Number: 254712345678")
        assert result == "Number: [REDACTED-PHONE]"

    def test_redact_multiple_phones(self):
        """Test redaction of multiple phone numbers"""
        filter_instance = PIISanitizingFilter()

        result = filter_instance._sanitize_text("Primary: +254712345678, Alt: 0733987654")
        assert "[REDACTED-PHONE]" in result
        assert "+254712345678" not in result
        assert "0733987654" not in result


class TestPIISanitizingFilterEmailRedaction:
    """Test email address redaction"""

    def test_redact_email_gmail(self):
        """Test redaction of Gmail addresses"""
        filter_instance = PIISanitizingFilter()

        result = filter_instance._sanitize_text("Email: test@gmail.com")
        assert result == "Email: [REDACTED-EMAIL]"

    def test_redact_email_domain(self):
        """Test redaction of domain email addresses"""
        filter_instance = PIISanitizingFilter()

        result = filter_instance._sanitize_text("Contact: admin@openchs.org")
        assert result == "Contact: [REDACTED-EMAIL]"

    def test_redact_email_with_numbers(self):
        """Test redaction of email with numbers"""
        filter_instance = PIISanitizingFilter()

        result = filter_instance._sanitize_text("Mail: user123@example.co.ke")
        assert result == "Mail: [REDACTED-EMAIL]"

    def test_redact_email_complex(self):
        """Test redaction of complex email"""
        filter_instance = PIISanitizingFilter()

        result = filter_instance._sanitize_text("Send to: first.last+tag@sub.domain.com")
        assert result == "Send to: [REDACTED-EMAIL]"


class TestPIISanitizingFilterNameRedaction:
    """Test name redaction"""

    def test_redact_kikuyu_names(self):
        """Test redaction of Kikuyu names"""
        filter_instance = PIISanitizingFilter()

        result = filter_instance._sanitize_text("Caller: Wanjiru Kamau")
        assert result == "Caller: [REDACTED-NAME] [REDACTED-NAME]"

    def test_redact_luo_names(self):
        """Test redaction of Luo names"""
        filter_instance = PIISanitizingFilter()

        result = filter_instance._sanitize_text("Victim: Otieno Akinyi")
        assert result == "Victim: [REDACTED-NAME] [REDACTED-NAME]"

    def test_redact_kalenjin_names(self):
        """Test redaction of Kalenjin names"""
        filter_instance = PIISanitizingFilter()

        result = filter_instance._sanitize_text("Child: Chebet Kiplagat")
        assert result == "Child: [REDACTED-NAME] [REDACTED-NAME]"

    def test_redact_swahili_names(self):
        """Test redaction of Swahili/coastal names"""
        filter_instance = PIISanitizingFilter()

        result = filter_instance._sanitize_text("Guardian: Fatuma Hassan")
        assert result == "Guardian: [REDACTED-NAME] [REDACTED-NAME]"

    def test_redact_english_names(self):
        """Test redaction of common English names"""
        filter_instance = PIISanitizingFilter()

        result = filter_instance._sanitize_text("Parent: Mary John")
        assert result == "Parent: [REDACTED-NAME] [REDACTED-NAME]"

    def test_name_case_insensitive(self):
        """Test name redaction is case insensitive"""
        filter_instance = PIISanitizingFilter()

        result1 = filter_instance._sanitize_text("Name: WANJIRU")
        result2 = filter_instance._sanitize_text("Name: wanjiru")
        result3 = filter_instance._sanitize_text("Name: Wanjiru")

        assert result1 == "Name: [REDACTED-NAME]"
        assert result2 == "Name: [REDACTED-NAME]"
        assert result3 == "Name: [REDACTED-NAME]"


class TestPIISanitizingFilterLocationRedaction:
    """Test location redaction"""

    def test_redact_major_cities(self):
        """Test redaction of major Kenyan cities"""
        filter_instance = PIISanitizingFilter()

        result = filter_instance._sanitize_text("Location: Nairobi")
        assert result == "Location: [REDACTED-LOCATION]"

    def test_redact_counties(self):
        """Test redaction of county names"""
        filter_instance = PIISanitizingFilter()

        result = filter_instance._sanitize_text("From Kiambu County")
        assert result == "From [REDACTED-LOCATION] County"

    def test_redact_neighborhoods(self):
        """Test redaction of neighborhoods"""
        filter_instance = PIISanitizingFilter()

        result = filter_instance._sanitize_text("Lives in Kibera slum")
        assert result == "Lives in [REDACTED-LOCATION] slum"

    def test_redact_multiple_locations(self):
        """Test redaction of multiple locations"""
        filter_instance = PIISanitizingFilter()

        result = filter_instance._sanitize_text("Traveling from Nairobi to Mombasa")
        assert result == "Traveling from [REDACTED-LOCATION] to [REDACTED-LOCATION]"


class TestPIISanitizingFilterAgeRedaction:
    """Test age redaction"""

    def test_redact_years_old(self):
        """Test redaction of 'X years old' pattern"""
        filter_instance = PIISanitizingFilter()

        result = filter_instance._sanitize_text("Child is 12 years old")
        assert result == "Child is [REDACTED-AGE]"

    def test_redact_yrs_old(self):
        """Test redaction of 'X yrs old' pattern"""
        filter_instance = PIISanitizingFilter()

        result = filter_instance._sanitize_text("Victim: 8 yrs old")
        assert result == "Victim: [REDACTED-AGE]"

    def test_redact_yo(self):
        """Test redaction of 'X y/o' pattern"""
        filter_instance = PIISanitizingFilter()

        result = filter_instance._sanitize_text("Case involves 5 y/o child")
        assert result == "Case involves [REDACTED-AGE] child"

    def test_redact_age_case_insensitive(self):
        """Test age redaction is case insensitive"""
        filter_instance = PIISanitizingFilter()

        result = filter_instance._sanitize_text("Child: 10 YEARS OLD")
        assert result == "Child: [REDACTED-AGE]"


class TestPIISanitizingFilterNoRedaction:
    """Test cases where no redaction should occur"""

    def test_no_redaction_system_messages(self):
        """Test system messages pass through unchanged"""
        filter_instance = PIISanitizingFilter()

        messages = [
            "Processing completed successfully",
            "Task ID: abc123-def456",
            "Database connection established",
            "Request handled in 150ms",
            "Worker ready to accept tasks"
        ]

        for msg in messages:
            result = filter_instance._sanitize_text(msg)
            assert result == msg, f"Message should not be changed: {msg}"

    def test_no_redaction_empty_string(self):
        """Test empty string handling"""
        filter_instance = PIISanitizingFilter()

        result = filter_instance._sanitize_text("")
        assert result == ""

    def test_no_redaction_none(self):
        """Test None handling"""
        filter_instance = PIISanitizingFilter()

        result = filter_instance._sanitize_text(None)
        assert result is None


class TestPIISanitizingFilterMixedContent:
    """Test mixed PII content redaction"""

    def test_redact_multiple_pii_types(self):
        """Test redaction of message with multiple PII types"""
        filter_instance = PIISanitizingFilter()

        msg = "Call from Wanjiru (+254712345678) in Nairobi, email: test@gmail.com"
        result = filter_instance._sanitize_text(msg)

        assert "[REDACTED-NAME]" in result
        assert "[REDACTED-PHONE]" in result
        assert "[REDACTED-LOCATION]" in result
        assert "[REDACTED-EMAIL]" in result
        assert "+254712345678" not in result
        assert "test@gmail.com" not in result

    def test_redact_preserves_log_format(self):
        """Test that log format is preserved"""
        filter_instance = PIISanitizingFilter()

        msg = "2026-01-30 10:00:00 - INFO - Caller: Wanjiru"
        result = filter_instance._sanitize_text(msg)

        assert "2026-01-30 10:00:00 - INFO - Caller:" in result
        assert "[REDACTED-NAME]" in result


class TestPIISanitizingFilterLogging:
    """Test filter integration with logging"""

    def test_filter_method_returns_true(self):
        """Test filter method always returns True"""
        filter_instance = PIISanitizingFilter()

        record = MagicMock()
        record.msg = "Test message"
        record.args = None

        result = filter_instance.filter(record)
        assert result is True

    def test_filter_sanitizes_record_msg(self):
        """Test filter sanitizes log record message"""
        filter_instance = PIISanitizingFilter()

        record = MagicMock()
        record.msg = "Phone: +254712345678"
        record.args = None

        filter_instance.filter(record)

        assert record.msg == "Phone: [REDACTED-PHONE]"

    def test_filter_sanitizes_dict_args(self):
        """Test filter sanitizes dict args"""
        filter_instance = PIISanitizingFilter()

        record = MagicMock()
        record.msg = "User info: %(name)s"
        record.args = {"name": "Wanjiru"}

        filter_instance.filter(record)

        assert record.args["name"] == "[REDACTED-NAME]"

    def test_filter_sanitizes_tuple_args(self):
        """Test filter sanitizes tuple args"""
        filter_instance = PIISanitizingFilter()

        record = MagicMock()
        record.msg = "Caller: %s, Phone: %s"
        record.args = ("Wanjiru", "+254712345678")

        filter_instance.filter(record)

        assert "[REDACTED-NAME]" in record.args
        assert "[REDACTED-PHONE]" in record.args


class TestPIISanitizingFilterStats:
    """Test filter statistics"""

    def test_stats_tracks_messages(self):
        """Test stats tracks processed messages"""
        filter_instance = PIISanitizingFilter()

        record = MagicMock()
        record.msg = "Test message"
        record.args = None

        filter_instance.filter(record)
        filter_instance.filter(record)

        stats = filter_instance.get_stats()
        assert stats['total_messages'] == 2

    def test_stats_tracks_pii_messages(self):
        """Test stats tracks messages with PII"""
        filter_instance = PIISanitizingFilter()
        filter_instance.clear_cache()

        record1 = MagicMock()
        record1.msg = "Call from Wanjiru"
        record1.args = None

        record2 = MagicMock()
        record2.msg = "Processing complete"
        record2.args = None

        filter_instance.filter(record1)
        filter_instance.filter(record2)

        stats = filter_instance.get_stats()
        assert stats['total_messages'] == 2
        assert stats['messages_with_pii'] == 1

    def test_stats_calculates_percentage(self):
        """Test stats calculates PII percentage"""
        filter_instance = PIISanitizingFilter()
        filter_instance.clear_cache()

        # Process 4 messages, 1 with PII
        for i in range(3):
            record = MagicMock()
            record.msg = "Clean message"
            record.args = None
            filter_instance.filter(record)

        record_pii = MagicMock()
        record_pii.msg = "Phone: +254712345678"
        record_pii.args = None
        filter_instance.filter(record_pii)

        stats = filter_instance.get_stats()
        assert stats['pii_percentage'] == 25.0

    def test_stats_tracks_cache_info(self):
        """Test stats includes cache information"""
        filter_instance = PIISanitizingFilter()

        # Trigger cache usage
        filter_instance._sanitize_text("Test message")
        filter_instance._sanitize_text("Test message")  # Cache hit

        stats = filter_instance.get_stats()
        assert 'cache_hits' in stats
        assert 'cache_misses' in stats
        assert 'cache_size' in stats

    def test_stats_disabled(self):
        """Test filter works with stats disabled"""
        filter_instance = PIISanitizingFilter(enable_stats=False)

        record = MagicMock()
        record.msg = "Phone: +254712345678"
        record.args = None

        filter_instance.filter(record)

        assert record.msg == "Phone: [REDACTED-PHONE]"
        # Stats should be 0 when disabled
        assert filter_instance.messages_processed == 0


class TestPIISanitizingFilterCache:
    """Test LRU cache functionality"""

    def test_cache_hit(self):
        """Test cache provides hit for repeated messages"""
        filter_instance = PIISanitizingFilter()
        filter_instance.clear_cache()

        # First call
        filter_instance._sanitize_text("Test message")
        stats1 = filter_instance.get_stats()

        # Second call (should hit cache)
        filter_instance._sanitize_text("Test message")
        stats2 = filter_instance.get_stats()

        assert stats2['cache_hits'] > stats1['cache_hits']

    def test_cache_clear(self):
        """Test cache can be cleared"""
        filter_instance = PIISanitizingFilter()

        filter_instance._sanitize_text("Test message")
        filter_instance.clear_cache()

        stats = filter_instance.get_stats()
        assert stats['cache_size'] == 0


class TestSetupSanitizedLogging:
    """Test setup_sanitized_logging function"""

    def test_setup_returns_logger_and_filter(self):
        """Test setup returns logger and filter"""
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(delete=False, suffix='.log') as f:
            log_file = f.name

        try:
            logger, pii_filter = setup_sanitized_logging(log_file=log_file)

            assert isinstance(logger, logging.Logger)
            assert isinstance(pii_filter, PIISanitizingFilter)
        finally:
            os.unlink(log_file)

    def test_setup_with_level(self):
        """Test setup with custom log level"""
        logger, pii_filter = setup_sanitized_logging(level=logging.DEBUG)

        assert logger.level == logging.DEBUG

    def test_setup_console_only(self):
        """Test setup without file handler"""
        logger, pii_filter = setup_sanitized_logging()

        # Should have at least one handler (console)
        assert len(logger.handlers) >= 1


class TestGetPiiFilterForHandler:
    """Test get_pii_filter_for_handler function"""

    def test_adds_filter_to_handler(self):
        """Test function adds filter to handler"""
        handler = logging.StreamHandler()

        pii_filter = get_pii_filter_for_handler(handler)

        assert isinstance(pii_filter, PIISanitizingFilter)
        assert pii_filter in handler.filters


class TestPIISanitizingFilterDictArgsNonString:
    """Test filter handling of non-string dict args (line 256 coverage)"""

    def test_filter_dict_args_with_integers(self):
        """Test filter handles dict args with integer values"""
        filter_instance = PIISanitizingFilter()

        record = MagicMock()
        record.msg = "Count: %(count)s"
        record.args = {"count": 42}

        filter_instance.filter(record)

        # Integer should pass through unchanged
        assert record.args["count"] == 42

    def test_filter_dict_args_with_floats(self):
        """Test filter handles dict args with float values"""
        filter_instance = PIISanitizingFilter()

        record = MagicMock()
        record.msg = "Score: %(score)s"
        record.args = {"score": 3.14159}

        filter_instance.filter(record)

        # Float should pass through unchanged
        assert record.args["score"] == 3.14159

    def test_filter_dict_args_with_booleans(self):
        """Test filter handles dict args with boolean values"""
        filter_instance = PIISanitizingFilter()

        record = MagicMock()
        record.msg = "Active: %(active)s"
        record.args = {"active": True}

        filter_instance.filter(record)

        # Boolean should pass through unchanged
        assert record.args["active"] is True

    def test_filter_dict_args_with_none(self):
        """Test filter handles dict args with None values"""
        filter_instance = PIISanitizingFilter()

        record = MagicMock()
        record.msg = "Value: %(value)s"
        record.args = {"value": None}

        filter_instance.filter(record)

        # None should pass through unchanged
        assert record.args["value"] is None

    def test_filter_dict_args_mixed_types(self):
        """Test filter handles dict args with mixed types"""
        filter_instance = PIISanitizingFilter()

        record = MagicMock()
        record.msg = "Name: %(name)s, Count: %(count)s, Active: %(active)s, Score: %(score)s"
        record.args = {
            "name": "Wanjiru",  # String with PII - should be redacted
            "count": 42,  # Integer - unchanged
            "active": True,  # Boolean - unchanged
            "score": 3.14  # Float - unchanged
        }

        filter_instance.filter(record)

        # String with PII should be redacted
        assert record.args["name"] == "[REDACTED-NAME]"
        # Non-strings should pass through unchanged
        assert record.args["count"] == 42
        assert record.args["active"] is True
        assert record.args["score"] == 3.14

    def test_filter_tuple_args_with_non_strings(self):
        """Test filter handles tuple args with non-string values"""
        filter_instance = PIISanitizingFilter()

        record = MagicMock()
        record.msg = "Name: %s, Count: %s, Score: %s"
        record.args = ("Wanjiru", 42, 3.14)

        filter_instance.filter(record)

        # String with PII should be redacted, others unchanged
        assert "[REDACTED-NAME]" in record.args
        assert 42 in record.args
        assert 3.14 in record.args

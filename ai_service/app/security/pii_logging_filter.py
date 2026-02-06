"""
Real-Time PII Sanitization for Python Logging

This module provides a logging filter that automatically redacts PII
from log messages in real-time before they're written to files.

Features:
- Detects and redacts phone numbers (Kenyan formats)
- Redacts email addresses
- Redacts common Kenyan/Swahili names
- Redacts location patterns
- Fast regex-based detection (no external dependencies)
- Thread-safe with LRU cache

Usage:
    import logging
    from app.security import PIISanitizingFilter

    # Add filter to your logger
    logger = logging.getLogger(__name__)
    logger.addFilter(PIISanitizingFilter())

    # PII will be automatically redacted
    logger.info(f"Processing call from {caller_name}")  # Logged as: "[REDACTED-NAME]"
    logger.info(f"Phone: +254712345678")  # Logged as: "[REDACTED-PHONE]"

"""

import re
import logging
from typing import Dict, List, Tuple
from functools import lru_cache
from datetime import datetime


class PIISanitizingFilter(logging.Filter):
    """
    Logging filter that automatically redacts PII from log messages

    Features:
    - Detects and redacts phone numbers (Kenyan formats)
    - Redacts email addresses
    - Redacts common Kenyan/Swahili names
    - Redacts location patterns
    - Fast regex-based detection (no external dependencies)
    - Thread-safe
    """

    def __init__(self, name: str = '', enable_stats: bool = True):
        """
        Initialize PII sanitizing filter

        Args:
            name: Filter name (optional)
            enable_stats: Track redaction statistics
        """
        super().__init__(name)
        self._compile_patterns()
        self.enable_stats = enable_stats
        self.redaction_count = 0
        self.messages_processed = 0
        self.messages_with_pii = 0
        self._start_time = datetime.now()

    def _compile_patterns(self):
        """Compile regex patterns for PII detection"""

        # Kenyan phone numbers (various formats)
        self.phone_patterns: List[Tuple[re.Pattern, str]] = [
            (re.compile(r'\+254\s?[17]\d{8}'), '[REDACTED-PHONE]'),  # +254 7XXXXXXXX
            (re.compile(r'\b0[17]\d{8}\b'), '[REDACTED-PHONE]'),  # 07XXXXXXXX
            (re.compile(r'\+254\s?\d{3}\s?\d{3}\s?\d{3}'), '[REDACTED-PHONE]'),  # +254 712 345 678
            (re.compile(r'\b254[17]\d{8}\b'), '[REDACTED-PHONE]'),  # 2547XXXXXXXX
        ]

        # Email addresses
        self.email_pattern: Tuple[re.Pattern, str] = (
            re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            '[REDACTED-EMAIL]'
        )

        # Common Kenyan/Swahili names (comprehensive list)
        common_names = [
            # Kikuyu names
            'Wanjiru', 'Kamau', 'Njeri', 'Mwangi', 'Wanjiku', 'Karanja', 'Njoroge',
            'Wairimu', 'Nyambura', 'Muthoni', 'Wambui', 'Mumbi', 'Wangari', 'Njoki',
            'Gathoni', 'Nyokabi', 'Gitau', 'Kiarie', 'Kimani', 'Kariuki', 'Macharia',
            # Luo names
            'Otieno', 'Akinyi', 'Omondi', 'Adhiambo', 'Ochieng', 'Awino', 'Oduor',
            'Onyango', 'Akoth', 'Owino', 'Auma', 'Odhiambo', 'Anyango', 'Atieno',
            # Kalenjin names
            'Chebet', 'Kiplagat', 'Rotich', 'Kibet', 'Jepkorir', 'Kosgei', 'Kipruto',
            'Chepkoech', 'Kipchoge', 'Kiptoo', 'Cherono', 'Tanui', 'Kimutai',
            # Luhya names
            'Wekesa', 'Nafula', 'Simiyu', 'Nekesa', 'Wasike', 'Wanyama', 'Barasa',
            'Makokha', 'Wafula', 'Nasimiyu', 'Khisa', 'Masinde',
            # Kamba names
            'Mutua', 'Mwende', 'Musyoka', 'Ndinda', 'Kioko', 'Muthama', 'Kilonzo',
            'Musau', 'Nthenya', 'Wambua', 'Mutinda', 'Kavata',
            # Coastal/Swahili names
            'Mwanaisha', 'Bakari', 'Hamisi', 'Fatuma', 'Salim', 'Amina', 'Hassan',
            'Zainab', 'Omar', 'Khadija', 'Mohamed', 'Aisha', 'Yusuf', 'Halima',
            # Common English names used in Kenya
            'John', 'Mary', 'Peter', 'Grace', 'James', 'Jane', 'David', 'Sarah',
            'Michael', 'Elizabeth', 'Daniel', 'Margaret', 'Joseph', 'Anne',
            # Titles that might indicate names follow
            'Mama', 'Baba', 'Mzee', 'Bibi',
        ]

        # Build regex pattern (case-insensitive word boundaries)
        name_pattern = r'\b(' + '|'.join(re.escape(name) for name in common_names) + r')\b'
        self.name_pattern: Tuple[re.Pattern, str] = (
            re.compile(name_pattern, re.IGNORECASE),
            '[REDACTED-NAME]'
        )

        # Kenyan national ID numbers (8 digits, standalone)
        self.id_pattern: Tuple[re.Pattern, str] = (
            re.compile(r'\b\d{7,8}\b'),  # 7-8 digit IDs
            '[REDACTED-ID]'
        )

        # Common Kenyan location patterns (counties, major towns)
        locations = [
            # Major cities
            'Nairobi', 'Mombasa', 'Kisumu', 'Nakuru', 'Eldoret', 'Thika', 'Malindi',
            'Kitale', 'Garissa', 'Kakamega', 'Nyeri', 'Meru', 'Embu', 'Machakos',
            # Counties
            'Kiambu', 'Kajiado', 'Narok', 'Turkana', 'Samburu', 'Kilifi', 'Kwale',
            'Taita', 'Taveta', 'Lamu', 'Tana River', 'Isiolo', 'Marsabit', 'Wajir',
            'Mandera', 'Moyale', 'Busia', 'Siaya', 'Homa Bay', 'Migori', 'Kisii',
            'Nyamira', 'Bomet', 'Kericho', 'Nandi', 'Uasin Gishu', 'Trans Nzoia',
            'Elgeyo Marakwet', 'Baringo', 'Laikipia', 'Nyandarua', 'Kirinyaga',
            'Muranga', 'Tharaka Nithi', 'Kitui', 'Makueni', 'Vihiga', 'Bungoma',
            # Neighborhoods/Areas
            'Kibera', 'Mathare', 'Eastleigh', 'Westlands', 'Karen', 'Langata',
            'Kasarani', 'Embakasi', 'Dagoretti', 'Ruaraka', 'Starehe', 'Makadara',
            'Kamukunji', 'Roysambu', 'Githurai', 'Ruiru', 'Juja', 'Limuru',
        ]
        location_pattern = r'\b(' + '|'.join(re.escape(loc) for loc in locations) + r')\b'
        self.location_pattern: Tuple[re.Pattern, str] = (
            re.compile(location_pattern, re.IGNORECASE),
            '[REDACTED-LOCATION]'
        )

        # Date patterns that might be sensitive (birth dates, incident dates)
        self.date_patterns: List[Tuple[re.Pattern, str]] = [
            # DD/MM/YYYY or DD-MM-YYYY
            (re.compile(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b'), '[REDACTED-DATE]'),
            # YYYY-MM-DD (ISO format)
            (re.compile(r'\b\d{4}-\d{2}-\d{2}\b'), '[REDACTED-DATE]'),
        ]

        # Age patterns
        self.age_pattern: Tuple[re.Pattern, str] = (
            re.compile(r'\b(\d{1,2})\s*(years?\s*old|yrs?\s*old|y/?o)\b', re.IGNORECASE),
            '[REDACTED-AGE]'
        )

    @lru_cache(maxsize=2048)
    def _sanitize_text(self, text: str) -> str:
        """
        Sanitize text by redacting PII

        Uses LRU cache for performance on repeated messages.

        Args:
            text: Original log message

        Returns:
            Sanitized text with PII redacted
        """
        if not text or not isinstance(text, str):
            return text

        sanitized = text
        had_pii = False

        # Redact phone numbers (high priority - most sensitive)
        for pattern, replacement in self.phone_patterns:
            if pattern.search(sanitized):
                sanitized = pattern.sub(replacement, sanitized)
                had_pii = True

        # Redact emails
        pattern, replacement = self.email_pattern
        if pattern.search(sanitized):
            sanitized = pattern.sub(replacement, sanitized)
            had_pii = True

        # Redact names
        pattern, replacement = self.name_pattern
        if pattern.search(sanitized):
            sanitized = pattern.sub(replacement, sanitized)
            had_pii = True

        # Redact locations (lower priority - context dependent)
        pattern, replacement = self.location_pattern
        if pattern.search(sanitized):
            sanitized = pattern.sub(replacement, sanitized)
            had_pii = True

        # Redact ages
        pattern, replacement = self.age_pattern
        if pattern.search(sanitized):
            sanitized = pattern.sub(replacement, sanitized)
            had_pii = True

        # Note: ID pattern commented out to avoid false positives with task IDs, timestamps
        # Uncomment if needed:
        # pattern, replacement = self.id_pattern
        # if pattern.search(sanitized):
        #     sanitized = pattern.sub(replacement, sanitized)
        #     had_pii = True

        # Update stats
        if self.enable_stats and had_pii:
            self.redaction_count += 1

        return sanitized

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter method called by Python logging system

        Args:
            record: Log record to process

        Returns:
            Always True (allow logging after sanitization)
        """
        if self.enable_stats:
            self.messages_processed += 1

        original_msg = None

        # Sanitize the message
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            original_msg = record.msg
            record.msg = self._sanitize_text(record.msg)

            if self.enable_stats and record.msg != original_msg:
                self.messages_with_pii += 1

        # Sanitize args if present (for format strings like "Hello %s")
        if hasattr(record, 'args') and record.args:
            if isinstance(record.args, dict):
                sanitized_args = {}
                for key, arg in record.args.items():
                    if isinstance(arg, str):
                        sanitized_args[key] = self._sanitize_text(arg)
                    else:
                        sanitized_args[key] = arg
                record.args = sanitized_args
            elif isinstance(record.args, (tuple, list)):
                sanitized_args = []
                for arg in record.args:
                    if isinstance(arg, str):
                        sanitized_args.append(self._sanitize_text(arg))
                    else:
                        sanitized_args.append(arg)
                record.args = tuple(sanitized_args)

        return True

    def get_stats(self) -> Dict:
        """Get statistics about redactions"""
        uptime = (datetime.now() - self._start_time).total_seconds()
        cache_info = self._sanitize_text.cache_info()

        return {
            'total_messages': self.messages_processed,
            'messages_with_pii': self.messages_with_pii,
            'pii_percentage': (self.messages_with_pii / self.messages_processed * 100) if self.messages_processed > 0 else 0,
            'total_redactions': self.redaction_count,
            'uptime_seconds': uptime,
            'cache_hits': cache_info.hits,
            'cache_misses': cache_info.misses,
            'cache_size': cache_info.currsize,
            'cache_maxsize': cache_info.maxsize,
        }

    def clear_cache(self):
        """Clear the LRU cache (useful for testing)"""
        self._sanitize_text.cache_clear()


def setup_sanitized_logging(
    log_file: str = None,
    level: int = logging.INFO,
    format_string: str = None
) -> Tuple[logging.Logger, PIISanitizingFilter]:
    """
    Setup logging with PII sanitization

    Args:
        log_file: Path to log file (optional, logs to console if not provided)
        level: Logging level
        format_string: Custom format string

    Returns:
        Tuple of (configured logger, PII filter instance)
    """
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Default format
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    formatter = logging.Formatter(format_string)

    # Create PII sanitizing filter
    pii_filter = PIISanitizingFilter()

    # Console handler (always add)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(pii_filter)
    logger.addHandler(console_handler)

    # File handler (if log file specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        file_handler.addFilter(pii_filter)
        logger.addHandler(file_handler)

    logger.info("Logging configured with PII sanitization enabled")

    return logger, pii_filter


def get_pii_filter_for_handler(handler: logging.Handler) -> PIISanitizingFilter:
    """
    Get or create a PII filter for an existing handler

    Args:
        handler: Logging handler to add filter to

    Returns:
        The PII filter instance
    """
    pii_filter = PIISanitizingFilter()
    handler.addFilter(pii_filter)
    return pii_filter


# Example usage and testing
if __name__ == '__main__':
    print("Testing PII Sanitization Filter")
    print("=" * 50)

    # Setup logging with sanitization
    logger, pii_filter = setup_sanitized_logging(
        log_file='test_sanitized.log',
        level=logging.INFO
    )

    # Test cases
    test_messages = [
        # Phone numbers
        ("Phone: +254712345678", "Should redact Kenyan phone"),
        ("Call from 0722123456", "Should redact local phone"),
        ("Contact: +254 712 345 678", "Should redact spaced phone"),

        # Names
        ("Caller: Wanjiru Kamau", "Should redact Kenyan names"),
        ("Victim name: Otieno Ochieng", "Should redact Luo names"),
        ("Processing for Mary John", "Should redact common names"),

        # Emails
        ("Email: user@example.com", "Should redact email"),
        ("Contact wanjiru@gmail.com", "Should redact Gmail"),

        # Locations
        ("Location: Nairobi, Kiambu County", "Should redact locations"),
        ("Caller from Kibera slum", "Should redact neighborhood"),

        # Ages
        ("Child is 12 years old", "Should redact age"),
        ("Victim: 8 yr old girl", "Should redact age"),

        # No PII
        ("Processing completed successfully", "Should pass unchanged"),
        ("Task ID: abc123-def456", "Should pass unchanged"),
        ("Database connection established", "Should pass unchanged"),
    ]

    print("\nTest Results:")
    print("-" * 50)

    for original, description in test_messages:
        logger.info(original)
        sanitized = pii_filter._sanitize_text(original)
        changed = "REDACTED" if sanitized != original else "unchanged"
        print(f"[{changed}] {description}")
        print(f"  Original:  {original}")
        print(f"  Sanitized: {sanitized}")
        print()

    # Print statistics
    print("=" * 50)
    print("Statistics:")
    stats = pii_filter.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\nTest complete. Check 'test_sanitized.log' for file output.")

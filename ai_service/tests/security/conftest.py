"""
Pytest fixtures for security module tests
"""
import pytest
import tempfile
import os
from pathlib import Path


@pytest.fixture
def temp_log_file():
    """Create a temporary log file with PII data in model prediction format for testing"""
    content = """2026-01-30 10:00:00 - INFO - {'task': 'transcription', 'prediction': '"Processing call from Wanjiru Kamau"'}
2026-01-30 10:00:01 - INFO - {'task': 'transcription', 'prediction': '"Caller phone is +254712345678"'}
2026-01-30 10:00:02 - INFO - {'task': 'transcription', 'prediction': '"Email contact at caller@gmail.com"'}
2026-01-30 10:00:03 - INFO - {'task': 'transcription', 'prediction': '"Location is Nairobi, Kiambu County"'}
2026-01-30 10:00:04 - INFO - {'task': 'transcription', 'prediction': '"Child name is Otieno, age 12 years old"'}
2026-01-30 10:00:05 - INFO - Processing completed successfully
2026-01-30 10:00:06 - INFO - Task ID: abc123-def456
2026-01-30 10:00:07 - INFO - Database connection established
2026-01-30 10:00:08 - INFO - {'task': 'transcription', 'prediction': '"Caller from Mombasa reported issue"'}
2026-01-30 10:00:09 - INFO - {'task': 'transcription', 'prediction': '"Contact number is 0722123456"'}
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
        f.write(content)
        temp_path = f.name

    yield Path(temp_path)

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def temp_log_dir():
    """Create a temporary directory with log files for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create log file with PII in prediction format
        log1 = temp_path / "app.log"
        log1.write_text("""2026-01-30 10:00:00 - INFO - {'task': 'transcription', 'prediction': '"Call from Wanjiru"'}
2026-01-30 10:00:01 - INFO - {'task': 'transcription', 'prediction': '"Phone is +254712345678"'}
2026-01-30 10:00:02 - INFO - Processing completed
""")

        # Create log file without PII
        log2 = temp_path / "system.log"
        log2.write_text("""2026-01-30 10:00:00 - INFO - System started
2026-01-30 10:00:01 - INFO - Database connected
2026-01-30 10:00:02 - INFO - Ready to accept requests
""")

        yield temp_path


@pytest.fixture
def clean_log_file():
    """Create a temporary log file without PII"""
    content = """2026-01-30 10:00:00 - INFO - System started
2026-01-30 10:00:01 - INFO - Database connected
2026-01-30 10:00:02 - INFO - Ready to accept requests
2026-01-30 10:00:03 - INFO - Task abc123 completed
2026-01-30 10:00:04 - INFO - Processing completed successfully
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
        f.write(content)
        temp_path = f.name

    yield Path(temp_path)

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)

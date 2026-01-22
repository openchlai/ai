"""
Pytest configuration for this test module.
Shared fixtures and test configurations.
"""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Fixture for FastAPI TestClient"""
    from app.main import app
    return TestClient(app)

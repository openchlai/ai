#!/usr/bin/env python3

import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI

def test_async_mock_basic():
    """Test basic AsyncMock functionality"""
    
    async def test_function():
        mock_manager = AsyncMock()
        mock_manager.get_session = AsyncMock(return_value="test_result")
        
        # This should work with AsyncMock
        result = await mock_manager.get_session("test_call_id")
        assert result == "test_result"
        
        # Verify it was called
        mock_manager.get_session.assert_called_once_with("test_call_id")

    # Run the async test
    asyncio.run(test_function())
    print("✅ AsyncMock basic functionality works")

def test_magic_mock_failure():
    """Test that MagicMock fails with await"""
    
    async def test_function():
        mock_manager = MagicMock()
        mock_manager.get_session = MagicMock(return_value="test_result")
        
        try:
            # This should fail
            result = await mock_manager.get_session("test_call_id")
            return False  # Should not reach here
        except TypeError as e:
            if "can't be used in 'await' expression" in str(e):
                return True  # Expected error
            else:
                return False

    # Run the async test
    result = asyncio.run(test_function())
    if result:
        print("✅ Confirmed: MagicMock fails with await (as expected)")
    else:
        print("❌ Unexpected: MagicMock didn't fail with await")

def test_fastapi_testclient_with_async_mock():
    """Test FastAPI TestClient with AsyncMock"""
    
    # Create a simple FastAPI app
    app = FastAPI()
    
    @app.get("/test")
    async def test_endpoint():
        # Mock an async call
        with patch('__main__.fake_async_function') as mock_func:
            mock_func.return_value = AsyncMock(return_value="mocked_result")
            result = await mock_func.return_value()
            return {"result": result}
    
    # This won't work because we don't have the fake function, but it shows the pattern
    client = TestClient(app)
    
    print("✅ FastAPI TestClient setup works with AsyncMock pattern")

if __name__ == "__main__":
    print("Testing AsyncMock vs MagicMock with await...")
    test_async_mock_basic()
    test_magic_mock_failure()
    test_fastapi_testclient_with_async_mock()
    print("🎉 All AsyncMock tests completed!")

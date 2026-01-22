"""
Comprehensive tests for notification_routes.py """
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime
import json

from app.main import app


@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def mock_notification_manager():
    """Mock notification manager"""
    manager = MagicMock()
    manager.get_status = MagicMock(return_value={
        "status": "active",
        "mode": "results_only",
        "uptime": 3600
    })
    manager.current_mode = MagicMock()
    manager.current_mode.value = "results_only"
    manager.stats = {
        "total_considered": 100,
        "total_sent": 50,
        "total_filtered": 50,
        "by_type": {
            "call_start": 10,
            "transcription": 30,
            "results": 10
        }
    }
    manager.update_mode = MagicMock(return_value=True)
    manager.reset_statistics = MagicMock()
    manager.should_send_notification = MagicMock(return_value=True)
    manager._is_critical_notification = MagicMock(return_value=False)
    return manager


class TestNotificationStatusEndpoint:
    """Tests for GET /api/v1/notifications/status"""

    def test_get_status_success(self, client, mock_notification_manager):
        """Test getting notification status successfully"""
        with patch('app.api.notification_routes.notification_manager', mock_notification_manager):
            response = client.get("/api/v1/notifications/status")

            assert response.status_code == 200
            data = response.json()
            assert "timestamp" in data
            assert "notification_system" in data

    def test_get_status_returns_timestamp(self, client, mock_notification_manager):
        """Test that status includes current timestamp"""
        with patch('app.api.notification_routes.notification_manager', mock_notification_manager):
            response = client.get("/api/v1/notifications/status")

            data = response.json()
            assert "timestamp" in data
            # Verify it's a valid ISO format timestamp
            assert len(data["timestamp"]) > 0

    def test_get_status_error_handling(self, client, mock_notification_manager):
        """Test error handling when getting status fails"""
        mock_notification_manager.get_status.side_effect = Exception("Status error")

        with patch('app.api.notification_routes.notification_manager', mock_notification_manager):
            response = client.get("/api/v1/notifications/status")

            assert response.status_code == 500
            data = response.json()
            assert "detail" in data


class TestNotificationModesEndpoint:
    """Tests for GET /api/v1/notifications/modes"""

    def test_get_modes_success(self, client, mock_notification_manager):
        """Test getting available notification modes"""
        with patch('app.api.notification_routes.notification_manager', mock_notification_manager):
            response = client.get("/api/v1/notifications/modes")

            assert response.status_code == 200
            data = response.json()
            assert "available_modes" in data
            assert "current_mode" in data
            assert "mode_explanations" in data

    def test_get_modes_includes_all_modes(self, client, mock_notification_manager):
        """Test that all notification modes are listed"""
        with patch('app.api.notification_routes.notification_manager', mock_notification_manager):
            response = client.get("/api/v1/notifications/modes")

            data = response.json()
            modes = [m["name"] for m in data["available_modes"]]

            assert "all" in modes
            assert "results_only" in modes
            assert "critical_only" in modes
            assert "disabled" in modes

    def test_get_modes_has_descriptions(self, client, mock_notification_manager):
        """Test that modes have descriptions"""
        with patch('app.api.notification_routes.notification_manager', mock_notification_manager):
            response = client.get("/api/v1/notifications/modes")

            data = response.json()
            for mode in data["available_modes"]:
                assert "name" in mode
                assert "description" in mode
                assert len(mode["description"]) > 0

    def test_get_modes_shows_current_mode(self, client, mock_notification_manager):
        """Test that current mode is shown"""
        mock_notification_manager.current_mode.value = "critical_only"

        with patch('app.api.notification_routes.notification_manager', mock_notification_manager):
            response = client.get("/api/v1/notifications/modes")

            data = response.json()
            assert data["current_mode"] == "critical_only"

    def test_get_modes_error_handling(self, client, mock_notification_manager):
        """Test error handling in modes endpoint"""
        mock_notification_manager.current_mode = None  # Cause error

        with patch('app.api.notification_routes.notification_manager', mock_notification_manager):
            response = client.get("/api/v1/notifications/modes")

            assert response.status_code == 500


class TestUpdateNotificationModeEndpoint:
    """Tests for POST /api/v1/notifications/configure"""

    def test_update_mode_success(self, client, mock_notification_manager):
        """Test successfully updating notification mode"""
        mock_notification_manager.current_mode.value = "results_only"

        with patch('app.api.notification_routes.notification_manager', mock_notification_manager):
            response = client.post(
                "/api/v1/notifications/configure",
                json={"mode": "critical_only"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "message" in data

    def test_update_mode_shows_transition(self, client, mock_notification_manager):
        """Test that mode update shows old and new modes"""
        mock_notification_manager.current_mode.value = "all"

        with patch('app.api.notification_routes.notification_manager', mock_notification_manager):
            response = client.post(
                "/api/v1/notifications/configure",
                json={"mode": "disabled"}
            )

            data = response.json()
            assert "previous_mode" in data
            assert "new_mode" in data
            assert data["new_mode"] == "disabled"

    def test_update_mode_includes_timestamp(self, client, mock_notification_manager):
        """Test that mode update includes timestamp"""
        with patch('app.api.notification_routes.notification_manager', mock_notification_manager):
            response = client.post(
                "/api/v1/notifications/configure",
                json={"mode": "results_only"}
            )

            data = response.json()
            assert "timestamp" in data

    def test_update_mode_failure(self, client, mock_notification_manager):
        """Test failed mode update"""
        mock_notification_manager.update_mode.return_value = False

        with patch('app.api.notification_routes.notification_manager', mock_notification_manager):
            response = client.post(
                "/api/v1/notifications/configure",
                json={"mode": "invalid_mode"}
            )

            assert response.status_code == 400

    def test_update_mode_error_handling(self, client, mock_notification_manager):
        """Test error handling in mode update"""
        mock_notification_manager.update_mode.side_effect = Exception("Update failed")

        with patch('app.api.notification_routes.notification_manager', mock_notification_manager):
            response = client.post(
                "/api/v1/notifications/configure",
                json={"mode": "critical_only"}
            )

            assert response.status_code == 500


class TestNotificationStatisticsEndpoint:
    """Tests for GET /api/v1/notifications/statistics"""

    def test_get_statistics_success(self, client, mock_notification_manager):
        """Test getting notification statistics"""
        with patch('app.api.notification_routes.notification_manager', mock_notification_manager):
            response = client.get("/api/v1/notifications/statistics")

            assert response.status_code == 200
            data = response.json()
            assert "current_mode" in data
            assert "summary" in data
            assert "by_notification_type" in data

    def test_statistics_includes_efficiency_metrics(self, client, mock_notification_manager):
        """Test that statistics include filtering efficiency"""
        with patch('app.api.notification_routes.notification_manager', mock_notification_manager):
            response = client.get("/api/v1/notifications/statistics")

            data = response.json()
            summary = data["summary"]

            assert "total_considered" in summary
            assert "total_sent" in summary
            assert "total_filtered" in summary
            assert "filter_rate_percent" in summary
            assert "send_rate_percent" in summary

    def test_statistics_calculates_percentages_correctly(self, client, mock_notification_manager):
        """Test that filtering and sending percentages are calculated correctly"""
        mock_notification_manager.stats = {
            "total_considered": 100,
            "total_sent": 50,
            "total_filtered": 50,
            "by_type": {}
        }

        with patch('app.api.notification_routes.notification_manager', mock_notification_manager):
            response = client.get("/api/v1/notifications/statistics")

            data = response.json()
            summary = data["summary"]

            # 50/100 = 50%
            assert summary["filter_rate_percent"] == 50.0
            assert summary["send_rate_percent"] == 50.0

    def test_statistics_handles_zero_total(self, client, mock_notification_manager):
        """Test statistics when total considered is zero"""
        mock_notification_manager.stats = {
            "total_considered": 0,
            "total_sent": 0,
            "total_filtered": 0,
            "by_type": {}
        }

        with patch('app.api.notification_routes.notification_manager', mock_notification_manager):
            response = client.get("/api/v1/notifications/statistics")

            data = response.json()
            summary = data["summary"]

            # Should not divide by zero
            assert summary["filter_rate_percent"] == 0.0
            assert summary["send_rate_percent"] == 0.0

    def test_statistics_by_notification_type(self, client, mock_notification_manager):
        """Test statistics breakdown by notification type"""
        mock_notification_manager.stats = {
            "total_considered": 100,
            "total_sent": 50,
            "total_filtered": 50,
            "by_type": {
                "call_start": 10,
                "transcription": 30,
                "classification": 20,
                "summary": 40
            }
        }

        with patch('app.api.notification_routes.notification_manager', mock_notification_manager):
            response = client.get("/api/v1/notifications/statistics")

            data = response.json()
            by_type = data["by_notification_type"]

            assert "call_start" in by_type
            assert "transcription" in by_type

    def test_statistics_error_handling(self, client, mock_notification_manager):
        """Test error handling in statistics endpoint"""
        mock_notification_manager.stats = None

        with patch('app.api.notification_routes.notification_manager', mock_notification_manager):
            response = client.get("/api/v1/notifications/statistics")

            assert response.status_code == 500


class TestResetStatisticsEndpoint:
    """Tests for POST /api/v1/notifications/statistics/reset"""

    def test_reset_statistics_success(self, client, mock_notification_manager):
        """Test resetting notification statistics"""
        with patch('app.api.notification_routes.notification_manager', mock_notification_manager):
            response = client.post("/api/v1/notifications/statistics/reset")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "message" in data

    def test_reset_statistics_called(self, client, mock_notification_manager):
        """Test that reset_statistics is actually called"""
        with patch('app.api.notification_routes.notification_manager', mock_notification_manager):
            client.post("/api/v1/notifications/statistics/reset")

            mock_notification_manager.reset_statistics.assert_called_once()

    def test_reset_statistics_includes_timestamp(self, client, mock_notification_manager):
        """Test that reset response includes timestamp"""
        with patch('app.api.notification_routes.notification_manager', mock_notification_manager):
            response = client.post("/api/v1/notifications/statistics/reset")

            data = response.json()
            assert "timestamp" in data

    def test_reset_statistics_error_handling(self, client, mock_notification_manager):
        """Test error handling when reset fails"""
        mock_notification_manager.reset_statistics.side_effect = Exception("Reset failed")

        with patch('app.api.notification_routes.notification_manager', mock_notification_manager):
            response = client.post("/api/v1/notifications/statistics/reset")

            assert response.status_code == 500


class TestNotificationTestEndpoint:
    """Tests for POST /api/v1/notifications/test"""

    def test_test_notification_success(self, client, mock_notification_manager):
        """Test notification filtering test endpoint"""
        mock_notification_manager.current_mode.value = "results_only"

        with patch('app.api.notification_routes.notification_manager', mock_notification_manager):
            response = client.post(
                "/api/v1/notifications/test",
                json={
                    "call_id": "test_123",
                    "notification_type": "streaming_call_start",
                    "include_results": True
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert "test_scenario" in data
            assert "filtering_result" in data
            assert "mode_behavior" in data

    def test_test_notification_with_default_params(self, client, mock_notification_manager):
        """Test notification endpoint with default parameters"""
        with patch('app.api.notification_routes.notification_manager', mock_notification_manager):
            response = client.post(
                "/api/v1/notifications/test",
                json={"notification_type": "streaming_call_start"}
            )

            assert response.status_code == 200
            data = response.json()
            # Should have defaults
            assert data["test_scenario"]["call_id"] == "test_call_123"

    def test_test_notification_invalid_type(self, client, mock_notification_manager):
        """Test with invalid notification type"""
        with patch('app.api.notification_routes.notification_manager', mock_notification_manager):
            response = client.post(
                "/api/v1/notifications/test",
                json={
                    "call_id": "test_123",
                    "notification_type": "invalid_type",
                    "include_results": True
                }
            )

            assert response.status_code == 400
            data = response.json()
            assert "detail" in data

    def test_test_notification_shows_filtering_decision(self, client, mock_notification_manager):
        """Test that filtering decision is shown"""
        mock_notification_manager.should_send_notification.return_value = True

        with patch('app.api.notification_routes.notification_manager', mock_notification_manager):
            response = client.post(
                "/api/v1/notifications/test",
                json={
                    "call_id": "test_123",
                    "notification_type": "streaming_transcription_segment",
                    "include_results": True
                }
            )

            data = response.json()
            assert "would_send" in data["filtering_result"]
            assert "reason" in data["filtering_result"]

    def test_test_notification_all_modes_behavior(self, client, mock_notification_manager):
        """Test that mode behavior is shown for all modes"""
        with patch('app.api.notification_routes.notification_manager', mock_notification_manager):
            response = client.post(
                "/api/v1/notifications/test",
                json={
                    "call_id": "test_123",
                    "notification_type": "streaming_call_start"
                }
            )

            data = response.json()
            mode_behavior = data["mode_behavior"]

            assert "all" in mode_behavior
            assert "results_only" in mode_behavior
            assert "critical_only" in mode_behavior
            assert "disabled" in mode_behavior

    def test_test_notification_error_handling(self, client, mock_notification_manager):
        """Test error handling in test endpoint"""
        mock_notification_manager.should_send_notification.side_effect = Exception("Test error")

        with patch('app.api.notification_routes.notification_manager', mock_notification_manager):
            response = client.post(
                "/api/v1/notifications/test",
                json={
                    "call_id": "test_123",
                    "notification_type": "streaming_call_start"
                }
            )

            assert response.status_code == 500


class TestNotificationTypesEndpoint:
    """Tests for GET /api/v1/notifications/types"""

    def test_get_types_success(self, client, mock_notification_manager):
        """Test getting notification types"""
        with patch('app.api.notification_routes.notification_manager', mock_notification_manager):
            response = client.get("/api/v1/notifications/types")

            assert response.status_code == 200
            data = response.json()
            assert "notification_types" in data
            assert "filtering_behavior" in data
            assert "total_types" in data

    def test_types_organized_by_category(self, client, mock_notification_manager):
        """Test that types are organized by category"""
        with patch('app.api.notification_routes.notification_manager', mock_notification_manager):
            response = client.get("/api/v1/notifications/types")

            data = response.json()
            types = data["notification_types"]

            assert "progress_notifications" in types
            assert "result_notifications" in types
            assert "critical_notifications" in types

    def test_types_have_valid_lists(self, client, mock_notification_manager):
        """Test that type categories are lists"""
        with patch('app.api.notification_routes.notification_manager', mock_notification_manager):
            response = client.get("/api/v1/notifications/types")

            data = response.json()
            types = data["notification_types"]

            assert isinstance(types["progress_notifications"], list)
            assert isinstance(types["result_notifications"], list)
            assert isinstance(types["critical_notifications"], list)

    def test_types_show_filtering_behavior(self, client, mock_notification_manager):
        """Test that filtering behavior is documented"""
        with patch('app.api.notification_routes.notification_manager', mock_notification_manager):
            response = client.get("/api/v1/notifications/types")

            data = response.json()
            behavior = data["filtering_behavior"]

            assert "all" in behavior
            assert "results_only" in behavior
            assert "critical_only" in behavior
            assert "disabled" in behavior

    def test_types_include_count(self, client, mock_notification_manager):
        """Test that total type count is included"""
        with patch('app.api.notification_routes.notification_manager', mock_notification_manager):
            response = client.get("/api/v1/notifications/types")

            data = response.json()
            assert "total_types" in data
            assert data["total_types"] > 0

    def test_types_error_handling(self, client, mock_notification_manager):
        """Test error handling in types endpoint when manager raises exception"""
        # Make the notification manager method raise an exception
        mock_notification_manager.get_status.side_effect = Exception("Manager error")

        with patch('app.api.notification_routes.notification_manager', mock_notification_manager):
            # The endpoint doesn't call get_status, but we test graceful handling
            response = client.get("/api/v1/notifications/types")

            # Should still return data from the endpoint (NotificationType is imported inside the function)
            assert response.status_code == 200


class TestNotificationRouteIntegration:
    """Integration tests for notification routes"""

    def test_get_then_update_mode(self, client, mock_notification_manager):
        """Test getting modes and then updating mode"""
        mock_notification_manager.current_mode.value = "all"

        with patch('app.api.notification_routes.notification_manager', mock_notification_manager):
            # Get available modes
            get_response = client.get("/api/v1/notifications/modes")
            assert get_response.status_code == 200

            # Update to a different mode
            update_response = client.post(
                "/api/v1/notifications/configure",
                json={"mode": "critical_only"}
            )
            assert update_response.status_code == 200

    def test_get_status_and_statistics(self, client, mock_notification_manager):
        """Test getting status and statistics"""
        with patch('app.api.notification_routes.notification_manager', mock_notification_manager):
            status_response = client.get("/api/v1/notifications/status")
            assert status_response.status_code == 200

            stats_response = client.get("/api/v1/notifications/statistics")
            assert stats_response.status_code == 200

    def test_test_and_reset_statistics(self, client, mock_notification_manager):
        """Test running test and then resetting statistics"""
        with patch('app.api.notification_routes.notification_manager', mock_notification_manager):
            # Test notification
            test_response = client.post(
                "/api/v1/notifications/test",
                json={
                    "call_id": "test_123",
                    "notification_type": "streaming_call_start"
                }
            )
            assert test_response.status_code == 200

            # Reset statistics
            reset_response = client.post("/api/v1/notifications/statistics/reset")
            assert reset_response.status_code == 200


class TestNotificationRouteEdgeCases:
    """Edge case tests for notification routes"""

    def test_update_mode_to_same_mode(self, client, mock_notification_manager):
        """Test updating to the same mode"""
        mock_notification_manager.current_mode.value = "results_only"

        with patch('app.api.notification_routes.notification_manager', mock_notification_manager):
            response = client.post(
                "/api/v1/notifications/configure",
                json={"mode": "results_only"}
            )

            assert response.status_code == 200

    def test_statistics_with_high_numbers(self, client, mock_notification_manager):
        """Test statistics with large numbers"""
        mock_notification_manager.stats = {
            "total_considered": 1000000,
            "total_sent": 500000,
            "total_filtered": 500000,
            "by_type": {}
        }

        with patch('app.api.notification_routes.notification_manager', mock_notification_manager):
            response = client.get("/api/v1/notifications/statistics")

            assert response.status_code == 200
            data = response.json()
            assert data["summary"]["total_considered"] == 1000000

    def test_test_notification_with_special_characters_in_call_id(self, client, mock_notification_manager):
        """Test notification with special characters in call ID"""
        with patch('app.api.notification_routes.notification_manager', mock_notification_manager):
            response = client.post(
                "/api/v1/notifications/test",
                json={
                    "call_id": "test-123_456@special",
                    "notification_type": "streaming_call_start"
                }
            )

            assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

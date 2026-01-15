"""
Comprehensive tests for FeedbackRepository - Agent feedback database operations
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch, Mock, call
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.repositories.feedback_repository import FeedbackRepository
from app.db.models import AgentFeedback


class TestFeedbackRepositoryCreateInitialFeedback:
    """Tests for FeedbackRepository.create_initial_feedback method"""

    @patch('app.db.repositories.feedback_repository.logger')
    def test_create_initial_feedback_success(self, mock_logger):
        """Test successful creation of initial feedback"""
        mock_db = MagicMock(spec=Session)
        mock_feedback = MagicMock(spec=AgentFeedback)
        mock_db.refresh.return_value = None

        # Mock add and commit to succeed
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()

        with patch('app.db.repositories.feedback_repository.AgentFeedback') as mock_model:
            mock_model.return_value = mock_feedback
            mock_feedback.call_id = "call_123"
            mock_feedback.task = "classification"

            result = FeedbackRepository.create_initial_feedback(
                db=mock_db,
                call_id="call_123",
                task="classification",
                prediction={"class": "urgent"}
            )

            assert result == mock_feedback
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once()

    @patch('app.db.repositories.feedback_repository.logger')
    def test_create_initial_feedback_with_processing_mode(self, mock_logger):
        """Test feedback creation with processing_mode"""
        mock_db = MagicMock(spec=Session)
        mock_feedback = MagicMock(spec=AgentFeedback)
        mock_db.refresh.return_value = None

        with patch('app.db.repositories.feedback_repository.AgentFeedback') as mock_model:
            mock_model.return_value = mock_feedback

            FeedbackRepository.create_initial_feedback(
                db=mock_db,
                call_id="call_456",
                task="ner",
                prediction={"entities": []},
                processing_mode="realtime"
            )

            # Verify AgentFeedback was instantiated with processing_mode
            mock_model.assert_called_once()
            call_kwargs = mock_model.call_args.kwargs
            assert call_kwargs["processing_mode"] == "realtime"

    @patch('app.db.repositories.feedback_repository.logger')
    def test_create_initial_feedback_with_model_version(self, mock_logger):
        """Test feedback creation with model_version"""
        mock_db = MagicMock(spec=Session)
        mock_feedback = MagicMock(spec=AgentFeedback)
        mock_db.refresh.return_value = None

        with patch('app.db.repositories.feedback_repository.AgentFeedback') as mock_model:
            mock_model.return_value = mock_feedback

            FeedbackRepository.create_initial_feedback(
                db=mock_db,
                call_id="call_789",
                task="summarization",
                prediction={"summary": "test"},
                model_version="v2.0"
            )

            call_kwargs = mock_model.call_args.kwargs
            assert call_kwargs["model_version"] == "v2.0"

    @patch('app.db.repositories.feedback_repository.logger')
    def test_create_initial_feedback_integrity_error(self, mock_logger):
        """Test feedback creation handles IntegrityError"""
        mock_db = MagicMock(spec=Session)
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock(side_effect=IntegrityError("Duplicate", None, None))
        mock_db.rollback = MagicMock()

        with patch('app.db.repositories.feedback_repository.AgentFeedback') as mock_model:
            mock_feedback = MagicMock()
            mock_model.return_value = mock_feedback

            result = FeedbackRepository.create_initial_feedback(
                db=mock_db,
                call_id="call_dup",
                task="classification",
                prediction={"class": "test"}
            )

            assert result is None
            mock_db.rollback.assert_called_once()
            mock_logger.warning.assert_called_once()

    @patch('app.db.repositories.feedback_repository.logger')
    def test_create_initial_feedback_generic_exception(self, mock_logger):
        """Test feedback creation handles generic exceptions"""
        mock_db = MagicMock(spec=Session)
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock(side_effect=Exception("Database error"))
        mock_db.rollback = MagicMock()

        with patch('app.db.repositories.feedback_repository.AgentFeedback') as mock_model:
            mock_feedback = MagicMock()
            mock_model.return_value = mock_feedback

            result = FeedbackRepository.create_initial_feedback(
                db=mock_db,
                call_id="call_error",
                task="classification",
                prediction={"class": "test"}
            )

            assert result is None
            mock_db.rollback.assert_called_once()
            mock_logger.error.assert_called_once()

    @patch('app.db.repositories.feedback_repository.logger')
    def test_create_initial_feedback_feedback_is_none(self, mock_logger):
        """Test initial feedback has None feedback value"""
        mock_db = MagicMock(spec=Session)

        with patch('app.db.repositories.feedback_repository.AgentFeedback') as mock_model:
            mock_feedback = MagicMock()
            mock_model.return_value = mock_feedback

            FeedbackRepository.create_initial_feedback(
                db=mock_db,
                call_id="call_test",
                task="classification",
                prediction={"class": "test"}
            )

            call_kwargs = mock_model.call_args.kwargs
            assert call_kwargs["feedback"] is None

    @patch('app.db.repositories.feedback_repository.logger')
    def test_create_initial_feedback_reason_is_none(self, mock_logger):
        """Test initial feedback has None reason value"""
        mock_db = MagicMock(spec=Session)

        with patch('app.db.repositories.feedback_repository.AgentFeedback') as mock_model:
            mock_feedback = MagicMock()
            mock_model.return_value = mock_feedback

            FeedbackRepository.create_initial_feedback(
                db=mock_db,
                call_id="call_test",
                task="classification",
                prediction={"class": "test"}
            )

            call_kwargs = mock_model.call_args.kwargs
            assert call_kwargs["reason"] is None

    @patch('app.db.repositories.feedback_repository.logger')
    def test_create_initial_feedback_complex_prediction(self, mock_logger):
        """Test feedback creation with complex prediction JSON"""
        mock_db = MagicMock(spec=Session)
        mock_feedback = MagicMock(spec=AgentFeedback)
        mock_db.refresh.return_value = None

        complex_prediction = {
            "class": "urgent",
            "confidence": 0.95,
            "details": {"reason": "high priority"}
        }

        with patch('app.db.repositories.feedback_repository.AgentFeedback') as mock_model:
            mock_model.return_value = mock_feedback

            result = FeedbackRepository.create_initial_feedback(
                db=mock_db,
                call_id="call_complex",
                task="classification",
                prediction=complex_prediction
            )

            call_kwargs = mock_model.call_args.kwargs
            assert call_kwargs["prediction"] == complex_prediction


class TestFeedbackRepositoryUpdateFeedback:
    """Tests for FeedbackRepository.update_feedback method"""

    @patch('app.db.repositories.feedback_repository.logger')
    def test_update_feedback_success(self, mock_logger):
        """Test successful feedback update"""
        mock_db = MagicMock(spec=Session)
        mock_feedback = MagicMock(spec=AgentFeedback)
        mock_feedback.feedback = None
        mock_feedback.reason = None
        mock_feedback.updated_at = None

        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_feedback
        mock_db.query.return_value = mock_query
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()

        result = FeedbackRepository.update_feedback(
            db=mock_db,
            call_id="call_123",
            task="classification",
            feedback_rating=5,
            reason="Correct prediction"
        )

        assert result == mock_feedback
        assert mock_feedback.feedback == 5
        assert mock_feedback.reason == "Correct prediction"
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @patch('app.db.repositories.feedback_repository.logger')
    def test_update_feedback_all_rating_values(self, mock_logger):
        """Test update_feedback with all valid rating values"""
        for rating in [1, 2, 3, 4, 5]:
            mock_db = MagicMock(spec=Session)
            mock_feedback = MagicMock(spec=AgentFeedback)

            mock_query = MagicMock()
            mock_query.filter.return_value.first.return_value = mock_feedback
            mock_db.query.return_value = mock_query

            result = FeedbackRepository.update_feedback(
                db=mock_db,
                call_id="call_test",
                task="classification",
                feedback_rating=rating
            )

            assert result == mock_feedback
            assert mock_feedback.feedback == rating

    @patch('app.db.repositories.feedback_repository.logger')
    def test_update_feedback_rating_too_low(self, mock_logger):
        """Test update_feedback rejects rating below 1"""
        mock_db = MagicMock(spec=Session)

        with pytest.raises(ValueError, match="between 1 and 5"):
            FeedbackRepository.update_feedback(
                db=mock_db,
                call_id="call_test",
                task="classification",
                feedback_rating=0
            )

    @patch('app.db.repositories.feedback_repository.logger')
    def test_update_feedback_rating_too_high(self, mock_logger):
        """Test update_feedback rejects rating above 5"""
        mock_db = MagicMock(spec=Session)

        with pytest.raises(ValueError, match="between 1 and 5"):
            FeedbackRepository.update_feedback(
                db=mock_db,
                call_id="call_test",
                task="classification",
                feedback_rating=6
            )

    @patch('app.db.repositories.feedback_repository.logger')
    def test_update_feedback_not_found(self, mock_logger):
        """Test update_feedback when entry doesn't exist"""
        mock_db = MagicMock(spec=Session)
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query

        result = FeedbackRepository.update_feedback(
            db=mock_db,
            call_id="call_notfound",
            task="classification",
            feedback_rating=5
        )

        assert result is None
        mock_logger.warning.assert_called_once()

    @patch('app.db.repositories.feedback_repository.logger')
    def test_update_feedback_exception_handling(self, mock_logger):
        """Test update_feedback handles exceptions"""
        mock_db = MagicMock(spec=Session)
        mock_db.query = MagicMock(side_effect=Exception("Database error"))
        mock_db.rollback = MagicMock()

        result = FeedbackRepository.update_feedback(
            db=mock_db,
            call_id="call_error",
            task="classification",
            feedback_rating=5
        )

        assert result is None
        mock_db.rollback.assert_called_once()
        mock_logger.error.assert_called_once()

    @patch('app.db.repositories.feedback_repository.logger')
    def test_update_feedback_with_long_reason(self, mock_logger):
        """Test update_feedback with long reason text"""
        mock_db = MagicMock(spec=Session)
        mock_feedback = MagicMock(spec=AgentFeedback)

        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_feedback
        mock_db.query.return_value = mock_query

        long_reason = "This is a very long reason " * 10

        result = FeedbackRepository.update_feedback(
            db=mock_db,
            call_id="call_long",
            task="classification",
            feedback_rating=4,
            reason=long_reason
        )

        assert result == mock_feedback
        assert mock_feedback.reason == long_reason

    @patch('app.db.repositories.feedback_repository.logger')
    def test_update_feedback_without_reason(self, mock_logger):
        """Test update_feedback without providing reason"""
        mock_db = MagicMock(spec=Session)
        mock_feedback = MagicMock(spec=AgentFeedback)
        mock_feedback.reason = None

        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_feedback
        mock_db.query.return_value = mock_query

        result = FeedbackRepository.update_feedback(
            db=mock_db,
            call_id="call_noreason",
            task="classification",
            feedback_rating=3
        )

        assert result == mock_feedback

    @patch('app.db.repositories.feedback_repository.logger')
    def test_update_feedback_updates_timestamp(self, mock_logger):
        """Test update_feedback sets updated_at timestamp"""
        mock_db = MagicMock(spec=Session)
        mock_feedback = MagicMock(spec=AgentFeedback)

        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_feedback
        mock_db.query.return_value = mock_query

        FeedbackRepository.update_feedback(
            db=mock_db,
            call_id="call_timestamp",
            task="classification",
            feedback_rating=4
        )

        # Check updated_at was set
        assert mock_feedback.updated_at is not None


class TestFeedbackRepositoryGetFeedback:
    """Tests for FeedbackRepository.get_feedback method"""

    @patch('app.db.repositories.feedback_repository.logger')
    def test_get_feedback_by_call_id(self, mock_logger):
        """Test retrieving feedback by call_id"""
        mock_db = MagicMock(spec=Session)
        mock_feedback1 = MagicMock(spec=AgentFeedback)
        mock_feedback2 = MagicMock(spec=AgentFeedback)

        mock_query = MagicMock()
        mock_query.filter.return_value.all.return_value = [mock_feedback1, mock_feedback2]
        mock_db.query.return_value = mock_query

        result = FeedbackRepository.get_feedback(
            db=mock_db,
            call_id="call_123"
        )

        assert len(result) == 2
        assert mock_feedback1 in result
        assert mock_feedback2 in result

    @patch('app.db.repositories.feedback_repository.logger')
    def test_get_feedback_with_task_filter(self, mock_logger):
        """Test retrieving feedback filtered by task"""
        mock_db = MagicMock(spec=Session)
        mock_feedback = MagicMock(spec=AgentFeedback)

        mock_query = MagicMock()
        mock_query.filter.return_value.filter.return_value.all.return_value = [mock_feedback]
        mock_db.query.return_value = mock_query

        result = FeedbackRepository.get_feedback(
            db=mock_db,
            call_id="call_123",
            task="classification"
        )

        assert len(result) == 1
        assert mock_feedback in result

    @patch('app.db.repositories.feedback_repository.logger')
    def test_get_feedback_empty_result(self, mock_logger):
        """Test get_feedback when no results found"""
        mock_db = MagicMock(spec=Session)
        mock_query = MagicMock()
        mock_query.filter.return_value.all.return_value = []
        mock_db.query.return_value = mock_query

        result = FeedbackRepository.get_feedback(
            db=mock_db,
            call_id="call_notfound"
        )

        assert result == []

    @patch('app.db.repositories.feedback_repository.logger')
    def test_get_feedback_exception_handling(self, mock_logger):
        """Test get_feedback handles exceptions"""
        mock_db = MagicMock(spec=Session)
        mock_db.query = MagicMock(side_effect=Exception("Query error"))

        result = FeedbackRepository.get_feedback(
            db=mock_db,
            call_id="call_error"
        )

        assert result == []
        mock_logger.error.assert_called_once()

    @patch('app.db.repositories.feedback_repository.logger')
    def test_get_feedback_multiple_tasks(self, mock_logger):
        """Test get_feedback returns multiple task types"""
        mock_db = MagicMock(spec=Session)
        mock_feedback_ner = MagicMock(spec=AgentFeedback)
        mock_feedback_classification = MagicMock(spec=AgentFeedback)

        mock_query = MagicMock()
        mock_query.filter.return_value.all.return_value = [
            mock_feedback_ner,
            mock_feedback_classification
        ]
        mock_db.query.return_value = mock_query

        result = FeedbackRepository.get_feedback(
            db=mock_db,
            call_id="call_123"
        )

        assert len(result) == 2


class TestFeedbackRepositoryGetStatistics:
    """Tests for FeedbackRepository.get_feedback_statistics method"""

    @patch('app.db.repositories.feedback_repository.logger')
    @patch('app.db.repositories.feedback_repository.datetime')
    def test_get_feedback_statistics_success(self, mock_datetime, mock_logger):
        """Test successful statistics retrieval"""
        mock_db = MagicMock(spec=Session)
        mock_datetime.now.return_value = datetime(2024, 1, 15)

        mock_row = MagicMock()
        mock_row.task = "classification"
        mock_row.total_count = 100
        mock_row.rated_count = 80
        mock_row.avg_rating = 4.2
        mock_row.min_rating = 1
        mock_row.max_rating = 5

        mock_query = MagicMock()
        mock_query.filter.return_value.filter.return_value.filter.return_value.group_by.return_value.all.return_value = [mock_row]
        mock_db.query.return_value = mock_query

        result = FeedbackRepository.get_feedback_statistics(
            db=mock_db,
            days=30
        )

        assert "period_days" in result
        assert result["period_days"] == 30
        assert "tasks" in result

    @patch('app.db.repositories.feedback_repository.logger')
    @patch('app.db.repositories.feedback_repository.datetime')
    def test_get_feedback_statistics_with_task_filter(self, mock_datetime, mock_logger):
        """Test statistics retrieval filtered by task"""
        mock_db = MagicMock(spec=Session)
        mock_datetime.now.return_value = datetime(2024, 1, 15)

        mock_row = MagicMock()
        mock_row.task = "ner"
        mock_row.total_count = 50
        mock_row.rated_count = 40
        mock_row.avg_rating = 4.0
        mock_row.min_rating = 2
        mock_row.max_rating = 5

        mock_query = MagicMock()
        mock_query.filter.return_value.filter.return_value.filter.return_value.group_by.return_value.all.return_value = [mock_row]
        mock_db.query.return_value = mock_query

        result = FeedbackRepository.get_feedback_statistics(
            db=mock_db,
            task="ner",
            days=30
        )

        assert result["period_days"] == 30

    @patch('app.db.repositories.feedback_repository.logger')
    @patch('app.db.repositories.feedback_repository.datetime')
    def test_get_feedback_statistics_rating_coverage_calculation(self, mock_datetime, mock_logger):
        """Test rating coverage percentage calculation"""
        mock_db = MagicMock(spec=Session)
        mock_datetime.now.return_value = datetime(2024, 1, 15)

        mock_row = MagicMock()
        mock_row.task = "classification"
        mock_row.total_count = 100
        mock_row.rated_count = 75
        mock_row.avg_rating = 4.5
        mock_row.min_rating = 3
        mock_row.max_rating = 5

        # Use a chainable mock for query
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.group_by.return_value = mock_query
        mock_query.all.return_value = [mock_row]
        mock_db.query.return_value = mock_query

        result = FeedbackRepository.get_feedback_statistics(
            db=mock_db,
            days=30
        )

        # Rating coverage should be 75%
        task_stats = result["tasks"]["classification"]
        assert task_stats["rating_coverage"] == 75.0

    @patch('app.db.repositories.feedback_repository.logger')
    @patch('app.db.repositories.feedback_repository.datetime')
    def test_get_feedback_statistics_no_ratings(self, mock_datetime, mock_logger):
        """Test statistics when no ratings exist"""
        mock_db = MagicMock(spec=Session)
        mock_datetime.now.return_value = datetime(2024, 1, 15)

        mock_row = MagicMock()
        mock_row.task = "classification"
        mock_row.total_count = 50
        mock_row.rated_count = 0
        mock_row.avg_rating = None
        mock_row.min_rating = None
        mock_row.max_rating = None

        # Use a chainable mock for query
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.group_by.return_value = mock_query
        mock_query.all.return_value = [mock_row]
        mock_db.query.return_value = mock_query

        result = FeedbackRepository.get_feedback_statistics(
            db=mock_db,
            days=30
        )

        task_stats = result["tasks"]["classification"]
        assert task_stats["rating_coverage"] == 0.0

    @patch('app.db.repositories.feedback_repository.logger')
    @patch('app.db.repositories.feedback_repository.datetime')
    def test_get_feedback_statistics_exception_handling(self, mock_datetime, mock_logger):
        """Test statistics handles exceptions"""
        mock_db = MagicMock(spec=Session)
        mock_db.query = MagicMock(side_effect=Exception("Statistics error"))

        result = FeedbackRepository.get_feedback_statistics(
            db=mock_db,
            days=30
        )

        assert "error" in result
        mock_logger.error.assert_called_once()

    @patch('app.db.repositories.feedback_repository.logger')
    @patch('app.db.repositories.feedback_repository.datetime')
    def test_get_feedback_statistics_multiple_tasks(self, mock_datetime, mock_logger):
        """Test statistics for multiple tasks"""
        mock_db = MagicMock(spec=Session)
        mock_datetime.now.return_value = datetime(2024, 1, 15)

        mock_row1 = MagicMock()
        mock_row1.task = "classification"
        mock_row1.total_count = 100
        mock_row1.rated_count = 80
        mock_row1.avg_rating = 4.2
        mock_row1.min_rating = 1
        mock_row1.max_rating = 5

        mock_row2 = MagicMock()
        mock_row2.task = "ner"
        mock_row2.total_count = 60
        mock_row2.rated_count = 50
        mock_row2.avg_rating = 4.0
        mock_row2.min_rating = 2
        mock_row2.max_rating = 5

        # Use a chainable mock for query
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.group_by.return_value = mock_query
        mock_query.all.return_value = [mock_row1, mock_row2]
        mock_db.query.return_value = mock_query

        result = FeedbackRepository.get_feedback_statistics(
            db=mock_db,
            days=30
        )

        assert "classification" in result["tasks"]
        assert "ner" in result["tasks"]

    @patch('app.db.repositories.feedback_repository.logger')
    @patch('app.db.repositories.feedback_repository.datetime')
    def test_get_feedback_statistics_different_days(self, mock_datetime, mock_logger):
        """Test statistics with different time periods"""
        for days in [7, 14, 30, 60, 90]:
            mock_db = MagicMock(spec=Session)
            mock_datetime.now.return_value = datetime(2024, 1, 15)

            mock_row = MagicMock()
            mock_row.task = "classification"
            mock_row.total_count = 100
            mock_row.rated_count = 80
            mock_row.avg_rating = 4.2
            mock_row.min_rating = 1
            mock_row.max_rating = 5

            mock_query = MagicMock()
            mock_query.filter.return_value.filter.return_value.filter.return_value.group_by.return_value.all.return_value = [mock_row]
            mock_db.query.return_value = mock_query

            result = FeedbackRepository.get_feedback_statistics(
                db=mock_db,
                days=days
            )

            assert result["period_days"] == days


class TestFeedbackRepositoryStatic:
    """Tests for static method behavior"""

    def test_create_initial_feedback_is_static(self):
        """Test create_initial_feedback is a static method"""
        assert isinstance(
            FeedbackRepository.__dict__['create_initial_feedback'],
            staticmethod
        )

    def test_update_feedback_is_static(self):
        """Test update_feedback is a static method"""
        assert isinstance(
            FeedbackRepository.__dict__['update_feedback'],
            staticmethod
        )

    def test_get_feedback_is_static(self):
        """Test get_feedback is a static method"""
        assert isinstance(
            FeedbackRepository.__dict__['get_feedback'],
            staticmethod
        )

    def test_get_feedback_statistics_is_static(self):
        """Test get_feedback_statistics is a static method"""
        assert isinstance(
            FeedbackRepository.__dict__['get_feedback_statistics'],
            staticmethod
        )

    def test_all_methods_are_static(self):
        """Test all public methods are static"""
        methods = [
            'create_initial_feedback',
            'update_feedback',
            'get_feedback',
            'get_feedback_statistics'
        ]
        for method_name in methods:
            assert isinstance(
                FeedbackRepository.__dict__[method_name],
                staticmethod
            ), f"{method_name} is not static"

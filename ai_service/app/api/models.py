"""
Shared API models and schemas for standardized responses.

This module defines common Pydantic models used across all API endpoints
for consistent request/response structures and OpenAPI documentation.
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime


class ErrorDetail(BaseModel):
    """Detailed error information for debugging and logging."""

    error_code: str = Field(
        ...,
        description="Machine-readable error code (e.g., 'MODEL_NOT_READY', 'VALIDATION_ERROR')",
        example="MODEL_NOT_READY"
    )
    message: str = Field(
        ...,
        description="Human-readable error message",
        example="The NER model is not ready. Please check /health/models for status."
    )
    detail: Optional[str] = Field(
        None,
        description="Additional error details for debugging",
        example="Model failed to load due to missing dependencies"
    )
    field: Optional[str] = Field(
        None,
        description="Field name if this is a validation error",
        example="text"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="When the error occurred (ISO 8601 format)",
        example="2024-01-18T10:30:00Z"
    )


class ErrorResponse(BaseModel):
    """
    Standardized error response for all API endpoints.

    This model ensures consistent error reporting across the entire API,
    making it easier for clients to handle errors programmatically.

    Example:
        {
            "error": {
                "error_code": "MODEL_NOT_READY",
                "message": "NER model not ready",
                "detail": "Model initialization failed",
                "timestamp": "2024-01-18T10:30:00Z"
            },
            "status": "error",
            "request_id": "req_123456"
        }
    """

    error: ErrorDetail = Field(
        ...,
        description="Error details"
    )
    status: str = Field(
        default="error",
        description="Response status (always 'error' for error responses)",
        example="error"
    )
    request_id: Optional[str] = Field(
        None,
        description="Request ID for tracking and debugging",
        example="req_abc123def456"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "error": {
                    "error_code": "TASK_SUBMISSION_FAILED",
                    "message": "Failed to submit task to Celery queue",
                    "detail": "Redis connection timeout",
                    "timestamp": "2024-01-18T10:30:00.000Z"
                },
                "status": "error",
                "request_id": "req_abc123"
            }
        }


class TaskResponse(BaseModel):
    """
    Standardized response for async task submission endpoints.

    Used by all endpoints that submit Celery tasks and return task IDs
    for polling via task status endpoints.
    """

    task_id: str = Field(
        ...,
        description="Unique task identifier for polling status",
        example="task_abc123def456"
    )
    status: str = Field(
        default="queued",
        description="Initial task status (always 'queued' for new tasks)",
        example="queued"
    )
    message: str = Field(
        default="Task submitted successfully",
        description="Human-readable status message",
        example="NER extraction task submitted and queued for processing"
    )
    status_endpoint: str = Field(
        ...,
        description="URL endpoint to poll for task status",
        example="/ner/task/task_abc123def456"
    )
    estimated_time: Optional[int] = Field(
        None,
        description="Estimated processing time in seconds (if available)",
        example=5
    )

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "task_a1b2c3d4",
                "status": "queued",
                "message": "Classification task submitted successfully",
                "status_endpoint": "/classifier/task/task_a1b2c3d4",
                "estimated_time": 3
            }
        }


class TaskStatusResponse(BaseModel):
    """
    Standardized response for task status polling endpoints.

    Provides consistent structure for checking the status of async tasks.
    """

    task_id: str = Field(
        ...,
        description="Task identifier",
        example="task_abc123"
    )
    status: str = Field(
        ...,
        description="Current task status: 'pending', 'processing', 'success', 'failed'",
        example="processing"
    )
    progress: Optional[Dict[str, Any]] = Field(
        None,
        description="Progress information (if task is processing)",
        example={"percent": 50, "step": "entity_extraction"}
    )
    result: Optional[Dict[str, Any]] = Field(
        None,
        description="Task result (if status is 'success')",
        example={"entities": [{"text": "John", "label": "PERSON"}]}
    )
    error: Optional[str] = Field(
        None,
        description="Error message (if status is 'failed')",
        example="Model not available"
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "summary": "Task pending",
                    "value": {
                        "task_id": "task_123",
                        "status": "pending",
                        "progress": {"message": "Task queued for processing"}
                    }
                },
                {
                    "summary": "Task processing",
                    "value": {
                        "task_id": "task_123",
                        "status": "processing",
                        "progress": {"percent": 50, "step": "classification"}
                    }
                },
                {
                    "summary": "Task success",
                    "value": {
                        "task_id": "task_123",
                        "status": "success",
                        "result": {
                            "main_category": "abuse",
                            "confidence": 0.95,
                            "processing_time": 1.2
                        }
                    }
                },
                {
                    "summary": "Task failed",
                    "value": {
                        "task_id": "task_123",
                        "status": "failed",
                        "error": "Classification model not ready"
                    }
                }
            ]
        }


class HealthCheckResponse(BaseModel):
    """Standardized health check response."""

    status: str = Field(
        ...,
        description="Overall health status: 'healthy', 'degraded', 'unhealthy'",
        example="healthy"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Health check timestamp",
        example="2024-01-18T10:30:00Z"
    )
    checks: Optional[Dict[str, Any]] = Field(
        None,
        description="Detailed health check results by component",
        example={
            "database": {"status": "healthy"},
            "redis": {"status": "healthy"},
            "models": {"status": "healthy", "ready": 6, "failed": 0}
        }
    )


# Standard error codes for consistent error handling
class ErrorCodes:
    """Standard error codes used across the API."""

    # Model errors (1xxx)
    MODEL_NOT_READY = "MODEL_NOT_READY"
    MODEL_NOT_AVAILABLE = "MODEL_NOT_AVAILABLE"
    MODEL_LOADING_FAILED = "MODEL_LOADING_FAILED"

    # Task errors (2xxx)
    TASK_SUBMISSION_FAILED = "TASK_SUBMISSION_FAILED"
    TASK_NOT_FOUND = "TASK_NOT_FOUND"
    TASK_TIMEOUT = "TASK_TIMEOUT"
    TASK_CANCELLED = "TASK_CANCELLED"

    # Validation errors (3xxx)
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"

    # Resource errors (4xxx)
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_UNAVAILABLE = "RESOURCE_UNAVAILABLE"
    INSUFFICIENT_RESOURCES = "INSUFFICIENT_RESOURCES"

    # System errors (5xxx)
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    TIMEOUT = "TIMEOUT"

    # File errors (6xxx)
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    INVALID_FILE_FORMAT = "INVALID_FILE_FORMAT"
    FILE_UPLOAD_FAILED = "FILE_UPLOAD_FAILED"


def create_error_response(
    error_code: str,
    message: str,
    detail: Optional[str] = None,
    field: Optional[str] = None,
    request_id: Optional[str] = None
) -> ErrorResponse:
    """
    Helper function to create standardized error responses.

    Args:
        error_code: Machine-readable error code from ErrorCodes
        message: Human-readable error message
        detail: Optional additional error details
        field: Optional field name for validation errors
        request_id: Optional request ID for tracking

    Returns:
        ErrorResponse: Standardized error response

    Example:
        >>> error = create_error_response(
        ...     error_code=ErrorCodes.MODEL_NOT_READY,
        ...     message="NER model is not ready",
        ...     detail="Model initialization failed"
        ... )
    """
    return ErrorResponse(
        error=ErrorDetail(
            error_code=error_code,
            message=message,
            detail=detail,
            field=field
        ),
        request_id=request_id
    )

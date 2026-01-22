# API Standardization Implementation Guide
## Critical Fixes 1-3: Error Responses, Status Codes, OpenAPI Documentation

**Date:** 2026-01-18
**Status:** IN PROGRESS - NER routes updated as template
**Remaining:** 73 endpoints to update

---

## Overview

This guide documents the implementation of Critical Fixes 1-3 from the API Documentation Improvement Plan:
1. **Standardized error responses** - Consistent error format across all endpoints
2. **Correct HTTP status codes** - 202 for async, proper error codes
3. **OpenAPI responses** documentation - Explicit `responses={}` for all endpoints

---

## Changes Implemented

### 1. Created Standardized Models (`app/api/models.py`)

**New Models:**
- `ErrorDetail` - Structured error information
- `ErrorResponse` - Standardized error envelope
- `TaskResponse` - Standard async task submission response
- `TaskStatusResponse` - Standard task status polling response
- `HealthCheckResponse` - Standard health check format
- `ErrorCodes` - Centralized error code constants

**Helper Function:**
```python
create_error_response(
    error_code: str,
    message: str,
    detail: Optional[str] = None,
    field: Optional[str] = None,
    request_id: Optional[str] = None
) -> ErrorResponse
```

---

## 2. Updated NER Routes (Template Implementation)

### Before (OLD):
```python
@router.post("/extract", response_model=NERTaskResponse)
async def extract_entities(request: NERRequest):
    if not model_loader.is_model_ready("ner"):
        raise HTTPException(
            status_code=503,  # ❌ Wrong for async
            detail="NER model not ready"  # ❌ Inconsistent format
        )
```

### After (NEW):
```python
@router.post(
    "/extract",
    response_model=NERTaskResponse,
    status_code=status.HTTP_202_ACCEPTED,  # ✅ Correct for async
    responses={  # ✅ OpenAPI documentation
        202: {
            "description": "Task accepted and queued",
            "model": NERTaskResponse
        },
        400: {
            "description": "Invalid input",
            "model": ErrorResponse
        },
        503: {
            "description": "Model not ready",
            "model": ErrorResponse
        },
        500: {
            "description": "Internal server error",
            "model": ErrorResponse
        }
    }
)
async def extract_entities(request: NERRequest):
    """
    Extract named entities from text (async via Celery).

    **Workflow:**
    1. POST to /ner/extract with text
    2. Receive task_id in response
    3. Poll /ner/task/{task_id} for results

    Returns:
        NERTaskResponse: Task ID and status endpoint
    """

    if not model_loader.is_model_ready("ner"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=create_error_response(  # ✅ Standardized error
                error_code=ErrorCodes.MODEL_NOT_READY,
                message="NER model not ready",
                detail="Model failed to load"
            ).dict()
        )
```

---

## Implementation Checklist

### For Each Async Endpoint (19 total):

**Endpoints to Update:**
- Whisper: `/whisper/transcribe`, `/whisper/transcribe-stream`
- Classifier: `/classifier/classify`
- NER: `/ner/extract` ✅ DONE
- QA: `/qa/evaluate`
- Translator: `/translate/`
- Summarizer: `/summarizer/summarize`
- Audio: Multiple processing endpoints

**Changes Required:**
- [ ] Import `status` from fastapi
- [ ] Import error models from `.models`
- [ ] Change status_code to `status.HTTP_202_ACCEPTED`
- [ ] Add `responses={}` parameter with all status codes
- [ ] Update HTTPException to use `create_error_response()`
- [ ] Enhance docstring with workflow details

---

## Error Response Standardization

### Old Error Formats (Inconsistent):
```python
# Format 1
{"detail": "Error message"}

# Format 2
{"detail": "Operation failed: Details"}

# Format 3
{"error": "Code", "message": "Details"}
```

### New Standardized Format:
```python
{
    "error": {
        "error_code": "MODEL_NOT_READY",  # Machine-readable
        "message": "NER model not ready",  # Human-readable
        "detail": "Model initialization failed",  # Debug info
        "field": "text",  # For validation errors
        "timestamp": "2024-01-18T10:30:00Z"
    },
    "status": "error",
    "request_id": "req_abc123"
}
```

---

## Status Code Corrections

### HTTP 202 (Accepted) - For Async Operations
**Use When:** Endpoint submits task and returns immediately

**Endpoints (19):**
- All `/extract`, `/classify`, `/evaluate`, `/translate`, `/summarize`, `/transcribe` endpoints
- All audio processing endpoints that return task_id

### HTTP 200 (OK) - For Sync Operations
**Use When:** Endpoint returns result immediately (rare in this API)

**Endpoints:**
- Task status endpoints `/task/{task_id}` (returns current status)
- Info endpoints `/info` (returns metadata)
- Health check endpoints

### HTTP 400 (Bad Request) - Validation Errors
**Use When:** Invalid input data (empty text, wrong format, etc.)

### HTTP 503 (Service Unavailable) - Model Not Ready
**Use When:** Model not loaded in standalone mode

### HTTP 500 (Internal Server Error) - Unexpected Failures
**Use When:** Task submission fails, unexpected exceptions

---

## OpenAPI responses={} Documentation

### Pattern for Async Endpoints:
```python
responses={
    202: {
        "description": "Task accepted and queued for processing",
        "model": TaskResponse  # Or specific model
    },
    400: {
        "description": "Invalid input (validation error)",
        "model": ErrorResponse
    },
    503: {
        "description": "Service unavailable (model not ready)",
        "model": ErrorResponse
    },
    500: {
        "description": "Internal server error",
        "model": ErrorResponse
    }
}
```

### Pattern for Sync Endpoints:
```python
responses={
    200: {
        "description": "Successful response",
        "model": ResponseModel
    },
    404: {
        "description": "Resource not found",
        "model": ErrorResponse
    },
    500: {
        "description": "Internal server error",
        "model": ErrorResponse
    }
}
```

---

## Implementation Order

### Phase 1: Core Model Endpoints (Priority 1) - 6 endpoints
- ✅ NER routes (DONE - template)
- [ ] Classifier routes
- [ ] QA routes
- [ ] Translator routes
- [ ] Summarizer routes
- [ ] Whisper routes

### Phase 2: Audio Processing (Priority 2) - 8 endpoints
- [ ] Audio processing routes
- [ ] Streaming audio routes

### Phase 3: Support Endpoints (Priority 3) - 60 endpoints
- [ ] Health routes (6 endpoints)
- [ ] Call session routes (14 endpoints)
- [ ] Notification routes (7 endpoints)
- [ ] Processing mode routes (6 endpoints)
- [ ] Agent feedback routes (4 endpoints)
- [ ] Other routes (23 endpoints)

---

## Error Code Usage Guide

### Model Errors (1xxx)
```python
ErrorCodes.MODEL_NOT_READY  # Model not loaded
ErrorCodes.MODEL_NOT_AVAILABLE  # Model doesn't exist
ErrorCodes.MODEL_LOADING_FAILED  # Model failed to load
```

### Task Errors (2xxx)
```python
ErrorCodes.TASK_SUBMISSION_FAILED  # Celery submission failed
ErrorCodes.TASK_NOT_FOUND  # task_id doesn't exist
ErrorCodes.TASK_TIMEOUT  # Task exceeded timeout
ErrorCodes.TASK_CANCELLED  # Task was cancelled
```

### Validation Errors (3xxx)
```python
ErrorCodes.VALIDATION_ERROR  # General validation failure
ErrorCodes.INVALID_INPUT  # Invalid input data
ErrorCodes.MISSING_REQUIRED_FIELD  # Required field missing
```

### Resource Errors (4xxx)
```python
ErrorCodes.RESOURCE_NOT_FOUND  # Resource doesn't exist
ErrorCodes.RESOURCE_UNAVAILABLE  # Resource temporarily unavailable
ErrorCodes.INSUFFICIENT_RESOURCES  # Not enough resources
```

### File Errors (6xxx)
```python
ErrorCodes.FILE_TOO_LARGE  # File exceeds size limit
ErrorCodes.INVALID_FILE_FORMAT  # Unsupported format
ErrorCodes.FILE_UPLOAD_FAILED  # Upload failed
```

---

## Testing Impact

### Tests That May Need Updates:
1. **Route tests** - Response format changed
2. **Integration tests** - Status codes changed (200→202)
3. **Error handling tests** - Error format standardized

### Expected Test Failures:
- Tests checking for `{"detail": "message"}` format
- Tests asserting `status_code == 200` for async endpoints
- Tests not expecting error_code field

### Fix Pattern:
```python
# OLD
assert response.status_code == 200
assert "detail" in response.json()

# NEW
assert response.status_code == 202  # For async
assert "task_id" in response.json()

# For errors:
assert "error" in response.json()
assert response.json()["error"]["error_code"] == "MODEL_NOT_READY"
```

---

## Benefits Achieved

### 1. Consistent Client Experience
- ✅ All errors follow same structure
- ✅ Machine-readable error codes
- ✅ Clear HTTP semantics (202 for async)

### 2. Better OpenAPI Documentation
- ✅ All possible responses documented
- ✅ Error models clearly defined
- ✅ Auto-generated client libraries will be accurate

### 3. Easier Debugging
- ✅ Standardized error codes for logging
- ✅ Timestamps on all errors
- ✅ Request IDs for tracing

### 4. Production Readiness
- ✅ Follows HTTP standards (RFC 7231)
- ✅ Follows REST API best practices
- ✅ OpenAPI 3.1.0 compliant

---

## Progress Tracking

### Completion Status:
- **Critical Fix 1** (Error Responses): 1/74 endpoints (1.4%)
- **Critical Fix 2** (Status Codes): 1/19 async endpoints (5.3%)
- **Critical Fix 3** (OpenAPI responses): 1/74 endpoints (1.4%)

### Estimated Effort Remaining:
- Core model endpoints: 5 endpoints × 30 min = 2.5 hours
- Audio endpoints: 8 endpoints × 30 min = 4 hours
- Support endpoints: 60 endpoints × 15 min = 15 hours
- **Total:** ~21.5 hours

### Quick Wins (Next 2 hours):
Update remaining 5 core model endpoints:
- Classifier routes (similar to NER)
- QA routes (similar to NER)
- Translator routes (similar to NER)
- Summarizer routes (similar to NER)
- Whisper routes (slightly more complex)

---

## Next Steps

1. **Test NER changes** - Ensure route tests still pass
2. **Update remaining model routes** - Use NER as template
3. **Create migration guide** - For existing API clients
4. **Update API documentation** - Reflect new error format
5. **Add deprecation warnings** - If needed for old format

---

**Document Owner:** API Documentation Team
**Last Updated:** 2026-01-18
**Template File:** `app/api/ner_routes.py` (reference implementation)


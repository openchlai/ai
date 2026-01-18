# API Documentation Improvement Plan
## Implementation Roadmap for Opensourcing Readiness

**Created:** 2026-01-18
**Based on:** Comprehensive OpenAPI Audit Report
**Target:** 95% OpenAPI compliance for open-source release
**Timeline:** 4-5 weeks (155-200 hours)

---

## CRITICAL ISSUES TO FIX (Weeks 1-2, 40 hours)

### Fix 1: Standardize Error Responses
**Impact:** HIGH - Blocks client library generation
**Effort:** 4 hours
**Files:** All 74 endpoints

**Current State:**
```python
# Multiple inconsistent formats
{"detail": "Error message"}
{"detail": "Operation failed: Exception details"}
{"error": "code", "message": "details"}
```

**Required:**
Create standard `ErrorResponse` model:
```python
class ErrorResponse(BaseModel):
    error_code: str  # e.g., "INVALID_AUDIO_FORMAT"
    message: str  # User-friendly
    detail: Optional[str]  # Technical details
    timestamp: datetime
    request_id: Optional[str]
    documentation_url: Optional[str]

class ValidationErrorResponse(ErrorResponse):
    validation_errors: List[FieldError]
```

**Implementation:**
1. Create `app/schemas/error_responses.py`
2. Import in all route files
3. Update all HTTPException raises to use standard format
4. Add to FastAPI `responses={}` for all endpoints

**Files to Update:**
- `app/api/health_routes.py`
- `app/api/whisper_routes.py`
- `app/api/summarizer_routes.py`
- `app/api/translator_routes.py`
- `app/api/ner_routes.py`
- `app/api/classifier_routes.py`
- `app/api/qa_routes.py`
- `app/api/audio_routes.py`
- `app/api/call_session_routes.py`
- And 3 more route files

---

### Fix 2: Change Async Endpoints from 200 → 202 Status
**Impact:** CRITICAL - Violates HTTP semantics
**Effort:** 3 hours
**Files:** 19 async endpoints

**Current State:**
All async POST endpoints return HTTP 200 but should return 202 (Accepted)

**Required Changes:**

```python
# BEFORE
@router.post("/transcribe", response_model=WhisperTaskResponse)
async def transcribe_audio(...):
    task = whisper_transcribe_task.apply_async(...)
    return WhisperTaskResponse(task_id=task.id, ...)  # Returns 200!

# AFTER
@router.post(
    "/transcribe",
    response_model=WhisperTaskResponse,
    status_code=status.HTTP_202_ACCEPTED
)
async def transcribe_audio(...):
    task = whisper_transcribe_task.apply_async(...)
    return WhisperTaskResponse(task_id=task.id, ...)  # Returns 202!
```

**Affected Endpoints:**
1. Whisper: POST /transcribe
2. Classifier: POST /classify
3. NER: POST /extract
4. QA: POST /evaluate
5. Translator: POST /
6. Summarizer: POST /summarize
7. Audio: POST /process, POST /analyze, POST /process-stream, POST /process-stream-realtime
8. All 4 demo endpoints

**Files to Update:** 7 route files

---

### Fix 3: Add Explicit `responses={}` to All Endpoints
**Impact:** HIGH - Required for OpenAPI validation
**Effort:** 6 hours
**Files:** All 74 endpoints

**Current State:**
Most endpoints missing explicit response documentation

**Required Pattern:**
```python
@router.get(
    "/info",
    response_model=WhisperInfoResponse,
    responses={
        200: {
            "description": "Model information retrieved successfully",
            "model": WhisperInfoResponse
        },
        500: {
            "description": "Server error retrieving model info",
            "model": ErrorResponse
        },
        503: {
            "description": "Model not available or service unavailable",
            "model": ErrorResponse
        }
    }
)
async def get_whisper_info() -> WhisperInfoResponse:
    """Get Whisper model information"""
    ...
```

**Steps:**
1. Identify all unique response codes per endpoint
2. Document error scenarios
3. Add responses parameter to all 74 endpoints
4. Document each response in OpenAPI

**Common Status Codes to Document:**
- 200: Success
- 202: Accepted (async tasks)
- 400: Bad Request
- 404: Not Found
- 413: Payload Too Large
- 422: Validation Error
- 429: Rate Limited
- 500: Internal Server Error
- 503: Service Unavailable

---

### Fix 4: Document Task Status Polling Contract
**Impact:** CRITICAL - Async pattern undefined
**Effort:** 4 hours
**Files:** 7 status endpoint files

**Current Problem:**
```python
@router.get("/task/{task_id}", response_model=WhisperTaskStatusResponse)
async def get_whisper_task_status(task_id: str):
    """Get whisper transcription task status"""
    # Missing: What happens if task_id doesn't exist?
    # Missing: How long are results retained?
    # Missing: Can I poll indefinitely?
    # Missing: Recommended polling interval?
```

**Required Documentation:**
```python
@router.get(
    "/task/{task_id}",
    response_model=WhisperTaskStatusResponse,
    responses={
        200: {
            "description": "Task status retrieved",
            "content": {
                "application/json": {
                    "schema": WhisperTaskStatusResponse,
                    "examples": {
                        "pending": {
                            "value": {
                                "task_id": "abc-123",
                                "status": "PENDING",
                                "progress": {"message": "Queued"}
                            }
                        },
                        "processing": {
                            "value": {
                                "task_id": "abc-123",
                                "status": "PROCESSING",
                                "progress": {"step": "transcribing", "percent": 45}
                            }
                        },
                        "success": {
                            "value": {
                                "task_id": "abc-123",
                                "status": "SUCCESS",
                                "result": {...}
                            }
                        }
                    }
                }
            }
        },
        404: {
            "description": "Task ID not found or expired (results retained 24 hours)",
            "model": ErrorResponse
        },
        500: {
            "description": "Error retrieving task status",
            "model": ErrorResponse
        }
    }
)
async def get_whisper_task_status(
    task_id: str = Path(..., description="Task ID returned from submission endpoint")
) -> WhisperTaskStatusResponse:
    """
    Get status of a whisper transcription task.

    **Task Lifecycle:**
    1. PENDING - Task queued, waiting for worker
    2. PROCESSING - Task executing, check progress field
    3. SUCCESS - Completed, result available
    4. FAILURE - Error occurred, check error field
    5. RETRY - Retrying due to failure

    **Polling Guidelines:**
    - Recommended interval: 5-10 seconds
    - Maximum result retention: 24 hours
    - After 24 hours: 404 Not Found (result expired)

    **Example Polling Loop:**
    ```bash
    TASK_ID="abc-123def-456"
    while true; do
        curl -s http://localhost:8125/whisper/task/$TASK_ID
        # Check status field
        # If status == "SUCCESS": result ready, break
        # If status == "FAILURE": error occurred, break
        # Else: sleep 5 and retry
        sleep 5
    done
    ```
    """
    ...
```

**All 7 Task Status Endpoints Need:**
- Explicit status code documentation
- Status value enumeration (PENDING, PROCESSING, SUCCESS, FAILURE, RETRY)
- Result retention policy (24-hour TTL)
- Example polling loop in docstring
- Progress field documentation
- Error field documentation

---

### Fix 5: Define Authentication/Authorization Model
**Impact:** CRITICAL - Security model undefined
**Effort:** 12 hours
**Decision Point:** Choose auth strategy first

**Current State:**
- Zero authentication
- CORS allows all origins
- Anyone can DELETE any task
- `/health/detailed` exposes system info
- No rate limiting
- No per-user quotas

**Options to Evaluate:**
1. **API Key (Simplest)**
   - Header: `X-API-Key: your-key`
   - Storage: In-memory or database
   - Scope: Per-key rate limiting
   - Complexity: 4 hours

2. **Bearer Token (OAuth2/JWT)**
   - Header: `Authorization: Bearer <token>`
   - JWTs signed by server
   - Scope: Per-user rate limiting, role-based access
   - Complexity: 8 hours

3. **None / Documentation Only (Easiest)**
   - Document that API is unauthenticated
   - Warn about production security risks
   - Document rate limiting policies
   - Complexity: 2 hours

**Recommended:** API Key for open-source (simplest, still secure)

**Implementation:**
1. Choose authentication strategy
2. Implement FastAPI security scheme
3. Create `SecuritySchemes` in OpenAPI
4. Document in all endpoint docstrings
5. Add examples in OpenAPI

---

### Fix 6: Add 95% Missing Example Values
**Impact:** HIGH - Developer experience
**Effort:** 11 hours
**Files:** All 74 endpoints (72 need examples)

**Current State:**
Only 2 endpoints have examples → 97% missing

**Required:**
Every request/response model needs `example=` field

```python
# BEFORE
class NERResponse(BaseModel):
    entities: List[NEREntity]
    processing_time: float
    timestamp: str

# AFTER
class NERResponse(BaseModel):
    entities: List[NEREntity] = Field(
        ...,
        example=[
            {
                "text": "Nairobi",
                "label": "LOCATION",
                "start": 50,
                "end": 56,
                "confidence": 0.98
            }
        ],
        description="Extracted named entities with positions and confidence scores"
    )
    processing_time: float = Field(
        ...,
        example=5.2,
        description="Processing time in seconds"
    )
    timestamp: str = Field(
        ...,
        example="2025-01-18T10:30:45.123456+00:00",
        description="ISO 8601 UTC timestamp"
    )
```

**Endpoints Prioritize:**
1. Model inference endpoints (5 models × 4 endpoints = 20)
2. Audio processing endpoints (8)
3. Health/Status endpoints (6)
4. Call session endpoints (14)
5. Others (20)

---

## HIGH PRIORITY ISSUES (Weeks 3-4, 60 hours)

### Fix 7: Complete Parameter Documentation
**Files:** 48 endpoints missing parameter docs
**Effort:** 20 hours

Add to every parameter:
- `description` - What it does
- `example` - Valid value
- Validation constraints (min, max, regex, enum)
- Unit specifications (seconds, MB, etc.)

```python
# BEFORE
@router.post("/process")
async def process_audio(
    audio: UploadFile = File(...),
    language: Optional[str] = Form(None),
    include_translation: bool = Form(True),
    include_insights: bool = Form(True)
):
    """Process audio"""

# AFTER
@router.post("/process")
async def process_audio(
    audio: UploadFile = File(
        ...,
        description="Audio file in WAV, MP3, FLAC, M4A, OGG, or WebM format",
        media_type="audio/*"
    ),
    language: Optional[str] = Form(
        None,
        description="Language code for transcription. Use 'en' (English), 'sw' (Swahili), 'fr' (French), or 'auto' for auto-detection. Defaults to Swahili if not specified.",
        example="sw",
        regex="^(en|sw|fr|es|ar|auto)$"
    ),
    include_translation: bool = Form(
        True,
        description="Include English translation of transcript (adds ~15 seconds processing)"
    ),
    include_insights: bool = Form(
        True,
        description="Include NER, classification, and QA analysis (adds ~20 seconds processing)"
    )
):
    """
    Process audio file through complete AI pipeline...
    """
```

### Fix 8: Comprehensive Endpoint Descriptions
**Files:** 35 endpoints with insufficient descriptions
**Effort:** 15 hours

Expand docstrings to include:
- What the endpoint does
- When to use it
- Expected inputs
- Expected outputs
- Error conditions
- Performance characteristics
- Related endpoints

Example pattern:
```python
@router.post("/process")
async def process_audio(...):
    """
    Complete end-to-end audio-to-insights pipeline.

    This endpoint processes audio files through multiple AI models:
    1. Transcription (Whisper) - Converts audio to text
    2. Translation (optional) - Translates to English
    3. NER - Extracts named entities (people, locations, etc.)
    4. Classification - Determines case category and priority
    5. Summarization - Generates summary of content
    6. QA Scoring - Evaluates quality assurance metrics
    7. Insights - Generates risk assessment and analysis

    **When to Use:**
    - Processing complete audio calls for comprehensive analysis
    - Need all insights in one request
    - Batch processing with background jobs

    **Performance:**
    - Typical processing time: 30-120 seconds (depends on audio length)
    - Maximum file size: 100MB
    - Supported formats: WAV, MP3, FLAC, M4A, OGG, WebM

    **Error Scenarios:**
    - 400: Invalid audio format or missing file
    - 413: File larger than 100MB
    - 429: Rate limit exceeded
    - 503: Models not loaded or workers offline

    **Related Endpoints:**
    - GET /audio/task/{task_id} - Check progress
    - DELETE /audio/task/{task_id} - Cancel processing
    - POST /audio/analyze - Quick analysis (faster, fewer insights)
    """
    ...
```

### Fix 9: Response Field Documentation
**Files:** All models (100+ fields)
**Effort:** 15 hours

Add Field descriptions to every response model field:
```python
class ClassificationResponse(BaseModel):
    main_category: str = Field(
        ...,
        description="Primary case category (e.g., 'abuse', 'neglect', 'exploitation')",
        example="abuse"
    )
    sub_category: str = Field(
        ...,
        description="Secondary category within main category",
        example="physical_abuse"
    )
    confidence_scores: ConfidenceScores = Field(
        ...,
        description="Confidence scores (0-1) for each classification decision",
        example={
            "main_category": 0.92,
            "sub_category": 0.87,
            "intervention": 0.95
        }
    )
```

### Fix 10: Rate Limiting Implementation
**Effort:** 10 hours
**Required:** Implement + document

Steps:
1. Choose rate limit strategy (per-IP, per-key, per-endpoint)
2. Implement middleware
3. Return rate limit headers
4. Document limits per endpoint
5. Document in OpenAPI

Example header documentation:
```python
responses={
    429: {
        "description": "Rate limit exceeded. Check rate limit headers.",
        "headers": {
            "X-RateLimit-Limit": {
                "schema": {"type": "integer"},
                "description": "Maximum requests per minute (100)"
            },
            "X-RateLimit-Remaining": {
                "schema": {"type": "integer"},
                "description": "Remaining requests in current window"
            },
            "X-RateLimit-Reset": {
                "schema": {"type": "integer"},
                "description": "Unix timestamp when limit resets"
            }
        }
    }
}
```

---

## MEDIUM PRIORITY (Weeks 5-6, 35 hours)

### Fix 11: Standardize Health Endpoints
**Issue:** 6 endpoints, 6 different response structures
**Effort:** 8 hours

Create unified health response model:
```python
class HealthResponse(BaseModel):
    status: str  # "healthy", "degraded", "unhealthy"
    timestamp: datetime
    version: str
    checks: Dict[str, Dict[str, Any]]  # Unified structure for all health checks
```

### Fix 12: Mode-Dependent Response Documentation
**Issue:** Same endpoint returns different schemas based on execution mode
**Effort:** 10 hours

Solutions:
1. Use discriminator models (Pydantic discriminator)
2. Separate endpoints for each mode
3. Full documentation of mode-dependency

Example:
```python
@router.get("/info", discriminator='mode')
async def get_whisper_info():
    """
    Get Whisper model information.

    **Response varies by execution mode:**

    - **API Server Mode:** Returns worker configuration info
      ```json
      {
        "status": "api_server_mode",
        "message": "Whisper model loaded on Celery workers",
        "mode": "api_server"
      }
      ```

    - **Standalone Mode:** Returns local model information
      ```json
      {
        "status": "ready",
        "model_info": {
          "model": "openai/whisper-small",
          "version": "v20231106"
        }
      }
      ```
    """
```

### Fix 13: Fix Deprecation Documentation
**Effort:** 5 hours
**Required:** Mark demo endpoints and establish deprecation policy

```python
@router.post("/demo", deprecated=True)
async def whisper_demo():
    """
    DEMO ENDPOINT - For testing only.

    This endpoint uses hardcoded sample data and is not suitable for production.
    It will be removed in v2.0 (2025-Q3).

    For production use, see:
    - POST /whisper/transcribe - Real transcription
    - GET /whisper/info - Model information
    """
```

### Fix 14: Document Async/Polling Pattern
**Effort:** 8 hours

Add comprehensive polling documentation:
```python
# Create guides for:
# 1. How to submit tasks
# 2. How to poll for results
# 3. How to cancel tasks
# 4. Error handling during polling
# 5. Timeout and retry strategies
# 6. WebSocket alternative (if available)
```

### Fix 15: License and Version Info
**Effort:** 4 hours

Update FastAPI configuration:
```python
app = FastAPI(
    title="AI Pipeline",
    description="...",
    version="0.1.0",
    license_info={
        "name": "Apache License 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html"
    },
    contact={
        "name": "OpenCHLAI",
        "url": "https://github.com/openchlai/ai",
        "email": "support@openchlai.org"
    },
    servers=[
        {
            "url": "https://api.production.example.com",
            "description": "Production environment"
        },
        {
            "url": "https://api.staging.example.com",
            "description": "Staging for testing"
        },
        {
            "url": "http://localhost:8125",
            "description": "Local development"
        }
    ]
)
```

---

## IMPLEMENTATION ORDER

### Week 1: Foundations
1. **Day 1:** Create ErrorResponse model + implement (6 hours)
2. **Day 1-2:** Change async endpoints to 202 (3 hours)
3. **Day 2-3:** Add responses parameter to all endpoints (6 hours)
4. **Day 3:** Document task polling contract (4 hours)
5. **Day 4:** Plan and choose auth strategy (2 hours)
6. **Day 5:** Implement basic auth (4 hours + tests)

### Week 2: Examples and Docs
1. **Day 6-7:** Add example values (11 hours)
2. **Day 8:** Parameter documentation (5 hours)
3. **Day 9:** Endpoint description improvements (8 hours)
4. **Day 10:** Response field documentation (8 hours)

### Week 3: High Priority Completion
1. **Day 11:** Rate limiting implementation (10 hours)
2. **Day 12:** Remaining examples (6 hours)
3. **Day 13:** Parameter docs completion (5 hours)
4. **Day 14:** Endpoint descriptions completion (7 hours)
5. **Day 15:** Response field docs completion (4 hours)

### Week 4-5: Polish and Testing
1. **Day 16-17:** Health endpoint standardization (8 hours)
2. **Day 18:** Mode-dependent response documentation (5 hours)
3. **Day 19:** Deprecation paths (5 hours)
4. **Day 20:** License/version/servers info (4 hours)
5. **Days 21-25:** Review, testing, final adjustments (20 hours)

---

## VALIDATION CHECKLIST

Before declaring "OpenAPI Compliant," verify:

- [ ] All 74 endpoints have explicit `response_model`
- [ ] All 74 endpoints have explicit `responses={}` parameter
- [ ] Every HTTP status code documented and correct
- [ ] No endpoint returns 200 for async (should be 202)
- [ ] All error responses use standard ErrorResponse schema
- [ ] All 74 endpoints have comprehensive docstrings
- [ ] Every parameter has description + example
- [ ] Every response field has description + example
- [ ] Authentication method defined and documented
- [ ] Rate limiting implemented and documented
- [ ] All task status endpoints document polling behavior
- [ ] All demo endpoints marked with `deprecated=True`
- [ ] License, contact, servers defined in FastAPI config
- [ ] Health endpoints use consistent response model
- [ ] Mode-dependent responses documented with examples
- [ ] API versioning strategy defined
- [ ] Deprecation policy defined
- [ ] OpenAPI JSON validates against OpenAPI 3.1.0 spec
- [ ] Auto-generated client libraries work correctly
- [ ] README includes API documentation links

---

## SUCCESS METRICS

| Metric | Current | Target | Pass? |
|--------|---------|--------|-------|
| % Endpoints with response_model | 58% | 100% | |
| % Endpoints with responses= | 5% | 100% | |
| % Endpoints with examples | 3% | 100% | |
| % Parameters documented | 35% | 95% | |
| Async endpoints using 202 | 0% | 100% | |
| OpenAPI Schema validation | FAIL | PASS | |
| Client library generation | FAIL | PASS | |
| OpenAPI score | 1.8/5 | 8.5/5 | |

---

## RISKS AND MITIGATION

| Risk | Mitigation |
|------|-----------|
| Changes break existing clients | Maintain backward compatibility, version endpoints |
| Status code changes cause issues | Provide migration guide for 200→202 |
| Auth implementation delays | Implement API key version first, upgrade later |
| Time overruns on examples | Use code generation tools, templates |
| Rate limiting breaks users | Implement with generous limits, document clearly |
| Schema validation failures | Test with openapi-cli validator |

---

## PARALLEL WORK TRACKING

**API Documentation:** This plan (155-200 hours)
**Test Coverage:** Phase 1-3 concurrent (see TEST_COVERAGE_IMPROVEMENT_PLAN.md)

**Coordination Points:**
1. Both complete by Day 30
2. Weekly progress reviews
3. Shared documentation updates
4. Combined final validation

---

**Plan Status:** READY FOR IMPLEMENTATION
**Start Date:** 2026-01-18
**Target Completion:** 2026-02-28


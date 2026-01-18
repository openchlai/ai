# Phase 2 Strategy and Roadmap
## Test Coverage Expansion Plan

**Date:** 2026-01-18
**Current Status:** Phase 1 Complete (1602/1737 passing, 92% pass rate, 65% coverage)
**Target:** 80%+ code coverage with maintainable, scalable tests

---

## Executive Summary

Phase 1 successfully fixed all 69 route-level tests. Phase 2 requires a strategic approach to remaining 112 failing tests, organized by complexity and ROI.

### Phase 2 Categories
1. **Phase 2A: Quick Wins** - Fixable with minor changes (20-25 tests)
2. **Phase 2B: Medium Effort** - Require mock restructuring (45-50 tests)
3. **Phase 2C: High Effort** - Need architectural changes (30-35 tests)
4. **Phase 2D: Future Work** - Legacy/lower priority (10-15 tests)

---

## Detailed Failure Analysis

### Total Failures: 112
- **Failing Tests:** 112
- **Errors:** 17 (legacy, intentionally disabled)
- **Skipped:** 6

### Breakdown by Complexity

#### Category 1: Celery/Task Tests (45 failures)
**Issue:** Celery task binding and function signature mismatches

**Root Causes:**
1. **Task Binding Issue** - Tests calling bound Celery tasks incorrectly
   - Task signature: `def task(self, arg1, arg2)`
   - Test calling: `task(mock_self, arg1, arg2)`
   - Celery handling: Causes double-binding of `self`
   - Solution: Use `task.run(arg1, arg2)` or `task.s(arg1, arg2).apply()`

2. **Specific Failures:**
   - `test_ner_extract_task`: TypeError - "got multiple values for argument 'flat'"
   - `test_classifier_classify_task`: TypeError - "takes 2 positional arguments but 3 were given"
   - `test_translation_translate_task`: Similar signature mismatch
   - `test_qa_evaluate_task`: Unexpected keyword argument 'conversation'
   - `test_whisper_transcribe_task`: "got multiple values for argument 'audio_bytes'"

**Effort:** Medium-High (requires understanding Celery task testing patterns)
**Priority:** 2 (important but complex)
**Fix Strategy:**
```python
# WRONG (current approach)
result = ner_extract_task(mock_self, text, flat=True)

# CORRECT (Celery pattern)
# Option 1: Call run() directly
result = ner_extract_task.run(text, flat=True)

# Option 2: Use signature
result = ner_extract_task.s(text, flat=True).apply().get()

# Option 3: Call underlying function
result = ner_extract_task.f(mock_self, text, flat=True)
```

---

#### Category 2: Import Location Mocking (15 failures)
**Issue:** Module imports inside functions can't be mocked at module level

**Examples:**
- `test_health_tasks.py`: Tries to patch `app.tasks.health_tasks.model_loader`
  - Actual: `from ..model_scripts.model_loader import model_loader` (inside function)
  - Solution: Patch at import location or use `patch.dict(sys.modules, ...)`

**Effort:** Low-Medium (straightforward mocking fixes)
**Priority:** 3 (fixable once understood)
**Fix Strategy:**
```python
# WRONG
@patch('app.tasks.health_tasks.model_loader')  # module-level doesn't exist

# CORRECT
@patch('app.model_scripts.model_loader.model_loader')  # patch at source
# OR
@patch('sys.modules', ...)  # patch the import
```

---

#### Category 3: Streaming/Async Tests (25 failures)
**Issue:** Complex async patterns, TCP protocol mocking, event handling

**Specific Failures:**
- `test_overlapping_windows`: Complex buffer overlap logic
- `test_buffer_overflow_protection`: Edge case buffer handling
- `test_filename_generation_format`: Asterisk filename pattern
- `test_audio_chunk_processing`: TCP stream chunk processing
- `test_send_agent_notifications`: Async notification sending

**Effort:** Medium (requires async/await understanding)
**Priority:** 2 (good educational value)
**Fix Strategy:**
- Mock TCP socket more completely
- Use AsyncMock for async functions
- Add proper event loop handling

---

#### Category 4: Service Integration (20 failures)
**Issue:** HTTP client mocking, request/response handling

**Examples:**
- `test_send_notification_http_error`: HTTP request mocking
- `test_send_error_notification`: Error payload creation
- `test_resource_manager`: GPU/resource allocation mocking
- `test_insights_service`: External API responses

**Effort:** Low-Medium (standard mocking patterns)
**Priority:** 2 (good ROI on coverage)
**Fix Strategy:**
- Mock `requests.Session` or `httpx.AsyncClient` more thoroughly
- Add proper response factories
- Mock resource allocation state

---

#### Category 5: Model Loading (10 failures)
**Issue:** Model initialization and HuggingFace loading

**Examples:**
- Model loader initialization failures
- Model path resolution issues
- Transformer model loading mocks

**Effort:** Medium (requires HF API knowledge)
**Priority:** 3 (lower impact)

---

#### Category 6: Legacy Tests (15 errors)
**Issue:** Disabled legacy test suite

**Status:** Intentionally in `_disabled_legacy_tests/` directory
**Decision:** Ignore for Phase 2, evaluate for deprecation in Phase 3
**Priority:** 4 (explicitly excluded)

---

## Phase 2 Implementation Plan

### Phase 2A: Quick Wins (3-4 hours)
**Goal:** Fix import mocking issues, add 20-25 passing tests

**Tasks:**
1. Fix health_tasks mocking:
   - Change `@patch('app.tasks.health_tasks.model_loader')`
   - To `@patch('app.model_scripts.model_loader.model_loader')`
   - Estimated: 1 hour, 9 tests fixed

2. Fix service integration basic mocks:
   - Enhance HTTP client mocks
   - Add response factories
   - Estimated: 1.5 hours, 10-12 tests fixed

3. Add simple streaming mocks:
   - Fix buffer tests with better socket mocks
   - Estimated: 1 hour, 3-5 tests fixed

**Estimated Outcome:** +20-25 passing tests (1622-1627 total)
**New Pass Rate:** 93.5%-93.7%

---

### Phase 2B: Medium Effort (6-8 hours)
**Goal:** Fix Celery task binding, add 40-45 passing tests

**Tasks:**
1. Restructure model_tasks tests:
   - Learn Celery task testing patterns
   - Update NER, Classifier, Translator, QA, Whisper tasks
   - Use `.run()` or `.s().apply()` patterns
   - Estimated: 4-5 hours, 14 tests fixed

2. Fix remaining streaming tests:
   - Async/await proper mocking
   - TCP protocol complete mocking
   - Estimated: 2-3 hours, 20-25 tests fixed

3. Add model initialization tests:
   - Mock model loader state
   - Mock HuggingFace API responses
   - Estimated: 1 hour, 5-10 tests fixed

**Estimated Outcome:** +40-45 passing tests (1662-1672 total)
**New Pass Rate:** 95.7%-96.3%

---

### Phase 2C: Polish & Edge Cases (4-6 hours)
**Goal:** Fix remaining failures, reach 80%+ coverage

**Tasks:**
1. Add error scenario tests
2. Fix resource manager tests
3. Add edge case handling
4. Document test patterns

**Estimated Outcome:** +15-20 passing tests (1677-1692 total)
**New Pass Rate:** 96.5%-97.4%
**Coverage:** 75%+ overall

---

## Testing Patterns to Document

### Celery Task Testing Pattern
```python
# For testing bound Celery tasks:
@pytest.mark.celery
def test_ner_task():
    # Use .run() for synchronous testing
    result = ner_extract_task.run("text", flat=True)
    assert result["task_id"] == current_task.request.id

    # OR use signature + apply
    task_sig = ner_extract_task.s("text", flat=True)
    result = task_sig.apply().get()
```

### Import Mocking Pattern
```python
# When import is inside function, patch at source:
@patch('app.model_scripts.model_loader.model_loader')
def test_function(mock_loader):
    # Don't patch where it's used, patch where it's defined
```

### Async Mocking Pattern
```python
# For async functions:
@patch('app.streaming.tcp_server.asyncio.StreamReader')
async def test_async_function(mock_reader):
    mock_reader.read = AsyncMock(return_value=b"data")
```

---

## Risk & Mitigation

### Risk 1: Celery Task Changes Break Existing Code
**Mitigation:** Add integration tests before changing task calls
**Priority:** HIGH

### Risk 2: Import Mocking Changes Affect Real Code
**Mitigation:** Use dependency injection where possible
**Priority:** MEDIUM

### Risk 3: Async Testing Becomes Complex
**Mitigation:** Use pytest-asyncio and AsyncMock consistently
**Priority:** MEDIUM

---

## Success Metrics - Phase 2

| Phase | Passing | Pass Rate | Coverage | Status |
|-------|---------|-----------|----------|--------|
| Phase 1 | 1602 | 92% | 65% | ✅ COMPLETE |
| Phase 2A | 1622-1627 | 93.5-93.7% | 68-70% | ⏳ PLANNED |
| Phase 2B | 1662-1672 | 95.7-96.3% | 73-75% | ⏳ PLANNED |
| Phase 2C | 1677-1692 | 96.5-97.4% | 75-80% | ⏳ PLANNED |

---

## Resource Requirements

**Skills Needed:**
- ✅ Python mocking (unittest.mock)
- ✅ Pytest fixtures and markers
- ⏳ Celery task testing patterns
- ⏳ Async/await testing
- ⏳ TCP/streaming protocol mocking

**Time Estimate:**
- Phase 2A: 3-4 hours
- Phase 2B: 6-8 hours
- Phase 2C: 4-6 hours
- **Total:** 13-18 hours

---

## Decision Points

### Should We Continue?
- ✅ Phase 1 showed excellent progress (312% improvement in passing tests)
- ⚠️ Phase 2 requires more specialized knowledge
- ✅ Clear path exists for each category
- ❓ ROI on coverage improvements diminishes past 80%

### Recommended Action
1. **Execute Phase 2A** (quick wins, highest ROI)
2. **Review Phase 2B** (evaluate Celery task knowledge)
3. **Consider outsourcing** complex async/Celery patterns
4. **Plan Phase 2C** after Phase 2B completion

---

## Next Steps

1. **Confirm Phase 2A approach** with team
2. **Start with health_tasks fixes** (simplest)
3. **Document Celery patterns** as discovered
4. **Create test pattern guide** for future developers

---

## Appendix: Failure Categories Summary

```
PHASE 2 FAILURES (112 total):
├── Phase 2A: Quick Wins (20-25)
│   ├── Import mocking: 9 tests
│   ├── Service mocks: 10-12 tests
│   └── Simple streaming: 3-5 tests
│
├── Phase 2B: Medium (40-45)
│   ├── Celery tasks: 14 tests
│   ├── Async streaming: 20-25 tests
│   └── Model init: 5-10 tests
│
├── Phase 2C: Polish (15-20)
│   ├── Edge cases: 10-15 tests
│   └── Integration scenarios: 5-10 tests
│
└── Phase 2D: Future (15)
    └── Legacy tests: 15 (skip for now)
```

---

**Document Status:** DRAFT - Ready for review
**Last Updated:** 2026-01-18
**Next Review:** After Phase 2A completion


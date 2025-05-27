# 📘 Testing Strategy

## 1. Overview

This document describes the testing frameworks, directory structure, and workflow used across:

- Frontend (Vue 3, Vanilla JS)
- Backend (PHP)
- AI Components (Python)

## 2. Frameworks Used

| Component   | Stack        | Testing Tools              |
|-------------|--------------|---------------------------|
| Frontend    | Vue 3        | `vitest`, `vue/test-utils` |
| JS Scripts  | Vanilla JS   | `mocha`, `chai`           |
| Backend     | PHP          | `PHPUnit`                 |
| AI Services | Python       | `pytest`, `unittest`      |

## 3. Directory Structure

```bash
frontend/tests/       # Vitest tests for Vue components
backend/tests/        # PHPUnit tests for backend
ai_service/tests/     # Pytest unit tests for AI pipeline
docs/stakeholders/    # User stories & manual test cases
```

## 4. CI & Automation

GitHub Actions automate:

- Test runs
- Linting checks
- Reporting

## 5. Contributing to Tests

- Add tests for any new component or service.
- Ensure all tests pass before submitting a PR.
- Run `npm run test` or `pytest` locally before pushing.

---

### ✅ 3. New File: `docs/stakeholders/user_stories/sample_case_dashboard.md`

```markdown
# 🎮 User Story: Case Manager Dashboard

## Summary

**As a** case worker  
**I want** a dashboard that shows my caseload interactively  
**So that** I can prioritize my tasks effectively

## Acceptance Criteria

- Dashboard loads the current day's tickets
- Tickets are visually marked by priority
- Clicking a ticket shows full details
- Game mode displays XP/levels for completed cases

## Related Test Cases

- `dashboard_loads.spec.js`
- `priority_coloring.spec.js`
- `game_mode_toggle.spec.js`
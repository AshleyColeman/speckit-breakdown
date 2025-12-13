# 🧪 SpecKit Breakdown – Testing Strategy & Game Plan

> **Goal**: Achieve 100% confidence in the system through a robust, multi-layer testing strategy.
> **Philosophy**: "Test behavior, not implementation details."

---

## 1. Technology Stack

### Python (Core Logic)
- **Runner**: `pytest` (Industry standard, rich plugin ecosystem)
- **Coverage**: `pytest-cov` (Track code coverage to ensure no blind spots)
- **Async**: `pytest-asyncio` (For testing async DB and IO operations)
- **Mocking**: `pytest-mock` (Standard `unittest.mock` wrapper)

### Bash (Installers & Scripts)
- **Framework**: `bats-core` (Bash Automated Testing System)
- **Why**: It allows us to test `install.sh` and the generated `quick-start.sh` scripts in a real shell environment.

---

## 2. Testing Pyramid

### Level 1: Unit Tests (Python)
**Scope**: Individual functions/classes in `src/`.  
**Goal**: Verify logic in isolation (parsing, validation, data transformation).  
**Target Coverage**: >90%

**New Areas to Cover**:
- `rollback_manager.py`: Mock failure scenarios to ensure rollback triggers.
- `metrics.py`: Verify metrics collection doesn't crash the app.
- `ai_job_service.py`: Verify state transitions of AI jobs.

**Command**:
```bash
pytest tests/unit --cov=src
```

### Level 2: Service Integration Tests (Python)
**Scope**: Interaction between services (orchestrator -> gateway -> db).  
**Goal**: Verify the "Happy Path" and "Known Error Paths" using a real (or in-memory) database.  
**Target Coverage**: Critical user flows.

**Existing**: `test_db_prepare_*.py` (Already strong).  
**New**:
- Test the full lifecycle of a Breakdown (Project -> Features -> Tasks).
- Simulate network failures during "Context Packing".

**Command**:
```bash
pytest tests/integration
```

### Level 3: Script & CLI Tests (Bash/Bats)
**Scope**: `install.sh`, `scripts/*.sh`, and the *output* of the breakdown tool.  
**Goal**: Ensure the "Developer Experience" works on a fresh machine.

**Scenarios to Test**:
1.  **Installation**: run `install.sh` in a docker container. Verify files exist.
2.  **Idempotency**: run `install.sh` twice. Should not fail.
3.  **Generated Scripts**: Run `/speckit.breakdown`, then EXECUTE the generated `quick-start.sh`. It should run without syntax errors.

**Command**:
```bash
bats tests/bash
```

---

## 3. The Game Plan

### Phase 1: Solidify Python Foundation (Immediate)
1.  **Add `pytest-cov`**: measure current baseline.
2.  **Fill Gaps**: Add unit tests for `rollback_manager` and `task_run_service` if missing.
3.  **Refactor**: Ensure all logic is testable (dependency injection where needed).

### Phase 2: Introduce Bash Testing (Next)
1.  **Install Bats**: `npm install -g bats` (or via apt/brew).
2.  **Test Installer**: Create `tests/bash/test_install.bats`.
3.  **Test Workflows**: Create a bats test that mocks the user input vs the breakdown workflow.

### Phase 3: Continuous Integration (CI)
Create a `.github/workflows/test.yml` that runs:
1.  Linting (`ruff` or `black`).
2.  Type Checking (`mypy`).
3.  Pytest Unit + Integration.
4.  Bats Tests.

---

## 4. How to Run Tests

### Python
```bash
# Run all
pytest

# Run with coverage report
pytest --cov=src --cov-report=term-missing
```

### Bash (Future)
```bash
bats tests/bash/
```

---

## 5. Definition of Done ("Proud System")
- [ ] CI pipeline passes on every commit.
- [ ] Code coverage is >85%.
- [ ] No "flaky" tests.
- [ ] `install.sh` is automatically tested (no manual "does it work?" checks).

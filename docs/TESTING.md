# Testing Guide

## 🚀 Quick Start (The "Dummies Guide")

This guide explains how to run the automated tests for the SpecKit system.

### 1. Prerequisites
- **Python 3.10+** installed.
- **Dependencies** installed (`pip install -r requirements-dev.txt`).
- **Bats Core** installed (`npm install -g bats`, or via your package manager) for Shell script testing.
- **PostgreSQL** running (for integration tests).

### 2. Running All Tests
To run every test in the suite (Unit + Integration + Scripts):
```bash
# Run Python Tests
pytest

# Run Bash Script Tests
bats tests/bash/
```

### 3. Running Specific Tests

**Run only fast Unit Tests (No Database required):**
```bash
pytest tests/unit
```

**Run specific services:**
```bash
pytest tests/unit/test_rollback_manager.py
pytest tests/unit/test_ai_job_service.py
pytest tests/unit/test_metrics.py
```

**Run Installer Script Tests:**
```bash
bats tests/bash/test_install.bats
```

---

## 🔧 Technical Guide (The Breakdown)

This section explains what the tests actually do and how they map to the system architecture.

### Test Architecture
The test suite is divided into three layers:

1.  **Unit Tests** (`tests/unit/`):
    *   **Scope**: Isolated functions and classes.
    *   **Focus**: Verifies logic like "Does this Markdown parse correctly?", "Does rollback execute in LIFO order?", "Does the logger handle exceptions?".
    *   **Speed**: Very fast (<1s).
    *   **Key Files**: 
        *   `test_rollback_manager.py`: Verifies transactional safety.
        *   `test_ai_job_service.py`: Verifies AI job creation logic.
        *   `test_metrics.py`: Verifies safe logging.

2.  **Integration Tests** (`tests/integration/`):
    *   **Scope**: The full `BootstrapOrchestrator` workflow.
    *   **Focus**: Verifies that individual components (Parsers -> Validators -> Service -> Gateway) work together.
    *   **Backends**: SQLite/Memory and PostgreSQL.

3.  **Script Tests** (`tests/bash/`):
    *   **Scope**: Shell scripts and CLI workflows.
    *   **Focus**: Verifies installation scripts, file system creation, and error handling for missing prerequisites.
    *   **Tool**: `bats-core`.
    *   **Key Files**:
        *   `test_install.bats`: Verifies `install-local.sh` behavior (creation of `.windsurf/workflows`, failure if SpecKit missing).

### Data Flow Validation
When you run the PostgreSQL integration test (`test_db_prepare_postgres.py`), it validates the following "Waterfall" sequence:

1.  **Project Parsing**: Reads `project.md`.
2.  **Feature Ingestion**: Reads `features/*.md`.
3.  **Spec Definition**: Reads `specs/*.md`.
4.  **Task Creation**: Reads `tasks/*.md`.
5.  **Dependencies**: Reads `TaskDependencies` block.

---

## 📊 Coverage & Health

### Current Status
*   **Total Tests**: ~15+ Files covering Parsing, Validation, CLI, Persistence, and Scripts.
*   **Coverage**:
    *   ✅ **Core Logic**: High (Parsers & Validators).
    *   ✅ **Services**: High (Rollback, AI Jobs, Metrics).
    *   ✅ **Scripts**: High (Installation happy/sad paths).
    *   ✅ **Database Integrity**: High (PostgreSQL test verifies FKs).

### Continuous Integration
Tests are automatically run on GitHub Actions via `.github/workflows/test.yml`.

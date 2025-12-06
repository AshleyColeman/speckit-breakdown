# Testing Guide

## 🚀 Quick Start (The "Dummies Guide")

This guide explains how to run the automated tests for the SpecKit system.

### 1. Prerequisites
- **Python 3.10+** installed.
- **Dependencies** installed (`pip install -r requirements.txt`).
- **PostgreSQL** running (for integration tests).

### 2. Running All Tests
To run every test in the suite (Unit + Integration):
```bash
pytest
```

### 3. Running Specific Tests
**Run only fast Unit Tests (No Database required):**
```bash
pytest tests/unit
```

**Run Integration Tests (Simulates full workflow):**
```bash
pytest tests/integration
```

**Run the PostgreSQL Database Integration Test:**
*(Requires `DATABASE_URL` environment variable if not using default localhost)*
```bash
# Default (localhost:5432/action_db)
pytest tests/integration/test_db_prepare_postgres.py

# Custom DB URL
DATABASE_URL="postgresql://user:pass@host:5432/db" pytest tests/integration/test_db_prepare_postgres.py
```

---

## 🔧 Technical Guide (The Breakdown)

This section explains what the tests actually do and how they map to the system architecture.

### Test Architecture
The test suite is divided into two layers:

1.  **Unit Tests** (`tests/unit/`):
    *   **Scope**: Isolated functions and classes.
    *   **Focus**: Verifies logic like "Does this Markdown parse correctly?" or "Does this validation rule catch a duplicate?".
    *   **Speed**: Very fast (<1s).
    *   **Key Files**: `test_parser_markdown_kv.py` (Parser logic), `test_db_prepare_flags.py` (CLI args).

2.  **Integration Tests** (`tests/integration/`):
    *   **Scope**: The full `BootstrapOrchestrator` workflow.
    *   **Focus**: Verifies that individual components (Parsers -> Validators -> Service -> Gateway) work together.
    *   **Backends**: 
        *   **SQLite/Memory**: Default for logic checks (`test_db_prepare_success.py`).
        *   **PostgreSQL**: Verifies real database persistence (`test_db_prepare_postgres.py`).

### Data Flow Validation
When you run the PostgreSQL integration test (`test_db_prepare_postgres.py`), it validates the following "Waterfall" sequence:

1.  **Project Parsing**: Reads `project.md`.
    *   *Action*: Inserts into `projects` table.
    *   *Validation*: Queries DB for Project Name to ensure it exists.
2.  **Feature Ingestion**: Reads `features/*.md`.
    *   *Action*: Resolves the Parent Project (via Name) -> Inserts into `features` table.
    *   *Validation*: Checks that `project_id` on the feature matches the Project.
3.  **Spec Definition**: Reads `specs/*.md`.
    *   *Action*: Resolves the Parent Feature (via Name) -> Inserts into `specs` table.
    *   *Validation*: Checks that `feature_id` on the spec matches the Feature.
4.  **Task Creation**: Reads `tasks/*.md`.
    *   *Action*: Resolves Parent Feature & Project -> Inserts into `tasks` table.
    *   *Metadata*: Stores original SpecKit code (e.g., `TASK-123`) in `metadata->>'code'`.
    *   *Validation*: Checks `status`, `metadata`, and foreign keys.
5.  **Dependencies**: Reads `TaskDependencies` block.
    *   *Action*: Resolves Predecessor and Successor UUIDs -> Inserts into `task_dependencies`.
    *   *Validation*: Ensures database constraints (FKs) are satisfied.

### Schema Mapping Strategy
The test accounts for the schema differences between SpecKit (Code-based) and the Database (UUID-based):
*   **Projects/Features/Specs**: Resolved using **Natural Keys** (Name/Title).
*   **Tasks**: Resolved using **Metadata** (`metadata->>'code'`).

## 📊 Assessment: Do we need more tests?

### Current Status
*   **Total Tests**: ~12 Files covering Parsing, Validation, CLI, and Persistence.
*   **Coverage**:
    *   ✅ **Core Logic**: High (Parsers & Validators).
    *   ✅ **Happy Path**: High (Full end-to-end verified).
    *   ✅ **Database Integrity**: High (PostgreSQL test verifies FKs).

### Gaps & Recommendations
1.  **`ai_jobs` & `task_runs`**:
    *   *Status*: Not implemented in Gateway yet.
    *   *Need*: **High**. Once implemented, we need integration tests to verify that AI job logs and task execution attempts are correctly persisted.
2.  **Performance**:
    *   *Status*: N/A.
    *   *Need*: **Medium**. If we expect >1000s of files, we need a load test to verify `DataStoreGateway` performance (batch sizing).
3.  **Error Handling (PostgreSQL)**:
    *   *Status*: Basic.
    *   *Need*: **Low/Medium**. Tests for specific Postgres constraint violations (e.g. duplicate names) would be beneficial.

**Verdict**: The current suite is robust for the *preparation* phase (`db_prepare`). You are safe to deploy this logic. Future tests should focus on the *execution* phase (`ai_jobs`).

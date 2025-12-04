# Tasks: Speckit DB Bootstrap Command

**Input**: Design documents from `/specs/001-db-bootstrap/`

**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: Required per specification (validation + idempotency scenarios must be verified via automated tests).

**Organization**: Tasks are grouped by user story so each increment is independently implementable and testable.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish CLI scaffolding, configuration, and logging so subsequent features have a stable surface.

- [X] T001 Create `/speckit.db.prepare` command entrypoint and registration in `src/cli/commands/db_prepare.py`
- [X] T002 Initialize configuration loader for documentation + storage paths in `src/lib/config_loader.py`
- [X] T003 [P] Implement CLI argument parser for global flags (`--dry-run`, `--force`, `--project`, `--skip-*`) in `src/cli/commands/db_prepare.py`
- [X] T004 [P] Configure structured logging + verbosity toggles (human + JSON) in `src/lib/logging.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core services for discovery, validation orchestration, storage access, and resource controls. All user stories depend on these components.

- [X] T005 Implement documentation discovery service that verifies `project.md`, `features/`, `specs/`, `tasks/`, `dependencies/` presence in `src/services/doc_discovery.py`
- [X] T006 [P] Define normalized entity DTOs (projects, features, specs, tasks, dependencies, task_runs, ai_jobs) in `src/models/entities.py`
- [X] T007 Create data storage gateway with create/update/delete primitives (including dependency edges) in `src/services/data_store_gateway.py`
- [X] T008 Build validation pipeline orchestrator shell (hooks for rules, severity, reporting) in `src/services/validation_pipeline.py`
- [X] T009 [P] Implement file-level locking + queue management utilities in `src/lib/locking.py`
- [X] T010 Implement rollback manager and transaction context for multi-entity operations in `src/services/rollback_manager.py`
- [X] T011 [P] Add resource guard (memory/CPU/file-size tracking + graceful degradation policies) in `src/lib/resource_guard.py`

**Checkpoint**: Foundation complete → user stories can execute in parallel.

---

## Phase 3: User Story 1 - System Data Initialization (Priority: P1) 🎯 MVP

**Goal**: Parse full documentation stack (including dependencies) and populate data storage with linked projects, features, specs, tasks, dependencies, task runs, and AI jobs.

**Independent Test**: Run `/speckit.db.prepare --dry-run` against a complete sample project; ensure all entities parsed, validated, persisted (or queued), and summarized without errors.

### Tests for User Story 1

- [ ] T012 [P] [US1] Integration test validating successful bootstrap (entities + dependency graph + derived task runs/AI jobs) in `tests/integration/test_db_prepare_success.py`
- [ ] T013 [P] [US1] Full project fixture containing dependencies, task-run hints, and AI job metadata in `tests/fixtures/projects/full_project/`
- [ ] T014 [P] [US1] Golden datastore snapshot/assertions for success case in `tests/helpers/data_store_assertions.py`

### Implementation for User Story 1

- [ ] T015 [P] [US1] Implement project parser reading project.md metadata in `src/services/parser/project_parser.py`
- [ ] T016 [P] [US1] Implement feature parser that links features to projects in `src/services/parser/feature_parser.py`
- [ ] T017 [P] [US1] Implement spec + task parser (status, acceptance criteria, dependency refs) in `src/services/parser/feature_parser.py`
- [ ] T018 [P] [US1] Implement dedicated dependency parser that normalizes task dependency edges in `src/services/parser/dependency_parser.py`
- [ ] T019 [US1] Build bootstrap orchestrator chaining discovery → parsing → validation → persistence in `src/services/bootstrap_orchestrator.py`
- [ ] T020 [US1] Wire dry-run summary output (entity counts + pending writes + skip reasons) into `src/cli/commands/db_prepare.py`
- [ ] T021 [US1] Implement upsert service for projects/features/specs/tasks in `src/services/upsert_service.py`
- [ ] T022 [US1] Persist task dependencies via gateway + relationship mapper in `src/services/data_store_gateway.py`
- [ ] T023 [US1] Implement task-run creation service (auto create unless skipped) in `src/services/task_run_service.py`
- [ ] T024 [US1] Implement AI job creation service (auto create unless skipped) in `src/services/ai_job_service.py`
- [ ] T025 [US1] Emit operation metrics + success report (per-entity totals, duration) in `src/lib/metrics.py`

**Checkpoint**: `/speckit.db.prepare --dry-run` completes successfully with accurate summaries and derived entities.

---

## Phase 4: User Story 2 - Validation and Error Handling (Priority: P1)

**Goal**: Block invalid documentation before persistence, with descriptive error reporting, rollback summaries, and resilience to malformed docs/network issues/schema drift.

**Independent Test**: Run `/speckit.db.prepare --dry-run` with intentionally invalid docs; verify execution halts before storage writes, reports precise errors (file/line), and emits rollback summaries.

### Tests for User Story 2

- [ ] T026 [P] [US2] Integration test covering circular dependency + duplicate IDs in `tests/integration/test_db_prepare_validation_errors.py`
- [ ] T027 [P] [US2] Invalid documentation fixtures (missing metadata, duplicates, circular tasks) in `tests/fixtures/projects/invalid_project/`
- [ ] T028 [P] [US2] Malformed markdown + missing frontmatter fixtures in `tests/fixtures/projects/malformed_docs/`
- [ ] T029 [P] [US2] Integration test for malformed documentation detection in `tests/integration/test_db_prepare_malformed_docs.py`
- [ ] T030 [P] [US2] Unit test simulating network/data-store failures with retry expectations in `tests/unit/test_db_prepare_network_failures.py`
- [ ] T031 [P] [US2] Integration test detecting schema drift and surfacing remediation guidance in `tests/integration/test_db_prepare_schema_drift.py`

### Implementation for User Story 2

- [ ] T032 [P] [US2] Implement validation rules for duplicates, circular dependencies, missing metadata, and malformed markdown in `src/services/validation/rules.py`
- [ ] T033 [US2] Integrate validation pipeline into command preflight with severity gating + halt on high severity in `src/services/validation_pipeline.py`
- [ ] T034 [US2] Build error reporter that surfaces file/line numbers, remediation suggestions, and grouped outputs in `src/lib/error_reporter.py`
- [ ] T035 [US2] Format CLI output + exit codes for validation failures, including rollback summary blocks, in `src/cli/commands/db_prepare.py`
- [ ] T036 [US2] Add rollback summary emitter that lists reverted operations in `src/services/rollback_manager.py`
- [ ] T037 [US2] Implement network-failure retry/backoff + observability hooks in `src/services/data_store_gateway.py`
- [ ] T038 [US2] Detect schema drift (unexpected columns/entities) and surface remediation guidance in `src/services/data_store_gateway.py`

**Checkpoint**: Invalid or unstable documentation fails fast with actionable remediation details.

---

## Phase 5: User Story 3 - Idempotent Operations & Force Mode (Priority: P2)

**Goal**: Support repeated runs without duplicate data, plus a safe `--force` option that overwrites mismatched entities with full audit trails.

**Independent Test**: Run `/speckit.db.prepare` three times in succession on the same project, then run with `--force` on mismatched data; verify entity counts remain stable and forced overwrites are logged.

### Tests for User Story 3

- [ ] T039 [P] [US3] Integration test executing command thrice and asserting stable counts in `tests/integration/test_db_prepare_idempotent.py`
- [ ] T040 [P] [US3] Shared datastore assertion helpers for before/after snapshots in `tests/helpers/data_store_assertions.py`
- [ ] T041 [P] [US3] Integration test for `--force` overwrite workflow in `tests/integration/test_db_prepare_force_mode.py`

### Implementation for User Story 3

- [ ] T042 [P] [US3] Implement entity matcher resolving existing records via codes/checksums in `src/services/matchers/entity_matcher.py`
- [ ] T043 [US3] Extend upsert service with idempotent diff + merge logic in `src/services/upsert_service.py`
- [ ] T044 [US3] Enforce concurrency-safe queues + retries in `src/lib/locking.py`
- [ ] T045 [US3] Emit idempotency metrics (unchanged counts, retries) in `src/lib/metrics.py`
- [ ] T046 [US3] Implement force-mode reconciliation (audit log + warning output) in `src/services/upsert_service.py`

**Checkpoint**: Command can be re-run safely and force mode has auditable behavior.

---

## Phase 6: User Story 4 - Selective Bootstrap Options (Priority: P3)

**Goal**: Allow operators to skip optional entities or scope execution to specific projects via CLI flags.

**Independent Test**: Run `/speckit.db.prepare` with `--skip-ai-jobs`, `--skip-task-runs`, and `--project <id>` flags; verify storage contains only the requested entities.

### Tests for User Story 4

- [ ] T047 [P] [US4] Unit test covering CLI option combinations + validation in `tests/unit/test_db_prepare_flags.py`
- [ ] T048 [P] [US4] Scoped project fixtures for selective bootstrap scenarios in `tests/fixtures/projects/scoped_project/`

### Implementation for User Story 4

- [ ] T049 [P] [US4] Implement option parsing + validation for skip/project flags in `src/cli/options/db_prepare_options.py`
- [ ] T050 [US4] Update bootstrap orchestrator to branch entity processing per flag set in `src/services/bootstrap_orchestrator.py`
- [ ] T051 [US4] Add selective persistence filters (per-entity toggles) in `src/services/data_store_gateway.py`
- [ ] T052 [US4] Document usage examples + flag matrix in `docs/cli/db_prepare.md`

**Checkpoint**: Operators can tailor entity creation per environment requirements.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Hardening, documentation, and performance verification spanning all stories.

- [ ] T053 [P] Expand observability + logging guide for ops teams in `docs/operations/db_prepare_logging.md`
- [ ] T054 Create quickstart validation walkthrough referencing new command in `quickstart/db_prepare.md`
- [ ] T055 [P] Add performance benchmarking script with SC-001/SC-007 thresholds + baseline doc in `scripts/benchmarks/db_prepare_perf.py`
- [ ] T056 [P] Add CI gate that fails when benchmark thresholds exceed limits in `.github/workflows/ci.yml`
- [ ] T057 Polish CLI help/UX copy and ensure examples reflect selective flags + force mode in `src/cli/commands/db_prepare.py`
- [ ] T058 Update high-level documentation with bootstrap workflow + configuration overview in `README.md`

---

## Dependencies & Execution Order

- **Phase 1 → Phase 2**: Setup must complete before foundational services can use the CLI scaffolding.
- **Phase 2 → User Stories (3-6)**: Validation, storage gateway, locking, and resource guard are prerequisites for all user stories.
- **User Story Order**: US1 (P1) and US2 (P1) can begin immediately after Phase 2 (they interact but remain independently testable). US3 (P2) depends on US1 persistence primitives. US4 (P3) depends on US1 orchestration and US2 validation hooks.
- **Polish (Phase 7)**: Runs after targeted user stories are feature-complete.

### User Story Dependency Graph

```
Setup → Foundational → {US1, US2}
US3 → depends on US1
US4 → depends on US1 & US2
Polish → depends on desired user stories (US1–US4)
```

---

## Parallel Execution Examples

1. **Setup**: T003 and T004 can run concurrently once T001 scaffolds command file.
2. **Foundational**: T006, T009, and T011 touch distinct modules and can proceed in parallel after discovery service (T005) spec is signed off.
3. **User Story 1**: Parser tasks T015–T018 can proceed concurrently, unblocking orchestrator work (T019) once DTO contracts are defined (T006).
4. **User Story 2**: Test fixtures (T027–T031) can be built in parallel while validation rules (T032) and error reporter (T034) progress.
5. **User Story 3**: Integration tests (T039–T041) and matcher implementation (T042) operate on separate paths (`tests/` vs `src/services/matchers/`).
6. **User Story 4**: T047 unit tests and T049 option parsing are parallelizable; they integrate when T050 updates orchestrator behavior.

---

## Implementation Strategy

1. **MVP (US1 only)**:
   - Execute Phase 1 → Phase 2 sequentially.
   - Complete Phase 3 (US1) and validate via dry-run test suite.
   - Ship CLI with parsing + persistence pipeline; document limitations for validation/idempotency/flags.
2. **Incremental Delivery**:
   - Layer US2 immediately after MVP to guard against invalid documentation.
   - Add US3 to guarantee safe re-runs and concurrency resilience.
   - Implement US4 for selective bootstrap when deployment flexibility is required.
3. **Parallel Teaming**:
   - One developer owns CLI + orchestration (US1), another focuses on validation/error UX (US2), third handles idempotency (US3), fourth addresses selective options & docs (US4).
   - Synchronize via shared models (T006) and gateway contracts (T007/T036) defined during Phase 2.

---

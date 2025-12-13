🧾 REPOSITORY AUDIT REPORT

🟢 Executive Summary

Overall health score (1–10): **5/10**

This repository is a useful and pragmatic add-on around the SpecKit workflow ecosystem, with a clear user-facing purpose and decent test/CI presence. However, the implementation reveals a split-brain architecture: Markdown “workflows” (the main product surface) are relatively coherent, while the Python “bootstrap/db.prepare” subsystem is partially scaffolded, inconsistently typed, and mixes production and “test-only workaround” logic in core paths (notably the PostgreSQL branch in `src/services/data_store_gateway.py`). The codebase will likely remain maintainable for a small team, but the first things to break as usage grows will be correctness of persistence (especially Postgres), schema compatibility assumptions, and consistency between docs (claims) vs runtime behavior.

Biggest systemic risk (1–2 items)

1. **PostgreSQL support is not production-grade**: key CRUD read paths are incomplete (`get_project` returns `None`, `_log_entities` is a stub, task/spec/feature getters mismatch actual Postgres schema assumptions), and the write path contains explicit “dangerous for real use” workarounds. This is the highest risk for data integrity and confusing failures.
2. **Accidental architecture drift**: the repo documents a “robust” system with rollback safety and validations, but several critical integrations are missing or incomplete (transactionality across persistence steps, file locking unused, resource guard unused, Postgres schema verification skipped). As the system evolves, the risk is “it works in tests” but fails in real projects and is hard to debug.

🧱 Architecture Review

Findings

1. **Two primary subsystems**

- Workflow layer (Markdown): `workflows/*.md` drives the user-facing `/speckit.*` commands (e.g. `workflows/speckit.breakdown.md`).
- Python CLI layer: `src/cli/commands/db_prepare.py` wires `/speckit.db.prepare` to the bootstrap orchestrator.

This separation is intentional conceptually, but in practice the repository is not cleanly layered: the Python “bootstrap” subsystem is a semi-independent product with its own schema expectations and lifecycle.

2. **Orchestration is reasonably centralized**

- `src/services/bootstrap_orchestrator.py` is the authoritative “pipeline”: discovery → parse → validate → compute step orders → persist → create task runs / ai jobs.

This is a good direction: it makes the dataflow understandable.

3. **Layering and dependency direction are mixed**

- Orchestrator depends on parsers + validation + persistence gateway.
- Gateway embeds schema creation and both SQLite + Postgres logic in one class (`src/services/data_store_gateway.py`).

This makes `DataStoreGateway` a “god adapter” that will grow quickly as more entities/states are added.

4. **Architecture appears partially accidental**

Evidence:

- `DataStoreGateway` contains explicit “test workaround” commentary and placeholder stubs (`create_task_runs`, `create_ai_jobs`, `_log_entities`, `get_project`).
- Docs claim “transactional safety” and “rollback manager integrated” (`docs/speckit_system_guide.md`), but orchestrator does not use `RollbackManager` or a DB transaction across the whole run.

What will break first as the system grows?

- **DB compatibility**: any divergence between “expected Postgres schema” and what `DataStoreGateway` assumes.
- **Feature volume**: `BootstrapOrchestrator._calculate_step_orders()` uses a Python list as a queue (`pop(0)`), which is O(n²) in worst case; this will show up at scale.
- **More commands**: as more Python CLI commands are added, current lack of packaging/deps management will become painful (see Data/DB and DX sections).

Risks

- **High coupling in persistence layer**: SQLite schema creation + Postgres ad-hoc mapping in one file, with no clear interface boundary.
- **Dependency direction inversion**: `UpsertService` accepts `gateway: object` and punts typing “for circular dep risk” (`src/services/upsert_service.py`). That’s a signal the architecture is fighting itself.
- **Workflows as product surface**: `workflows/speckit.breakdown.md` instructs agents to write files directly via `write_to_file`. That’s fine, but the repo itself doesn’t validate generated outputs or enforce a schema for them.

Recommendations

1. **Define an explicit storage interface and split backends** (incremental, not a rewrite)

- Introduce a `DataStoreGateway` protocol (write/read methods used by orchestrator), then implement `SqliteGateway` and `PostgresGateway` behind it.
- Keep the orchestrator unchanged; just inject the appropriate implementation.

2. **Make Postgres support explicitly experimental until fixed**

- Add a “support tier” statement in docs: SQLite stable; Postgres experimental.
- Or gate Postgres with a flag and fail fast unless explicitly enabled.

3. **Remove “test-only mapping logic” from production classes**

- Anything described as “dangerous for real use” should be isolated to test fixtures or a dedicated “compat mode” module.

🧼 Code Quality Review

Findings

1. **Several files exceed stated hard limits**

- `src/services/data_store_gateway.py` is ~627 lines.
- `src/services/bootstrap_orchestrator.py` is ~280 lines.
- `src/services/parser/feature_parser.py` is ~600 lines.

This conflicts with the repository’s own “Hard Rules” in `AGENT.md` (max 500 lines per file, 40 lines per function). That’s not just style—it’s a maintainability drift warning.

2. **Inconsistent typing / incomplete interfaces**

- `UpsertService.__init__(..., gateway: object)` is intentionally untyped.
- `BootstrapSummary.validation_result: Optional[object]` makes the CLI/reporting layer lose type safety.

3. **Comments indicate unfinished production behavior**

- `DataStoreGateway.verify_schema()` for Postgres is `pass`.
- `create_task_runs`, `create_ai_jobs`, `_log_entities` are `pass`.
- `get_project` returns `None`.

These are “it compiles” placeholders that will hide bugs.

4. **Minor but real implementation issues**

- `BootstrapOrchestrator._calculate_step_orders()` uses `queue.pop(0)`; use `collections.deque` to avoid O(n²) behavior.
- Validation rules include self-noted uncertainty and mismatched attribute commentary (e.g. in `DuplicateEntityRule` line ~67 in `src/services/validation/rules.py`). That’s a smell: validation is safety-critical.

Smells Detected

- **God file**: `src/services/data_store_gateway.py` (schema creation, migrations-ish concerns, read/write, postgres/sqlite branching, retry decorator).
- **Hidden coupling**: Postgres mapping depends on heuristics (“replace '-' with ' '”, matching by name) rather than stable keys.
- **Implicit assumptions**:
  - Task codes are unique and stable across runs.
  - Postgres schema stores `metadata->>'code'` for tasks.
  - Feature/project “code” can be derived and then mapped to DB “name”.

Recommendations

- **Split the large parser file**: `feature_parser.py` currently contains Feature/Spec/Task parsing. Incremental split into `feature_parser.py`, `spec_parser.py`, `task_parser.py` while keeping imports stable.
- **Make validation and persistence strict**: fail fast if required fields aren’t present; avoid silently continuing on parse errors (currently many `except Exception: logger.error(...); continue`).
- **Replace placeholder implementations with explicit “Not Implemented” errors** where unsafe. Silent `pass` is worse than a hard failure.

🗄️ Data & Database Review

Findings

1. **SQLite schema is embedded and auto-created** (`src/services/data_store_gateway.py`)

- Tables: `projects`, `features`, `specs`, `tasks`, `task_dependencies`.
- Very weak constraints (e.g., FK exists but likely not enforced unless `PRAGMA foreign_keys=ON` is set; not present here).

2. **Postgres support is schema-assumption heavy and inconsistent**

Evidence:

- Tasks rely on `metadata->>'code'` (good) but Projects/Features/Specs rely on name matching heuristics.
- `create_or_update_features()` contains extensive “workaround” commentary and uses `projects WHERE name = project_code` and then `LOWER(name) = LOWER(project_code.replace('-', ' '))`.

This is not reliable in real multi-project databases.

3. **Read interface is incomplete**

- `get_project()` returns `None`, so `EntityMatcher.find_existing_project()` cannot work.
- `get_feature()` / `get_spec()` Postgres queries appear to assume `features.code`, `specs.code`, etc. But the integration test (`tests/integration/test_db_prepare_postgres.py`) verifies via `features WHERE name = 'Test Feature'` and `specs WHERE name = 'Test Spec'`, suggesting the DB schema differs from what these getters expect.

4. **Dependencies table mismatch between SQLite and Postgres**

- SQLite: `task_dependencies(task_code, depends_on)`.
- Postgres: `task_dependencies(predecessor_id, successor_id)`.

The translation layer exists but depends on being able to resolve task IDs reliably.

Risks

- **Data integrity risk**: name-based linking will attach features/specs/tasks to the wrong project in multi-project DBs.
- **Partial writes**: orchestrator persists projects/features/specs/tasks, then dependencies, then task_runs, then ai_jobs. There is no transaction spanning these steps.
- **Schema drift**: Postgres `verify_schema()` is skipped; SQLite schema drift check exists, but only checks columns, not constraints.

Recommendations

1. **Stabilize identifiers across all entities**

- Ensure Postgres schema stores a stable “code” on projects/features/specs (not only tasks).
- If you cannot change schema, persist “code” in `metadata` for all entities and query by it.

2. **Make persistence transactional per run**

- SQLite: wrap in a single transaction.
- Postgres: use a single connection and transaction for all writes.

3. **Turn on SQLite foreign keys**

- Execute `PRAGMA foreign_keys=ON` per connection.

4. **Align read methods with actual Postgres schema**

- Make `get_feature`/`get_spec` consistent with integration tests, or update tests to reflect intended schema. Right now, they are contradictory.

🛡️ Security Review

Findings

1. **Installer downloads remote workflow code** (`install.sh`)

- Uses `curl -fsSL https://raw.githubusercontent.com/...` and writes into `.windsurf/workflows/`.

This is expected for an installer, but it’s a supply-chain risk if users run it blindly.

2. **Postgres connection string handling**

- CLI accepts `--db-url` and the integration test uses a default URL containing credentials (`postgres:password@localhost`).

This is fine for tests, but docs should warn users not to hardcode secrets in repo.

3. **Input trust boundary**

- Parsers ingest markdown content and frontmatter. YAML parsing attempts `import yaml` (PyYAML), but `requirements.txt` does not include PyYAML.

If PyYAML is installed implicitly in someone’s environment, you’ll parse YAML. If not, you’ll fallback to a very permissive parser. This inconsistency is a security and correctness concern.

Critical Issues (if any)

- **Supply chain / remote execution risk**: Installing via remote `curl | sh` is always a risk. At minimum, document verification steps (pin to tag/commit, checksum).
- **Ambiguous YAML parsing dependency**: behavior changes depending on global env packages.

Recommendations

- Add guidance: “Prefer pinning to a release tag; review the script before running.”
- Add PyYAML explicitly if YAML is a first-class feature, or remove YAML parsing and standardize on the simple parser.

⚡ Performance & Scalability

Findings

- `_calculate_step_orders()` uses list queue with `pop(0)` → O(n²) behavior on large task graphs.
- SQLite gateway uses per-method connections and no batching for some operations; acceptable at small scale but will degrade.
- Postgres code repeatedly opens new connections (`psycopg2.connect`) inside loops in some methods (`create_or_update_projects`, etc.).

Hotspots

- `src/services/data_store_gateway.py`: per-entity loops + new DB connections.
- `src/services/parser/feature_parser.py`: repeated regex scans and multiple directory passes; OK for small docs, but could slow on large specs.

📚 Documentation & DX

Missing / Weak Docs

- **Python runtime packaging**: no `pyproject.toml`, no pinned deps, and `requirements.txt` only includes test dependencies.
- **Postgres schema contract**: docs reference Postgres usage, but there is no canonical schema definition or migration tooling in this repo.
- **Developer onboarding for Python CLI**: README focuses on workflows/installation, not how to run `src/cli/main.py` or install runtime deps.

Improvements

- Add a short “Python CLI” section in README:
  - How to install runtime deps
  - How to run `/speckit.db.prepare` locally
  - What schemas are supported
- Add a “Support Matrix” section: SQLite stable; Postgres experimental.

🚧 Priority Action Plan

High Priority (Must Fix Soon)

1. **Make Postgres support either correct or explicitly disabled**

- **What to fix**: Remove/guard heuristic name-matching logic in `DataStoreGateway` and implement stable identifier mapping, or fail fast when `postgresql://` is used.
- **Why it matters**: Data integrity + hard-to-debug mis-linking.
- **Effort level**: High

2. **Replace placeholder `pass` stubs with explicit behavior**

- **What to fix**: `DataStoreGateway.create_task_runs`, `create_ai_jobs`, `_log_entities`, `get_project`.
- **Why it matters**: silent “success” hides bugs; idempotency/force mode correctness relies on reads.
- **Effort level**: Medium

3. **Make YAML parsing behavior deterministic**

- **What to fix**: Add `PyYAML` as an explicit dependency or remove YAML parsing and standardize.
- **Why it matters**: inconsistent parsing across machines is a production footgun.
- **Effort level**: Low–Medium

Medium Priority

1. **Refactor `DataStoreGateway` into backend-specific modules**

- **What to fix**: split SQLite vs Postgres implementations; introduce a protocol interface.
- **Why it matters**: reduces god-file risk and allows cleaner tests.
- **Effort level**: Medium

2. **Make step order computation scalable**

- **What to fix**: use `collections.deque` and/or compute topological order with an explicit queue.
- **Why it matters**: prevents performance cliffs for large dependency graphs.
- **Effort level**: Low

3. **Add end-to-end “real project fixture” tests for breakdown workflow outputs**

- **What to fix**: Bats tests exist; extend to validate generated files schema, not just script execution.
- **Why it matters**: workflows are the primary product surface.
- **Effort level**: Medium

Low Priority / Cleanup

1. **Align repository “hard rules” with reality**

- **What to fix**: Either enforce file/function size limits or update `AGENT.md` to reflect reality.
- **Why it matters**: mismatch creates churn and inconsistent PR reviews.
- **Effort level**: Low

2. **Improve typing clarity**

- **What to fix**: type `gateway` in `UpsertService`, type `validation_result` in `BootstrapSummary`.
- **Why it matters**: helps future contributors refactor safely.
- **Effort level**: Low

🧠 Final Auditor Notes

Long-term risks

- The biggest long-term failure mode is “compatibility drift”: docs and workflows evolve quickly, while Python persistence lags and becomes a brittle integration point.
- Postgres support, as written, will become an operational liability if used beyond tests.

Strategic advice

- Treat the Python CLI subsystem as a product with a strict contract (inputs, schema, outputs). Write that contract down.
- Keep the workflows as high-level orchestration, but ensure critical correctness is in typed, tested code.

“If I owned this repo…” guidance

- I would stabilize a single backend first (SQLite), declare it the default and supported mode, and make Postgres either fully supported with explicit schema/migrations or clearly experimental.
- I would split `DataStoreGateway` and `feature_parser.py` into smaller, testable units to reduce the bus factor and improve reviewability.

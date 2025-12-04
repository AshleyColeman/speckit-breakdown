# Speckit Breakdown Constitution

## Core Principles

### I. CLI-First Execution (MUST)
All functionality must be invokable via deterministic CLI commands that read from stdin/args and write structured results to stdout with errors routed to stderr. Human-readable and JSON outputs are both required when practical.

### II. Test-First Delivery (MUST)
New behavior must start with failing automated tests (unit, integration, or contract). No implementation code may merge unless corresponding tests cover success paths, failure modes, and edge cases described in specs.

### III. Structured Observability (MUST)
Every command and service must emit structured logs with configurable verbosity, correlation IDs, and success/error metrics. Logging must not be optional; dry runs and real runs must both produce traceable output.

### IV. Deterministic Persistence (MUST)
Bootstrap and storage workflows must be idempotent, enforce file-level locking, and provide transactional rollback for multi-entity writes. Force modes must explicitly document overrides and safety checks.

### V. Documentation Integrity (SHOULD)
Specifications, plans, tasks, and quickstarts must stay in sync. Any new directory, model, or CLI flag must be reflected in the design artifacts before code implementation begins.

## Delivery Workflow

1. `/speckit.specify` → Approved specification with user stories, requirements, and edge cases.
2. `/speckit.plan` → Concrete implementation plan including tech stack, architecture, and gating assumptions.
3. `/speckit.tasks` → Executable checklist grouped by user story with file paths and dependencies.
4. `/speckit.implement` → Execution strictly following tasks, updating docs/tests as functionality evolves.

## Quality Gates

- Constitution compliance review is required before merging any PR.
- Performance, observability, and rollback requirements are non-negotiable for data-manipulating commands.
- Any detected ambiguity or placeholder text must be resolved before implementation starts.
- Each user story must remain independently testable; cross-story coupling must be called out explicitly.

## Governance

This constitution supersedes prior guidelines. Amendments require documented rationale, reviewer approval, and backfills to existing docs/tasks so that history stays auditable. When conflicts arise between this file and other artifacts, this constitution prevails.

**Version**: 1.0.0 | **Ratified**: 2025-12-04 | **Last Amended**: 2025-12-04

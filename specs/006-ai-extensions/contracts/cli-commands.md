# CLI Contracts: SpecKit Advanced AI Extensions

This document specifies the high-level contracts for the new `/speckit.*` commands introduced by the `006-ai-extensions` feature. It focuses on inputs, outputs, and expected behaviors, not implementation details.

> **Note**: All commands are expected to be:
>
> - Safe by default (no destructive git operations).  
> - Idempotent where applicable (re-running updates outputs deterministically).  
> - CLI-first, with clear exit codes and human-readable messages.

---

## 1. `/speckit.arch`

**Purpose**  
Generate or update an `architecture.md` document for the project or a specific feature.

**Inputs**
- Scope: `project` (default) or `feature:<id>` (e.g., `feature:006-ai-extensions`).
- Existing design artifacts: `spec.md`, `plan.md`, and optional `architecture.md`.

**Outputs**
- Project-level: `docs/architecture.md`.  
- Feature-level: `specs/<feature-id>/architecture.md`.  
- Exit code `0` on success; non-zero on failure with a clear error message.

---

## 2. `/speckit.bundle`

**Purpose**  
Build a context pack for AI agents and automation.

**Inputs**
- Scope: `project` or `feature:<id>`.  
- Design artifacts: `spec.md`, `plan.md`, `tasks.md`, `architecture.md`, constitution, and related markdown.

**Outputs**
- `.speckit/context/context.json`  
- `.speckit/context/spec.md`  
- `.speckit/context/plan.md`  
- `.speckit/context/tasks.md`  
- `.speckit/context/architecture.md`  
- `.speckit/context/tech-stack.md` (if available)

---

## 3. `/speckit.health`

**Purpose**  
Assess project or feature health based on SpecKit artifacts and workflow status.

**Inputs**
- Optional scope flag to restrict to a specific feature.

**Outputs**
- `.speckit/health/report.json` (machine-readable).  
- `.speckit/health/report.md` (human-readable).  
- Exit code semantics (example):
  - `0`: healthy or minor warnings.  
  - `1`: warnings present.  
  - `2`: critical issues.

---

## 4. `/speckit.branch` (Phase 2)

**Purpose**  
Create and switch to a git branch corresponding to a feature or a task.

**Inputs**
- Reference file: feature spec (`specs/<feature-id>/spec.md`) or task file (`tasks/Txxx-*.md`).
- Optional flags (e.g., `--dry-run`).

**Outputs**
- New local branch created if not present (e.g., `feature/06-ai-extensions` or `task/T123-short-name`).  
- Terminal output describing the intended git commands and final branch.

**Constraints**
- Must **not** push or modify remotes.  
- Must fail gracefully if run outside a git repo.

---

## 5. `/speckit.sync.patch` (Phase 2)

**Purpose**  
Extend `/speckit.sync` to emit git patch files and suggested commit messages instead of directly applying changes.

**Inputs**
- Proposed spec/plan/task edits from `/speckit.sync` workflows.

**Outputs**
- `.speckit/patches/<timestamp>-spec-sync.patch`  
- `.speckit/patches/<timestamp>.msg` (suggested commit message)

**Constraints**
- Must not apply patches or create commits automatically.

---

## 6. `/speckit.dataset` (Phase 2)

**Purpose**  
Export design-time training data derived from SpecKit artifacts.

**Inputs**
- Completed or stable features with `spec.md`, `plan.md`, and `tasks.md`.

**Outputs**
- `ai/datasets/speckit-dataset.jsonl`  
- Each line contains:
  - `input_type` (e.g., `spec_to_plan`, `plan_to_tasks`).  
  - `input` content (or reference).  
  - `output` content.  
  - `meta` with project/feature identifiers and timestamps.

**Constraints**
- Default scope: **design-time markdown only**.  
- Code inclusion (if ever supported) must be an explicit, opt-in configuration.

---

## 7. `/speckit.agentize`

**Purpose**  
Generate an agent-ready bundle from an existing context pack.

**Inputs**
- Existing `.speckit/context/context.json` and related markdown files.

**Outputs**
- `.speckit/agent/config.json`  
- `.speckit/agent/chunks/*.md`  
- `.speckit/agent/instructions/*.md`

**Behavior**
- Splits long files into smaller chunks with stable IDs.  
- Tags chunks by role (`spec`, `plan`, `tasks`, `architecture`, `decision`, etc.).

---

## 8. `/speckit.graph` (Phase 2)

**Purpose**  
Visualize task dependencies as a graph.

**Inputs**
- `tasks.md` with IDs, phases, and dependency markers (e.g., `depends_on: T001, T002`).

**Outputs**
- `docs/diagrams/tasks-graph.mmd` (Mermaid).  
- Optionally `docs/diagrams/tasks-graph.svg` if a renderer is available.

---

## 9. `/speckit.hint`

**Purpose**  
Provide pre-implementation guidance for a specific task.

**Inputs**
- A single task file `tasks/Txxx-*.md`.  
- Supporting context: `plan.md`, `architecture.md`, and tech stack info.

**Outputs**
- `tasks/Txxx-hints.md` containing:
  - Suggested API/file shapes.  
  - Data models and interfaces.  
  - Edge cases and testing ideas.

---

## 10. `/speckit.release`

**Purpose**  
Generate release notes from SpecKit artifacts and, optionally, git history.

**Inputs**
- Completed tasks and updated specs/plans for delivered features.  
- Repository `VERSION` file (primary version source).  
- Optional CLI parameter to override version.

**Outputs**
- `docs/release-notes/<version>.md`  
- Optionally `docs/release-notes/latest.md` alias/symlink.

**Behavior**
- Organizes notes into sections: Summary, New Features, Improvements, Fixes, Breaking Changes, Known Issues, Links.

---

## Exit Code and Error Handling Guidelines

- Use `0` for successful command completion.  
- Use non-zero codes when:
  - Required inputs are missing (e.g., `spec.md` absent).  
  - Health checks detect critical issues.  
  - Underlying git operations fail.  
- Error messages should:
  - Indicate what went wrong.  
  - Suggest the next recommended `/speckit.*` command or file to inspect.

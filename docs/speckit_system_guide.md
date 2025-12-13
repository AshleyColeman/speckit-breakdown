# SpecKit System Guide

This document serves as both a **Technical Reference** for the available SpecKit commands and a **Beginner's Guide** ("Dummies Guide") on how to use the system end-to-end.

---

## 🛠 Part 1: Technical Reference & Command Inventory

Below is the list of all commands, categorized by their subsystem.

### 🐍 Python CLI Commands (New Architecture)

These commands are built as robust Python applications with strict validation and error handling.

#### `/speckit.db.prepare`
**Description**: Bootstraps the local data store from documentation files. 
*   **Topological Sort**: Automatically calculates the visual **Step Order** (Column 1, 2, 3...) for every task based on dependencies.
*   **Validation**: Enforces strict rules (e.g., "Ready" tasks must have "Completed" dependencies).
*   **Parallelism**: Correctly groups parallel siblings (A -> B, A -> C) into the same execution step.

**Usage**:
```bash
/speckit.db.prepare [OPTIONS]
```

**Local Python invocation (outside Windsurf)**:
```bash
pip install -r requirements-dev.txt
python -m src.cli.main speckit.db.prepare --dry-run
```

**Support tiers**:
- SQLite: Stable (default).
- PostgreSQL: Experimental and disabled by default. Requires `--db-url` and `--enable-experimental-postgres`.

**Schema expectations**:
- SQLite: Initializes required tables automatically.
- PostgreSQL: Requires a pre-existing schema contract. In particular, `tasks.metadata` must be `json/jsonb` and support `metadata->>'code'` lookups.

**Key Options**:
- `--dry-run`: Preview changes without writing to DB.
- `--force`: Overwrite existing entities if they have changed.
- `--project <ID>`: Only process a specific project.
- `--skip-task-runs`, `--skip-ai-jobs`: Skip identifying implied secondary entities.

**Status**: ✅ **Created & Verified** (Phases 1-6 complete).

---

### 🤖 Agent/Workflow Commands (Markdown Workflows)

These commands are defined as AI agent workflows (in `.claude/commands` or `workflows/`).

| Command | Status | Description |
| :--- | :--- | :--- |
| `/speckit.agentize` | ✅ Created | Converts a task into a prompt for a specialized sub-agent. |
| `/speckit.analyze` | ✅ Created | Analyzes code or docs for patterns/issues. |
| `/speckit.arch` | ✅ Created | Generates high-level architecture diagrams/docs. |
| `/speckit.breakdown` | ✅ Created | Decomposing large projects into features. |
| `/speckit.bundle` | ✅ Created | Bundles project context for export/analysis. |
| `/speckit.checklist` | ✅ Created | Verifies project health against a standard checklist. |
| `/speckit.clarify` | ✅ Created | Interactively refines specifications. |
| `/speckit.constitution` | ✅ Created | Defines core rules/principles for the agent. |
| `/speckit.health` | ✅ Created | Checks project health metrics. |
| `/speckit.implement` | ✅ Created | Core loop for writing code from tasks. |
| `/speckit.orchestrate` | ✅ Created | High-level coordination of multiple agents/tasks. |
| `/speckit.parallelize` | ✅ Created | Identifies tasks that can run in parallel. |
| `/speckit.plan` | ✅ Created | Generates technical implementation plans. |
| `/speckit.planreview` | ✅ Created | AI review of an implementation plan. |
| `/speckit.specify` | ✅ Created | Generates detailed specifications (PRDs). |
| `/speckit.specreview` | ✅ Created | AI review of a specification. |
| `/speckit.sync` | ✅ Created | Synchronizes state between docs and code (lightweight). |
| `/speckit.tasks` | ✅ Created | Generates `tasks.md` from a plan. |
| `/speckit.taskreview` | ✅ Created | Reviews task lists for completeness/ordering. |
| `/speckit.techadvisor` | ✅ Created | Recommends technology choices (stack selection). |
| `/speckit.techstack` | ✅ Created | Documents the chosen tech stack. |
| `/speckit.testgen` | ✅ Created | Generates test cases from specs. |

### 🛡️ Integrated Core Services

The following capabilities are fully active and integrated into the core pipeline (powering `/speckit.db.prepare`):

- **Database transactions**: `db.prepare` persistence runs inside a single database transaction via the configured gateway. If an error occurs, the gateway rolls back the transaction to keep the store consistent.
- **Validation Reporting**: A robust reporting engine flags circular dependencies, duplicates, and schema violations with actionable CLI error messages before data is committed.

---

## 🤖 Part 3: Advanced AI Workflows (The "Context" Layer)

These commands (introduced in Spec 006) enable **Agentic Development** by treating the project context as a portable data asset.

### `/speckit.arch`
**Goal**: Technical Architecture Snapshot.
*   **Action**: Synthesizes `spec.md`, `plan.md`, and `tasks.md` into a single high-level `architecture.md`.
*   **Use Code**: Runs `build-architecture.sh`.
*   **When to use**: After `/speckit.plan`, before `/speckit.implement`.

### `/speckit.checklist`
**Goal**: "Unit Tests for Requirements".
*   **Action**: Generates a quality checklist (e.g. `checklists/ux.md`) to verify your requirements are clear, complete, and testable.
*   **Use Code**: Runs `check-prerequisites.sh`.
*   **When to use**: After `/speckit.specify`, before `/speckit.plan`.

### `/speckit.bundle`
**Goal**: Context Packing for Agents.
*   **Action**: Gathers all design artifacts (spec, plan, tasks, research, arch) into a standardized JSON "Context Pack" (`.speckit/context/`).
*   **Use Code**: Runs `build-context-pack.sh`.
*   **When to use**: Before handing off complex tasks to an autonomous agent; automatically creates the "Brain" for the agent.

### `/speckit.health`
**Goal**: Project Health Monitor.
*   **Action**: Runs a physical consistency check (missing docs, outdated plans) and reports status.
*   **Use Code**: Runs `health-check.sh`.
*   **When to use**: Periodically during `implement` phase or before a release.

---

## 📚 Recommended Usage Order

1.  **Planning Phase**:
    *   `breakdown` -> `specify` -> `clarify` -> **`checklist`** (Quality Gate)
    *   `specreview` -> `techadvisor` -> `plan` -> `planreview`
    *   **`arch`** (System Design) -> `tasks` -> `taskreview`

2.  **Bootstrap Phase**:
    *   `db.prepare` (Populate System DB)
    *   **`bundle`** (Export Context for Agents)

3.  **Execution Phase**:
    *   `implement` (Iterative coding)
    *   `testgen` (Create tests)
    *   **`health`** (Quality Assurance)
    *   `sync` (Docs <-> Code reconciliation)

---

## 🐢 Part 2: The "Dummies" Guide (How to Use SpecKit)

SpecKit is an AI-driven software development lifecycle tool. It helps you go from a vague idea to working code through a structured series of steps.

### The Golden Workflow

Follow these steps in order to build a feature or project.

#### 1. Start with an Idea (`/speckit.breakdown`)
**Goal**: Turn a high-level project plan into a list of specific features.
*   **Input**: A project brief or `project.md`.
*   **Action**: Runs an analysis to identify distinct features (e.g., "User Login", "Payment Processing").
*   **Output**: A list of feature files in `docs/features/`.

#### 2. Define the Requirement (`/speckit.specify`)
**Goal**: Describe *what* a single feature should do.
*   **Input**: A feature name or description.
*   **Action**: Generates a detailed "Product Requirement Document" (PRD) for that feature.
*   **Output**: A detailed markdown file in `specs/`.

#### 3. Refine & Verify (`/speckit.clarify` & `/speckit.checklist`)
**Goal**: Remove ambiguity and ensure quality.
*   **Input**: The specification from step 2.
*   **Action**: The AI asks clarifying questions, then generates a "Unit Test" checklist for your requirements.
*   **Output**: A sharper spec and a `checklists/domain.md` validation file.

#### 4. Create Tech & Arch Plans (`/speckit.plan` & `/speckit.arch`)
**Goal**: Decide *how* to build it and document the system design.
*   **Input**: The clarified specification.
*   **Action**: Designs the component architecture (`arch`) and detailed implementation steps (`plan`).
*   **Output**: `architecture.md` and `implementation_plan.md`.

#### 5. Break into Tasks (`/speckit.tasks`)
**Goal**: Create a checklist.
*   **Input**: The Implementation Plan.
*   **Action**: Generates a detailed checklist of tiny, actionable coding tasks (e.g., "Create user table", "Add login route").
*   **Output**: A `tasks.md` file.

#### 6. System Sync (`/speckit.db.prepare` & `/speckit.bundle`)
**Goal**: **Sync your docs to the system brain.**
*   **Input**: The markdown files created in previous steps.
*   **Action**: Persists data to the local DB and creates a "Context Pack" for autonomous agents.
*   **Output**: `db.sqlite` populated and `.speckit/context/` generated.

#### 7. Write & Monitor (`/speckit.implement` & `/speckit.health`)
**Goal**: Build it and keep it healthy.
*   **Input**: The `tasks.md` file and database context.
*   **Action**: An AI agent writes the code. You run health checks to identify missing docs or drift.
*   **Output**: Actual source code and health reports.

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

### ❌ Missing / Not Yet Created

The following commands might be planned or implied but are not explicitly found in the latest command set:

- **Rollback Manager CLI**: While `db.prepare` handles some transactional logic, a dedicated `/speckit.db.rollback` command is not yet exposed.
- **Advanced Reporting**: A command like `/speckit.report` to generate PDF/HTML summaries of the DB state is not yet created.

---

## 📚 Recommended Usage Order

1.  **Planning Phase**:
    *   `breakdown` -> `specify` -> `clarify` -> `specreview`
    *   `techadvisor` -> `techstack` -> `arch`
    *   `plan` -> `planreview` -> `tasks` -> `taskreview`

2.  **Bootstrap Phase**:
    *   `db.prepare` (Populate System DB)

3.  **Execution Phase**:
    *   `implement` (Iterative coding)
    *   `testgen` (Create tests)
    *   `health` / `checklist` (Quality Assurance)

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

#### 3. Refine the Spec (`/speckit.clarify`)
**Goal**: Remove ambiguity.
*   **Input**: The specification from step 2.
*   **Action**: The AI asks you questions to clarify edge cases and business rules.
*   **Output**: An updated, much sharper specification.

#### 4. Create a Tech Plan (`/speckit.plan`)
**Goal**: Decide *how* to build it.
*   **Input**: The clarified specification.
*   **Action**: Designs the database schema, API endpoints, and component architecture.
*   **Output**: An Implementation Plan (usually `implementation_plan.md`).

#### 5. Break into Tasks (`/speckit.tasks`)
**Goal**: Create a checklist.
*   **Input**: The Implementation Plan.
*   **Action**: Generates a detailed checklist of tiny, actionable coding tasks (e.g., "Create user table", "Add login route").
*   **Output**: A `tasks.md` file.

#### 6. Load into Database (`/speckit.db.prepare`)
**Goal**: **Sync your docs to the system brain.**
*   **Input**: The markdown files created in previous steps.
*   **Action**: Parses all projects, features, specs, and tasks and saves them into a structured SQLite database. This allows the system to understand relationships and dependencies programmatically.
*   **Output**: `db.sqlite` populated with your project data.

#### 7. Write Code (`/speckit.implement`)
**Goal**: Build it!
*   **Input**: The `tasks.md` file and the database context.
*   **Action**: An AI agent picks up tasks one by one and writes the code.
*   **Output**: Actual source code in your project.

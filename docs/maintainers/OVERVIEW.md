# SpecKit Breakdown – Project Overview

This document is the **maintainer/author overview** for the `speckit-breakdown` repository. It explains:

- **What** SpecKit Breakdown is and how it fits into SpecKit
- **How** end users install and use it
- **How this repo is structured** (commands, scripts, workflows, specs)
- **How the 001–005 feature specs map to real commands and scripts**

If you are trying to understand or extend this tool tonight, start here.

---

## 1. What SpecKit Breakdown Is

SpecKit Breakdown is an add‑on to the **SpecKit** workflow system that does one core job:

> **Take a single high‑level project specification (one big doc) and turn it into a set of well‑scoped features and execution workflows that SpecKit can process.**

At a high level:

- Input: a project spec markdown file like `docs/PROJECT_SPEC.md`
- Command: `/speckit.breakdown docs/PROJECT_SPEC.md`
- Output in the user project:
  - `docs/project-breakdown.md` – master breakdown & roadmap
  - `docs/features/feature-XX-*.md` – 5–12 individual feature files
  - (optionally) `docs/features/quick-start.sh` – helper commands

From there, the user feeds each feature into the **core SpecKit pipeline**:

- `/speckit.specify` → `/speckit.clarify` → `/speckit.plan` → `/speckit.tasks` → `/speckit.orchestrate` → `python -m src.cli.main` → `/speckit.implement`

This repo also ships a set of **advanced SpecKit commands** (001–005) that add review, orchestration, tech‑advice, and advanced SDD flows on top of that core pipeline.

---

## 2. Top‑Level Docs & How to Read Them

Root documentation files and what they’re for:

- **`README.md`**  
  High‑level public documentation for SpecKit Breakdown.  
  Explains what the tool does, prerequisites, installation, usage, examples, and troubleshooting.

- **`docs/guides/QUICK_START.md`**  
  5‑minute, **do‑this‑now** guide.  
  Ideal for someone who already has SpecKit installed and just wants the shortest path: install → create `PROJECT_SPEC.md` → run `/speckit.breakdown`.

- **`docs/guides/GET_STARTED.md`**  
  Narrative “you already have a working tool in `/tmp/speckit-breakdown`” and how to test it locally, then publish it to GitHub.  
  Focus: helping you turn a local prototype into a shareable tool.

- **`docs/guides/HOW_TO_USE.md`**  
  More detailed explanation of **how users will install and use** the tool once it’s published.  
  Includes the end‑user experience, outputs, and why it’s better than manual breakdown.

- **`docs/guides/INSTALLATION_GUIDE.md`**  
  Post‑publish installation guide pointing at the GitHub repo (`https://github.com/AshleyColeman/speckit-breakdown`).  
  Shows the canonical one‑liner installer and the shape of generated files.

- **`docs/maintainers/SETUP_AS_REPO.md`**  
  Step‑by‑step instructions to:
  - Create the GitHub repo
  - Push this code
  - Fix URLs in `install.sh`
  - Add examples & optional packaging/CI
  
  This is your **publisher/maintainer guide**.

- **`LICENSE`**  
  MIT License for the project.

- **`VERSION`**  
  Plain text version file (e.g. `1.0.0`).

- **`templates/project-spec.template.md`**  
  Canonical template users should copy as `docs/PROJECT_SPEC.md` in their own projects.  
  Defines structure: Overview, Business Objectives, Target Users, Features, Tech Requirements, Success Criteria, Constraints, etc.

- **`examples/nextjs-admin-panel/`**  
  A full worked example of running SpecKit Breakdown on a large Next.js admin panel spec.  
  Contains:
  - `PROJECT_SPEC.md` – original spec
  - `nextjs-admin-project-breakdown.md` – generated breakdown
  - `features/feature-XX-*.md` – 12 feature files + `quick-start.sh`

---

## 3. End‑to‑End User Flow (Consumer Project)

This is the **happy path** for someone using `speckit-breakdown` in a separate project.

### 3.1 Prerequisites

**Critical**: Users must have the official SpecKit system installed before using SpecKit Breakdown. This is a two-step installation process:

1. **Step 1**: Install official SpecKit from `github/spec-kit`
2. **Step 2**: Install SpecKit Breakdown enhancement from this repo

The tool will check for existing SpecKit workflows and guide users if they're missing.

### 3.2 Install SpecKit Breakdown

From within the **user’s project root**:

- **Interactive installer (recommended)** – from `install.sh` (as described in `INSTALLATION_GUIDE.md`):
  - **Verifies official SpecKit is installed** (checks for `.windsurf/workflows/` with core commands)
  - If SpecKit is missing, provides clear instructions to install from `github/spec-kit` first
  - Detects IDE/editor (Windsurf / Cursor / VS Code / Other)
  - Ensures `.windsurf/workflows/` exists (or creates it)
  - Copies or downloads `speckit.breakdown.md` into `.windsurf/workflows/`
  - Creates `docs/features/`
  - For Cursor/VS Code, writes `.cursorrules` so the assistant knows how to execute the workflow

- **Local testing (for you as author)** – from `scripts/install/install-local.sh` (see `docs/guides/GET_STARTED.md` / `docs/guides/HOW_TO_USE.md`):
  - Use when you have a local clone (e.g. `/tmp/speckit-breakdown`) and want to test in a project without going through GitHub.

### 3.3 Author a Project Spec

In the user project (not here):

1. Copy the template from this repo:
   - `templates/project-spec.template.md` → `docs/PROJECT_SPEC.md`
2. Fill it out with:
   - Overview, business objectives, target users
   - Features & requirements (even if they are messy / mixed together)
   - Tech stack, constraints, success criteria

### 3.4 Run the Breakdown

In the user project:

```bash
/speckit.breakdown docs/PROJECT_SPEC.md
```

This uses the workflow defined in this repo’s **`workflows/speckit.breakdown.md`** (installed into the user’s `.windsurf/workflows/`).

Results (in the user project):

- `docs/project-breakdown.md` – master view
- `docs/features/feature-01-*.md` .. `feature-0N-*.md` – individual features
- Optional `docs/features/quick-start.sh` – helper script with the core SpecKit commands in dependency order

### 3.5 Feed Features into Core SpecKit

For each `feature-XX-*.md` in the user project, the intended downstream flow is:

1. `/speckit.specify` – turn feature description into a structured spec
2. `/speckit.clarify` – interactive ambiguity resolution
3. `/speckit.plan` – implementation plan for the feature
4. `/speckit.tasks` – concrete `tasks.md`
5. `/speckit.orchestrate` – convert `tasks.md` into ordered task docs
6. `python -m src.cli.main` (or `/speckit.db.prepare`) – sync to the system brain
7. `/speckit.implement` – implementation; later enhanced by features 003 and 005 below

The rest of this document explains the **extra commands** and architecture that sit around that core flow.

---

## 4. Internal Architecture – High‑Level

This repo contains three main building blocks:

1. **Workflows** – what the IDE sees as slash commands
2. **Claude command prompts** – `.claude/commands/speckit.*.md` (SpecKit + breakdown extras)
3. **Bash scripts** – `.specify/scripts/bash/*.sh` that perform structured file operations

### 4.1 Workflows

- **`workflows/speckit.breakdown.md`**  
  The primary workflow that implements `/speckit.breakdown` in user projects.  
  When installed, it is copied to the consumer project’s `.windsurf/workflows/` directory.

### 4.2 SpecKit & Breakdown Commands (`.claude/commands`)

Current commands in `.claude/commands/`:

- **Core SpecKit commands** (shipped here for convenience):
  - `speckit.specify.md`
  - `speckit.clarify.md`
  - `speckit.plan.md`
  - `speckit.tasks.md`
  - `speckit.implement.md`
  - `speckit.analyze.md`
  - `speckit.checklist.md`
  - `speckit.constitution.md`
  - `speckit.taskstoissues.md`

- **Review & QA commands** (from 001 & 002):
  - `speckit.specreview.md` – review `spec.md` against the constitution and quality heuristics (001).
  - `speckit.taskreview.md` – review `tasks.md`/`plan.md` for granularity and dependency sanity (001).
  - `speckit.planreview.md` – validate `plan.md` against `spec.md` and `constitution.md` (002).

- **Task orchestration & agentic workflow** (from 001–003):
  - `speckit.parallelize.md` – break large tasks into parallelizable sub‑tasks and update `tasks.md` (001).
  - `speckit.taskfile.md` – generate a dedicated `tasks/Txxx-*.md` context file for a specific task (002).
  - `speckit.orchestrate.md` – convert `tasks.md` into ordered, parallelizable task files in `tasks/` (003).

- **Tech guidance** (from 002 & 004):
  - `speckit.techstack.md` – analyze `plan.md` and suggest concrete libraries/versions consistent with the project (002).
  - `speckit.techadvisor.md` – interactive “solutions architect” that helps choose a tech stack from `spec.md` + constitution (004).

- **Advanced SDD (Test‑First, Self‑Healing, Sync)** (from 005):
  - `speckit.testgen.md` – generate tests for a task before implementation (TDD) (005).
  - `speckit.sync.md` – compare code vs `spec.md` and propose spec updates (reverse sync) (005).
  - `speckit.implement.md` – updated to:
    - Accept task files as input (e.g. `tasks/01-T001-*.md`)
    - Run tests and perform a limited **test‑fix‑retry loop** (005, and also referenced by 003).

### 4.3 Bash Scripts (`.specify/scripts/bash`)

Current scripts in `.specify/scripts/bash/`:

- **`build-agent-bundle.sh`**
  Converts a Context Pack (generated by `build-context-pack.sh`) into an agent-ready bundle (`.speckit/agent`) containing chunked markdown and role-specific instructions.

- **`build-architecture.sh`**
  Resolves architectural paths and context for the `/speckit.arch` workflow. Outputs JSON or text describing where architecture docs live.

- **`build-context-pack.sh`**
  Gathers all design-time artifacts (spec, plan, tasks, research, etc.) into a standardized "Context Pack" (`.speckit/context`) for downstream processing.

- **`check-prerequisites.sh`**  
  Shared helper to verify environment/prereqs for SpecKit/Breakdown (e.g., tools, directories).  
  Used by other scripts and/or workflows as a guard.

- **`common.sh`**  
  Shared Bash utilities used by the other scripts.

- **`create-new-feature.sh`**  
  Core SpecKit script for creating a new feature skeleton.  
  Feature 001 includes a **bug fix** to silence noisy `git fetch` output that was causing parsing issues.

- **`create-task-doc.sh`**  
  Introduced in Feature 002.  
  Given a task ID, title, and context, it creates a markdown file in `tasks/` (e.g. `tasks/T001-title.md`) with a standard template.

- **`expand-tasks.sh`**  
  Introduced in Feature 001.  
  Intended workflow:
  - Accept parent task ID and JSON list of new sub‑tasks
  - Find the highest existing task ID in `tasks.md`
  - Assign new IDs (e.g. `T051`, `T052` …)
  - Insert them after the parent task in `tasks.md`
  - Optionally mark parent as expanded/completed

- **`health-check.sh`**
  Runs a "physical" check on the feature directory, ensuring critical files (spec, plan, tasks) exist. Generates a JSON/Markdown report in `.speckit/health`.

- **`orchestrate-tasks.sh`**  
  Introduced in Feature 003.  
  Batch command that takes a JSON description of tasks (IDs, order, parallel flags) and generates orchestrated task files, typically by calling `create-task-doc.sh` under the hood and injecting YAML frontmatter.

- **`setup-plan.sh`**  
  Part of the broader SpecKit tooling; used to bootstrap or adjust `plan.md` for a feature.

- **`update-agent-context.sh`**  
  Maintains “active technologies” and other context for agents.  
  Referenced by tech‑stack related commands (e.g. `speckit.techstack.md`) to keep library recommendations aligned with the project.

---

## 5. Design Specs 001–005 and Their Implementations

The `specs/` directory contains **design‑time artifacts** for five major capability areas. Each folder follows the same pattern:

```text
specs/
  001-workflow-enhancements/
  002-additional-commands/
  003-task-orchestration/
  004-tech-advisor/
  005-advanced-sdd/

# Within each:
- spec.md   # Feature specification (user stories, requirements)
- plan.md   # Implementation plan
- tasks.md  # Delivery tasks (all currently checked as completed)
```

Below is a mapping from each spec to the concrete commands/scripts it introduced.

### 5.1 001 – Workflow Enhancements

**Goal:** Improve **quality** and **velocity** of the SpecKit workflow via review commands and parallel task expansion.

- **Docs:**
  - `specs/001-workflow-enhancements/spec.md`
  - `specs/001-workflow-enhancements/plan.md`
  - `specs/001-workflow-enhancements/tasks.md` (all tasks marked `[x]`)

- **New / Modified Commands:**
  - `.claude/commands/speckit.specreview.md`
    - Reviews `spec.md` against `.specify/memory/constitution.md` and general quality heuristics.
  - `.claude/commands/speckit.taskreview.md`
    - Reviews `tasks.md` + `plan.md` for formatting, dependency sanity, and actionable granularity.
  - `.claude/commands/speckit.parallelize.md`
    - Generates sub‑tasks for a chosen task and drives insertion via `expand-tasks.sh`.

- **New / Modified Scripts:**
  - `.specify/scripts/bash/expand-tasks.sh`
    - Implements the actual mutation logic on `tasks.md` when parallelizing.
  - `.specify/scripts/bash/create-new-feature.sh`
    - Patched to silence `git fetch` output and avoid numeric parsing errors.

### 5.2 002 – Additional Commands

**Goal:** Add deeper review and isolation tools: plan review, tech‑stack analysis, and per‑task documentation.

- **Docs:**
  - `specs/002-additional-commands/spec.md`
  - `specs/002-additional-commands/plan.md`
  - `specs/002-additional-commands/tasks.md` (all tasks marked `[x]`)

- **New Commands:**
  - `.claude/commands/speckit.planreview.md`
    - Cross‑checks `plan.md` against `spec.md` and the constitution; produces a gap analysis.
  - `.claude/commands/speckit.techstack.md`
    - Reads `plan.md` and active project context to suggest concrete libraries/versions for “NEEDS CLARIFICATION” items.
  - `.claude/commands/speckit.taskfile.md`
    - Given a Task ID, assembles context from `tasks.md` + `spec.md` + `plan.md` and generates a dedicated `tasks/Txxx-*.md` file.

- **New Script:**
  - `.specify/scripts/bash/create-task-doc.sh`
    - Creates the `tasks/` file with consistent naming (`Txxx-title.md`) and a standard markdown template.

### 5.3 003 – Task Orchestration

**Goal:** Turn a flat `tasks.md` into an **executable schedule** of task files with explicit order and parallelization metadata; enable `/speckit.implement` to consume those files.

- **Docs:**
  - `specs/003-task-orchestration/spec.md`
  - `specs/003-task-orchestration/plan.md`
  - `specs/003-task-orchestration/tasks.md` (all tasks marked `[x]`)

- **New Command:**
  - `.claude/commands/speckit.orchestrate.md`
    - Reads `tasks.md` + `spec.md` + `plan.md`, parses phases and `[P]` markers, assigns sequence numbers, and produces a JSON payload for the script.

- **New Script:**
  - `.specify/scripts/bash/orchestrate-tasks.sh`
    - Consumes the JSON produced by `/speckit.orchestrate` and generates task files in `tasks/` with YAML frontmatter:
      - `id`: Task ID (e.g. `T001`)
      - `order`: integer sequence
      - `parallel`: boolean

- **Updated Command:**
  - `.claude/commands/speckit.implement.md`
    - Enhanced to accept an explicit task file path (e.g. `tasks/01-T001-*.md`) and focus on that file as the primary context.

### 5.4 004 – Tech Advisor

**Goal:** Provide an interactive **tech stack advisor** to bridge from spec → architecture.

- **Docs:**
  - `specs/004-tech-advisor/spec.md`
  - `specs/004-tech-advisor/plan.md`
  - `specs/004-tech-advisor/tasks.md` (single task marked `[x]`)

- **New Command:**
  - `.claude/commands/speckit.techadvisor.md`
    - Reads `spec.md` + `constitution.md`.
    - Acts as a “Senior Tech Lead” that:
      - Analyzes functional & non‑functional requirements
      - Asks clarifying questions (SQL vs NoSQL, state management, etc.)
      - Outputs a cohesive **Recommended Stack** block suitable to paste into `plan.md`.

### 5.5 005 – Advanced SDD (TestGen, Self‑Healing, Sync)

**Goal:** Move closer to “Holy Grail” SDD: test‑first generation, self‑healing implementation loops, and spec ↔ code synchronization.

- **Docs:**
  - `specs/005-advanced-sdd/spec.md`
  - `specs/005-advanced-sdd/plan.md`
  - `specs/005-advanced-sdd/tasks.md` (all tasks marked `[x]`)

- **New Commands:**
  - `.claude/commands/speckit.testgen.md`
    - Given a task file + `plan.md`, generates test files that express the requirements, but do **not** implement the feature.
  - `.claude/commands/speckit.sync.md`
    - Reads `spec.md` and selected code files, then produces a “spec diff” report and suggested edits to keep documentation aligned.

- **Updated Command:**
  - `.claude/commands/speckit.implement.md`
    - Enriched with an explicit **Test‑Fix‑Retry loop**:
      - Run tests (e.g. `npm test` or equivalent from `plan.md`)
      - If they fail, read the error output
      - Attempt a fix and re‑run tests
      - Limit number of automatic retries (e.g. 3) to avoid infinite loops

---

## 6. Canonical Combined Workflow (Inside a Feature Repo)

To understand how everything fits together, here is a **conceptual end‑to‑end flow** once this repo’s tooling is installed into a project:

1. **Project Spec → Features**
   - Author `docs/PROJECT_SPEC.md` using `templates/project-spec.template.md`.
   - Run `/speckit.breakdown docs/PROJECT_SPEC.md`.
   - Inspect `docs/project-breakdown.md` and `docs/features/feature-XX-*.md`.

2. **Per‑Feature Spec & Plan**
   - For each feature file:
     - `/speckit.specify` → creates `spec.md` for the feature.
     - `/speckit.specreview` → optional spec quality/constitution review.
     - `/speckit.plan` → implementation plan.
     - `/speckit.planreview` → verify plan covers spec and respects constitution.
     - `/speckit.techadvisor` → optional interactive stack selection for the feature.
     - `/speckit.techstack` → align tech choices with project‑wide stack.

3. **Tasks & Parallelization**
   - `/speckit.tasks` → produce `tasks.md` for the feature.
   - `/speckit.taskreview` → validate task format, dependencies, and granularity.
   - `/speckit.parallelize` → split large or repetitive tasks into parallel sub‑tasks via `expand-tasks.sh`.

4. **Task Files & Orchestration**
   - `/speckit.taskfile` → generate focused `tasks/Txxx-*.md` files for individual tasks.
   - `/speckit.orchestrate` → turn `tasks.md` into an ordered set of files with explicit `order` + `parallel` metadata, using `orchestrate-tasks.sh`.
   - `/speckit.db.prepare` → **Sync to System DB**. Parses all tasks, verifies dependencies, calculates Topological Step Order, and persists to the database.

5. **The Persistence Phase (Critical Order)**
   To maintain referential integrity (foreign keys), the `SqliteGateway` and `PostgresGateway` insert data in a strict hierarchy. If you are extending the schema, you **must** follow this order:
   1.  `projects` (Root)
   2.  `features` (Belongs to project)
   3.  `specs` (Belongs to feature)
   4.  `tasks` (Belongs to feature/spec)
   5.  `task_dependencies` (Links two tasks)
   6.  `task_runs` (Operational state for a task)
   7.  `ai_jobs` (Derived work for an agent)

   > [!IMPORTANT]
   > The `step_order` (calculated during this phase) is strictly non-zero. It maps direct dependencies into sequential "steps" (Column 1, 2, 3...) while allowing independent tasks to share a step for parallel execution.

7. **Storage Backends & Data Flow**
   The system uses a **Gateway Pattern** to decouple the orchestration logic from the physical database. 
   - **Local Storage**: By default, data is saved to `.speckit/db.sqlite`.
   - **External Storage**: Using the `--db-url` flag with a `postgresql://` prefix redirects all persistence to an external PostgreSQL instance.
   - **Data Flow**:
     1. `BootstrapOrchestrator` generates DTOs from Markdown.
     2. `DataStoreGateway` detects the connection string type.
     3. `PostgresGateway` (or `SqliteGateway`) executes the SQL upserts in the [Critical Order](#5-the-persistence-phase-critical-order) defined above.
   
   For detailed setup instructions for external databases, refer to the [db_prepare.md Reference](../cli/db_prepare.md).

8. **Tests, Implementation, Sync**
   - `/speckit.testgen <task-file>` → generate tests for the task using stack info from `plan.md`.
   - `/speckit.implement <task-file>` → implement that task with a test‑fix‑retry loop.
   - `/speckit.sync` → periodically reconcile code against `spec.md` and propose documentation updates.

This is the **intended final shape** of the SpecKit + Breakdown + Advanced SDD ecosystem represented by this repo.

---

## 7. Quick Repo Map (For Navigation)

At a glance, the most important paths:

- **Root docs**
  - `README.md` – main documentation
  - `docs/guides/QUICK_START.md` – 5‑minute guide
  - `docs/guides/GET_STARTED.md` / `docs/guides/HOW_TO_USE.md` – local prototype vs shareable tool usage
  - `docs/guides/INSTALLATION_GUIDE.md` / `docs/maintainers/SETUP_AS_REPO.md` – installation + publishing
  - `LICENSE`, `VERSION`

- **Workflows & templates**
  - `workflows/speckit.breakdown.md` – main breakdown workflow definition
  - `templates/project-spec.template.md` – spec template users copy into their projects

- **Examples**
  - `examples/nextjs-admin-panel/` – full breakdown example (Next.js admin panel)

- **SpecKit extension specs**
  - `specs/001-workflow-enhancements/{spec,plan,tasks}.md`
  - `specs/002-additional-commands/{spec,plan,tasks}.md`
  - `specs/003-task-orchestration/{spec,plan,tasks}.md`
  - `specs/004-tech-advisor/{spec,plan,tasks}.md`
  - `specs/005-advanced-sdd/{spec,plan,tasks}.md`

- **Commands & scripts**
  - `.claude/commands/speckit.*.md` – all SpecKit & Breakdown commands
  - `.specify/scripts/bash/*.sh` – helper scripts referenced in the 001–005 plans

This overview should give you enough context to **reason about the whole system, find the right file quickly, and safely extend it** without re‑reading every individual spec tonight.

# Quickstart: SpecKit Advanced AI Extensions (006-ai-extensions)

This quickstart explains how to use the new `/speckit.*` commands introduced by the `006-ai-extensions` feature once the underlying prompts, scripts, and workflows are implemented.

> **Prerequisites**
>
> - You are inside a SpecKit-enabled repository (with `specs/`, `.specify/`, `.claude/`, and workflows configured).
> - You have already run the base SpecKit workflow for at least one feature:
>   - `/speckit.breakdown`
>   - `/speckit.specify`
>   - `/speckit.specreview`
>   - `/speckit.plan` and `/speckit.planreview`
>   - `/speckit.tasks` and `/speckit.taskreview`

---

## 1. Generate an Architecture Snapshot

**Command** (editor workflow or CLI):

- `/speckit.arch` (scoped to project or feature)

**What it does**
- Reads `spec.md`, `plan.md`, and any existing `architecture.md` for the chosen scope.  
- Produces or updates an `architecture.md` file:
  - Project-level: `docs/architecture.md`  
  - Feature-level: `specs/<feature-id>/architecture.md`

**When to run**
- After the feature spec and plan are stable.  
- Before generating context packs or asking agents to design/implement.

---

## 2. Build a Context Pack for Agents

**Command**:

- `/speckit.bundle`

**What it does**
- Gathers the key design-time artifacts for the current project or feature:
  - `spec.md`, `plan.md`, `tasks.md`, `architecture.md`, constitution, and related markdown.  
- Produces `.speckit/context/` contents such as:
  - `context.json`
  - `spec.md`, `plan.md`, `tasks.md`, `architecture.md`, `tech-stack.md` (if present)

**When to run**
- After the initial design flow is complete or updated.  
- Before running external automation or RAG-style agents.

---

## 3. Run a Project or Feature Health Check

**Command**:

- `/speckit.health`

**What it does**
- Scans the current repository (or feature) for SpecKit consistency and completeness:
  - Missing or stale `spec.md`, `plan.md`, `tasks.md`.  
  - Orchestrated vs. non-orchestrated tasks.  
  - Optional checks for test generation or sync recency.
- Writes reports to:
  - `.speckit/health/report.json`
  - `.speckit/health/report.md`

**When to run**
- Before starting a large implementation session.  
- Before cutting a release.

---

## 4. Enable Agent-Ready Mode

**Command**:

- `/speckit.agentize`

**What it does**
- Consumes the context pack.  
- Splits large artifacts into small, labelled chunks (e.g., 1–2k tokens).  
- Creates `.speckit/agent/`:
  - `config.json`  
  - `chunks/*.md`  
  - `instructions/*.md` for different agent roles.

**When to run**
- Before connecting the repo to a multi-agent system or RAG index.  
- After significant changes to specs/plans/tasks.

---

## 5. Export a Dataset

**Command**:

- `/speckit.dataset`

**What it does**
- Collects design-time mappings for training or evaluation:
  - `spec.md → plan.md`
  - `plan.md → tasks.md`
- Writes JSONL to:
  - `ai/datasets/speckit-dataset.jsonl`

**When to run**
- After a feature (or project) has gone through a full SpecKit cycle and is in a reasonably stable state.

---

## 6. Visualize Task Dependencies

**Command**:

- `/speckit.graph`

**What it does**
- Parses `tasks.md` for IDs, phases, and `depends_on` markers.  
- Produces:
  - `docs/diagrams/tasks-graph.mmd` (Mermaid)
  - Optionally, `docs/diagrams/tasks-graph.svg` if a Mermaid renderer is available.

**When to run**
- During planning review.  
- Before parallelizing implementation with `/speckit.parallelize`.

---

## 7. Get Implementation Hints Per Task

**Command**:

- `/speckit.hint` (run while viewing a specific task file)

**What it does**
- Reads a single `tasks/Txxx-*.md` plus related `plan.md`, `architecture.md`, and tech stack info.  
- Produces `tasks/Txxx-hints.md` with:
  - Suggested API or function shapes.  
  - Suggested file paths and modules.  
  - Edge cases and testing ideas.

**When to run**
- Before implementing a task.  
- When handing off a task to another developer or an AI agent.

---

## 8. Generate Release Notes

**Command**:

- `/speckit.release`

**What it does**
- Reads:
  - Completed tasks (checked items in `tasks.md` and task files).  
  - Updated specs/plans for delivered features.  
  - Optionally recent git commits.  
- Uses the repository `VERSION` file (with optional override) to determine the target version.  
- Writes:
  - `docs/release-notes/<version>.md`
  - Optionally `docs/release-notes/latest.md` alias.

**When to run**
- As part of the release flow, after updating tasks and before tagging or deploying.

---

## 9. Typical Flow With Advanced AI Extensions

1. Use the existing SpecKit design flow to reach a stable feature spec, plan, and tasks.  
2. Run `/speckit.arch` to capture architecture.  
3. Run `/speckit.bundle` to build a context pack.  
4. Run `/speckit.health` to confirm project/feature health.  
5. Run `/speckit.agentize` to prepare an agent bundle.  
6. For individual tasks, use `/speckit.hint` before implementation.  
7. After delivery, run `/speckit.dataset` to update datasets and `/speckit.release` to publish release notes.

## Single-Feature Walkthrough (Example)

This example shows how a solo dev would run the advanced commands for a single
feature once `spec.md`, `plan.md`, and `tasks.md` are in place.

### Example setup

- You are working on feature `006-ai-extensions` (or any other feature with
  completed design docs).
- The repository already has the advanced scripts and workflows installed.

From the editor, run the following Slash commands in order:

1. **Generate architecture**
   - Run: `/speckit.arch`
   - Scope: current feature (default)
   - Expected output:
     - `specs/006-ai-extensions/architecture.md` (architecture snapshot for the feature)

2. **Build a context pack**
   - Run: `/speckit.bundle`
   - Scope: current feature
   - Expected outputs under `.speckit/context/`:
     - `context.json`
     - `spec.md`, `plan.md`, `tasks.md`, `architecture.md`
     - `research.md`, `data-model.md`, `quickstart.md` (if present)

3. **Run a health check**
   - Run: `/speckit.health`
   - Scope: current feature
   - Expected outputs under `.speckit/health/`:
     - `report.json` (machine-readable status and issues)
     - `report.md` (human-readable summary)

4. **Generate an agent bundle**
   - Run: `/speckit.agentize`
   - Scope: current feature
   - Expected outputs under `.speckit/agent/`:
     - `config.json` (bundle metadata)
     - `chunks/*.md` (chunked design artifacts)
     - `instructions/*.md` (role-specific instructions, e.g. planner, implementer, reviewer)

After this sequence, you have:

- A dedicated architecture snapshot for the feature.  
- A context pack (`.speckit/context/`) suitable for RAG or downstream tools.  
- A health snapshot (`.speckit/health/`) indicating whether design artifacts are complete.  
- An agent bundle (`.speckit/agent/`) that downstream agents or automation can consume.

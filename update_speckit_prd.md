A. PRD – SpecKit Advanced Extensions
A1. Summary

We extend SpecKit + Breakdown + 001–005 with extra commands and scripts that:

Give a clear architecture snapshot per feature/project.

Build AI-friendly context packs.

Run a project health check.

Manage git branches per feature/task.

Turn spec/code diffs into git patches.

Build training datasets from specs/plans/tasks.

Prepare “agent-ready” bundles for RAG / AI agents.

Visualise task dependency graphs.

Provide an implementation buddy (pre-implement hints).

Generate release notes automatically.

These are additional SpecKit commands (/speckit.*) plus supporting bash scripts and folder structures, consistent with how 001–005 work.

A2. Problem Statement

Right now, SpecKit + Breakdown:

Breaks big specs into features.

Turns features into specs, plans, tasks, orchestrated task files.

Adds QA, tech guidance, and advanced SDD.

But:

Architecture is often kept in the dev’s head.

Context for AI agents is manual.

Project health is not checked automatically.

git workflow is not integrated with SpecKit.

Documentation/spec updates don’t easily become git patches.

We’re not building reusable training data from this rich process.

There is no standard format for “agent-ready” bundles.

Dependency flows are not visualised.

There’s no pre-implementation “buddy” step.

Release notes still require manual effort.

We want to make this system truly AI-native and workflow-complete.

A3. Goals & Success Criteria
Goals

Reduce friction when using AI agents and n8n with SpecKit.

Make project state visible: architecture, health, dependencies, progress.

Automate boring but critical things: branches, release notes, patches.

Create reusable training datasets from real project flows.

Success Metrics (qualitative)

You can spin up a fully AI-ready project from a spec with minimal manual work.

For any feature, you can quickly answer:

What’s the architecture?

Is the project healthy?

What’s next?

What changed?

n8n and other agents can:

Pull context packs.

Read agent bundles.

Process tasks in parallel.

Suggest or apply safe updates.

A4. Scope
In Scope (Features)

We define ten new capabilities:

F1 – Architecture Snapshot – /speckit.arch

F2 – Context Pack Builder – /speckit.bundle

F3 – Project Health Check – /speckit.health

F4 – Auto-Brancher – /speckit.branch

F5 – Spec Diff → Git Patch – /speckit.sync.patch

F6 – Dataset Builder – /speckit.dataset

F7 – Agent-Ready Mode – /speckit.agentize

F8 – Dependency Tree Visualizer – /speckit.graph

F9 – Implementation Buddy – /speckit.hint

F10 – Release Notes Generator – /speckit.release

Priority / Phasing

Phase 1 (MVP – must have):

F1 – Architecture Snapshot

F2 – Context Pack Builder

F3 – Project Health Check

F7 – Agent-Ready Mode

F9 – Implementation Buddy

F10 – Release Notes Generator

Phase 2 (Advanced / nice-to-have):

F4 – Auto-Brancher

F5 – Spec Diff → Git Patch

F6 – Dataset Builder

F8 – Dependency Tree Visualizer

(See implementation details in Blueprint B4 – each feature maps 1:1.)

A5. Users & Personas

Solo Dev / System Developer (you)

Wants structure, less mental load, more automation.

AI Agents (Claude, Gemini, etc.)

Consume context packs, agent bundles, tasks, and architecture to implement code or docs.

Automation Orchestrator (n8n)

Runs workflows, polls tables, triggers speckit.* commands, processes results.

Team Lead / Reviewer (future)

Wants to see health, architecture, progress, and release notes without opening every file.

A6. Updated Canonical Workflow (High-Level)

This extends existing flow:

Existing (simplified)

PROJECT_SPEC.md

/speckit.breakdown → features

Per feature:

/speckit.specify

/speckit.specreview

/speckit.plan

/speckit.planreview

/speckit.techadvisor / /speckit.techstack

/speckit.tasks

/speckit.taskreview

/speckit.parallelize

/speckit.taskfile

/speckit.orchestrate

/speckit.testgen

/speckit.implement

/speckit.sync

Extended with new steps

Per feature or project:

Architecture Snapshot

/speckit.arch → architecture.md

Context Pack

/speckit.bundle → .speckit/context/context.json + markdown

Agent-Ready Bundle

/speckit.agentize → .speckit/agent/**

Project Health Check

/speckit.health → reports in .speckit/health/

Implementation Buddy (per task)

/speckit.hint tasks/xx-Txxx-*.md

Release Notes

/speckit.release → docs/release-notes/…

Phase 2 extra

/speckit.branch, /speckit.sync.patch, /speckit.dataset, /speckit.graph

(See Blueprint B3 for how these outputs are structured.)

A7. Functional Requirements (by Feature)
F1 – Architecture Snapshot – /speckit.arch

Description
Generate a concise architecture.md capturing the current intended architecture for a project or feature.

Inputs

spec.md (feature or project-level)

plan.md

Optionally: existing architecture.md (for update)

Outputs

docs/architecture.md (project-level) or

features/<feature-id>/architecture.md (feature-level)

Required Content

High-level diagram description (layers, services, UI, DB).

Main modules/components and their responsibilities.

Data flows (API and DB).

External dependencies (APIs, queues, storage).

Constraints and decisions (e.g. React + Next.js + Prisma + Postgres).

Usage

CLI/command: /speckit.arch [scope]

scope could be project or feature:<id>.

Acceptance Criteria

Architecture file exists in expected path.

It references consistent names from spec.md/plan.md.

It is idempotent: running it again updates, doesn’t duplicate.

Implementation reference: see Blueprint B4.1.

F2 – Context Pack Builder – /speckit.bundle

Description
Create a single context JSON pack + markdown files for use by AI agents or n8n.

Inputs

spec.md

plan.md

tasks.md

architecture.md

constitution.md

Any relevant *.md under the feature/project.

Outputs

.speckit/context/context.json

.speckit/context/spec.md

.speckit/context/plan.md

.speckit/context/tasks.md

.speckit/context/architecture.md

.speckit/context/tech-stack.md (if available)

JSON Structure (high level)
(Details in Blueprint B3.1)

{
  "projectName": "string",
  "featureId": "string|null",
  "files": [
    { "path": "docs/spec.md", "role": "spec", "content": "..." },
    { "path": "docs/plan.md", "role": "plan", "content": "..." }
  ],
  "constraints": [],
  "techStack": [],
  "version": "1.0.0"
}


Acceptance Criteria

Pack contains all required files, no empty mandatory sections.

Size stays reasonable (e.g. can be limited using simple truncation with markers).

Implementation reference: see Blueprint B4.2.

F3 – Project Health Check – /speckit.health

Description
Run consistency and completeness checks across a project or feature.

Checks Examples

Missing spec.md, plan.md, tasks.md.

tasks.md exists but no tasks/*.md after orchestration.

testgen not run for tasks (optional).

sync not run recently (based on timestamps).

Spec vs code drift markers (if available).

Outputs

.speckit/health/report.json

.speckit/health/report.md

Optional status summary printed in terminal.

Report Fields (high level)

status: healthy | warning | critical

issues: list of { id, severity, message, file, suggestion }

Acceptance Criteria

Running /speckit.health in a valid project always produces a report.

When serious issues exist, status should be critical or warning.

Implementation reference: see Blueprint B4.3.

F4 – Auto-Brancher – /speckit.branch (Phase 2)

Description
Create and switch to a git branch based on feature or task.

Inputs

Feature: features/feature-XX-*.md

Task: tasks/Txxx-*.md

Branch Naming

Feature: feature/XX-short-name

Task: task/Txxx-short-name

Outputs

New git branch (if not exists).

Commit (optional flag) of current planning/spec structure.

Requirements

Detect git repo (fail gracefully if not).

Never auto-push; local only.

Option to be “dry-run” (just display intended commands).

Implementation reference: Blueprint B4.4.

F5 – Spec Diff → Git Patch – /speckit.sync.patch (Phase 2)

Description
Extend /speckit.sync to output git patch files and suggested commit messages.

Inputs

Existing spec.md, plan.md, etc.

Proposed edits from /speckit.sync.

Outputs

.speckit/patches/<timestamp>-spec-sync.patch

Suggested commit message (.speckit/patches/<timestamp>.msg)

Acceptance Criteria

Patch applies cleanly in a typical case.

No direct git commit or git apply without explicit user choice.

Implementation reference: Blueprint B4.5.

F6 – Dataset Builder – /speckit.dataset (Phase 2)

Description
Create JSONL training data from existing SpecKit project.

Mappings Examples

Input: spec.md → Output: plan.md.

Input: plan.md → Output: tasks.md.

Input: tasks/Txxx-*.md → Output: implementation snippets (future).

Outputs

ai/datasets/speckit-dataset.jsonl

Optionally separate files per mapping (spec→plan, plan→tasks, etc.)

Acceptance Criteria

JSONL is valid.

Each line includes input, output, and metadata fields.

Implementation reference: Blueprint B4.6.

F7 – Agent-Ready Mode – /speckit.agentize

Description
Produce a bundle optimised for RAG / AI agents.

Inputs

Existing context pack (/speckit.bundle outputs).

feature or project root.

Outputs

.speckit/agent/config.json

.speckit/agent/chunks/*.md (small, chunked pieces)

.speckit/agent/instructions/*.md (prompt templates for different agent roles)

Capabilities

Split long files into smaller chunks with stable IDs.

Tag chunks by role (spec, plan, task, code, decision).

Provide simple metadata suitable for indexing.

Acceptance Criteria

Agent bundle can be used by external tools without needing to know internal file layout.

Implementation reference: Blueprint B4.7.

F8 – Dependency Tree Visualizer – /speckit.graph (Phase 2)

Description
Create a visual representation of tasks.md dependencies.

Inputs

tasks.md (with phases and/or markers like [P] or depends_on:).

Outputs

docs/diagrams/tasks-graph.mmd (Mermaid)

docs/diagrams/tasks-graph.svg (optional)

Acceptance Criteria

Graph shows ordering and parallel groups clearly.

Implementation reference: Blueprint B4.8.

F9 – Implementation Buddy – /speckit.hint

Description
Pre-implementation helper that analyses a task file and plan, then outputs:

Suggested API shapes.

Suggested file paths.

Data models / interfaces.

Edge cases to consider.

Test ideas.

Inputs

tasks/Txxx-*.md

plan.md

architecture.md

tech-stack info.

Outputs

tasks/Txxx-hints.md

Console summary of key points.

Acceptance Criteria

Output is specific to the task, not generic fluff.

References actual tech stack and architecture.

Implementation reference: Blueprint B4.9.

F10 – Release Notes Generator – /speckit.release

Description
Generate release notes from:

tasks completed (tasks.md, git history, tasks checked [x]).

specs updated.

features delivered.

Outputs

docs/release-notes/<version>.md

Optional docs/release-notes/latest.md symlink/alias.

Release Notes Sections

Summary

New Features

Improvements

Fixes

Breaking Changes

Known Issues

Links (specs, features)

Acceptance Criteria

Content uses real project terms (features/tasks), not generic.

Can be run repeatedly with same version (idempotent).

Implementation reference: Blueprint B4.10.

A8. Non-Functional Requirements

Performance – Commands should run in seconds for normal-sized projects.

DX – Clear error messages if files missing or repo not initialised.

Consistency – Use same naming patterns as existing speckit.* commands.

Safety – No automatic destructive git actions (no force pushes, etc.).

Portability – Scripts must work on typical Posix shells (Linux/macOS).

A9. Risks & Mitigations

Risk: Complexity creep.

Mitigation: Keep each feature small and modular (see Blueprint structure).

Risk: Git-related failures.

Mitigation: Dry-run mode, clear messages, no auto-apply patches.

Risk: Bloated context packs.

Mitigation: Chunking, limits, truncation markers, agent config.

B. Technical Blueprint

Now: how to build this inside the existing repo, with file paths.

B1. Architectural Overview

We extend the existing structure:

.claude/commands/speckit.*.md – prompt-level logic.

.specify/scripts/bash/*.sh – file + system operations.

workflows/speckit.*.md – IDE/editor slash workflows that glue it together.

specs/00x-*/{spec,plan,tasks}.md – design-time specs.

We add:

New commands: speckit.arch, speckit.bundle, etc.

New scripts: build-context-pack.sh, health-check.sh, etc.

New spec folder(s) for these capabilities (e.g. 006-ai-extensions or one per group, optional).

B2. Repo Structure Additions (Summary)
.claude/
  commands/
    speckit.arch.md
    speckit.bundle.md
    speckit.health.md
    speckit.branch.md
    speckit.sync.patch.md
    speckit.dataset.md
    speckit.agentize.md
    speckit.graph.md
    speckit.hint.md
    speckit.release.md

.specify/
  scripts/
    bash/
      build-architecture.sh
      build-context-pack.sh
      health-check.sh
      git-auto-branch.sh
      git-generate-patch.sh
      build-dataset.sh
      build-agent-bundle.sh
      build-dependency-graph.sh
      build-implementation-hints.sh
      build-release-notes.sh

workflows/
  speckit.arch.md
  speckit.bundle.md
  speckit.health.md
  speckit.branch.md
  speckit.sync.patch.md
  speckit.dataset.md
  speckit.agentize.md
  speckit.graph.md
  speckit.hint.md
  speckit.release.md

.speckit/
  context/
    context.json
    spec.md
    plan.md
    tasks.md
    architecture.md
    tech-stack.md
  health/
    report.json
    report.md
  agent/
    config.json
    chunks/
      chunk-001-spec-overview.md
      ...
    instructions/
      planner.md
      implementer.md
      reviewer.md
  patches/
    2025-12-04T1900-spec-sync.patch
    2025-12-04T1900.msg

ai/
  datasets/
    speckit-dataset.jsonl

docs/
  architecture.md            # project-level
  diagrams/
    tasks-graph.mmd
    tasks-graph.svg
  release-notes/
    0.1.0.md
    latest.md                # optional

B3. Data Structures (Key Schemas)
B3.1 Context Pack – .speckit/context/context.json
{
  "projectName": "string",
  "featureId": "string|null",
  "version": "1.0.0",
  "generatedAt": "ISO-8601",
  "files": [
    {
      "path": "docs/spec.md",
      "role": "spec",
      "title": "Feature Spec: X",
      "content": "full markdown or truncated with markers"
    },
    {
      "path": "docs/plan.md",
      "role": "plan",
      "title": "Implementation Plan",
      "content": "..."
    }
  ],
  "techStack": [
    { "name": "Next.js", "version": "15", "category": "frontend" }
  ],
  "constraints": [
    "Must use PostgreSQL",
    "Edge runtime only"
  ]
}

B3.2 Health Report – .speckit/health/report.json
{
  "status": "healthy | warning | critical",
  "generatedAt": "ISO-8601",
  "projectName": "string",
  "issues": [
    {
      "id": "MISSING_SPEC",
      "severity": "critical",
      "message": "spec.md is missing for feature X",
      "file": "features/feature-01-api/spec.md",
      "suggestion": "Run /speckit.specify for this feature."
    }
  ]
}

B3.3 Agent Config – .speckit/agent/config.json
{
  "projectName": "string",
  "featureId": "string|null",
  "version": "1.0.0",
  "chunksPath": ".speckit/agent/chunks",
  "instructionsPath": ".speckit/agent/instructions",
  "chunkSchemaVersion": "1.0.0"
}


Each chunk:

<!-- chunk-id: spec-001 -->
<!-- role: spec -->
<!-- source: docs/spec.md -->
# Feature Overview
...

B3.4 Dataset JSONL – ai/datasets/speckit-dataset.jsonl

Each line:

{
  "input_type": "spec_to_plan",
  "input": "markdown from spec.md",
  "output": "markdown from plan.md",
  "meta": {
    "projectName": "string",
    "featureId": "feature-01",
    "timestamp": "ISO-8601"
  }
}

B4. Per-Feature Implementation Blueprint
B4.1 F1 – Architecture Snapshot

Files

.claude/commands/speckit.arch.md

.specify/scripts/bash/build-architecture.sh

workflows/speckit.arch.md

Workflow

User runs /speckit.arch in editor.

workflows/speckit.arch.md:

Collects context (project root, target scope).

Calls Claude with speckit.arch.md prompt + relevant files.

Claude returns the architecture.md content.

Script build-architecture.sh writes to:

docs/architecture.md (project) or

features/<feature-id>/architecture.md.

Command prompt responsibilities

Read spec.md, plan.md, existing architecture.md if present.

Produce updated architecture doc with sections:

High-level overview

Components

Data flow

Tech stack

Decisions

B4.2 F2 – Context Pack Builder

Files

.claude/commands/speckit.bundle.md

.specify/scripts/bash/build-context-pack.sh

workflows/speckit.bundle.md

Workflow

/speckit.bundle triggered.

build-context-pack.sh:

Gathers relevant files (spec, plan, tasks, architecture, constitution).

(Optional) trims very large files.

Claude command speckit.bundle.md:

Normalises metadata (names, roles, titles).

Builds context.json with clear structure.

Script writes final .speckit/context/**.

B4.3 F3 – Project Health Check

Files

.claude/commands/speckit.health.md

.specify/scripts/bash/health-check.sh

workflows/speckit.health.md

Workflow

Script health-check.sh scans:

Required file existence.

Timestamps.

Simple patterns (e.g. tasks with [ ] but never orchestrated).

Script builds a machine-friendly report (JSON).

Claude command speckit.health.md:

Turns JSON into human-readable report.md, adds suggestions.

B4.4 F4 – Auto-Brancher

Files

.claude/commands/speckit.branch.md (lightweight – mostly UX)

.specify/scripts/bash/git-auto-branch.sh

workflows/speckit.branch.md

Workflow

User selects feature or task; runs /speckit.branch.

Command suggests branch name (or reads it from file frontmatter later).

git-auto-branch.sh:

Checks if repository.

Checks if branch exists.

Creates + checks out branch using git checkout -b.

Claude responds with confirmation and recommendations (e.g. “commit your specs now”).

B4.5 F5 – Spec Diff → Git Patch

Files

.claude/commands/speckit.sync.patch.md

.specify/scripts/bash/git-generate-patch.sh

workflows/speckit.sync.patch.md

Workflow

Claude computes proposed edits (similar to /speckit.sync).

Instead of directly applying, it outputs “before/after” blocks or unified diff suggestions.

git-generate-patch.sh:

Applies changes to temp files.

Runs git diff to generate patch file under .speckit/patches.

Prompt suggests commit message stored as .msg file.

B4.6 F6 – Dataset Builder

Files

.claude/commands/speckit.dataset.md

.specify/scripts/bash/build-dataset.sh

workflows/speckit.dataset.md

Workflow

build-dataset.sh collects file pairs:

spec.md ↔ plan.md

plan.md ↔ tasks.md

Claude (speckit.dataset.md) cleans up text, ensures no junk (like timestamps if not needed).

Script writes JSONL into ai/datasets/.

B4.7 F7 – Agent-Ready Mode

Files

.claude/commands/speckit.agentize.md

.specify/scripts/bash/build-agent-bundle.sh

workflows/speckit.agentize.md

Workflow

build-agent-bundle.sh:

Reads context pack.

Splits large content into chunks (e.g. 1–2k tokens each).

Adds simple metadata in HTML comments.

Claude command speckit.agentize.md:

Optionally refines chunk labels and generates instructions for:

Planner agent

Implementer agent

Reviewer agent

Final .speckit/agent/** tree written.

B4.8 F8 – Dependency Tree Visualizer

Files

.claude/commands/speckit.graph.md

.specify/scripts/bash/build-dependency-graph.sh

workflows/speckit.graph.md

Workflow

Script parses tasks.md lines:

IDs

phases

dependency annotations (depends_on: T001, T002).

Claude command speckit.graph.md converts JSON representation → Mermaid graph text.

Script writes docs/diagrams/tasks-graph.mmd.

If mmdc or similar available, generate tasks-graph.svg.

B4.9 F9 – Implementation Buddy

Files

.claude/commands/speckit.hint.md

.specify/scripts/bash/build-implementation-hints.sh

workflows/speckit.hint.md

Workflow

Script build-implementation-hints.sh:

Reads one tasks/Txxx-*.md.

Extracts related context (spec.md, plan.md, architecture.md).

Claude speckit.hint.md:

Produces specific implementation hints:

API endpoints

function signatures

file paths

edge cases

test ideas

Script writes tasks/Txxx-hints.md.

B4.10 F10 – Release Notes Generator

Files

.claude/commands/speckit.release.md

.specify/scripts/bash/build-release-notes.sh

workflows/speckit.release.md

Workflow

Script collects:

Completed tasks ([x] markers).

Feature names.

Optionally recent git commits.

Claude command speckit.release.md:

Groups changes:

Features

Improvements

Fixes

Breaking changes

Writes markdown release notes.

Script writes docs/release-notes/<version>.md.

Version may come from VERSION file or parameter.

B5. Integration with Existing 001–005

001–003 – Already handle workflow, parallelisation, and orchestration.

New features reuse tasks.md and task files generated there.

004 (Tech Advisor) – Feeds into:

Architecture snapshot (/speckit.arch) definitions.

Implementation hints (/speckit.hint) to suggest libraries and patterns.

005 (Advanced SDD) – Together with:

/speckit.testgen and /speckit.implement,

New commands will:

Provide extra context (/speckit.bundle, /speckit.agentize).

Build training data from successful runs (/speckit.dataset).

Keep documentation aligned (/speckit.sync.patch).

B6. Extensibility Notes

Each new feature is modular:

One command, one script, one workflow.

New specs for these could live under e.g.:

specs/
  006-ai-extensions/
    spec.md
    plan.md
    tasks.md


Future additions:

Multi-project rollups (/speckit.portfolio.health).

Per-agent configurations (different bundles for different roles).
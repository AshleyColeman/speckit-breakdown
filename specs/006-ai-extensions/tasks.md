---

description: "Task list for 006-ai-extensions (SpecKit Advanced AI Extensions)"
---

# Tasks: SpecKit Advanced AI Extensions

**Input**: Design documents from `/specs/006-ai-extensions/`  
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: Dedicated test tasks are **optional** and not required by this feature; basic scripted integration checks for the new scripts are covered as implementation tasks.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., [US1], [US2], [US3])
- All tasks include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare repository structure and documentation to support advanced SpecKit extensions.

- [X] T001 Create base directories `.speckit/context`, `.speckit/health`, `.speckit/agent/chunks`, `.speckit/agent/instructions`, `.speckit/patches`, `ai/datasets`, `docs/diagrams`, and `docs/release-notes` at repository root.
- [X] T002 [P] Document the advanced extensions versioning policy in the root `VERSION` file based on `specs/006-ai-extensions/research.md`.
- [X] T003 [P] Add a short section to `QUICK_START.md` pointing to `specs/006-ai-extensions/quickstart.md` and explaining when to use the advanced `/speckit.*` commands.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core contracts and shared helpers required before any user story work.

**⚠️ CRITICAL**: No user story work should begin until this phase is complete.

- [X] T004 Finalize CLI contracts for all new commands in `specs/006-ai-extensions/contracts/cli-commands.md` (ensure inputs/outputs/exit codes match the spec and research decisions).
- [X] T005 [P] Finalize the conceptual data model in `specs/006-ai-extensions/data-model.md` for context packs, health reports, agent bundles, datasets, and release notes.
- [X] T006 [P] Extend `.specify/scripts/bash/common.sh` with shared helpers for logging, JSON output, safe git detection, and repo-root resolution to be reused by all new `build-*` scripts.
- [X] T007 Update `.specify/scripts/bash/check-prerequisites.sh` so it validates the presence of `.speckit/` subdirectories, `ai/datasets`, `docs/diagrams`, `docs/release-notes`, and `VERSION` before running advanced `/speckit.*` commands.

**Checkpoint**: Foundational contracts and helpers are ready – user story implementation can now begin.

---

## Phase 3: User Story 1 – Solo dev generates AI-ready context (Priority: P1) 🎯 MVP

**Goal**: A solo developer can generate architecture, context pack, health report, and agent bundle for a single feature using a small set of `/speckit.*` commands.

**Independent Test**: Starting from an existing SpecKit feature with `spec.md`, `plan.md`, and `tasks.md`, running the documented commands produces up-to-date `architecture.md`, context pack, health report, and agent bundle without manual file assembly.

### Implementation for User Story 1

- [X] T008 [P] [US1] Create prompt definition `.claude/commands/speckit.arch.md` that reads `spec.md`, `plan.md`, and existing `architecture.md` (if present) and outputs an updated architecture document with sections from the spec.
- [X] T009 [P] [US1] Implement `.specify/scripts/bash/build-architecture.sh` to call `speckit.arch` and write `docs/architecture.md` for project scope or `specs/<feature-id>/architecture.md` for feature scope.
- [X] T010 [P] [US1] Create workflow `workflows/speckit.arch.md` wiring the `/speckit.arch` slash command to `.specify/scripts/bash/build-architecture.sh` with appropriate scope arguments.

- [X] T011 [P] [US1] Create prompt definition `.claude/commands/speckit.bundle.md` to normalize context-pack metadata and roles for `spec.md`, `plan.md`, `tasks.md`, `architecture.md`, and related files.
- [X] T012 [P] [US1] Implement `.specify/scripts/bash/build-context-pack.sh` to gather design-time markdown and write `.speckit/context/context.json` plus `.speckit/context/spec.md`, `plan.md`, `tasks.md`, `architecture.md`, `tech-stack.md`.
- [X] T013 [P] [US1] Create workflow `workflows/speckit.bundle.md` wiring `/speckit.bundle` to `.specify/scripts/bash/build-context-pack.sh` for project or feature scope.

- [X] T014 [P] [US1] Create prompt definition `.claude/commands/speckit.health.md` to transform a JSON health summary into a readable markdown report with suggestions.
- [X] T015 [P] [US1] Implement `.specify/scripts/bash/health-check.sh` to scan for missing or stale `spec.md`, `plan.md`, `tasks.md`, orchestrated tasks, and sync recency, writing `.speckit/health/report.json` and `.speckit/health/report.md`.
- [X] T016 [P] [US1] Create workflow `workflows/speckit.health.md` wiring `/speckit.health` to `.specify/scripts/bash/health-check.sh` and displaying a summary in the editor.

- [X] T017 [P] [US1] Create prompt definition `.claude/commands/speckit.agentize.md` to label and refine chunk metadata and agent instructions based on the context pack.
- [X] T018 [P] [US1] Implement `.specify/scripts/bash/build-agent-bundle.sh` to consume `.speckit/context/context.json` and write `.speckit/agent/config.json`, `.speckit/agent/chunks/*.md`, and `.speckit/agent/instructions/*.md`.
- [X] T019 [P] [US1] Create workflow `workflows/speckit.agentize.md` wiring `/speckit.agentize` to `.specify/scripts/bash/build-agent-bundle.sh`.

- [X] T020 [US1] Add a concrete single-feature walkthrough to `specs/006-ai-extensions/quickstart.md` showing the exact `/speckit.arch`, `/speckit.bundle`, `/speckit.health`, and `/speckit.agentize` commands and the expected output paths for a feature.
- [X] T021 [US1] Perform an end-to-end run of `/speckit.arch`, `/speckit.bundle`, `/speckit.health`, and `/speckit.agentize` on one sample feature and record any follow-up decisions or tweaks in `specs/006-ai-extensions/research.md`.

**Checkpoint**: User Story 1 is fully functional; a solo dev can generate AI-ready context for a feature.

---

## Phase 4: User Story 2 – Automation orchestrator monitors health and pulls context (Priority: P2)

**Goal**: An automation workflow (e.g., scheduler or n8n flow) can periodically run health checks and rebuild context packs/agent bundles using non-interactive commands and machine-readable outputs.

**Independent Test**: A simple script or workflow can invoke the advanced commands on a schedule, rely on documented exit codes and JSON summaries, and route outputs to downstream agents without manual intervention.

### Implementation for User Story 2

- [ ] T022 [P] [US2] Extend `.specify/scripts/bash/build-context-pack.sh` to support explicit `--scope` and non-interactive modes, and to optionally print a short JSON summary of generated files to stdout for orchestrators.
- [ ] T023 [P] [US2] Extend `.specify/scripts/bash/health-check.sh` to standardize exit-code semantics and add an optional `--json` flag that prints a compact health summary to stdout while still writing reports to `.speckit/health/`.

- [ ] T024 [P] [US2] Create prompt definition `.claude/commands/speckit.dataset.md` that validates and normalizes training examples for `ai/datasets/speckit-dataset.jsonl` based on `specs/006-ai-extensions/data-model.md`.
- [ ] T025 [P] [US2] Implement `.specify/scripts/bash/build-dataset.sh` to collect `spec.md → plan.md` and `plan.md → tasks.md` pairs and write `ai/datasets/speckit-dataset.jsonl` with `input_type`, `input`, `output`, and `meta` fields.
- [ ] T026 [P] [US2] Create workflow `workflows/speckit.dataset.md` wiring `/speckit.dataset` to `.specify/scripts/bash/build-dataset.sh` with feature or project scope.

- [ ] T027 [P] [US2] Create prompt definition `.claude/commands/speckit.graph.md` to convert a JSON task-dependency model into a Mermaid graph for `docs/diagrams/tasks-graph.mmd`.
- [ ] T028 [P] [US2] Implement `.specify/scripts/bash/build-dependency-graph.sh` to parse `specs/*/tasks.md`, build a JSON representation of task dependencies, call `speckit.graph`, and write `docs/diagrams/tasks-graph.mmd` (and optionally `docs/diagrams/tasks-graph.svg`).
- [ ] T029 [P] [US2] Create workflow `workflows/speckit.graph.md` wiring `/speckit.graph` to `.specify/scripts/bash/build-dependency-graph.sh`.

- [ ] T030 [US2] Document orchestrator-friendly patterns (exit codes, `--json` flags, and recommended scheduling) for `/speckit.health`, `/speckit.bundle`, `/speckit.dataset`, and `/speckit.graph` in `specs/006-ai-extensions/quickstart.md`.

**Checkpoint**: User Story 2 is complete; an orchestrator can run advanced commands non-interactively and consume their outputs.

---

## Phase 5: User Story 3 – Reviewer gets a clear snapshot of what changed (Priority: P3)

**Goal**: A reviewer can quickly understand architecture, health, and delivered changes for a release or feature without opening every SpecKit file manually.

**Independent Test**: For a given release, the reviewer can open release notes, architecture docs, and health reports and confidently answer “What changed?” and “Is the project/feature healthy?” without inspecting raw specs/plans/tasks.

### Implementation for User Story 3

- [ ] T031 [P] [US3] Create prompt definition `.claude/commands/speckit.release.md` that groups completed work into Summary, New Features, Improvements, Fixes, Breaking Changes, Known Issues, and Links sections.
- [ ] T032 [P] [US3] Implement `.specify/scripts/bash/build-release-notes.sh` to read completed tasks, updated specs/plans, and the `VERSION` file, then write `docs/release-notes/<version>.md` and `docs/release-notes/latest.md`.
- [ ] T033 [P] [US3] Create workflow `workflows/speckit.release.md` wiring `/speckit.release` to `.specify/scripts/bash/build-release-notes.sh` and surfacing a concise summary for reviewers.

- [ ] T034 [P] [US3] Create prompt definition `.claude/commands/speckit.sync.patch.md` that outputs suggested spec/code changes as unified diffs instead of applying them directly.
- [ ] T035 [P] [US3] Implement `.specify/scripts/bash/git-generate-patch.sh` to apply proposed changes to temp files, run `git diff` to create `.speckit/patches/<timestamp>-spec-sync.patch`, and write `.speckit/patches/<timestamp>.msg` without applying patches.
- [ ] T036 [P] [US3] Create workflow `workflows/speckit.sync.patch.md` wiring `/speckit.sync.patch` to `.specify/scripts/bash/git-generate-patch.sh` so reviewers can request patch files from within the editor.

- [ ] T037 [US3] Update `docs/architecture.md` and `specs/006-ai-extensions/quickstart.md` with a short “Reviewer checklist” explaining how to combine architecture snapshot, health report, and release notes when reviewing a feature or release.

**Checkpoint**: User Story 3 is complete; reviewers have a single place to see architecture, health, and release notes.

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements and hardening that affect multiple user stories.

- [ ] T038 [P] Add example diagrams or basic rendering workflow for `docs/diagrams/tasks-graph.mmd` (and optional `tasks-graph.svg`) and document how to regenerate them in `docs/diagrams/README.md`.
- [ ] T039 [P] Add an "Advanced Extensions" section to `HOW_TO_USE.md` linking to `specs/006-ai-extensions/quickstart.md` and describing when to adopt the new flows.
- [ ] T040 [P] Create `.ci/speckit-advanced-extensions-checks.sh` to run `shellcheck` on new `.specify/scripts/bash/*` scripts and execute a minimal integration check for `/speckit.arch`, `/speckit.bundle`, `/speckit.health`, and `/speckit.release`.
- [ ] T041 Perform a final end-to-end dry run of all advanced commands against an example SpecKit project and record final learnings or follow-ups in `specs/006-ai-extensions/research.md`.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies – can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion – **blocks all user stories**.
- **User Story 1 (Phase 3, P1)**: Can start after Foundational – no dependencies on other stories; forms the **MVP**.
- **User Story 2 (Phase 4, P2)**: Can start after Foundational – integrates with User Story 1 outputs but should remain independently testable.
- **User Story 3 (Phase 5, P3)**: Can start after Foundational and ideally after core outputs from User Story 1; depends on tasks and health data but remains independently testable.
- **Polish (Final Phase)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Base experience for a solo dev; required before relying on orchestration or reviewer flows.
- **User Story 2 (P2)**: Builds on User Story 1 artifacts (context, health, datasets) but should not break or tightly couple to specific features.
- **User Story 3 (P3)**: Consumes outputs of previous stories (architecture, health, tasks) to generate reviewer-facing views and patches.

### Within Each User Story

- Shared helpers and contracts from Phases 1–2 must be in place before implementing story-specific commands and scripts.
- For each story, implement prompt files (`.claude/commands/*`) and scripts (`.specify/scripts/bash/*`) before wiring workflows and documentation.
- Validate each story’s independent test (from the spec) before moving to the next priority.

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel.
- Foundational tasks T005–T007 marked [P] can run in parallel once T004 is underway.
- In story phases, most `[P]` tasks can be split by file (prompt vs script vs workflow) and worked on concurrently.
- Once Foundational is complete, User Stories 1–3 can proceed in parallel **as long as** their contracts remain consistent and each story is independently testable.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.  
2. Complete Phase 2: Foundational (CRITICAL – blocks all stories).  
3. Complete Phase 3: User Story 1 (solo dev AI-ready context).  
4. **STOP and VALIDATE**: Run the full single-feature flow and confirm architecture, context pack, health report, and agent bundle are correct.  
5. Demo or adopt this flow before adding orchestration or release automation.

### Incremental Delivery

1. Deliver MVP (User Story 1) and validate with one or two real features.  
2. Add User Story 2 to support automation/orchestration, validate in CI or a scheduler.  
3. Add User Story 3 to support reviewers and release notes.  
4. Apply the Polish phase to improve documentation, diagrams, and basic CI checks.

### Parallel Team Strategy

With multiple developers or agents:

1. Team completes Setup + Foundational together.  
2. Assign stories:
   - Developer/Agent A: User Story 1 (P1).  
   - Developer/Agent B: User Story 2 (P2).  
   - Developer/Agent C: User Story 3 (P3).  
3. Coordinate changes to shared scripts (`common.sh`, `check-prerequisites.sh`) via small, well-scoped PRs to avoid conflicts.  
4. Integrate and validate stories one by one, keeping each story independently testable.

---

## Notes

- `[P]` tasks can safely run in parallel because they operate on different files or are logically independent.
- `[USx]` labels map tasks to specific user stories for traceability and MVP planning.
- Each user story should be independently completable and testable against its acceptance criteria from the spec.
- Prefer small, frequent commits per task to keep diffs and patches manageable.
- Avoid vague tasks, shared-file conflicts, and hidden cross-story dependencies that undermine independent delivery.

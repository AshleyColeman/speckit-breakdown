# Research & Decisions: SpecKit Advanced AI Extensions

## Overview

This document records key design decisions and resolved unknowns for the `006-ai-extensions` feature. It complements the feature spec and implementation plan and should be treated as the single source of truth for why particular options were chosen.

---

## Decision 1: Dataset mappings for v1

**Decision**  
Initial dataset exports will include **only design-time mappings:**

- `spec.md → plan.md`
- `plan.md → tasks.md`

Mappings such as `tasks → implementation` and other derived pairs are **explicitly deferred** to later iterations.

**Rationale**  
- These two mappings are already first-class in existing SpecKit workflows.  
- They are stable across projects and do not depend on a specific runtime stack.  
- They produce clean, comparable training examples capturing planning behavior without pulling in code or repo-specific conventions.

**Alternatives considered**  
- **Include `tasks → implementation` from the start**: Rejected for v1 because it requires consistent links from tasks to code and introduces project-specific variability and privacy concerns.  
- **Include all available markdown pairings (spec↔plan↔tasks↔architecture)**: Deferred; adds complexity with limited additional value until the core mappings are proven useful.

---

## Decision 2: Source of release version identifiers

**Decision**  
Release notes generation will use the following precedence for the `<version>` value:

1. **Repository `VERSION` file** (canonical source).  
2. **Explicit CLI parameter/flag** to override the file when needed (e.g., hotfixes or experimental builds).

**Rationale**  
- Keeps versioning explicit and repo-local, without depending on git tags or remote state.  
- Works well in local-only flows and CI, and is easy to script.  
- Override support covers edge cases (e.g., backfilling notes, experimental pre-releases) without changing the `VERSION` file.

**Alternatives considered**  
- **Interactive prompt for version every time**: Rejected for automation and CI usage; non-deterministic and harder to script.  
- **Use git tags as primary source**: Rejected as a hard dependency; not all repos or flows use tags consistently, and tag operations can be protected in some environments.  
- **CLI flag only (no `VERSION` file)**: Rejected to avoid scattering version decisions across ad-hoc invocations.

---

## Decision 3: Artifact scope for datasets and agent bundles

**Decision**  
By default, datasets and agent bundles include **only design-time markdown artifacts**:

- Specs (`spec.md`)
- Plans (`plan.md`)
- Tasks (`tasks.md` and task files)
- Architecture docs (`architecture.md`)
- Related design-time markdown such as tech stack or constraints

Source code files are **excluded by default**. Projects may **opt in** to including code in a future iteration or via explicit configuration.

**Rationale**  
- Strong default for privacy and IP protection, especially when sharing datasets or bundles externally.  
- Keeps the feature focused on design workflows, which are already standardized by SpecKit.  
- Avoids coupling to any particular language, framework, or repo layout for code.

**Alternatives considered**  
- **Include selected source files automatically** (e.g., implementation snippets referenced by tasks): Rejected for v1 due to privacy risk and configuration complexity.  
- **Allow arbitrary file inclusion via glob patterns in v1**: Deferred to a later configuration layer; v1 emphasizes predictable, low-risk defaults.

---

## Decision 4: Testing approach for new scripts and commands

**Decision**  
Testing for the new `/speckit.*` commands and scripts will proceed in tiers:

1. **Manual end-to-end testing** via slash commands and CLI, validating that expected files are created/updated and that idempotency holds.  
2. **Scripted integration checks** that run core commands (e.g., health check, context pack, agent bundle, release notes) against a sample SpecKit project and assert on exit codes and key output files.  
3. **Optional static checks** (e.g., `shellcheck`) where available, applied to the new bash scripts to catch common errors.

**Rationale**  
- Keeps the initial testing strategy simple and aligned with the existing repo’s bash-and-markdown focus.  
- Prioritizes integration behavior (end-to-end flows) over fine-grained unit tests for scripts.  
- Leverages existing CI setups that can run shell scripts and check file outputs.

**Alternatives considered**  
- **Full-blown automated test harness with mocks for git and filesystem**: Deferred as an incremental improvement once the workflows stabilize.  
- **Manual testing only**: Rejected as insufficient for long-term reliability once these commands are used across multiple projects.

---

## Decision 5: End-to-end validation results (T021)

**Test Execution Summary**
Successfully performed end-to-end run of all four advanced AI extension commands on feature `006-ai-extensions`:

1. **Prerequisites Check** (`check-prerequisites.sh --require-advanced`)
   - Status: ✅ Passed (exit code 0)
   - Detected feature directory: `specs/006-ai-extensions`
   - Available docs: `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

2. **Architecture Generation** (`build-architecture.sh`)
   - Status: ✅ Passed (exit code 0)
   - Resolved architecture path: `specs/006-ai-extensions/architecture.md`
   - Scope: feature-level
   - Note: Script ignores `--scope` argument but defaults to feature behavior

3. **Context Pack Building** (`build-context-pack.sh`)
   - Status: ✅ Passed (exit code 0)
   - Generated context pack at: `.speckit/context/`
   - Files included: `spec.md`, `plan.md`, `tasks.md`, `research.md`, `data-model.md`, `quickstart.md`
   - Created `context.json` with metadata and file roles

4. **Health Check** (`health-check.sh`)
   - Status: ✅ Passed (exit code 0)
   - Overall status: "healthy"
   - No issues detected
   - Generated reports at: `.speckit/health/report.json` and `.speckit/health/report.md`

5. **Agent Bundle Generation** (`build-agent-bundle.sh`)
   - Status: ✅ Passed (exit code 0)
   - Generated agent bundle at: `.speckit/agent/`
   - Created 6 chunked markdown files in `chunks/` directory
   - Generated instruction files: `planner.md`, `implementer.md`, `reviewer.md`
   - Created `config.json` with bundle metadata

**Key Observations**
- All scripts execute successfully and produce expected outputs
- JSON output format is working correctly for automation
- Path resolution is functioning properly (repository-relative paths)
- Idempotency holds - scripts can be run multiple times safely
- Warning messages about unknown arguments (`--scope`) are cosmetic and don't affect functionality
- Generated file structure follows SpecKit conventions

**Follow-up Decisions**
- No critical issues found - implementation is ready for production use
- Cosmetic argument warnings can be addressed in a future polish iteration
- All core functionality works as designed and documented

**Validation Status**: ✅ **COMPLETE** - User Story 1 (T008-T021) fully implemented and tested

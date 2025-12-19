# SpecKit Breakdown – Project Overview

> **Version**: 1.0.0  
> **Last Updated**: 2025-12-13

---

## What Is SpecKit Breakdown?

**SpecKit Breakdown** is an add-on to the [SpecKit](https://github.com/github/spec-kit) workflow system that transforms a single, high-level project specification into a set of well-scoped, independent features ready for structured AI-driven development.

**In simple terms**: You write *one* document describing your entire project idea, and SpecKit Breakdown intelligently splits it into 5–12 manageable features—each sized for 1.5–3 weeks of work, with clear user stories, success criteria, and dependencies mapped.

---

## The Problem It Solves

| Before SpecKit Breakdown | After SpecKit Breakdown |
|--------------------------|-------------------------|
| 2–3 days manually analyzing and breaking down a project | 30 minutes to complete breakdown |
| Inconsistent feature sizes | Consistent 1.5–3 week features |
| Missing or unclear dependencies | Dependencies automatically mapped |
| Vague user stories | 3–6 user stories per feature |
| Guesswork estimates | Realistic estimates with complexity ratings |

---

## How It Works

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        SpecKit Breakdown Pipeline                        │
└─────────────────────────────────────────────────────────────────────────┘

     PROJECT_SPEC.md                    /speckit.breakdown
    ┌────────────────┐                 ┌─────────────────────────────────┐
    │ Your high-     │  ────────────►  │ • project-breakdown.md          │
    │ level project  │                 │ • feature-01-auth.md            │
    │ description    │                 │ • feature-02-dashboard.md       │
    │                │                 │ • feature-N-*.md                │
    │ (all features  │                 │ • quick-start.sh                │
    │  mixed together)│                 └─────────────────────────────────┘
    └────────────────┘                           │
                                                 ▼
                                    ┌─────────────────────────────────┐
                                    │  Per-Feature SpecKit Pipeline   │
                                    │                                 │
                                    │  /speckit.specify → spec.md     │
                                    │  /speckit.clarify               │
                                    │  /speckit.plan    → plan.md     │
                                    │  /speckit.tasks   → tasks.md    │
                                    │  /speckit.db.prepare            │
                                    │  /speckit.implement             │
                                    └─────────────────────────────────┘
```

---

## Core Commands

### Primary Command

| Command | Purpose |
|---------|---------|
| `/speckit.breakdown` | Splits a project spec into individual features |

### Planning & Specification

| Command | Purpose |
|---------|---------|
| `/speckit.specify` | Create detailed PRD for a feature |
| `/speckit.clarify` | Interactive ambiguity resolution |
| `/speckit.plan` | Generate implementation plan |
| `/speckit.tasks` | Create task breakdown |

### Review & Quality

| Command | Purpose |
|---------|---------|
| `/speckit.specreview` | Review spec against constitution |
| `/speckit.planreview` | Validate plan covers spec |
| `/speckit.taskreview` | Check task granularity and dependencies |

### Execution

| Command | Purpose |
|---------|---------|
| `/speckit.db.prepare` | Sync docs to system database |
| `/speckit.implement` | AI-driven code generation |
| `/speckit.testgen` | Generate tests before implementation |
| `/speckit.sync` | Reconcile code with spec |

### Advanced

| Command | Purpose |
|---------|---------|
| `/speckit.orchestrate` | Order tasks with parallelization metadata |
| `/speckit.techadvisor` | Interactive tech stack selection |
| `/speckit.techstack` | Document chosen tech stack |
| `/speckit.parallelize` | Split large tasks into parallel sub-tasks |

---

## The Golden Workflow

```
1. /speckit.breakdown     → Break project into features
2. /speckit.specify       → Create detailed spec for each feature
3. /speckit.clarify       → Resolve ambiguities
4. /speckit.plan          → Generate implementation plan
5. /speckit.tasks         → Create task breakdown
6. /speckit.db.prepare    → Sync to system database
7. /speckit.implement     → Execute implementation
```

---

## Output Structure

After running `/speckit.breakdown`, your project will contain:

```
docs/
├── project-breakdown.md           # Master breakdown with all features
└── features/
    ├── feature-01-description.md  # Individual feature files
    ├── feature-02-description.md
    ├── feature-03-description.md
    └── quick-start.sh             # Commands in dependency order
```

Each feature file includes:
- Feature description and scope
- 3–6 user stories
- Success criteria
- Dependencies on other features
- Ready-to-use `/speckit.specify` command

---

## What Makes a Good Feature?

### ✅ Good Feature Characteristics

- **Clear User Value**: Users can see and use it
- **Complete Workflow**: Full user journey start to finish
- **Right Size**: 1.5–3 weeks of work
- **Testable**: Can verify it works independently
- **Minimal Dependencies**: Mostly independent development

### ✅ Good Examples

- "User Authentication System" (complete login/register flow)
- "Product Search & Browse" (full product discovery)
- "Shopping Cart & Checkout" (complete purchase workflow)

### ❌ Bad Examples

- "Database Layer" (too technical, not user-facing)
- "Login Button" (too small, part of larger feature)
- "Entire E-commerce Platform" (too large, needs breakdown)

---

## Installation

### Prerequisites

1. **SpecKit installed** in your project:
   ```bash
   uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
   specify init
   ```

### Quick Install

```bash
curl -fsSL https://raw.githubusercontent.com/AshleyColeman/speckit-breakdown/main/install.sh -o /tmp/sb-install.sh && chmod +x /tmp/sb-install.sh && /tmp/sb-install.sh && rm /tmp/sb-install.sh
```

---

## Repository Structure

```
speckit-breakdown/
├── README.md                          # Main documentation
├── docs/
│   ├── guides/                        # User guides
│   ├── maintainers/                   # Maintainer documentation
│   ├── cli/                           # CLI command reference
│   └── speckit_system_guide.md        # Technical reference
├── workflows/
│   └── speckit.breakdown.md           # Main workflow definition
├── .claude/commands/                  # SpecKit command definitions
├── .specify/scripts/bash/             # Helper scripts
├── templates/                         # User templates
├── examples/                          # Worked examples
└── specs/                             # Feature specifications (001-005)
```

---

## Key Concepts

### SpecKit vs SpecKit Breakdown

- **SpecKit**: The core workflow system (specify → plan → tasks → implement)
- **SpecKit Breakdown**: An add-on that handles the *upstream* problem of breaking a project into features

### The "Brain" (Database)

The `/speckit.db.prepare` command syncs your documentation to a local SQLite database that:
- **Recursive Discovery**: Automatically identifies specs and tasks nested deep within your feature folders.
- **Dependency Validation**: Checks for circular dependencies and missing requirements.
- **Topological Sorting**: Calculates the optimal execution order (Step 1, Step 2, etc.).
- **Parallelization**: Groups independent tasks that can be built simultaneously.
- **Agent Context**: Providing a high-fidelity "Brain" for autonomous coding agents.

### Context Packs

The system can generate "Context Packs" (`.speckit/context/`) that bundle all design artifacts for autonomous AI agents.

---

## Related Documentation

- [System Guide](./speckit_system_guide.md) – Technical reference
- [Quick Start](./guides/QUICK_START.md) – 5-minute guide
- [Installation Guide](./guides/INSTALLATION_GUIDE.md) – Detailed installation
- [Existing Project Guide](./guides/EXISTING_PROJECT_GUIDE.md) – Brownfield integration
- [Maintainer Overview](./maintainers/OVERVIEW.md) – Full architecture details

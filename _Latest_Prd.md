PRD (v2.0) — includes all API endpoints, flows, and operational rules
📘 1. Product Name

Speckit DB Bootstrap Command
(Slash Command: /speckit.db.prepare)

📘 2. Summary

/speckit.db.prepare is a single setup command that reads the entire Speckit project documentation layer (project → features → specs → tasks → dependencies) and converts that into the execution layer (Postgres tables + API-ready state).

This is a foundational command that ensures:

The database is perfectly initialised

All data is consistent, idempotent, and ready for agents

All endpoints can now operate because all core rows exist

n8n workflows can begin processing tasks

AI agents can immediately run jobs

This PRD includes:

Complete requirements

Detailed flows

ALL API endpoints with usage examples

Request & response schemas

Database mapping

Task lifecycle

Error states

Operational constraints

Blueprint for engineers

Blueprint for agents

📘 3. Objectives
🟢 Primary Objective

Automate the initialization of the entire AI pipeline system from documentation → DB → API-ready.

🟡 Secondary Objectives

Standardise project setup

Allow repeatable bootstrapping in multiple environments

Generate a stable “starting state” for agents and workflows

Enable domain-driven design (docs = source of truth)

🔴 Out of Scope

Running migrations

Generating project code

Modifying existing endpoints

Scheduling workflows

📘 4. High-Level Architecture Overview

Markdown Docs → Parser Layer → Validator → API Layer → DB Layer → Logging

/docs
  project.md
  features/*.md
  specs/*.md
  tasks/*.md
  dependencies/*.md

 ↓ parsing

JSON Blueprint Model (P,F,S,T,D)

 ↓ validation

/speckit.db.prepare

 ↓ execution

POST /projects
POST /features
POST /specs
POST /tasks
POST /task-dependencies
POST /task-runs   (auto)
POST /ai-jobs     (optional)

 ↓ ready

Agents + n8n Workflows can run

📘 5. Required API Endpoints (FULL LIST)

All endpoints your slash command will use.

IMPORTANT
These endpoints exist today in your API.
They must be embedded into this PRD so the agents know how to use them.

🔵 5.1 PROJECT ENDPOINTS
Create Project
POST /projects


Body

{
  "name": "Solekka Engine",
  "description": "...",
  "repoDir": "/repo/main-project"
}

Update Project
PATCH /projects/:id

Get Projects
GET /projects

🟢 5.2 FEATURES ENDPOINTS
Create Feature
POST /features


Body

{
  "projectId": "uuid",
  "name": "Image Pipeline",
  "description": "process product images",
  "priority": 1
}

Update Feature
PATCH /features/:id

Get Features for Project
GET /features?projectId=:id

🔶 5.3 SPECS ENDPOINTS
Create Spec
POST /specs

Update Spec
PATCH /specs/:id

List Specs
GET /specs?featureId=:id

🟣 5.4 TASKS ENDPOINTS
Create Task
POST /tasks

Update Task
PATCH /tasks/:id

Query Tasks

Typical used endpoint:

GET /tasks?status=ready&projectId=<projectId>

🔻 5.5 TASK DEPENDENCY ENDPOINTS
Add Dependency
POST /task-dependencies


Body

{
  "predecessorId": "uuid",
  "successorId": "uuid"
}

🟠 5.6 TASK RUNS ENDPOINTS (Creation only)
Create Task Run
POST /task-runs


Body

{
  "taskId": "uuid",
  "phase": "main",
  "status": "running"
}

🔴 5.7 AI JOBS (Optional)
Create Job
POST /ai-jobs


Used only if task has agent_id or tool.

📘 6. Slash Command Specification
Command:
/speckit.db.prepare

Arguments:
Flag	Description
--dry-run	Validate only, no writes
--force	Overwrite mismatches
--skip-ai-jobs	Do not create AI job entries
--skip-task-runs	Do not create task-run rows
--project <id>	Target a specific project
📘 7. Required Behaviour (Functional Requirements)

Below is an expanded system behaviour for engineering + agent consumption.

🔵 7.1 PROJECT BOOTSTRAP
System must:

Parse /docs/project.md

Extract project name, description, repo path

Check if project exists (via GET /projects)

If exists → PATCH

If not → POST

🟢 7.2 FEATURES BOOTSTRAP
For each feature:

Parse header metadata

Check using:

GET /features?projectId=<id>


If exists → PATCH

Else → POST

🔶 7.3 SPECS BOOTSTRAP

For each spec file:

Extract name, version, content

Link to featureId

Use upsert logic

🟣 7.4 TASKS BOOTSTRAP

For each task:

Identify task type

Extract metadata

Extract acceptance criteria (if exists)

Insert using /tasks

🔻 7.5 DEPENDENCIES BOOTSTRAP

For every markdown dependency:

T002 depends on T001


Insert:

POST /task-dependencies


System must validate using circular dependency trigger (already in DB).

🟠 7.6 AUTOMATIC TASK RUN CREATION

Every task gets a new task-run unless:

already exists

run is active

user uses --skip-task-runs

🔴 7.7 AI JOB PRE-SEEDING

Only when:

task has an agent

task has a prompt

or task is type “ai”

Insert:

POST /ai-jobs

📘 8. Validation Rules

The system must validate:

❌ Missing project.md

Stop execution.

❌ Missing feature metadata

Stop execution.

❌ Missing task IDs

Stop execution.

❌ Circular dependencies

Detected via DB trigger.

⚠️ Missing optional fields

Warn and continue.

❌ Duplicate task IDs

Stop execution.

📘 9. Idempotency Logic

Running /speckit.db.prepare repeatedly must not create duplicates.

ID strategy:

Task IDs → stored as metadata inside tasks.metadata.task_code

Feature IDs → stored in features.metadata.feature_code

Spec IDs → stored in specs.metadata.spec_code

On second run → match by these codes, not name

📘 10. Execution Flow (FINAL)
Step 1 — Load all docs
Step 2 — Convert to JSON blueprint
Step 3 — Validate
Step 4 — Upsert project
Step 5 — Upsert features
Step 6 — Upsert specs
Step 7 — Upsert tasks
Step 8 — Insert dependencies
Step 9 — Create task runs
Step 10 — Create AI jobs
Step 11 — Generate execution logs
Step 12 — Command outputs summary
📘 11. Command Output Example
{
  "project": "Solekka Engine",
  "features": 14,
  "specs": 14,
  "tasks": 78,
  "dependencies": 33,
  "taskRuns": 78,
  "aiJobs": 21,
  "warnings": [],
  "status": "BOOTSTRAP_COMPLETE"
}

📘 12. Deliverables For Engineering Team
They must build:

Parser Layer

Validator Layer

API Client Layer

Database Transaction Layer

Logging Layer

CLI wrapper for /speckit.db.prepare

They must test:

Idempotent behaviour

Circular dependency detection

Missing file handling

Large project documents

n8n workflow readiness

📘 13. Deliverables for AI Agent (Feature Breaker)

Agent must break this PRD into:

Features:

DB Bootstrapping Engine

Parser Engine

Validator Engine

API Upsert Engine

Dependency Mapper

IDempotency Manager

AI Job Mapper

Task-Run Initialiser

Logging Engine

Error Manager

CLI Interface

Specs:

One spec per module above

API contract mapping

Data model mapping

Tasks:

Implementation tasks

Unit test tasks

Integration test tasks

Documentation tasks

n8n setup tasks

📘 14. Optional Future Expansions

Auto-generate full API documentation

Auto-generate OpenAPI spec

Auto-generate Figma diagrams

Auto-generate GitHub issues using /speckit.project.sync

Add CI command /speckit.db.migrate
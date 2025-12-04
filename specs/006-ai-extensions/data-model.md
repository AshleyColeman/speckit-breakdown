# Data Model: SpecKit Advanced AI Extensions

This document captures the key conceptual entities introduced or formalized by the `006-ai-extensions` feature and their relationships. It is technology-agnostic and intended for planners, reviewers, and tooling authors.

---

## 1. Architecture Snapshot

**Description**  
Represents the current intended architecture for either a project or a single feature.

**Key Fields**
- `id`: Stable identifier (e.g., `project-architecture` or `feature-006-overview`).
- `scope`: `project` | `feature`.
- `projectName`: Human-readable project name.
- `featureId` (optional): Feature identifier when `scope = feature`.
- `title`: Short title for the architecture document.
- `components`: List of components/modules with roles and boundaries.
- `dataFlows`: High-level flows between components, APIs, and storage.
- `externalDependencies`: External services/APIs, queues, or storage.
- `constraints`: Architectural constraints and key decisions.

---

## 2. Context Pack

**Description**  
Aggregated bundle of design-time artifacts and metadata, optimized for AI agents and automation.

**Key Fields**
- `id`: Unique pack identifier.
- `projectName`: Project name.
- `featureId` (optional): Feature identifier or `null` for project-level packs.
- `version`: Context pack schema version (e.g., `1.0.0`).
- `generatedAt`: ISO-8601 timestamp.
- `files[]`: Collection of referenced artifacts.
  - `path`: Relative path in the repo.
  - `role`: `spec` | `plan` | `tasks` | `architecture` | `tech-stack` | `other`.
  - `title`: Human-readable title.
  - `contentStrategy`: `full` | `truncated` | `summary` (how content was included).
- `techStack[]`: High-level technology descriptors (name, version, category).
- `constraints[]`: Project- or feature-level constraints relevant for planning.

---

## 3. Health Report

**Description**  
Structured assessment of project or feature health based on SpecKit artifacts and workflow status.

**Key Fields**
- `id`: Report identifier.
- `projectName`: Project name.
- `scope`: `project` | `feature`.
- `featureId` (optional): Feature identifier when applicable.
- `generatedAt`: ISO-8601 timestamp.
- `status`: `healthy` | `warning` | `critical`.
- `issues[]`: List of detected issues.
  - `issueId`: Machine-friendly identifier (e.g., `MISSING_SPEC`, `OUT_OF_DATE_PLAN`).
  - `severity`: `info` | `warning` | `critical`.
  - `message`: Human-readable description.
  - `file` (optional): Related file path.
  - `suggestion`: Recommended next action (e.g., run a specific `/speckit.*` command).

---

## 4. Agent Bundle

**Description**  
A chunked, labelled representation of key artifacts for use in retrieval-augmented generation and multi-agent workflows.

**Key Fields**
- `config`:
  - `projectName`
  - `featureId` (optional)
  - `version`: Agent bundle schema version (e.g., `1.0.0`).
  - `chunksPath`: Directory for chunk files.
  - `instructionsPath`: Directory for agent instructions.
- `chunks[]`:
  - `chunkId`: Stable identifier (e.g., `spec-001-overview`).
  - `role`: `spec` | `plan` | `tasks` | `architecture` | `decision` | `code-ref` (if ever opted in).
  - `sourcePath`: Original file path.
  - `title`: Short human-readable label.
  - `order`: Ordering within the source document.
- `instructions[]`:
  - `id`: Identifier (e.g., `planner`, `implementer`, `reviewer`).
  - `title`: Human-readable title.
  - `bodyPath`: Path to the markdown file describing the role’s guidance.

---

## 5. Training Dataset

**Description**  
Collection of input/output pairs derived from SpecKit artifacts for use in model training or evaluation.

**Key Fields**
- `datasetId`: Identifier for the dataset.
- `projectName`: Project name.
- `featureId` (optional): Feature identifier.
- `lines[]`: Individual training examples.
  - `input_type`: `spec_to_plan` | `plan_to_tasks` (for v1; extensible later).
  - `input_ref`: Reference to source artifact(s), usually a path plus optional section marker.
  - `output_ref`: Reference to target artifact(s).
  - `meta`:
    - `timestamp`: ISO-8601.
    - `sourceRepo`: Optional repo identifier.
    - `notes`: Optional free-text notes.

---

## 6. Release Notes Document

**Description**  
Human-readable release notes derived from SpecKit artifacts and git/project state.

**Key Fields**
- `version`: Version string, usually from the repository `VERSION` file or an override parameter.
- `date`: Release date.
- `summary`: High-level overview of the release.
- `newFeatures[]`: Items representing new functionality, typically linked to SpecKit features.
- `improvements[]`: Non-breaking improvements.
- `fixes[]`: Bug fixes.
- `breakingChanges[]`: Changes requiring action or migrations.
- `knownIssues[]`: Known outstanding issues.
- `links[]`: References to specs, features, tasks, and other documentation.

---

## 7. Relationships (High Level)

- **Context Pack** aggregates references to **Architecture Snapshots**, **Specs**, **Plans**, **Tasks**, and related markdown.  
- **Health Report** inspects the presence and freshness of these same artifacts and may point to missing or outdated entities.  
- **Agent Bundle** is derived from the **Context Pack**, transforming selected files into chunked, labelled entities and adding role-specific instructions.  
- **Training Dataset** is derived from design-time transitions (spec→plan, plan→tasks), referencing those artifacts rather than embedding them directly.  
- **Release Notes Document** summarizes changes inferred from completed tasks, updated specs/plans, and optionally git history.

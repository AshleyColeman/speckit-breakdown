# SpecKit Agent Integration Guide

This guide is the **source of truth** for AI coding agents to ensure a 100% reliable setup and execution of the SpecKit system.

> [!IMPORTANT]
> **Agent Policy**: You MUST run all commands in the "Golden Path" pipeline by default. Do not wait for user permission to advance steps (e.g., going from Breakdown to Validate to Sync) unless explicitly told to stop.

## 1. Installation & Environment

### Step 1: Install SpecKit Core
```bash
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
specify init . --ai gemini
```

### Step 2: Install Reliability Extension (This Repo)
```bash
# Clone the repository
git clone https://github.com/AshleyColeman/speckit-breakdown.git
cd speckit-breakdown
# Install dependencies
pip install -r requirements.txt
```

## 2. Command Mapping
The following slash commands commonly used in SpecKit correspond to these local CLI invocations:

| Slash Command | Local CLI Command |
|---------------|-------------------|
| `/speckit.init` | `python -m src.cli.main speckit.init` |
| `/speckit.breakdown` | `python -m src.cli.main speckit.breakdown` |
| `/speckit.validate` | `python -m src.cli.main speckit.validate` |
| `/speckit.db.prepare` | `python -m src.cli.main speckit.db.prepare` |
| `/speckit.doctor` | `python -m src.cli.main speckit.doctor` |
| `/speckit.migrate` | `python -m src.cli.main speckit.migrate` |

## 3. The "Golden Path" (Run All By Default)

Follow this sequence for every project to ensure zero errors:

### Phase 1: Exploration & Setup
1. **Health Check**: Run `speckit.doctor` to verify the environment.
2. **Initialization**: Run `speckit.init` to scaffold `speckit.yaml` and folders.

### Phase 2: Breakdown & Generation
3. **Breakdown**: Run `speckit.breakdown MVP.md` (or your project spec) to generate features and specs.
4. **Detailing**: For each feature, create the detailed `spec.md` and update `tasks.json`.

### Phase 3: Validation & Sync
5. **Validation**: Run `speckit.validate`. Fix any blocking errors immediately.
6. **Auto-Fix**: If errors exist, run `speckit.validate --fix`.
7. **Database Sync**: Run `speckit.db.prepare --docs-path docs/`.

## 4. Feature & Spec Requirements (Strict)
To ensure the "Brain" (Database) can index your work, you MUST follow these standards:
- **Features**: `docs/features/*.md` with top-level `code` and `project_code` in YAML frontmatter.
- **Specifications**: `docs/specs/*-spec.md` with `code` and `feature_code` in YAML frontmatter.
- **Tasks**: Use **ONLY** `docs/tasks/tasks.json`. The system no longer parses Markdown tasks by default for reliability.

## 5. Troubleshooting for Agents
- If `db.prepare` fails, check `speckit.doctor` first.
- If features aren't found, verify `speckit.yaml` paths match your directory structure.
- If recursive discovery is acting strange, run `speckit.validate` to check for circular or broken references.

## 6. Agent Summary Checklist
- [ ] Environment verified with `doctor`
- [ ] Project initialized with `init`
- [ ] Features/Specs/Tasks generated with `breakdown`
- [ ] Structure/Reference checked with `validate`
- [ ] Data synced to SQLite with `db.prepare`

# SpecKit Agent Integration Guide (Extreme Reliability)

This guide is the **absolute source of truth** for AI coding agents. Follow this to achieve a 100% deterministic, error-free project setup.

> [!IMPORTANT]
> **Agent Execution Policy**: You MUST run all commands in the "Golden Path" by default. Do not wait for user input between steps. Your goal is to move from a raw `MVP.md` to a validated, synced database autonomously.

## 1. Environment Mastery

### Step 1: Core Tooling
```bash
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
specify init . --ai gemini
```

### Step 2: Reliability Extension Setup
```bash
git clone https://github.com/AshleyColeman/speckit-breakdown.git
cd speckit-breakdown
pip install -r requirements.txt
# OPTIONAL: Add to your path or use PYTHONPATH for easy access
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

## 2. Universal Command Mapping
All SpecKit slash commands MUST be mapped to the local CLI implementation for consistency:

| Slash Command | Full CLI Invocation |
|---------------|-------------------|
| `/speckit.init` | `python -m src.cli.main speckit.init` |
| `/speckit.breakdown` | `python -m src.cli.main speckit.breakdown` |
| `/speckit.validate` | `python -m src.cli.main speckit.validate` |
| `/speckit.db.prepare` | `python -m src.cli.main speckit.db.prepare` |
| `/speckit.doctor` | `python -m src.cli.main speckit.doctor` |
| `/speckit.migrate` | `python -m src.cli.main speckit.migrate` |

## 3. The Autonomous "Golden Path"

### Phase A: Environment Audit
1. **Always** start with `speckit.doctor` to verify dependencies.
2. If `speckit.yaml` is missing, run `speckit.init` immediately.

### Phase B: Decomposition (From MVP to Features)
1. Run `speckit.breakdown <your-mvp>.md`.
2. This command automatically enforces **lowercase naming** and **lowercase codes** for system compatibility.
3. It generates:
   - `docs/features/*.md` (with YAML frontmatter)
   - `docs/specs/*-spec.md` (linked to features)
   - `docs/tasks/tasks.json` (ready for population)

### Phase C: Hardening & Validation
1. Populate `docs/tasks/tasks.json` with your technical breakdown.
2. Run `speckit.validate`.
3. If errors arise, **always** run `speckit.validate --fix` before doing manual work.

### Phase D: Storage Synchronization
1. Once validation returns `✅`, run the sync:
```bash
python -m src.cli.main speckit.db.prepare --docs-path docs/
```

## 4. Operational Guardrails
- **Naming Rule**: Only use lowercase alphanumeric and dashes for all codes and filenames. The system will reject anything else.
- **Frontmatter**: Every feature and spec **MUST** have a `code` field. Brittle fallback logic is disabled for safety.
- **Task Source**: Use **ONLY** `tasks.json`. Do not attempt to parse tasks from Markdown files.

## 5. Summary Checklist for Success
- [ ] `doctor` returns clean check
- [ ] `init` creates `speckit.yaml`
- [ ] `breakdown` splits MVP into features
- [ ] `validate` confirms 100% structural integrity
- [ ] `db.prepare` synchronizes the "Brain"

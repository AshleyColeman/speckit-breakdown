# 🗂️ SpecKit Multi-Agent Pipeline Index

This index defines the sequence, roles, and handoff protocols for the **SpecKit Modular Pipeline**. Follow this order to move from a raw idea to a production-ready codebase.

## 🚠 The Pipeline Roadmap

| Step | Agent Role | Protocol | Input | Output |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **The Bootstrapper** | [BOOTSTRAP_AGENT.md](file:///home/ashleycoleman/Projects/speckit-breakdown/docs/BOOTSTRAP_AGENT.md) | Repo URL | Init Env & DB |
| **2** | **The Decomposer** | [BREAKDOWN_AGENT.md](file:///home/ashleycoleman/Projects/speckit-breakdown/docs/BREAKDOWN_AGENT.md) | MVP.md | docs/features/ |
| **3** | **The Specifier** | [SPECIFICATION_AGENT.md](file:///home/ashleycoleman/Projects/speckit-breakdown/docs/SPECIFICATION_AGENT.md) | Features | docs/specs/ & plan.md |
| **4** | **The Orchestrator** | [ORCHESTRATION_AGENT.md](file:///home/ashleycoleman/Projects/speckit-breakdown/docs/ORCHESTRATION_AGENT.md) | Plans | tasks.json & Step Orders |
| **5** | **The Developer** | [IMPLEMENTATION_AGENT.md](file:///home/ashleycoleman/Projects/speckit-breakdown/docs/IMPLEMENTATION_AGENT.md) | Tasks | Production Code |

---

## 🏗️ Architecture of Handoffs

Every agent in the pipeline is bound by the **"Golden Path" Principle**:
1. **Retrieve Context**: Read the artifacts from the *previous* step.
2. **Execute Command**: Run the specific SpecKit CLI command for that phase.
3. **Verify**: Run `speckit validate` to ensure structural integrity.
4. **Sync**: Run `speckit.db.prepare` to persist state to the "System Brain" (SQLite).
5. **Mark Done**: Inform the user that the pipeline step is complete and the next agent is ready.

---

## 🚦 System Health check
Before starting any agent, ensure the environment is ready:
- `python -m src.cli.main speckit.doctor` (Structural Check)
- `speckit validate` (Reference Check)

---

> [!TIP]
> **Parallel Execution**: Only **Step 5 (Implementation)** is designed for massive parallel throughput. Steps 1-4 should be handled by a single "Architectural" stream to ensure logical consistency.

# SpecKit: Orchestration & Step Orders

This guide explains how SpecKit calculates the **Step Order** (Execution Plan) for your project tasks.

## Why Orchestration Matters

When you breakdown a project into features and tasks, you end up with a list of things to do. Some tasks depend on others (e.g., you can't implement a Login Service until the Database is set up). 

SpecKit's Orchestration logic:
1.  **Validates** that you don't have any circular dependencies (A depends on B, B depends on A).
2.  **Calculates** the "Longest Path" to determine the sequential step for each task.
3.  **Identifies** tasks that can be run in **Parallel**.

---

## The "Magic" of Step Orders

SpecKit uses a **Topological Sort** algorithm to assign a `step_order` to every task.

- **Step 1**: Tasks with **ZERO** dependencies. These can all start immediately (and potentially in parallel).
- **Step 2**: Tasks that only depend on Step 1 tasks.
- **Step N**: Tasks that depend on at least one task from Step N-1.

### Example

Imagine this dependency graph:
- **T001** (Setup DB) -> No deps
- **T002** (Create User Table) -> Depends on T001
- **T003** (Create Log Table) -> Depends on T001
- **T004** (Auth Service) -> Depends on T002

**Calculated Execution Plan:**
- **Step 1**: T001
- **Step 2**: T002, T003 (Parallelizable!)
- **Step 3**: T004

---

## Working with the Database

The `python -m src.cli.main` command (often referred to as `/speckit.db.prepare` in documentation) is the engine that computes these orders.

### Execution Plan Visibility
When you run with the `--verbose` flag, SpecKit logs the calculated plan:

```text
DEBUG | src.services.bootstrap_orchestrator - Calculated Execution Plan:
DEBUG | src.services.bootstrap_orchestrator -   [Step 1] t001
DEBUG | src.services.bootstrap_orchestrator -   [Step 2] t002
DEBUG | src.services.bootstrap_orchestrator -   [Step 2] t003
DEBUG | src.services.bootstrap_orchestrator -   [Step 3] t004
```

### Persistence
These orders are saved to the `task_runs` table in your database. This allows the **Implementation Agent** to:
1.  Query the DB for "Ready" tasks (Step 1).
2.  Implement them in parallel.
3.  Once a task is marked "Completed", the next step logic updates automatically.

---

## Best Practices

1.  **Be Explicit**: In your `tasks.md` or individual task files, always include the `Depends on: ID` field.
2.  **Think in Phases**: Try to group architectural setup in Phase 1 (Step 1) so implementation can scale in parallel later.
3.  **Check for Cycles**: If you see a "Validation Failed: Circular Dependency" error, check your `Depends on` fields. You likely have a loop that needs breaking.
4.  **Use Subcommands**: In a "Brownfield" (existing) project, use the recursive discovery feature by keeping your tasks nested within their feature folders.

---

## Summary
SpecKit Orchestration turns a flat list of markdown files into a high-performance **parallel execution engine**. By following the calculated Step Orders, you ensure that work is done in the correct sequence without manual management.

# Task 010: Make Step Order Computation Scalable (Avoid O(n²) Queue)

## Goal
Fix the O(n²) behavior in dependency resolution by replacing `list.pop(0)` queue usage with a scalable approach.

## Context (from audit)
- `BootstrapOrchestrator._calculate_step_orders()` uses a Python list as a queue with `pop(0)`.

## Scope
- Replace list queue with `collections.deque` (minimal change) or use an explicit topological sort with an efficient queue.

## Files likely involved
- `src/services/bootstrap_orchestrator.py`

## Steps
1. Locate `_calculate_step_orders()`.
2. Replace `queue = [...]` + `pop(0)` with `deque` + `popleft()`.
3. If there are other O(n²) patterns in the same routine, address them.
4. Add a performance-oriented unit test (non-flaky) that ensures the method runs within a reasonable time for a large synthetic graph.

## Acceptance criteria
- `_calculate_step_orders()` no longer uses `pop(0)` on a list.
- Test coverage exists for correctness and basic scalability.

## Non-goals
- Rewriting the entire orchestrator.

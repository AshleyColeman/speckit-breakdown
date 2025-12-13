# Audit Remediation Master Tasklist

This file tracks completion status for the audit remediation tasks in this folder.

## Checklist

- [x] 001: [Postgres support tier and gating](./001_postgres_support_tier_and_gating.md)
- [x] 002: [Postgres schema contract and read alignment](./002_postgres_schema_contract_and_read_alignment.md)
- [x] 003: [Remove Postgres heuristic name matching; use stable IDs](./003_replace_postgres_heuristic_name_matching_with_stable_ids.md)
- [x] 004: [Replace placeholder stubs with real behavior or fail-fast](./004_replace_placeholder_pass_stubs_with_real_behavior_or_fail_fast.md)
- [x] 005: [Make persistence transactional per run](./005_make_persistence_transactional_per_run.md)
- [x] 006: [Enable SQLite foreign keys and strengthen schema safety](./006_enable_sqlite_foreign_keys_and_strengthen_schema_constraints.md)
- [x] 007: [Implement Postgres verify_schema (or fail fast)](./007_implement_postgres_verify_schema_or_fail_fast.md)
- [x] 008: [Split DataStoreGateway into protocol + backend implementations](./008_split_datastoregateway_into_protocol_and_backend_implementations.md)
- [x] 009: [Reduce DB connection churn and add batching](./009_reduce_connection_churn_and_add_batching_for_db_operations.md)
- [x] 010: [Make step order computation scalable](./010_make_step_order_computation_scalable.md)
- [x] 011: [Split feature_parser into feature/spec/task parsers](./011_split_feature_parser_into_feature_spec_task_parsers.md)
- [x] 012: [Make YAML parsing deterministic](./012_make_yaml_parsing_deterministic.md)
- [x] 013: [Add Python CLI packaging and runtime dependencies](./013_add_python_cli_packaging_and_runtime_dependencies.md)
- [x] 014: [Document support matrix and Python CLI usage](./014_document_support_matrix_and_python_cli_usage.md)
- [x] 015: [Improve installer supply-chain guidance](./015_improve_installer_supply_chain_guidance.md)
- [x] 016: [Add end-to-end tests for workflow outputs](./016_add_end_to_end_tests_for_workflow_generated_outputs.md)
- [x] 017: [Tighten validation and fail fast on critical parse errors](./017_align_validation_rules_and_fail_fast_on_critical_parse_errors.md)
- [ ] 018: [Improve typing in UpsertService and BootstrapSummary](./018_fix_typing_in_upsertservice_and_bootstrapsummary.md)
- [ ] 019: [Align hard rules with reality or enforce them](./019_align_hard_rules_with_codebase_or_enforce_limits.md)
- [ ] 020: [Integrate (or remove) unused safety mechanisms: locking + rollback](./020_integrate_or_remove_unused_safety_mechanisms_locking_and_rollback.md)

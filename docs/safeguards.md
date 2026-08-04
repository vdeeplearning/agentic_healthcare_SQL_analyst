# Safeguards and threat model

Defense in depth includes request risk classification, prompt-injection flagging, typed plan validation, registered metrics, single-statement SQL parsing, read-only AST enforcement, schema/function allowlists, predicate-required joins, complexity caps, automatic row limits, `EXPLAIN QUERY PLAN`, read-only connections, timeouts, deterministic plausibility checks, small-cell suppression, fixed statistical functions, evidence-only answer templates, and audit logs.

High-risk patient-level requests are denied. Medium-risk demographic work is flagged and suppressed below 10. API keys are accepted only in process/session state and are never logged. SQLite is suitable for a portfolio demo; production PostgreSQL should add a SELECT-only role, statement timeout, network policy, row-level security, encrypted audit storage, authentication, approval workflows, and reviewed metric versions.


# Agentic Clinical SQL Analyst

[![CI](https://img.shields.io/badge/CI-GitHub_Actions-blue)](#testing) [![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB)](#quick-start) [![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A portfolio-grade, constrained analytics agent that turns natural-language questions into typed analysis plans, validated read-only SQL, verified statistics, and evidence-grounded answers over an entirely synthetic healthcare database. It demonstrates relational design, practical SQL, agentic orchestration, FastAPI, Streamlit, statistical tooling, Docker, CI, auditability, and explainability—without requiring a paid service to launch.

> **Synthetic data only. Educational/portfolio software, not a clinical decision system.** No record represents a real patient, provider, or hospital.

## Screenshots

| Analysis workspace | Validation and audit |
|---|---|
| ![Analysis workspace showing a natural-language question and verified hospital encounter results](docs/screenshots/analysis.png) | ![Validation and audit trace showing successful bounded workflow steps](docs/screenshots/audit.png) |

## Why this exists

Text-to-SQL demos often give a model excessive authority and trust plausible-looking output. This project separates interpretation from authority. The agent can propose a registered metric and SQL candidate, but deterministic code decides whether the query may run, recomputes important quantities, suppresses small cells, and checks whether the answer is supported.

### Key features

- 12-table normalized SQLite model, foreign keys, checks, indexes, views, and reproducible synthetic data
- Credential-free deterministic agent supporting curated analytical questions against the real database
- Pydantic analysis plans before SQL; ambiguity such as “Which hospital is worst?” triggers clarification
- SQLGlot single-statement AST checks, table/column/function allowlists, join/resource controls, and row limits
- SQLite URI read-only mode, `query_only`, timeout progress handler, and `EXPLAIN QUERY PLAN`
- Registered healthcare metrics and fixed statistical tools; arbitrary generated Python never runs
- Result plausibility checks, deterministic arithmetic, small-cell suppression, grounded answer templates
- FastAPI/OpenAPI, polished Streamlit UI, JSON audit trail, benchmarks, pytest, Docker Compose, and CI
- 20 annotated reference queries covering joins, CTEs, subqueries, date logic, views, indexes, and windows

## What the safety-focused description means in plain English

The project description says that it uses a **bounded AI workflow with structured planning, SQLGlot validation, privacy controls, approved statistical tools, deterministic result checks, evidence-grounded answers, and complete audit trails**. Put simply, the AI is allowed to suggest an analysis, but it is not trusted with unrestricted control. Ordinary application code decides what is safe to run, checks the results, limits what may be shown, and records what happened.

### Bounded AI workflow

“Bounded” means the AI operates inside a fixed process with clear limits. It can interpret a question and propose how to answer it, but it cannot connect directly to the database, change the database, run arbitrary programs, or retry forever.

For example, the workflow follows steps such as:

1. Understand the user's question.
2. Decide whether the question is clear and safe.
3. Create a structured analysis plan.
4. Propose SQL.
5. Validate the SQL with ordinary code.
6. Inspect the database query plan.
7. Execute the query through a read-only connection.
8. Check and suppress the returned results where necessary.
9. Optionally run one approved statistical function.
10. Produce an answer based only on verified evidence.
11. Save an audit record.

If the question is unclear—such as “Which hospital is worst?”—the application asks what “worst” means. If a request is unsafe, such as asking for patient-level exports, it is denied. If validation fails, execution stops safely.

### Structured planning

The AI cannot jump directly from a user's question to database execution. It must first complete a structured analysis plan that identifies items such as:

- the metric being requested;
- the population or cohort to analyze;
- inclusion and exclusion rules;
- the date range;
- grouping and comparison fields;
- the required database tables;
- the minimum acceptable group size;
- whether a statistical test is needed; and
- whether the question is ambiguous or presents a privacy risk.

Pydantic checks that this plan has the required fields and valid data types. This is similar to requiring someone to complete a standardized request form before they are allowed to submit a database query.

### SQLGlot validation

SQLGlot turns proposed SQL into a structured syntax tree so the application can inspect what the query actually does. This is safer than searching the SQL text for suspicious words because the validator can identify the statement type, tables, columns, functions, and joins.

The validator rejects, among other things:

- attempts to insert, update, or delete data;
- attempts to create, alter, replace, or drop database objects;
- multiple SQL statements hidden in one request;
- access to SQLite system tables or administrative commands;
- tables or columns that do not exist in the approved schema;
- functions that are not on the allowlist;
- joins without meaningful matching conditions; and
- queries that exceed configured complexity or result-size limits.

Even SQL that passes these checks is executed through a separate read-only database connection. The SQL validator and database permissions therefore provide two independent layers of protection.

### Privacy controls

The application is designed to return summarized information rather than individual records. Although the included data is synthetic, the project models privacy practices that would matter when working with healthcare information.

- Aggregate counts, rates, and trends are the default.
- Patient-level output and unrestricted exports are denied.
- Requests involving sensitive demographic combinations are flagged.
- Groups with fewer than 10 observations are suppressed.
- Only a small, verified result sample is provided as context for follow-up questions.
- API keys and direct identifiers are not written to audit logs.

For example, the application may report a hospital's complication rate when enough eligible cases exist, but it will not provide a list of the patients behind that rate.

### Approved statistical tools

The AI cannot write and execute arbitrary Python. It may only select a statistical operation from a predefined registry of reviewed functions, including:

- proportion confidence intervals;
- chi-square tests;
- Fisher exact tests;
- independent-samples t-tests;
- Mann–Whitney U tests;
- one-way ANOVA; and
- Pearson or Spearman correlations.

These functions check their inputs, sample sizes, missing values, and assumptions before running. They return structured results and warnings. The AI chooses from the available tools, but the application—not the AI—owns and executes the underlying Python implementation.

### Deterministic result checks

“Deterministic” means the same input is checked using explicit programming rules rather than model judgment. After a SQL query runs, ordinary Python code verifies conditions such as:

- denominators must be positive;
- counts cannot be negative;
- a numerator cannot exceed its denominator;
- rates must remain between 0 and 1;
- percentages must remain between 0 and 100;
- empty results must be reported clearly;
- suspicious values should produce warnings; and
- small groups must remain suppressed.

Important arithmetic is calculated from verified database values. The application does not ask the language model to perform or guess the final calculations.

### Evidence-grounded answers

The final answer is limited to information found in the validated plan, executed SQL, verified result table, approved statistical output, and recorded warnings. Names, categories, sample sizes, percentages, rankings, and comparisons must come from that evidence.

If the query returns no evidence—or if the evidence does not support a conclusion—the application should say so. It should not fill gaps with plausible-sounding medical or operational claims.

### Complete audit trails

Every analysis receives a unique run ID. The audit record stores information needed to reconstruct how the answer was produced, including:

- the original and normalized question;
- the selected model and schema version;
- the structured analysis plan;
- the generated and validated SQL;
- validation and execution status;
- execution time and returned row count;
- approved statistical tools used;
- warnings and limitations;
- the final grounded answer; and
- the creation timestamp.

Secrets such as OpenAI API keys are deliberately excluded. The audit trail makes the system easier to debug, test, explain, and review without exposing credentials.

### The division of responsibility

| The AI may | Deterministic application code must |
|---|---|
| Interpret the user's wording | Classify privacy risk and enforce policy |
| Identify ambiguity | Validate the structured plan |
| Select a registered metric | Control the metric definitions |
| Propose one SQL query | Parse, allowlist, limit, and approve the SQL |
| Request an approved statistical tool | Validate inputs and execute the fixed function |
| Draft an interpretation | Check values and ground claims in verified evidence |

The central idea is straightforward: **the AI proposes; deterministic software verifies and controls**.

## Architecture

```mermaid
flowchart LR
 U["User / Streamlit"] --> API["FastAPI"] --> G["Bounded agent workflow"]
 G --> P["Pydantic analysis plan"] --> V["SQLGlot + policy validators"]
 V --> Q["EXPLAIN + read-only SQLite"] --> R["Result + privacy validators"]
 R --> S["Approved statistics"] --> A["Grounded answer validator"]
 G --> L["Audit log"]
```

```mermaid
flowchart TD
 N["Normalize"] --> C["Classify risk/intent"]
 C -->|ambiguous| CL["Clarify and stop"]
 C -->|high risk| D["Deny and stop"]
 C --> P["Create typed plan"] --> PV["Validate plan"] --> SQL["Generate candidate SQL"]
 SQL --> SV["AST/schema/join validation"] --> EP["Inspect query plan"] --> EX["Read-only execution"]
 EX --> RV["Validate/suppress results"] --> ST["Optional approved tool"] --> GA["Compose grounded answer"] --> FV["Faithfulness check"] --> AU["Audit"]
```

```mermaid
erDiagram
 PATIENTS ||--o{ ENCOUNTERS : has
 HOSPITALS ||--o{ PROVIDERS : employs
 HOSPITALS ||--o{ ENCOUNTERS : hosts
 PROVIDERS ||--o{ ENCOUNTERS : attends
 ENCOUNTERS ||--o{ ENCOUNTER_DIAGNOSES : coded
 DIAGNOSES ||--o{ ENCOUNTER_DIAGNOSES : classifies
 ENCOUNTERS ||--o{ ENCOUNTER_PROCEDURES : receives
 PROCEDURES ||--o{ ENCOUNTER_PROCEDURES : defines
 ENCOUNTERS ||--o{ LAB_RESULTS : produces
 ENCOUNTERS ||--o| READMISSIONS : index
 HOSPITALS ||--o{ QUALITY_MEASURES : reports
```

Safeguards stack from outside inward: **privacy classification → typed plan → metric registry → AST/schema/join allowlists → plan inspection/resource caps → read-only database → result checks/suppression → fixed statistics → answer faithfulness → immutable provenance record**.

## Database and SQL

`patients`, `hospitals`, `providers`, and `encounters` form the core. Diagnoses and procedures use normalized vocabularies with many-to-many bridge tables. Labs, readmissions, quarterly quality measures, and audits are separate facts. The seeded full profile creates approximately 25,000 patients, 30 hospitals, 200 providers, and 100,000 encounters. Hospital risk, diagnosis, age proxy, rurality, seasonality, and temporal trends generate useful analytical variation. Controlled missingness, suspicious dates, rare categories, inconsistent codes, and small cohorts support quality tests.

The [reference curriculum](sql/reference_queries/README.md) visibly demonstrates `SELECT`, filtering, sorting, grouping, `HAVING`, inner/left joins, CTEs, subqueries, `CASE`, dates, aggregates, `ROW_NUMBER`, `RANK`, `DENSE_RANK`, `LAG`, rolling windows, views, parameterization, indexes, and `EXPLAIN QUERY PLAN`. Database construction uses an explicit transaction.

## What is agentic—and what is not

The workflow observes state, selects a bounded path, can request clarification, chooses a registered metric/tool, and records structured actions. It is not fully autonomous: retry limits are finite (two SQL repairs, one result repair, one evidence-only answer rewrite as extension contracts), high-risk requests terminate, and deterministic components retain execution authority. The trace shows decisions, validators, tool calls, warnings, and retry reasons—not hidden chain-of-thought.

The LLM does **not** directly execute unrestricted SQL. Generated SQL is parsed before execution; the database handle is read-only. The model cannot redefine metrics, calculate final rates, run arbitrary Python, expose small groups, or add claims absent from verified evidence. Model self-critique is secondary because a model can confidently repeat its own mistake.

The baseline demo is intentionally deterministic. When a session-only API key is supplied, non-demo questions use the OpenAI Responses API with Pydantic Structured Outputs to propose an `AnalysisPlan` and one SQL candidate. That candidate passes through exactly the same non-bypassable deterministic pipeline; OpenAI never receives a database connection and the API key is never logged. Curated questions remain deterministic for reproducible demonstrations.

## Metrics, privacy, statistics, and provenance

The registry fixes numerator, denominator, eligibility, sample size, unit, grouping, null handling, and caveats for readmission, mortality, complications, length of stay, emergency conversion, cost, volume, and prevalence. Rates are checked and important ratios are computed from numerator/denominator output.

Aggregate results are the default. Direct identifiers and patient-level exports are high risk and denied. Sensitive demographic combinations are medium risk, explicitly warned, and groups under 10 are suppressed. Only the minimum result fields needed for an answer should reach a live model.

Approved tools include Wilson proportion intervals, chi-square, Fisher exact, Welch t-test, Mann–Whitney U, one-way ANOVA, and Pearson/Spearman correlations. Each validates types/sample size and returns structured estimates, effects, assumptions, and warnings. Regression and standardization are documented extension points in this MVP.

Every run receives an ID and records question, normalized intent, model label, schema version, plan, SQL, validation/execution status, timing, row count, statistical tool, warnings, answer, and timestamp. API keys are excluded.

## Example

Question: “Which hospitals had the highest 30-day readmission rates for heart failure in 2025?”

```sql
WITH cohort AS (... validated eligibility joins ...)
SELECT hospital_name, COUNT(*) AS denominator,
       SUM(readmitted_within_30_days) AS numerator,
       1.0 * SUM(readmitted_within_30_days) / COUNT(*) AS readmission_rate
FROM cohort JOIN hospitals USING (hospital_id)
GROUP BY hospital_id, hospital_name
HAVING COUNT(*) >= 10
ORDER BY readmission_rate DESC;
```

Output includes the direct answer, verified table/chart, sample size, fixed metric definition, caveats, exact validated SQL, referenced tables/columns, optional test result, trace, query-plan provenance, and audit ID. If evidence is empty or inconclusive, the answer says so.

## Quick start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m src.database.seed --patients 2500 --encounters 10000
uvicorn src.api.main:app --reload
```

Open [http://localhost:8000/docs](http://localhost:8000/docs). In another terminal:

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501). No key is required. For the full dataset, run `python -m src.database.seed` (100,000 encounters). Configuration lives in [.env.example](.env.example); never commit `.env`.

### Testing and benchmark

```bash
python -m pytest
python -m src.cli benchmark
```

The seed benchmark spans aggregation, joins, rates, cohorts, ambiguity, privacy denial, statistics, and prompt injection. It reports executable SQL rate, exact table selection, clarification/denial accuracy, and latency. See [evaluation design](docs/evaluation.md). Benchmark results are intentionally a placeholder until run in CI against a pinned release artifact.

### Docker

```bash
docker compose up --build
```

API: port 8000; UI: port 8501; generated data uses a named volume.

## API

| Method | Path | Purpose |
|---|---|---|
| GET | `/`, `/health` | metadata and readiness |
| GET | `/schema`, `/metrics` | allowlisted schema and registry |
| POST | `/analyze` | execute the bounded workflow |
| POST | `/validate-sql` | validate without execution |
| GET | `/runs`, `/runs/{run_id}` | audit provenance |
| GET | `/reference-queries` | curriculum discovery |
| POST | `/demo/reset` | safely refuses destructive HTTP reset |

Full contracts are in OpenAPI and [docs/api.md](docs/api.md).

## Project map

`src/agent` owns typed orchestration; `src/safety` deterministic policy; `src/database` creation/read-only access; `src/metrics` immutable definitions; `src/statistics` fixed tools; `src/audit` provenance; `src/api` FastAPI; `src/ui` Streamlit; `src/evaluation` benchmarks; `sql` schema/views/indexes/reference queries; `tests` regression coverage; `docs` design detail.

## Design decisions, limits, and production hardening

SQLite makes the demo portable and inspectable; PostgreSQL should use a dedicated SELECT-only role and statement timeout. Curated SQL makes credential-free behavior reproducible. SQLGlot provides structural checks that regex cannot, though policy remains conservative. FastAPI supplies typed service contracts while Streamlit optimizes portfolio exploration.

Known limits: live planning requires network access, API credit, and access to the configured OpenAI model; relationship validation is conservative; statistics are unadjusted; no causal or clinical inference is intended; benchmark breadth should grow beyond the seed fixture; logistic/linear regression and standardized rates remain registry extensions; SQLite timeouts are cooperative; audit rows are not cryptographically tamper-evident. Production requires identity, authorization, encrypted/tamper-evident audit storage, migrations, PostgreSQL permissions/RLS, monitoring, reviewed metric governance, model/version pinning, red-team evaluation, approval queues, and incident response.

## Resume-ready description

**Agentic Clinical SQL Analyst: Designed a normalized healthcare database and a constrained LangGraph agent that converts natural-language questions into validated read-only SQL, executes multi-table analytics, invokes approved statistical tools, checks result plausibility, repairs failed queries, enforces privacy safeguards, and returns evidence-grounded findings with query provenance and audit trails.**

## Interview talking points

- Explain normalization, bridge tables, foreign keys, checks, index selection, views, and why cohorts use explicit primary-diagnosis logic.
- Walk through joins, CTEs, date calculations, `HAVING`, and window functions in `sql/reference_queries`.
- Describe natural-language-to-SQL as plan selection plus constrained compilation—not direct model execution.
- SQLGlot gives an AST for statement type, references, joins, functions, complexity, and rewriting; regex is only supplemental.
- Read-only permissions contain validator defects; query limits and timeouts contain resource abuse.
- Self-critique is probabilistic and correlated with generation errors, so deterministic policy and arithmetic stay authoritative.
- Contrast LLM duties (interpretation/candidate generation) with code duties (permission, computation, suppression, validation).
- Discuss test selection, assumptions, effects, confidence intervals, missingness, and why unadjusted significance is limited.
- Explain small-cell suppression, high-risk denial, data minimization, bounded retries, and structured audit provenance.
- FastAPI separates reusable contracts; Streamlit makes evidence and safeguards legible to reviewers.
- Docker provides reproducibility; GitHub Actions seeds, tests, measures coverage, and smoke-runs evaluation.

## Security and clinical disclaimer

This is a defense-in-depth educational prototype, not a security certification. It uses synthetic data only and must not receive PHI. It is not validated for patient care, diagnosis, treatment, operational decisions, regulatory reporting, or hospital comparison. Review SQL, metrics, and outputs with qualified domain experts.

MIT licensed. Contributions are welcome under [CONTRIBUTING.md](CONTRIBUTING.md).

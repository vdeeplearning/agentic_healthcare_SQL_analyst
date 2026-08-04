# API

Run `uvicorn src.api.main:app --reload` and open `/docs`. `GET /health`, `/schema`, `/metrics`, `/runs`, `/runs/{id}`, and `/reference-queries` are read endpoints. `POST /analyze` accepts `{"question":"..."}`; `POST /validate-sql` accepts `{"sql":"..."}`. `/demo/reset` intentionally refuses destructive reset over HTTP; regenerate explicitly from the CLI.

Errors use FastAPI's standard JSON format. Analyze responses include status, typed plan, validated SQL, verified rows, warnings, metric definition, approved statistics, trace, provenance, and audit ID.


"""Audit persistence."""
from __future__ import annotations
import json, sqlite3
from datetime import datetime,timezone
from pathlib import Path
from typing import Any

def write_audit(path:Path,record:dict[str,Any])->None:
    values=(record["run_id"],record.get("question",""),record.get("normalized_question",""),record.get("model_name","deterministic-demo"),"1.0",json.dumps(record.get("plan")),record.get("sql"),record.get("validation_status","unknown"),record.get("execution_status","unknown"),record.get("row_count",0),record.get("execution_time_ms"),json.dumps(record.get("statistical_tools")),json.dumps(record.get("warnings",[])),record.get("final_answer"),datetime.now(timezone.utc).isoformat())
    connection=sqlite3.connect(path); connection.execute("PRAGMA foreign_keys=ON"); connection.execute("INSERT INTO audit_runs VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",values); connection.commit(); connection.close()
def get_run(path:Path,run_id:str)->dict[str,Any]|None:
    connection=sqlite3.connect(path); connection.row_factory=sqlite3.Row; row=connection.execute("SELECT * FROM audit_runs WHERE run_id=?",(run_id,)).fetchone(); connection.close(); return dict(row) if row else None
def list_runs(path:Path,limit:int=50)->list[dict[str,Any]]:
    connection=sqlite3.connect(path); connection.row_factory=sqlite3.Row; rows=connection.execute("SELECT * FROM audit_runs ORDER BY created_at DESC LIMIT ?",(min(limit,100),)).fetchall(); connection.close(); return [dict(r) for r in rows]


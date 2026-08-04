"""Reproducible benchmark runner."""
from __future__ import annotations
import json,time
from pathlib import Path
from src.agent.workflow import Analyst
def load_benchmark()->list[dict]: return json.loads((Path(__file__).with_name("benchmark.json")).read_text())
def run_benchmark(db_path:Path,limit:int|None=None)->dict:
    items=load_benchmark()[:limit]; outcomes=[]; started=time.perf_counter()
    for item in items:
        result=Analyst(db_path).analyze(item["question"]); actual_tables=set(result.validation.tables if result.validation else [])
        outcomes.append({"question":item["question"],"status":result.status,"clarification_correct":(result.status=="clarification_required")==item["clarification"],"denial_correct":(result.status=="denied")==item["denied"],"table_selection_correct":actual_tables==set(item["expected_tables"]),"executable":result.status=="completed"})
    n=len(items) or 1
    return {"items":outcomes,"summary":{"questions":len(items),"executable_sql_rate":sum(x["executable"] for x in outcomes)/n,"table_selection_accuracy":sum(x["table_selection_correct"] for x in outcomes)/n,"clarification_accuracy":sum(x["clarification_correct"] for x in outcomes)/n,"unsafe_query_rejection_rate":sum(x["denial_correct"] for x in outcomes)/n,"average_latency_ms":(time.perf_counter()-started)*1000/n}}


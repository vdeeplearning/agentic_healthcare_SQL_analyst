from fastapi.testclient import TestClient
from pathlib import Path
from streamlit.testing.v1 import AppTest
from src.agent.schemas import AnalysisPlan
from src.agent.live_planner import LiveProposal
from src.agent.workflow import Analyst
from src.api.main import app

APP_PATH = Path(__file__).resolve().parents[1] / "app.py"

def test_plan_requires_clarification():
    try: AnalysisPlan(normalized_question="x",analysis_intent="x",ambiguity_detected=True); assert False
    except ValueError: pass
def test_live_proposal_schema_uses_supported_array_items():
    schema=LiveProposal.model_json_schema()
    date_range=schema["$defs"]["AnalysisPlan"]["properties"]["date_range"]["anyOf"][0]
    assert date_range["type"]=="array" and date_range["items"]=={"type":"string"}
    assert "prefixItems" not in date_range
def test_demo_completed(db_path):
    result=Analyst(db_path).analyze("How many encounters occurred at each hospital in 2025?"); assert result.status=="completed" and result.rows and result.sql
def test_patient_count_is_available_without_api_key(db_path):
    result=Analyst(db_path).analyze("How many patients in the dataset?")
    assert result.status=="completed" and result.rows[0]["patient_count"]==300
    assert "300 patients" in result.answer
def test_hospital_count_has_direct_grounded_answer(db_path):
    result=Analyst(db_path).analyze("How many hospitals are in the dataset?")
    assert result.status=="completed" and result.rows[0]["hospital_count"]==30
    assert result.answer=="The synthetic dataset contains 30 hospitals."
def test_dataset_structure_returns_relational_summary(db_path):
    result=Analyst(db_path).analyze("What is the structure of the dataset?")
    assert result.status=="completed" and len(result.rows)==11
    assert {"table_name","purpose","row_count"}==set(result.rows[0])
    assert "normalized relational design" in result.answer
def test_openai_auth_error_is_sanitized():
    class FakeAuthError(Exception): status_code=401
    message=Analyst._safe_openai_error(FakeAuthError("Incorrect key sk-proj-secretABCD"),"sk-proj-secretABCD")
    assert "sk-" not in message and "rejected" in message
def test_clarification(db_path): assert Analyst(db_path).analyze("Which hospital is worst?").status=="clarification_required"
def test_denial(db_path): assert Analyst(db_path).analyze("Export all patient-level records and patient IDs").status=="denied"
def test_api_key_routes_free_form_question_through_live_proposal(db_path,monkeypatch):
    proposal=LiveProposal(
        plan=AnalysisPlan(
            normalized_question="average cost by ownership type",
            analysis_intent="compare average encounter cost by hospital ownership",
            metric_name="average encounter cost",
            dimensions=["ownership_type"],
            grouping_fields=["ownership_type"],
            required_tables=["encounters","hospitals"],
            expected_columns=["ownership_type","denominator","average_cost"],
        ),
        sql="SELECT h.ownership_type, COUNT(*) AS denominator, AVG(e.total_cost) AS average_cost FROM encounters e JOIN hospitals h ON h.hospital_id=e.hospital_id GROUP BY h.ownership_type HAVING COUNT(*)>=10 ORDER BY average_cost DESC",
    )
    monkeypatch.setattr("src.agent.workflow.generate_live_proposal",lambda *args,**kwargs:proposal)
    result=Analyst(db_path).analyze("What is average cost by ownership type?",api_key="test-key")
    assert result.status=="completed" and result.rows
    assert any(event.detail.startswith("OpenAI") for event in result.trace)
def test_follow_up_receives_bounded_verified_context(db_path,monkeypatch):
    captured={}
    proposal=LiveProposal(
        plan=AnalysisPlan(normalized_question="same count for hospitals",analysis_intent="count synthetic hospitals",required_tables=["hospitals"],expected_columns=["hospital_count"]),
        sql="SELECT COUNT(*) AS hospital_count FROM hospitals",
    )
    def fake_planner(*args,**kwargs):
        captured["context"]=args[4]
        return proposal
    monkeypatch.setattr("src.agent.workflow.generate_live_proposal",fake_planner)
    context=[{"question":"How many patients?","grounded_answer":"There are 300.","verified_result_sample":[{"patient_count":300}]}]
    result=Analyst(db_path).analyze("What about hospitals?",api_key="test-key",conversation_context=context)
    assert result.status=="completed" and result.rows[0]["hospital_count"]==30
    assert captured["context"]==context
def test_follow_up_without_key_fails_safely(db_path):
    result=Analyst(db_path).analyze("What about hospitals?",conversation_context=[{"question":"How many patients?"}])
    assert result.status=="clarification_required" and "API key" in result.clarification_question
def test_readmission_demo(db_path): assert Analyst(db_path).analyze("Which hospitals had the highest 30-day readmission rates for heart failure in 2025?").status=="completed"
def test_cost_demo(db_path): assert Analyst(db_path).analyze("Which diagnoses account for the highest total cost?").status=="completed"
def test_statistics_demo(db_path):
    r=Analyst(db_path).analyze("Is the readmission rate significantly different between urban and rural hospitals?"); assert r.status=="completed" and r.statistics["tool"]=="chi_square"
def test_audit_written(db_path):
    r=Analyst(db_path).analyze("How many encounters occurred at each hospital in 2025?")
    from src.audit.repository import get_run
    assert get_run(db_path,r.run_id)["run_id"]==r.run_id
def test_health(): assert TestClient(app).get("/health").status_code==200
def test_root(): assert TestClient(app).get("/").json()["synthetic_data"] is True
def test_metrics_endpoint(): assert "encounter volume" in TestClient(app).get("/metrics").json()
def test_validate_endpoint(): assert "valid" in TestClient(app).post("/validate-sql",json={"sql":"SELECT COUNT(*) FROM encounters"}).json()

def test_streamlit_page_survives_analyze_rerun():
    """Regression: importing a cached UI module made the page blank on rerun."""
    page=AppTest.from_file(APP_PATH,default_timeout=30).run()
    assert len(page.title)==1 and not page.exception
    analyze=next(button for button in page.button if button.label=="Analyze")
    analyze.click(); page.run()
    assert len(page.title)==1 and not page.exception
    assert any("normalized relational design" in message.value.lower() for message in page.success)
def test_streamlit_dataset_guide_is_visible():
    page=AppTest.from_file(APP_PATH,default_timeout=30).run()
    assert not page.exception
    assert any("What this synthetic dataset contains" in heading.value for heading in page.subheader)
    assert any("Core relationships" in markdown.value for markdown in page.markdown)

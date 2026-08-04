"""Public agent contracts."""
from __future__ import annotations
from typing import Any, Literal
from pydantic import BaseModel, Field, model_validator

class AnalysisPlan(BaseModel):
    normalized_question: str
    analysis_intent: str
    metric_name: str | None = None
    population_definition: str = "all eligible encounters"
    inclusion_criteria: list[str] = Field(default_factory=list)
    exclusion_criteria: list[str] = Field(default_factory=list)
    # A bounded list emits Structured Outputs-compatible JSON Schema (`items` +
    # min/max length). Fixed tuples emit `prefixItems`, which the API rejects.
    date_range: list[str] | None = Field(default=None, min_length=2, max_length=2)
    dimensions: list[str] = Field(default_factory=list)
    grouping_fields: list[str] = Field(default_factory=list)
    comparison_type: str | None = None
    ranking_direction: Literal["ascending","descending"] | None = None
    minimum_group_size: int = Field(default=10, ge=10)
    required_tables: list[str] = Field(default_factory=list)
    expected_columns: list[str] = Field(default_factory=list)
    requires_statistical_test: bool = False
    statistical_test_type: str | None = None
    ambiguity_detected: bool = False
    clarification_question: str | None = None
    risk_tier: Literal["low","medium","high"] = "low"
    @model_validator(mode="after")
    def clarification_present(self):
        if self.ambiguity_detected and not self.clarification_question: raise ValueError("ambiguous plans require a clarification question")
        return self

class ValidationReport(BaseModel):
    valid: bool; errors: list[str]=Field(default_factory=list); warnings: list[str]=Field(default_factory=list)
    tables: list[str]=Field(default_factory=list); columns: list[str]=Field(default_factory=list); sql: str | None=None

class TraceEvent(BaseModel):
    step: str; status: Literal["ok","warning","blocked","skipped"]; detail: str

class AnalysisResponse(BaseModel):
    run_id: str; status: Literal["completed","clarification_required","denied","failed"]
    question: str; answer: str; clarification_question: str|None=None; plan: AnalysisPlan|None=None
    sql: str|None=None; columns: list[str]=Field(default_factory=list); rows: list[dict[str,Any]]=Field(default_factory=list)
    warnings: list[str]=Field(default_factory=list); validation: ValidationReport|None=None
    trace: list[TraceEvent]=Field(default_factory=list); metric_definition: dict[str,Any]|None=None
    statistics: dict[str,Any]|None=None; execution_time_ms: float|None=None; provenance: dict[str,Any]=Field(default_factory=dict)

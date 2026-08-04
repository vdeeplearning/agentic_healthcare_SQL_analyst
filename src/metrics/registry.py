"""Immutable clinical analytics metric registry."""
from typing import Literal
from pydantic import BaseModel

class MetricDefinition(BaseModel, frozen=True):
    name: str; numerator: str; denominator: str; eligibility: str; minimum_sample_size: int = 10
    unit: Literal["count","days","currency","proportion"]; allowed_groupings: tuple[str,...]
    null_handling: str; caveats: str

GROUPS=("hospital","urban_rural","quarter","year","diagnosis")
METRICS={m.name:m for m in [
 MetricDefinition(name="30-day readmission rate",numerator="eligible inpatient encounters readmitted within 30 days",denominator="eligible inpatient encounters",eligibility="inpatient index encounters with readmission assessment",unit="proportion",allowed_groupings=GROUPS,null_handling="exclude unknown assessment",caveats="Synthetic, unadjusted rate."),
 MetricDefinition(name="mortality rate",numerator="encounters with mortality_flag=1",denominator="eligible encounters",eligibility="all encounters",unit="proportion",allowed_groupings=GROUPS,null_handling="flags are non-null",caveats="Not risk adjusted."),
 MetricDefinition(name="complication rate",numerator="encounters with complication_flag=1",denominator="eligible encounters",eligibility="all encounters",unit="proportion",allowed_groupings=GROUPS,null_handling="flags are non-null",caveats="Not risk adjusted."),
 MetricDefinition(name="average length of stay",numerator="sum valid discharge-admission days",denominator="discharged inpatient encounters",eligibility="valid nonnegative stay",unit="days",allowed_groupings=GROUPS,null_handling="exclude missing discharge",caveats="Sensitive to outliers."),
 MetricDefinition(name="median length of stay",numerator="median valid discharge-admission days",denominator="discharged inpatient encounters",eligibility="valid nonnegative stay",unit="days",allowed_groupings=GROUPS,null_handling="exclude missing discharge",caveats="SQLite baseline computes median in Python."),
 MetricDefinition(name="emergency admission conversion rate",numerator="emergency encounters resulting in inpatient admission",denominator="emergency encounters",eligibility="emergency encounters",unit="proportion",allowed_groupings=GROUPS,null_handling="exclude unknown disposition",caveats="Synthetic encounter model uses disposition proxy."),
 MetricDefinition(name="average encounter cost",numerator="sum total_cost",denominator="encounters with cost",eligibility="non-null nonnegative cost",unit="currency",allowed_groupings=GROUPS,null_handling="exclude missing costs",caveats="Unadjusted synthetic charges."),
 MetricDefinition(name="total encounter cost",numerator="sum total_cost",denominator="not applicable",eligibility="non-null nonnegative cost",unit="currency",allowed_groupings=GROUPS,null_handling="exclude missing costs",caveats="Synthetic charges, not reimbursements."),
 MetricDefinition(name="encounter volume",numerator="count encounters",denominator="not applicable",eligibility="all encounters",unit="count",allowed_groupings=GROUPS,null_handling="not applicable",caveats="Counts encounters, not unique patients."),
 MetricDefinition(name="diagnosis prevalence",numerator="encounters with diagnosis",denominator="eligible encounters",eligibility="encounters in cohort",unit="proportion",allowed_groupings=GROUPS,null_handling="exclude missing diagnosis",caveats="Control primary versus any-position diagnoses explicitly.")
]}


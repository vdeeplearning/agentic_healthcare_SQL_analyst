"""Privacy classification and small-cell suppression."""
from __future__ import annotations
from typing import Any

SENSITIVE=("race","ethnicity","birth_date","patient_id","residential_region")

def classify_risk(question: str) -> tuple[str,list[str]]:
    q=question.lower(); warnings=[]
    if any(x in q for x in ("patient-level","patient ids","patient_id","export all","individual records")):
        return "high",["Patient-level output and unrestricted exports are denied."]
    if any(x in q for x in SENSITIVE): warnings.append("Sensitive demographic access requested; small groups require suppression."); return "medium",warnings
    return "low",warnings

def suppress_small_cells(rows: list[dict[str,Any]], threshold: int=10) -> tuple[list[dict[str,Any]],list[str]]:
    suppressed=0; output=[]
    for row in rows:
        copy=dict(row)
        count=next((v for k,v in row.items() if k.lower() in {"n","count","denominator","eligible_encounters","encounter_count"} and isinstance(v,(int,float))),None)
        if count is not None and 0 < count < threshold:
            for key,value in list(copy.items()):
                if key.lower() not in {"n","count","denominator","eligible_encounters","encounter_count"} and isinstance(value,(int,float)): copy[key]=None
            copy["suppressed"]=True; suppressed+=1
        output.append(copy)
    return output,([f"Suppressed {suppressed} group(s) with fewer than {threshold} observations."] if suppressed else [])


"""Deterministic result plausibility checks."""
from typing import Any
def validate_results(rows:list[dict[str,Any]]) -> list[str]:
    warnings=[]
    if not rows: return ["Query returned no rows."]
    for i,row in enumerate(rows):
        lower={k.lower():v for k,v in row.items()}
        num=lower.get("numerator",lower.get("readmissions")); den=lower.get("denominator",lower.get("eligible_encounters"))
        if den is not None and den<=0: warnings.append(f"Row {i+1} has a nonpositive denominator.")
        if num is not None and den is not None and not 0<=num<=den: warnings.append(f"Row {i+1} has numerator outside [0, denominator].")
        for key,value in lower.items():
            if value is not None and "rate" in key and not 0<=float(value)<=1: warnings.append(f"Row {i+1} has invalid rate {key}.")
            if value is not None and (key.endswith("count") or key in {"n","count"}) and float(value)<0: warnings.append(f"Row {i+1} has negative count.")
    return list(dict.fromkeys(warnings))

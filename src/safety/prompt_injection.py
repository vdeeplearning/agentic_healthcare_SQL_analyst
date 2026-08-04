"""Detect obvious attempts to override the bounded analytics contract."""
def injection_warnings(question: str) -> list[str]:
    q=question.lower(); patterns=("ignore previous","system prompt","developer message","bypass safeguards","disable validation","execute arbitrary")
    return ["Potential prompt-injection language detected; instructions were ignored."] if any(p in q for p in patterns) else []


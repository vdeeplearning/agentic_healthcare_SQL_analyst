# Evaluation

`python -m src.cli benchmark` runs adversarial and analytical cases through the real pipeline. The evaluator reports executable SQL rate, table-selection accuracy, clarification accuracy, unsafe-request rejection, and latency. The JSON fixture is deliberately human-reviewable. Extension metrics include exact/semantic result accuracy, hallucinated-column rejection, suppression accuracy, statistical selection, numeric faithfulness, retry success, tokens, and estimated cost.

The included suite is a working seed benchmark, not a claim of clinical validity. Expand it with at least 40 reviewed cases before comparing models, stratify by category, pin database seed/version, and report confidence intervals.


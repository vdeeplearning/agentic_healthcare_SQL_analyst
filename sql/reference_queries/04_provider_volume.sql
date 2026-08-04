-- Question: What is provider volume? Shape: provider_id, specialty, encounters. Assumption: null providers excluded. Concepts: INNER JOIN, aggregation.
SELECT p.provider_id,p.specialty,COUNT(*) encounters FROM providers p JOIN encounters e ON e.provider_id=p.provider_id GROUP BY p.provider_id,p.specialty ORDER BY encounters DESC;

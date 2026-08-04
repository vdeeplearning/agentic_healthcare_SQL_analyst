-- Question: Which encounters cost more than $50,000? Shape: encounter_id, total_cost. Assumption: synthetic charges. Concepts: WHERE, parameterization, LIMIT.
SELECT encounter_id,total_cost FROM encounters WHERE total_cost>:minimum_cost ORDER BY total_cost DESC LIMIT 100;

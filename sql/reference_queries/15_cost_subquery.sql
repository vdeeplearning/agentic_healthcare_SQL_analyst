-- Question: Encounters above overall average cost. Shape: encounter, cost. Assumption: valid costs. Concepts: scalar subquery.
SELECT encounter_id,total_cost FROM encounters WHERE total_cost>(SELECT AVG(total_cost) FROM encounters) ORDER BY total_cost DESC LIMIT 100;

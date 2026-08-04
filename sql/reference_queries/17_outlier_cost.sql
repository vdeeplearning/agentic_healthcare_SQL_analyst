-- Question: Flag costs above three times the hospital mean. Shape: encounter, hospital, cost, mean. Assumption: heuristic only. Concepts: window average, anomaly detection.
WITH x AS (SELECT encounter_id,hospital_id,total_cost,AVG(total_cost) OVER(PARTITION BY hospital_id) hospital_mean FROM encounters) SELECT * FROM x WHERE total_cost>3*hospital_mean ORDER BY total_cost DESC LIMIT 100;

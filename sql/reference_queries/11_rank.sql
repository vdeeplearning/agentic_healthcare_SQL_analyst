-- Question: Rank hospitals by encounter cost. Shape: hospital, avg_cost, rank. Assumption: non-null costs. Concepts: RANK window.
SELECT h.hospital_name,AVG(e.total_cost) avg_cost,RANK() OVER(ORDER BY AVG(e.total_cost) DESC) cost_rank FROM hospitals h JOIN encounters e ON e.hospital_id=h.hospital_id GROUP BY h.hospital_id,h.hospital_name;

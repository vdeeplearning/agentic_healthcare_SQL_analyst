-- Question: Hospital complication rates with at least 30 cases. Shape: hospital, n, rate. Assumption: all encounters eligible. Concepts: HAVING.
SELECT h.hospital_name,COUNT(*) n,AVG(e.complication_flag) complication_rate FROM hospitals h JOIN encounters e ON e.hospital_id=h.hospital_id GROUP BY h.hospital_id,h.hospital_name HAVING COUNT(*)>=30 ORDER BY complication_rate DESC;

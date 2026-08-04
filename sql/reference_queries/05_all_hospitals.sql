-- Question: Include hospitals with zero encounters in a period. Shape: hospital_name, encounters. Assumption: zero fill. Concepts: LEFT JOIN, conditional join.
SELECT h.hospital_name,COUNT(e.encounter_id) encounters FROM hospitals h LEFT JOIN encounters e ON e.hospital_id=h.hospital_id AND e.admission_date>='2025-01-01' GROUP BY h.hospital_id,h.hospital_name;

-- Question: How many encounters occurred by type?
-- Shape: encounter_type, encounter_count. Assumption: all encounter rows are eligible. Concepts: SELECT, GROUP BY, ORDER BY.
SELECT encounter_type, COUNT(*) AS encounter_count FROM encounters GROUP BY encounter_type ORDER BY encounter_count DESC;

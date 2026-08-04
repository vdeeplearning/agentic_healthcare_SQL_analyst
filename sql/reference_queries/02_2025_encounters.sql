-- Question: How many encounters did each hospital have in 2025?
-- Shape: hospital_name, encounter_count. Assumption: admission date defines year. Concepts: JOIN, WHERE, GROUP BY.
SELECT h.hospital_name, COUNT(*) encounter_count FROM encounters e JOIN hospitals h ON h.hospital_id=e.hospital_id WHERE e.admission_date>='2025-01-01' AND e.admission_date<'2026-01-01' GROUP BY h.hospital_id,h.hospital_name ORDER BY encounter_count DESC;

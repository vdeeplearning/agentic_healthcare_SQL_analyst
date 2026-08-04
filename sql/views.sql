CREATE VIEW IF NOT EXISTS encounter_facts AS
SELECT e.*, h.hospital_name, h.urban_rural,
       CAST(julianday(e.discharge_date)-julianday(e.admission_date) AS INTEGER) AS length_of_stay
FROM encounters e JOIN hospitals h ON h.hospital_id=e.hospital_id;
CREATE VIEW IF NOT EXISTS hospital_readmission_summary AS
SELECT h.hospital_id, h.hospital_name, COUNT(r.index_encounter_id) AS eligible_encounters,
       SUM(r.readmitted_within_30_days) AS readmissions,
       1.0*SUM(r.readmitted_within_30_days)/NULLIF(COUNT(r.index_encounter_id),0) AS readmission_rate
FROM hospitals h LEFT JOIN encounters e ON e.hospital_id=h.hospital_id
LEFT JOIN readmissions r ON r.index_encounter_id=e.encounter_id GROUP BY h.hospital_id, h.hospital_name;

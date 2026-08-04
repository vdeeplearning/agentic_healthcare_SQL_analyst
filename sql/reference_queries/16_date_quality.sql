-- Question: Find suspicious negative stays. Shape: encounter, dates. Assumption: deliberate anomalies exist. Concepts: date calculations, data quality.
SELECT encounter_id,admission_date,discharge_date,julianday(discharge_date)-julianday(admission_date) los FROM encounters WHERE discharge_date<admission_date;

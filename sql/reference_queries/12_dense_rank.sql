-- Question: Dense-rank diagnoses by volume. Shape: diagnosis, volume, rank. Assumption: any-position diagnosis. Concepts: DENSE_RANK.
SELECT d.diagnosis_name,COUNT(*) volume,DENSE_RANK() OVER(ORDER BY COUNT(*) DESC) volume_rank FROM diagnoses d JOIN encounter_diagnoses ed ON ed.diagnosis_id=d.diagnosis_id GROUP BY d.diagnosis_id,d.diagnosis_name;

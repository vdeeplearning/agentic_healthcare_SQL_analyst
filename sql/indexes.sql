CREATE INDEX IF NOT EXISTS idx_encounters_dates ON encounters(admission_date, discharge_date);
CREATE INDEX IF NOT EXISTS idx_encounters_hospital ON encounters(hospital_id, admission_date);
CREATE INDEX IF NOT EXISTS idx_encounters_patient ON encounters(patient_id, admission_date);
CREATE INDEX IF NOT EXISTS idx_encounters_provider ON encounters(provider_id);
CREATE INDEX IF NOT EXISTS idx_ed_diagnosis ON encounter_diagnoses(diagnosis_id, encounter_id);
CREATE INDEX IF NOT EXISTS idx_readmissions_index ON readmissions(index_encounter_id, readmitted_within_30_days);
CREATE INDEX IF NOT EXISTS idx_quality_period ON quality_measures(measure_name, measurement_period_start);
CREATE INDEX IF NOT EXISTS idx_labs_encounter ON lab_results(encounter_id, lab_name);


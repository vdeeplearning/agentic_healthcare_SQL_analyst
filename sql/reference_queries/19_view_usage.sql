-- Question: Query the readmission summary view. Shape: hospital summary. Assumption: view definition controls eligibility. Concepts: views, ORDER BY.
SELECT hospital_name,eligible_encounters,readmissions,readmission_rate FROM hospital_readmission_summary ORDER BY readmission_rate DESC;

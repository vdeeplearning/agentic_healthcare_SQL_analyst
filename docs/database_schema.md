# Database schema

The normalized model separates people, facilities, providers, encounters, vocabulary, bridge tables, labs, readmission episodes, quarterly measures, and audit runs. Foreign keys are enabled on every connection. Composite keys prevent duplicate bridge rows; checks constrain flags, categories, rates, and denominators; indexes cover dates and common joins. `encounter_facts` and `hospital_readmission_summary` demonstrate reusable views.

The generator is seeded and introduces meaningful hospital, diagnosis, temporal, and comorbidity patterns. Deliberate anomalies include negative stays, missing demographic/disposition values, an inconsistent diagnosis code, null-heavy optional fields, and low-volume quality-measure groups. Nothing represents a real person or institution.


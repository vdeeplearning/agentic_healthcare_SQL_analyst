"""Known plans and SQL for credential-free demonstrations."""
from __future__ import annotations
from src.agent.schemas import AnalysisPlan

def _year(question:str)->str: return "2025" if "2025" in question else "2024" if "2024" in question else "2025"
def curated(question:str)->tuple[AnalysisPlan,str]|None:
    q=" ".join(question.lower().strip().split()); year=_year(q)
    if "structure of the dataset" in q or "dataset structure" in q or "database structure" in q:
        sql="""SELECT 'patients' AS table_name, 'synthetic patient demographics' AS purpose, COUNT(*) AS row_count FROM patients
UNION ALL SELECT 'hospitals','facility attributes',COUNT(*) FROM hospitals
UNION ALL SELECT 'providers','provider specialties and experience',COUNT(*) FROM providers
UNION ALL SELECT 'encounters','clinical and financial encounter facts',COUNT(*) FROM encounters
UNION ALL SELECT 'diagnoses','diagnosis vocabulary',COUNT(*) FROM diagnoses
UNION ALL SELECT 'encounter_diagnoses','encounter-to-diagnosis bridge',COUNT(*) FROM encounter_diagnoses
UNION ALL SELECT 'procedures','procedure vocabulary',COUNT(*) FROM procedures
UNION ALL SELECT 'encounter_procedures','encounter-to-procedure bridge',COUNT(*) FROM encounter_procedures
UNION ALL SELECT 'lab_results','encounter laboratory observations',COUNT(*) FROM lab_results
UNION ALL SELECT 'readmissions','30-day readmission assessments',COUNT(*) FROM readmissions
UNION ALL SELECT 'quality_measures','quarterly hospital quality metrics',COUNT(*) FROM quality_measures"""
        return AnalysisPlan(normalized_question=q,analysis_intent="summarize relational dataset structure",required_tables=["patients","hospitals","providers","encounters","diagnoses","encounter_diagnoses","procedures","encounter_procedures","lab_results","readmissions","quality_measures"],expected_columns=["table_name","purpose","row_count"]),sql
    if "how many patients" in q or "patient count" in q:
        return AnalysisPlan(normalized_question=q,analysis_intent="count synthetic patients",metric_name=None,required_tables=["patients"],expected_columns=["patient_count"]),"SELECT COUNT(*) AS patient_count FROM patients"
    if "how many hospitals" in q or "hospital count" in q:
        return AnalysisPlan(normalized_question=q,analysis_intent="count synthetic hospitals",metric_name=None,required_tables=["hospitals"],expected_columns=["hospital_count"]),"SELECT COUNT(*) AS hospital_count FROM hospitals"
    if "how many encounters" in q and ("hospital" in q or "each hospital" in q):
        return AnalysisPlan(normalized_question=q,analysis_intent="aggregate encounter volume by hospital",metric_name="encounter volume",date_range=(f"{year}-01-01",f"{year}-12-31"),dimensions=["hospital"],grouping_fields=["hospital_name"],ranking_direction="descending",required_tables=["encounters","hospitals"],expected_columns=["hospital_name","encounter_count"]),f"SELECT h.hospital_name, COUNT(*) AS encounter_count FROM encounters e JOIN hospitals h ON h.hospital_id=e.hospital_id WHERE e.admission_date >= '{year}-01-01' AND e.admission_date < '{int(year)+1}-01-01' GROUP BY h.hospital_id,h.hospital_name ORDER BY encounter_count DESC"
    if "readmission" in q and "heart failure" in q:
        sql=f"""WITH cohort AS (SELECT e.encounter_id,e.hospital_id,r.readmitted_within_30_days FROM encounters e JOIN encounter_diagnoses ed ON ed.encounter_id=e.encounter_id AND ed.primary_diagnosis_flag=1 JOIN diagnoses d ON d.diagnosis_id=ed.diagnosis_id JOIN readmissions r ON r.index_encounter_id=e.encounter_id WHERE d.diagnosis_code='I50.9' AND e.admission_date >= '{year}-01-01' AND e.admission_date < '{int(year)+1}-01-01') SELECT h.hospital_name,COUNT(*) AS denominator,SUM(c.readmitted_within_30_days) AS numerator,1.0*SUM(c.readmitted_within_30_days)/COUNT(*) AS readmission_rate FROM cohort c JOIN hospitals h ON h.hospital_id=c.hospital_id GROUP BY h.hospital_id,h.hospital_name HAVING COUNT(*)>=10 ORDER BY readmission_rate DESC"""
        return AnalysisPlan(normalized_question=q,analysis_intent="rank heart failure readmission rates",metric_name="30-day readmission rate",date_range=(f"{year}-01-01",f"{year}-12-31"),dimensions=["hospital"],grouping_fields=["hospital_name"],ranking_direction="descending",required_tables=["encounters","encounter_diagnoses","diagnoses","readmissions","hospitals"],expected_columns=["hospital_name","denominator","numerator","readmission_rate"]),sql
    if "diagnos" in q and ("highest total cost" in q or "total cost" in q):
        return AnalysisPlan(normalized_question=q,analysis_intent="rank diagnoses by total encounter cost",metric_name="total encounter cost",dimensions=["diagnosis"],grouping_fields=["diagnosis_name"],ranking_direction="descending",required_tables=["encounters","encounter_diagnoses","diagnoses"],expected_columns=["diagnosis_name","encounter_count","total_cost"]),"SELECT d.diagnosis_name,COUNT(*) AS encounter_count,ROUND(SUM(e.total_cost),2) AS total_cost FROM encounters e JOIN encounter_diagnoses ed ON ed.encounter_id=e.encounter_id AND ed.primary_diagnosis_flag=1 JOIN diagnoses d ON d.diagnosis_id=ed.diagnosis_id GROUP BY d.diagnosis_id,d.diagnosis_name ORDER BY total_cost DESC"
    if "complication" in q and ("30" in q or "unusually high" in q):
        return AnalysisPlan(normalized_question=q,analysis_intent="rank hospital complication rates with minimum volume",metric_name="complication rate",dimensions=["hospital"],grouping_fields=["hospital_name"],minimum_group_size=30,ranking_direction="descending",required_tables=["encounters","hospitals"],expected_columns=["hospital_name","denominator","numerator","complication_rate"]),"SELECT h.hospital_name,COUNT(*) AS denominator,SUM(e.complication_flag) AS numerator,1.0*SUM(e.complication_flag)/COUNT(*) AS complication_rate FROM encounters e JOIN hospitals h ON h.hospital_id=e.hospital_id GROUP BY h.hospital_id,h.hospital_name HAVING COUNT(*)>=30 ORDER BY complication_rate DESC"
    if "urban" in q and "rural" in q and "readmission" in q:
        return AnalysisPlan(normalized_question=q,analysis_intent="compare readmission proportions by location",metric_name="30-day readmission rate",dimensions=["urban_rural"],grouping_fields=["urban_rural"],requires_statistical_test=True,statistical_test_type="chi_square",required_tables=["encounters","hospitals","readmissions"],expected_columns=["urban_rural","denominator","numerator","readmission_rate"]),"SELECT h.urban_rural,COUNT(*) AS denominator,SUM(r.readmitted_within_30_days) AS numerator,1.0*SUM(r.readmitted_within_30_days)/COUNT(*) AS readmission_rate FROM encounters e JOIN hospitals h ON h.hospital_id=e.hospital_id JOIN readmissions r ON r.index_encounter_id=e.encounter_id GROUP BY h.urban_rural ORDER BY h.urban_rural"
    return None

EXAMPLES=["What is the structure of the dataset?","How many patients are in the dataset?","How many encounters occurred at each hospital in 2025?","Which hospitals had the highest 30-day readmission rates for heart failure in 2025?","Which diagnoses account for the highest total cost?","Which hospitals have unusually high complication rates after excluding hospitals with fewer than 30 eligible cases?","Is the readmission rate significantly different between urban and rural hospitals?"]

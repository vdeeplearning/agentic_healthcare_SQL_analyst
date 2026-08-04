"""Deterministic, entirely fictional healthcare data generator."""
from __future__ import annotations
import argparse
import sqlite3
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import numpy as np
from src.database.connection import connect_writable

ROOT = Path(__file__).resolve().parents[2]
DIAGNOSES = [
 (1,"I50.9","Heart failure","cardiovascular"),(2,"E11.9","Type 2 diabetes","endocrine"),
 (3,"N18.9","Chronic kidney disease","renal"),(4,"J18.9","Pneumonia","respiratory"),
 (5,"I10","Hypertension","cardiovascular"),(6,"A41.9","Sepsis","infectious"),
 (7,"J44.1","COPD exacerbation","respiratory"),(8,"S72.0","Hip fracture","injury"),
 (9,"R07.9","Chest pain","symptom"),(10,"X99.?","Inconsistent test code","data_quality")]
PROCEDURES = [(1,"PROC001","Echocardiogram","diagnostic"),(2,"PROC002","CT scan","imaging"),(3,"PROC003","Dialysis","therapeutic"),(4,"PROC004","Cardiac catheterization","therapeutic")]


def _script(connection: sqlite3.Connection, name: str) -> None:
    connection.executescript((ROOT / "sql" / name).read_text(encoding="utf-8"))


def generate_database(path: Path, seed: int = 42, patients: int = 25_000, encounters: int = 100_000) -> dict[str, int]:
    """Rebuild the database reproducibly. Existing target is replaced intentionally."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    rng = np.random.default_rng(seed)
    connection = connect_writable(path)
    _script(connection, "schema.sql")
    states = ["NY","PA","OH","NC","GA","IL"]
    hospital_rows = []
    for hospital_id in range(1, 31):
        rural = hospital_id > 22
        hospital_rows.append((hospital_id, f"Synthetic {'Regional' if rural else 'Medical'} Center {hospital_id:02d}", states[(hospital_id-1)%len(states)], "rural" if rural else "urban", int(rng.integers(25,180) if rural else rng.integers(180,900)), "teaching" if hospital_id%3==0 else "non-teaching", ["nonprofit","public","for-profit"][hospital_id%3]))
    connection.executemany("INSERT INTO hospitals VALUES (?,?,?,?,?,?,?)", hospital_rows)
    specialties = ["hospitalist","cardiology","emergency","endocrinology","nephrology","surgery"]
    provider_rows = [(i, (i-1)%30+1, specialties[i%len(specialties)], int(rng.integers(1,41))) for i in range(1,201)]
    connection.executemany("INSERT INTO providers VALUES (?,?,?,?)", provider_rows)
    start_birth = date(1925,1,1)
    patient_rows=[]
    for patient_id in range(1, patients+1):
        birth = start_birth + timedelta(days=int(rng.integers(0, 85*365)))
        race = rng.choice(["White","Black","Hispanic","Asian","Other",None], p=[.46,.2,.18,.09,.05,.02])
        patient_rows.append((patient_id,birth.isoformat(),rng.choice(["F","M","X"],p=[.505,.49,.005]),race,rng.choice(["commercial","medicare","medicaid","self-pay"],p=[.39,.35,.21,.05]),rng.choice(["north","south","east","west",None],p=[.24,.24,.24,.24,.04]),"2023-01-01T00:00:00Z"))
    connection.executemany("INSERT INTO patients VALUES (?,?,?,?,?,?,?)", patient_rows)
    connection.executemany("INSERT INTO diagnoses VALUES (?,?,?,?)", DIAGNOSES)
    connection.executemany("INSERT INTO procedures VALUES (?,?,?,?)", PROCEDURES)
    provider_by_hospital={h:[p[0] for p in provider_rows if p[1]==h] for h in range(1,31)}
    encounter_rows=[]; diagnosis_rows=[]; procedure_rows=[]; lab_rows=[]
    first = date(2023,1,1)
    for encounter_id in range(1, encounters+1):
        patient_id=int(rng.integers(1,patients+1)); hospital_id=int(rng.integers(1,31))
        provider_id=int(rng.choice(provider_by_hospital[hospital_id])); kind=str(rng.choice(["inpatient","emergency","outpatient"],p=[.37,.35,.28]))
        day=int(rng.integers(0,1095)); admission=first+timedelta(days=day)
        primary=int(rng.choice(np.arange(1,10),p=[.14,.16,.10,.13,.13,.08,.09,.06,.11]))
        base_los={"inpatient":4,"emergency":1,"outpatient":0}[kind]
        los=max(0,int(rng.poisson(base_los + (2 if primary in (1,6) else 0))))
        discharge=admission+timedelta(days=los)
        # Deliberate suspicious date combinations are isolated to 0.01% for validator demonstrations.
        if encounter_id % 10000 == 0: discharge=admission-timedelta(days=1)
        hospital_risk=(hospital_id%7-3)*.004; complication=float(rng.random() < max(.005,.035+hospital_risk+.03*(primary==6)))
        mortality=float(rng.random() < max(.001,.012+hospital_risk+.035*(primary==6)))
        cost=max(100.0,float(rng.lognormal(8.2+.18*los+.25*(primary in (1,3,6)),.55)))
        disposition="expired" if mortality else str(rng.choice(["home","skilled nursing","rehabilitation",None],p=[.75,.12,.1,.03]))
        encounter_rows.append((encounter_id,patient_id,hospital_id,provider_id,kind,admission.isoformat(),discharge.isoformat(),disposition,round(cost,2),int(mortality),int(complication)))
        diagnosis_rows.append((encounter_id,primary,1,1))
        if rng.random()<.36:
            secondary=int(rng.choice([2,3,5]));
            if secondary != primary: diagnosis_rows.append((encounter_id,secondary,2,0))
        if rng.random()<.18: procedure_rows.append((encounter_id,int(rng.integers(1,5)),admission.isoformat()))
        if rng.random()<.22:
            value=float(rng.normal(110+25*(primary==2),28)); lab_rows.append((None,encounter_id,"glucose",round(value,1),"mg/dL",70.0,110.0,admission.isoformat()+"T08:00:00"))
        if len(encounter_rows)>=5000:
            connection.executemany("INSERT INTO encounters VALUES (?,?,?,?,?,?,?,?,?,?,?)", encounter_rows); encounter_rows=[]
            connection.executemany("INSERT INTO encounter_diagnoses VALUES (?,?,?,?)", diagnosis_rows); diagnosis_rows=[]
            connection.executemany("INSERT OR IGNORE INTO encounter_procedures VALUES (?,?,?)", procedure_rows); procedure_rows=[]
            connection.executemany("INSERT INTO lab_results VALUES (?,?,?,?,?,?,?,?)", lab_rows); lab_rows=[]
    if encounter_rows: connection.executemany("INSERT INTO encounters VALUES (?,?,?,?,?,?,?,?,?,?,?)", encounter_rows)
    if diagnosis_rows: connection.executemany("INSERT INTO encounter_diagnoses VALUES (?,?,?,?)", diagnosis_rows)
    if procedure_rows: connection.executemany("INSERT OR IGNORE INTO encounter_procedures VALUES (?,?,?)", procedure_rows)
    if lab_rows: connection.executemany("INSERT INTO lab_results VALUES (?,?,?,?,?,?,?,?)", lab_rows)
    # Deterministic risk-informed readmission flags; links are optional to avoid manufacturing false chronology.
    primary_by_enc=dict(connection.execute("SELECT encounter_id, diagnosis_id FROM encounter_diagnoses WHERE primary_diagnosis_flag=1"))
    readmission_rows=[]
    eligible=connection.execute("SELECT encounter_id,hospital_id,patient_id,admission_date FROM encounters WHERE encounter_type='inpatient'").fetchall()
    for rid,(eid,hid,pid,admit) in enumerate(eligible,1):
        risk=.09+.07*(primary_by_enc.get(eid) in (1,6))+.035*(primary_by_enc.get(eid)==3)+(hid%6)*.008
        readmitted=int(rng.random()<risk); days=int(rng.integers(2,31)) if readmitted else None
        readmission_rows.append((rid,eid,None,days,readmitted))
    connection.executemany("INSERT INTO readmissions VALUES (?,?,?,?,?)",readmission_rows)
    qrows=[]; qid=1
    for year in (2024,2025):
        for quarter in range(1,5):
            month=(quarter-1)*3+1; start=date(year,month,1); end=date(year+1,1,1)-timedelta(days=1) if quarter==4 else date(year,month+3,1)-timedelta(days=1)
            for hid in range(1,31):
                den=int(rng.integers(8,45) if hid>=28 else rng.integers(80,350)); trend=-.006*(year-2024)*4-.004*(quarter-1)
                rate=float(np.clip(.08+(hid%6)*.012+trend+rng.normal(0,.008),.02,.35)); num=int(round(den*rate))
                qrows.append((qid,hid,"30-day readmission rate",start.isoformat(),end.isoformat(),num,den,num/den)); qid+=1
    connection.executemany("INSERT INTO quality_measures VALUES (?,?,?,?,?,?,?,?)",qrows)
    _script(connection,"indexes.sql"); _script(connection,"views.sql")
    connection.commit(); connection.execute("PRAGMA optimize"); connection.close()
    return {"patients":patients,"hospitals":30,"providers":200,"encounters":encounters,"readmissions":len(readmission_rows)}


def main() -> None:
    parser=argparse.ArgumentParser(); parser.add_argument("--path",type=Path,default=Path("data/generated/clinical.db")); parser.add_argument("--seed",type=int,default=42); parser.add_argument("--patients",type=int,default=25_000); parser.add_argument("--encounters",type=int,default=100_000)
    args=parser.parse_args(); print(generate_database(args.path,args.seed,args.patients,args.encounters))

if __name__ == "__main__": main()

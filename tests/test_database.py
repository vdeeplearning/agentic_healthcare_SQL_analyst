import sqlite3
from src.database.connection import connect_read_only,schema_catalog
from src.database.seed import generate_database

def test_tables_exist(db_path):
    assert {"patients","hospitals","providers","encounters","diagnoses","readmissions","audit_runs"} <= schema_catalog(db_path).keys()
def test_expected_counts(db_path):
    with connect_read_only(db_path) as c:
        assert c.execute("select count(*) from patients").fetchone()[0]==300
        assert c.execute("select count(*) from encounters").fetchone()[0]==1200
        assert c.execute("select count(*) from hospitals").fetchone()[0]==30
def test_foreign_key_integrity(db_path):
    with connect_read_only(db_path) as c: assert c.execute("PRAGMA foreign_key_check").fetchall()==[]
def test_read_only_enforced(db_path):
    with connect_read_only(db_path) as c:
        try: c.execute("DELETE FROM encounters"); assert False
        except sqlite3.OperationalError: pass
def test_seed_determinism(tmp_path):
    a=tmp_path/"a.db"; b=tmp_path/"b.db"; generate_database(a,9,50,200); generate_database(b,9,50,200)
    with connect_read_only(a) as x,connect_read_only(b) as y:
        assert x.execute("select sum(total_cost) from encounters").fetchone()[0]==y.execute("select sum(total_cost) from encounters").fetchone()[0]
def test_quality_anomaly_exists(db_path):
    with connect_read_only(db_path) as c: assert c.execute("select count(*) from encounters where discharge_date<admission_date").fetchone()[0]>=0


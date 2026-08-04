from pathlib import Path
import pytest
from src.database.seed import generate_database
@pytest.fixture(scope="session")
def db_path(tmp_path_factory)->Path:
    path=tmp_path_factory.mktemp("data")/"test.db"; generate_database(path,17,patients=300,encounters=1200); return path


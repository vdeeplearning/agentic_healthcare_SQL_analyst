.PHONY: install seed demo test api ui benchmark docker
install:
	python -m pip install -e ".[dev]"
seed:
	python -m src.database.seed
demo:
	python -m src.database.seed --patients 2500 --encounters 10000
test:
	python -m pytest
api:
	uvicorn src.api.main:app --reload
ui:
	streamlit run app.py
benchmark:
	python -m src.cli benchmark
docker:
	docker compose up --build


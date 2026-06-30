.PHONY: install up down dev migrate format test bench init

install:
	pip install -r requirements.txt

init:
	mkdir -p data uploads logs sample_documents benchmark_outputs temporary_files

dev:
	uvicorn app.api.main:app --reload

up:
	docker compose up --build -d

down:
	docker compose down

migrate:
	alembic revision --autogenerate -m "auto"
	alembic upgrade head

format:
	black app tests scripts
	ruff check app tests scripts --fix

test:
	pytest tests/ -v

bench:
	python scripts/benchmark_suite.py

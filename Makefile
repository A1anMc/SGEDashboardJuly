.PHONY: install frontend backend dev test lint format db-reset

install:
	pip install -r requirements.txt
	cd frontend && npm install

frontend:
	cd frontend && npm run dev

backend:
	PYTHONPATH=. uvicorn app.main:app --reload

dev:
	make backend & make frontend

test:
	pytest
	cd frontend && npm run test

lint:
	ruff . && pylint .
	cd frontend && npm run lint

format:
	black . && isort .
	cd frontend && npm run format

db-reset:
	alembic downgrade base
	alembic upgrade head 
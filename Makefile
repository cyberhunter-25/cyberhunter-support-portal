# CyberHunter Security Portal Makefile

.PHONY: help install dev test lint security-check migrate run docker-build docker-up clean

help:
	@echo "CyberHunter Security Portal - Available Commands:"
	@echo "  make install       - Install all dependencies"
	@echo "  make dev          - Run development server"
	@echo "  make test         - Run all tests"
	@echo "  make lint         - Run code linting"
	@echo "  make security     - Run security checks"
	@echo "  make migrate      - Run database migrations"
	@echo "  make docker-build - Build Docker images"
	@echo "  make docker-up    - Start Docker containers"
	@echo "  make clean        - Clean up cache files"

install:
	python -m venv venv
	. venv/bin/activate && pip install --upgrade pip
	. venv/bin/activate && pip install -r requirements/dev.txt
	. venv/bin/activate && pre-commit install

dev:
	. venv/bin/activate && flask run --debug --host=0.0.0.0 --port=5000

test:
	. venv/bin/activate && pytest tests/ -v --cov=app --cov-report=html

test-unit:
	. venv/bin/activate && pytest tests/unit/ -v

test-integration:
	. venv/bin/activate && pytest tests/integration/ -v

test-security:
	. venv/bin/activate && pytest tests/security/ -v

lint:
	. venv/bin/activate && black app/ tests/
	. venv/bin/activate && isort app/ tests/
	. venv/bin/activate && flake8 app/ tests/
	. venv/bin/activate && mypy app/

security:
	. venv/bin/activate && bandit -r app/
	. venv/bin/activate && safety check
	. venv/bin/activate && pip-audit

migrate:
	. venv/bin/activate && flask db upgrade

migrate-init:
	. venv/bin/activate && flask db init
	. venv/bin/activate && flask db migrate -m "Initial migration"

celery:
	. venv/bin/activate && celery -A app.celery worker --loglevel=info

celery-beat:
	. venv/bin/activate && celery -A app.celery beat --loglevel=info

redis:
	redis-server

docker-build:
	docker-compose -f docker/docker-compose.yml build

docker-up:
	docker-compose -f docker/docker-compose.yml up -d

docker-down:
	docker-compose -f docker/docker-compose.yml down

docker-logs:
	docker-compose -f docker/docker-compose.yml logs -f

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".DS_Store" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf .mypy_cache

setup-db:
	. venv/bin/activate && python scripts/setup_database.py

create-admin:
	. venv/bin/activate && flask create-admin

backup:
	./scripts/backup.sh

deploy:
	./scripts/deploy.sh
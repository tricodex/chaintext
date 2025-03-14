.PHONY: setup run test lint docker-build docker-run docker-stop clean docker-clean

# Environment variables
PYTHON := python
UV := uv
PYTEST := pytest
APP_NAME := chaincontext-backend
PORT := 8000

# Commands
setup:
	$(PYTHON) -m venv .venv
	. .venv/bin/activate && pip install $(UV) && $(UV) pip install -r requirements.txt
	@if [ ! -f .env ]; then cp .env.example .env; fi

run:
	$(PYTHON) run.py

test:
	$(PYTEST) -v

lint:
	black app tests
	flake8 app tests

docker-build:
	docker build -t $(APP_NAME) .

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down

clean:
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	find . -type d -name "*.egg" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	rm -rf dist build .coverage htmlcov

docker-clean: docker-stop
	docker rmi $(APP_NAME)

help:
	@echo "Available commands:"
	@echo "  setup         - Create virtual environment and install dependencies"
	@echo "  run           - Run the ChainContext API server"
	@echo "  test          - Run tests"
	@echo "  lint          - Run code linters"
	@echo "  docker-build  - Build Docker image"
	@echo "  docker-run    - Run with Docker Compose"
	@echo "  docker-stop   - Stop Docker containers"
	@echo "  clean         - Clean Python cache files"
	@echo "  docker-clean  - Stop containers and remove images"

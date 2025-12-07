PHONY: venv check-deps update-deps install-deps isort black mypy flake8 bandit lint test migrate serve


VENV=.venv
PYTHON=PYTHONPATH=$(pwd) $(VENV)/bin/python3

venv: requirements-dev.txt Makefile
	python3 -m pip install --upgrade pip setuptools wheel
	python3 -m venv $(VENV)
	$(PYTHON) -m pip install -r requirements-dev.txt

check-deps:
	$(PYTHON) -m pur -r requirements-dev.txt -d

update-deps:
	$(PYTHON) -m pur -r requirements-dev.txt

install-deps:
	$(PYTHON) -m pip install -r requirements-dev.txt

isort:
	$(PYTHON) -m isort --check-only .

black:
	$(PYTHON) -m black --check .

mypy:
	$(PYTHON) -m mypy .

flake8:
	$(PYTHON) -m flake8 .

bandit:
	$(PYTHON) -m bandit -r app

lint: isort black mypy flake8 bandit

test:
	$(PYTHON) -m pytest

migrate:
	$(PYTHON) -m alembic upgrade head

serve:
	$(PYTHON) -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
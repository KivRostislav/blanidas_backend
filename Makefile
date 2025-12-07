PHONY: venv check-deps update-deps install-deps isort black mypy flake8 bandit lint test migrate serve

VENV=.venv
PYTHON=$(VENV)/bin/python3
PIP=$(VENV)/bin/pip
export PYTHONPATH := $(PWD)

# --- Створення віртуального середовища та встановлення залежностей ---
venv: requirements-dev.txt Makefile
	python3 -m pip install --upgrade pip setuptools wheel
	python3 -m venv $(VENV)
	$(PIP) install -r requirements-dev.txt

check-deps:
	$(PYTHON) -m pur -r requirements-dev.txt -d

update-deps:
	$(PYTHON) -m pur -r requirements-dev.txt

install-deps:
	$(PIP) install -r requirements-dev.txt

# --- Статичний аналіз ---
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

# --- Тести ---
test:
	$(PYTHON) -m pytest

# --- Міграції ---
migrate:
	PYTHONPATH=$(PWD) $(PYTHON) -m alembic upgrade head

# --- Сервер ---
serve:
	PYTHONPATH=$(PWD) $(PYTHON) -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

PY3 := python3
VENV := venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
FLAKE8 := $(VENV)/bin/flake8
ACTIVEV := $(VENV)/bin/activate
MYPY := $(VENV)/bin/mypy
MYPY_FLAGS := --warn-return-any --warn-unused-ignores \
              --ignore-missing-imports --disallow-untyped-defs \
              --check-untyped-defs

CONFIG := config.txt
.PHONY: help install run debug clean lint lint-strict

help:
	@echo "make install  create venv/ and install dev tools"
	@echo "make run          generate and display a maze"
	@echo "make debug        same, under the pdb debugger"
	@echo "make lint         flake8 + mypy with the required flags"
	@echo "make lint-strict  flake8 + mypy --strict"
	@echo "make clean        remove caches"

$(ACTIVEV): requirements.txt
	$(PY3) -m venv $(VENV)
	$(PIP) install -r requirements.txt

run: $(ACTIVEV)
	$(PYTHON) fly_in.py $(CONFIG)

install: $(ACTIVEV)
	@echo "Venv already installed"

debug: $(ACTIVEV)
	$(PYTHON) -m pdb fly_in.py $(CONFIG)

clean:
	find . -type d -name __pycache__ -exec rm -fr {} +
	rm -fr .mypy_cache
	rm -f .coverage

lint: $(ACTIVEV)
	$(FLAKE8) . 
	$(MYPY) . $(MYPY_FLAGS)

lint-strict: $(ACTIVEV)
	$(FLAKE8) .
	$(MYPY) . --strict


PYTHON ?= .venv/bin/python
PYTHON_JUP ?= .venv_jup/bin/python
PYTHON_PRE ?= ../.venv/bin/python

install:
	python3 -m venv .venv
	$(PYTHON) -m pip install poetry
	poetry update

	python3 -m venv .venv_jup
	$(PYTHON_JUP) -m pip install -r src/jup-requirements.txt

jup:
	$(PYTHON_JUP) -m jupyterlab

jup-darwin:
	$(PYTHON_JUP) -m jupyterlab --app-dir=/opt/homebrew/share/jupyter/lab

train:
	cd src && $(PYTHON_PRE) -m rasa train

run: 
	LOGURU_LEVEL=DEBUG cd src && $(PYTHON_PRE) -m rasa run actions

shell: 
	cd src && $(PYTHON_PRE) -m rasa shell

help: 
	cd src && $(PYTHON_PRE) -m rasa

test: 
	cd src && $(PYTHON_PRE) -m pytest -s

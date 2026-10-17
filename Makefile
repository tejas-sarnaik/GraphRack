PYTHON ?= python
.PHONY: install test lint demo
install:
	$(PYTHON) -m pip install -e '.[dev]'
test:
	$(PYTHON) -m pytest -q
lint:
	ruff check src tests
demo:
	graphrack index examples/docs --out index.json
	graphrack ask "Which benchmark evaluates Aurora?" --index index.json

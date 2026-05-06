.PHONY: install lint test build smoke schema examples clean

install:
	python -m pip install -e ".[dev]"

test:
	pytest

lint:
	ruff check .

build:
	python -m build

smoke:
	reportforge validate examples/acme_authorized_pentest.yaml --strict
	reportforge list-findings examples/acme_authorized_pentest.yaml
	reportforge metrics examples/acme_authorized_pentest.yaml
	reportforge doctor

schema:
	reportforge schema --output docs/reportforge.schema.json

examples:
	reportforge export examples/acme_authorized_pentest.yaml --format markdown --output reports/acme-report.md
	reportforge export examples/acme_authorized_pentest.yaml --format html --output reports/acme-report.html
	reportforge export examples/acme_authorized_pentest.yaml --format pdf --output reports/acme-report.pdf
	reportforge export examples/acme_authorized_pentest.yaml --format json --output reports/acme-report.json

clean:
	rm -rf .pytest_cache .ruff_cache .mypy_cache htmlcov .coverage dist build *.egg-info
	find . -type d -name __pycache__ -prune -exec rm -rf {} +

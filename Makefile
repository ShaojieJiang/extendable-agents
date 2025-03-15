lint:
	ruff check .
	mypy .
	ruff format . --check

format:
	ruff format .

test:
	pytest --cov --cov-report term-missing tests/

doc:
	mkdocs serve --dev-addr=0.0.0.0:8080

lint:
	ruff check .
	mypy .
	ruff format . --check

format:
	ruff format .
	ruff check . --select I001 --fix
	ruff check . --select F401 --fix

test:
	pytest --cov --cov-report term-missing tests/

doc:
	mkdocs serve --dev-addr=0.0.0.0:8080

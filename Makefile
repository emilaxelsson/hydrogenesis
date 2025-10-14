type-check:
	mypy src/ test/

doctest:
	python3 -m doctest src/*.py

unit-tests:
	PYTHONPATH=src pytest

all-tests: doctest unit-tests

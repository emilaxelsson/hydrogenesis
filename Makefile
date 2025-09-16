type-check:
	mypy src/ test/

doctest:
	python3 -m doctest src/*.py

unit-tests:
	PYTHONPATH=src python3 -m unittest discover -s test

all-tests: doctest unit-tests

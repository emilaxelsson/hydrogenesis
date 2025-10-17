type-check:
	mypy src/ test/

doctest:
	python3 -m doctest src/*.py

unit-tests:
	PYTHONPATH=src pytest --color=yes

all-tests: doctest unit-tests

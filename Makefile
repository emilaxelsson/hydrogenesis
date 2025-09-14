type-check:
	mypy src/

doctest:
	python3 -m doctest src/*.py

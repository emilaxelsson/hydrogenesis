from collections import Counter
from typing import TypeVar

T = TypeVar("T")


# https://www.geeksforgeeks.org/python/how-to-find-duplicates-in-a-list-python/
def find_duplicates(l: list[T]) -> list[T]:
    """
    >>> find_duplicates(["A", "B", "C"])
    []
    >>> find_duplicates(["A", "B", "A", "A", "C"])
    ['A']
    """
    counts = Counter(l)
    return [item for item, count in counts.items() if count > 1]

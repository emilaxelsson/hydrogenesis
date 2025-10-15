from typing import TypeVar
from hypothesis import given, strategies as st

from utils import find_duplicates


T = TypeVar("T")


@given(st.lists(st.integers()))
def test_find_duplicates_finds_duplicates(ns: list[T]):
    dups = find_duplicates(ns)
    assert all(ns.count(x) > 1 for x in dups)

@given(st.lists(st.integers()))
def test_find_duplicates_finds_all_duplicates(ns: list[T]):
    dups = find_duplicates(ns)
    rest = [n for n in ns if n not in dups]
    assert all(rest.count(x) == 1 for x in rest)

@given(st.lists(st.integers()))
def test_find_duplicates_reports_each_duplicate_once(ns: list[T]):
    dups = find_duplicates(ns)
    dupsdups = find_duplicates(dups)
    assert len(dupsdups) == 0

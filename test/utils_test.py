from hypothesis import assume, given, strategies as st

from utils import uniquify_names


@st.composite
def gen_name(draw: st.DrawFn) -> str:
    return draw(st.text(alphabet=["A", "B", "0", "1"], min_size=2, max_size=3))


@given(st.lists(gen_name()))
def test_list_of_names_sometimes_contains_dups(names: list[str]):
    assume(len(names) > len(set(names)))
    assert True


@given(st.lists(gen_name()))
def test_list_of_names_sometimes_contains_no_dups(names: list[str]):
    assume(len(names) == len(set(names)))
    assert True


@given(st.lists(gen_name()))
def test_uniquify_names_is_idempotent(names: list[str]):
    unique_names = uniquify_names(names)
    assert uniquify_names(unique_names) == unique_names


@given(st.lists(gen_name()))
def test_uniquify_names_returns_unique_names(names: list[str]):
    unique_names = uniquify_names(names)
    assert len(unique_names) == len(set(unique_names))


@given(st.lists(gen_name()))
def test_uniquify_names_retains_original_names(names: list[str]):
    new_names = uniquify_names(names)
    assert set(names).issubset(new_names)


def test_uniquify_names_example1():
    names = [
        "Apa",
        "Bepa",
        "Apa",
        "Apa",
        "Apa",
    ]
    assert uniquify_names(names) == ["Apa", "Bepa", "Apa1", "Apa2", "Apa3"]


def test_uniquify_names_example2():
    names = [
        "Apa2",
        "Bepa",
        "Apa",
        "Apa",
        "Apa",
        "Apa",
    ]
    assert uniquify_names(names) == ["Apa2", "Bepa", "Apa", "Apa1", "Apa3", "Apa4"]


def test_uniquify_names_example3():
    names = [
        "Apa2",
        "Bepa",
        "Apa2",
        "Apa2",
    ]
    assert uniquify_names(names) == ["Apa2", "Bepa", "Apa21", "Apa22"]

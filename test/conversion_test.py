from fractions import Fraction
from hypothesis import assume, given, strategies as st
from hypothesis.strategies import SearchStrategy
from pathlib import Path
import pytest
from typing import Optional, Tuple, TypeVar

from conversion import (
    BPMOp,
    TempoChange,
    convert_key,
    convert_note,
    convert_track,
    convert_volume,
    interpret_tempo_command,
    slice_pattern,
)
import hydrogen_format as hydrogen
from logger import SilentLogger
import mptm_format as mptm
from mptm_parser import Parser


T = TypeVar("T")


# Selects `None` with a probability of 10%
def optional(strategy: SearchStrategy[T]) -> SearchStrategy[Optional[T]]:
    return st.one_of(st.none(), *([strategy] * 9))


@given(st.integers(min_value=0))
def test_convert_volume_range(vol_pan: int):
    velocity = convert_volume(vol_pan)
    assert velocity >= 0
    assert velocity <= 1


@given(st.integers(min_value=0))
def test_convert_volume_monotonous(vol_pan: int):
    vel = convert_volume(vol_pan)

    if vol_pan > 0 and vol_pan < 64:
        assert vel > convert_volume(vol_pan - 1)
        assert vel < convert_volume(vol_pan + 1)

    if vol_pan == 0:
        assert vel == 0

    if vol_pan >= 64:
        assert vel == 1


@given(st.integers(max_value=-1))
def test_convert_volume_negative(vol_pan: int):
    with pytest.raises(ValueError):
        convert_volume(vol_pan)


@given(st.integers(min_value=0, max_value=119))
def test_convert_key(k: int):
    (key, octave) = convert_key(k)
    assert k == 12 * (octave + 3) + key


@given(st.integers(max_value=-1))
def test_convert_key_out_of_range1(k: int):
    with pytest.raises(ValueError):
        convert_key(k)


@given(st.integers(min_value=120))
def test_convert_key_out_of_range2(k: int):
    with pytest.raises(ValueError):
        convert_key(k)


@st.composite
def gen_command(draw: st.DrawFn) -> mptm.Command:
    # c1=20 is a tempo change
    c1 = draw(st.integers(min_value=15, max_value=25))
    c2 = draw(st.integers(min_value=0, max_value=255))
    return mptm.Command(
        c1=c1,
        c2=c2,
    )


@st.composite
def gen_cell(draw: st.DrawFn) -> mptm.Cell:
    instrument = draw(optional(st.integers()))
    note = draw(optional(st.integers(min_value=0, max_value=119)))
    vol_pan = draw(optional(st.integers(min_value=0, max_value=255)))
    command = draw(optional(gen_command()))
    return mptm.Cell(
        instrument=instrument,
        note=note,
        vol_pan=vol_pan,
        command=command,
    )


def note_to_cell(note: hydrogen.Note) -> mptm.Cell:
    return mptm.Cell(
        instrument=note.instrument + 1,
        note=12 * (note.octave + 3) + note.key,
        vol_pan=round(note.velocity * 64.0),
        command=None,
    )


@given(gen_cell())
def test_cell_to_note_roundrip(cell: mptm.Cell):
    vol_pan = cell.vol_pan
    if cell.vol_pan is None or cell.vol_pan > 64:
        vol_pan = 64

    adjusted_cell = mptm.Cell(
        instrument=cell.instrument,
        note=cell.note,
        vol_pan=vol_pan,
        command=None,
    )

    note = convert_note(Fraction(0), adjusted_cell)

    assume(note)
    assert note

    assert adjusted_cell == note_to_cell(note)


def to_int_or_none(s: str) -> Optional[int]:
    """
    to_int_or_none("1")
    1
    to_int_or_none("123")
    123
    to_int_or_none("")
    None
    to_int_or_none("abc")
    None
    """
    try:
        return int(s)
    except (TypeError, ValueError):
        return None


def split_pattern_name(name: str) -> Tuple[str, Optional[int]]:
    """
    >>> split_pattern_name("Apa")
    ('Apa', None)
    >>> split_pattern_name("Apa2")
    ('Apa2', None)
    >>> split_pattern_name("Apa#22")
    ('Apa', 22)
    >>> split_pattern_name("")
    ('', None)
    >>> split_pattern_name("Apa#Bepa")
    ('Apa', None)
    """
    frukt = name.split("#", 1)
    subscript = to_int_or_none(frukt[1]) if len(frukt) > 1 else None
    return (frukt[0], subscript)


def base_pattern_name(name: str) -> str:
    return split_pattern_name(name)[0]


# Merge each sequence of patterns with names "foo#0", "foo#1", etc. into a single pattern
# named "foo"
def unsplit_patterns(patterns: list[hydrogen.Pattern]) -> list[hydrogen.Pattern]:
    def set_base_name(pattern: hydrogen.Pattern) -> hydrogen.Pattern:
        return hydrogen.Pattern(
            size=pattern.size,
            name=base_pattern_name(pattern.name),
            notes=pattern.notes,
        )

    def merge(p1: hydrogen.Pattern, p2: hydrogen.Pattern) -> hydrogen.Pattern:
        return hydrogen.Pattern(
            size=p1.size + p2.size,
            name=p1.name,
            notes=p1.notes + p2.notes,
        )

    if patterns:
        first_pattern = patterns[0]
        patterns1 = patterns[1:]
    else:
        return []

    merged_patterns: list[hydrogen.Pattern] = []
    current = set_base_name(first_pattern)

    for pattern in patterns1:
        base = base_pattern_name(pattern.name)
        if base == current.name:
            current = merge(current, pattern)
        else:
            merged_patterns.append(current)
            current = set_base_name(pattern)

    merged_patterns.append(current)
    return merged_patterns


# Merge each sequence of references to patterns with names "foo#0", "foo#1", etc. into a
# single reference named "foo"
def unsplit_pattern_sequence(refs: list[str]) -> list[str]:
    """
    >>> unsplit_pattern_sequence([])
    []
    >>> unsplit_pattern_sequence(["A", "B"])
    ['A', 'B']
    >>> unsplit_pattern_sequence(["A", "B#0", "B#1", "C"])
    ['A', 'B', 'C']
    >>> unsplit_pattern_sequence(["A", "A", "A"])
    ['A', 'A', 'A']
    >>> unsplit_pattern_sequence(["A", "B#0", "B#1", "B#2", "B#0", "B#1", "B#2", "C#0", "C#1"])
    ['A', 'B', 'B', 'C']
    """
    if refs:
        first = refs[0]
        refs1 = refs[1:]
    else:
        return []

    merged_refs: list[str] = []
    current, current_sub = split_pattern_name(first)

    for ref in refs1:
        next, next_sub = split_pattern_name(ref)
        new_pattern = (
            next != current  # base name changed
            or next_sub is None  # no subscript
            or current_sub is None  # no subscript
            or next_sub < current_sub  # subscript jumped back
        )
        current_sub = next_sub
        if new_pattern:
            merged_refs.append(current)
            current = next

    merged_refs.append(current)
    return merged_refs


# Focuses on structure. Does not check:
#
#   * Timing (pattern length and note positions)
#   * Note conversion (mostly covered by tests above)
def check_conversion(track: mptm.Track):
    def check_converted_pattern(mp_rows: mptm.Pattern, h2_patt: hydrogen.Pattern):
        mp_notes = [
            cell
            for row in mp_rows
            for _, cell in row.items()
            if cell.note is not None and cell.instrument is not None
        ]
        assert len(h2_patt.notes) == len(mp_notes)

    h2 = convert_track(track)
    h2_patterns = unsplit_patterns(h2.patterns)
    h2_pattern_sequence = unsplit_pattern_sequence(h2.pattern_sequence)

    assert len(h2_patterns) == track.header.num_patterns

    if track.mp_extensions.pattern_names is not None:
        assert len(h2_patterns) >= len(track.mp_extensions.pattern_names)
        for mp_name, h2_patt in zip(track.mp_extensions.pattern_names, h2_patterns):
            assert mp_name == h2_patt.name

    for mp_patt, h2_patt in zip(track.patterns, h2_patterns):
        check_converted_pattern(mp_patt, h2_patt)

    h2_pattern_positions: dict[str, int] = {}
    for i, p in enumerate(h2_patterns):
        h2_pattern_positions[p.name] = i

    h2_orders = [h2_pattern_positions[p] for p in h2_pattern_sequence]

    assert h2_orders == track.header.orders
    # assert h2.bpm_timeline == []


def test_convert_file_empty():
    with Path("test/empty.it").open("rb") as f:
        pa = Parser(f, SilentLogger())
        track = pa.parse_track()
        check_conversion(track)


def test_convert_file_test1():
    with Path("test/test1.it").open("rb") as f:
        pa = Parser(f, SilentLogger())
        track = pa.parse_track()
        check_conversion(track)


def test_convert_file_test2():
    with Path("test/test2.mptm").open("rb") as f:
        pa = Parser(f, SilentLogger())
        track = pa.parse_track()
        check_conversion(track)


@st.composite
def gen_header(draw: st.DrawFn) -> mptm.ITHeader:
    title = draw(st.characters())
    num_instruments = draw(st.integers())
    num_samples = draw(st.integers())
    num_patterns = draw(st.integers(min_value=0, max_value=5))
    cwtv = draw(st.integers())
    cmwt = draw(st.integers())
    initial_speed = draw(st.integers())
    initial_tempo = draw(st.integers())

    if num_patterns == 0:
        orders = []
    else:
        orders = draw(st.lists(st.integers(min_value=0, max_value=num_patterns - 1)))

    return mptm.ITHeader(
        songname=title,
        ordnum=0,
        num_instruments=num_instruments,
        num_samples=num_samples,
        num_patterns=num_patterns,
        cwtv=cwtv,
        cmwt=cmwt,
        initial_speed=initial_speed,
        initial_tempo=initial_tempo,
        orders=orders,
    )


@st.composite
def gen_pattern(draw: st.DrawFn) -> mptm.Pattern:
    return draw(
        st.lists(
            st.dictionaries(keys=st.integers(), values=gen_cell(), max_size=5),
            max_size=7,
        )
    )


@st.composite
def gen_extended_pattern(draw: st.DrawFn) -> mptm.MPTMExtendedPattern:
    rpb = draw(optional(st.integers(min_value=1)))
    rpm = draw(optional(st.integers(min_value=1)))
    return mptm.MPTMExtendedPattern(
        rows_per_beat=rpb,
        rows_per_measure=rpm,
    )


@st.composite
def gen_track(draw: st.DrawFn) -> mptm.Track:
    header = draw(gen_header())
    patterns: list[mptm.Pattern] = draw(
        st.lists(
            gen_pattern(),
            min_size=header.num_patterns,
            max_size=header.num_patterns,
        )
    )

    # '#' is not allowed in pattern names, as it's used for subscripts when splitting
    # patterns at tempo changes
    names = draw(
        st.lists(st.characters(exclude_characters="#"), max_size=len(patterns))
    )
    unique_names = list(set(names))
    mp_extensions = mptm.MPExtensions(
        pattern_names=draw(optional(st.just(unique_names)))
    )
    mptm_extensions = mptm.MPTMExtensions(
        patterns=draw(
            optional(st.lists(gen_extended_pattern(), max_size=len(patterns)))
        )
    )

    return mptm.Track(
        header=header,
        patterns=patterns,
        mp_extensions=mp_extensions,
        mptm_extensions=mptm_extensions,
    )


@given(st.integers(min_value=0, max_value=255))
def test_interpret_tempo_command(command: int):
    def uninterpret_tempo_command(change: TempoChange) -> int:
        if change.operation == BPMOp.DecreaseBPM:
            return change.value // 5
        elif change.operation == BPMOp.IncreaseBPM:
            return change.value // 5 + 16
        else:
            return change.value

    change = interpret_tempo_command(command)
    command2 = uninterpret_tempo_command(change)
    assert command2 == command


@given(gen_pattern())
def test_slice_pattern_concat(pattern: mptm.Pattern):
    sliced_pat = slice_pattern(pattern)
    pattern2 = [row for _, slice in sliced_pat.slices for row in slice]
    assert pattern2 == pattern


@given(gen_track())
def test_convert_track(track: mptm.Track):
    check_conversion(track)

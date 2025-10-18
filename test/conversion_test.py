from pathlib import Path
from typing import Optional, TypeVar
from hypothesis import given, strategies as st
from hypothesis.strategies import SearchStrategy
import pytest

from conversion import convert_key, convert_track, convert_volume
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
    assert k == 12 * octave + key


@given(st.integers(max_value=-1))
def test_convert_key_out_of_range1(k: int):
    with pytest.raises(ValueError):
        convert_key(k)


@given(st.integers(min_value=120))
def test_convert_key_out_of_range2(k: int):
    with pytest.raises(ValueError):
        convert_key(k)


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

    assert len(h2.patterns) == track.header.num_patterns

    if track.mp_extensions.pattern_names is not None:
        assert len(h2.patterns) >= len(track.mp_extensions.pattern_names)
        for mp_name, h2_patt in zip(track.mp_extensions.pattern_names, h2.patterns):
            assert mp_name == h2_patt.name

    for mp_patt, h2_patt in zip(track.patterns, h2.patterns):
        check_converted_pattern(mp_patt, h2_patt)

    h2_pattern_positions: dict[str, int] = {}
    for i, p in enumerate(h2.patterns):
        h2_pattern_positions[p.name] = i

    h2_orders = [h2_pattern_positions[p] for p in h2.pattern_sequence]

    assert h2_orders == track.header.orders
    assert h2.bpm_timeline == [
        hydrogen.BpmMarker(bar=0, bpm=track.header.initial_tempo)
    ]


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
    num_patterns = draw(st.integers(min_value=0, max_value=10))
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
def gen_cell(draw: st.DrawFn) -> mptm.Cell:
    instrument = draw(optional(st.integers()))
    note = draw(optional(st.integers(min_value=0, max_value=119)))
    vol_pan = draw(optional(st.integers(min_value=0)))
    return mptm.Cell(
        instrument=instrument,
        note=note,
        vol_pan=vol_pan,
        command=None,
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
            st.lists(
                st.dictionaries(keys=st.integers(), values=gen_cell(), max_size=5),
                max_size=10,
            ),
            min_size=header.num_patterns,
            max_size=header.num_patterns,
        )
    )
    names = draw(st.lists(st.characters(), max_size=len(patterns)))
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


@given(gen_track())
def test_convert_track(track: mptm.Track):
    check_conversion(track)

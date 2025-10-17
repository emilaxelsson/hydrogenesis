from pathlib import Path
from hypothesis import given, strategies as st
import pytest

from conversion import convert_key, convert_track, convert_volume
import hydrogen_format as hydrogen
from logger import SilentLogger
import mptm_format as mptm
from mptm_parser import Parser


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
        mp_notes = [n for row in mp_rows for n in row]
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

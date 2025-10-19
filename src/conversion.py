from fractions import Fraction
from typing import Optional, Tuple
import hydrogen_format as hydrogen
import mptm_format as mptm
from utils import find_duplicates


default_resolution = Fraction(4)
hydrogen_ticks_per_beat = Fraction(48)


def convert_volume(vol_pan: Optional[int]) -> float:
    """
    >>> convert_volume(0)
    0.0
    >>> convert_volume(10)
    0.15625
    >>> convert_volume(64)
    1.0
    >>> convert_volume(65)
    1.0
    >>> convert_volume(None)
    1.0
    """

    default_volume = 1.0

    if vol_pan is None:
        return default_volume

    if vol_pan > 64:
        return default_volume

    if vol_pan < 0:
        raise ValueError(f"incorrect vol_pan value {vol_pan}")

    return vol_pan / 64


def convert_key(note: int) -> Tuple[int, int]:
    """
    >>> convert_key(0)
    (0, 0)
    >>> convert_key(1)
    (1, 0)
    >>> convert_key(11)
    (11, 0)
    >>> convert_key(12)
    (0, 1)
    >>> convert_key(36)
    (0, 3)
    >>> convert_key(119)
    (11, 9)
    """

    if note < 0 or note > 119:
        raise ValueError(f"incorrect note value {note}")

    key = note % 12
    octave = note // 12

    return (key, octave)


def convert_note(beat: Fraction, cell: mptm.Cell) -> Optional[hydrogen.Note]:
    if cell.instrument is None:
        return None

    if cell.note is None:
        return None

    position = round(beat * hydrogen_ticks_per_beat)
    velocity = convert_volume(cell.vol_pan)
    (key, octave) = convert_key(cell.note)

    return hydrogen.Note(
        position=position,
        instrument=cell.instrument - 1,
        velocity=velocity,
        key=key,
        octave=octave,
    )


def convertRow(resolution: Fraction, index: int, row: mptm.Row) -> list[hydrogen.Note]:
    return [
        note
        for _, cell in row.items()
        if (note := convert_note(Fraction(index) / resolution, cell)) is not None
    ]


def convert_track(track: mptm.Track) -> hydrogen.Song:
    def get_pattern_name(index: int) -> str:
        # Good chance of being a unique name
        default_name = f"Pattern {index}"

        names = track.mp_extensions.pattern_names

        if names is None:
            return default_name

        return names[index] if index < len(names) else default_name

    def get_pattern_resolution(index: int) -> Fraction:
        if track.mptm_extensions is None:
            return default_resolution

        patterns = track.mptm_extensions.patterns

        if patterns is None:
            return default_resolution

        extended_pattern = patterns[index] if index < len(patterns) else None

        if extended_pattern is None:
            return default_resolution

        rpb = extended_pattern.rows_per_beat

        return Fraction(rpb) if rpb is not None else default_resolution

    def convert_pattern(
        name: str, resolution: Fraction, rows: mptm.Pattern
    ) -> hydrogen.Pattern:
        size = round(Fraction(len(rows)) / resolution * hydrogen_ticks_per_beat)
        notes = [n for i, r in enumerate(rows) for n in convertRow(resolution, i, r)]
        return hydrogen.Pattern(name=name, size=size, notes=notes)

    patterns = [
        convert_pattern(get_pattern_name(i), get_pattern_resolution(i), p)
        for i, p in enumerate(track.patterns)
    ]

    duplicate_names = find_duplicates([p.name for p in patterns])
    if duplicate_names != []:
        raise ValueError(f"Duplicate pattern names: {duplicate_names}")

    pattern_sequence = [get_pattern_name(o) for o in track.header.orders]
    bpm_timeline = [hydrogen.BpmMarker(bar=0, bpm=track.header.initial_tempo)]

    return hydrogen.Song(
        patterns=patterns, pattern_sequence=pattern_sequence, bpm_timeline=bpm_timeline
    )

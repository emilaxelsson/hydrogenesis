from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from typing import Optional, Tuple
import hydrogen_format as hydrogen
import mptm_format as mptm
from utils import uniquify_names


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
    (0, -3)
    >>> convert_key(1)
    (1, -3)
    >>> convert_key(11)
    (11, -3)
    >>> convert_key(12)
    (0, -2)
    >>> convert_key(36)
    (0, 0)
    >>> convert_key(119)
    (11, 6)
    """

    if note < 0 or note > 119:
        raise ValueError(f"incorrect note value {note}")

    key = note % 12
    octave = note // 12

    # Hydrogen interprets MIDI key C3 as the "normal" pitch (no pitch shift). However, the
    # `.h2song` format uses C0 as the normal pitch, so we need to subtract 3.
    return (key, octave - 3)


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


def get_tempo_change(row: mptm.Row) -> Optional[int]:
    tempo_change: Optional[int] = None

    cells_left_to_right = [row[ch] for ch in sorted(row.keys())]

    # The last (i.e. right-most) tempo change wins in case of conflicting commands
    for cell in cells_left_to_right:
        if cell.command and cell.command.c1 == 20:
            tempo_change = cell.command.c2

    return tempo_change


class BPMOp(Enum):
    SetBPM = 0
    DecreaseBPM = 1
    IncreaseBPM = 2


@dataclass(frozen=True)
class TempoChange:
    operation: BPMOp
    value: int


@dataclass(frozen=True)
class TempoSlicedPattern:
    """
    A pattern divided into sub-patterns (slices) with different tempos. A slice may only
    have a tempo change on its first row. The `BPM` value paired with each slice should
    have the same value as the tempo change on the first row (if any).
    """

    slices: list[Tuple[Optional[TempoChange], mptm.Pattern]]


def interpret_tempo_command(command: int) -> TempoChange:
    if command < 0 or command > 255:
        raise ValueError(f"invalid tempo command {command}")

    if command <= 15:
        return TempoChange(operation=BPMOp.DecreaseBPM, value=command * 5)
    elif command <= 31:
        return TempoChange(operation=BPMOp.IncreaseBPM, value=(command - 16) * 5)
    else:
        return TempoChange(operation=BPMOp.SetBPM, value=command)


def slice_pattern(pattern: mptm.Pattern) -> TempoSlicedPattern:
    """
    Split a pattern into a sliced pattern. Concatenating the slices gives back the
    original pattern.
    """
    slices: list[Tuple[Optional[TempoChange], mptm.Pattern]] = []
    tempo: Optional[TempoChange] = None
    slice: mptm.Pattern = []

    for row in pattern:
        tempo_change = get_tempo_change(row)

        if tempo_change is None:
            slice.append(row)
        else:
            if slice:
                slices.append((tempo, slice))
            tempo = interpret_tempo_command(tempo_change)
            slice = [row]

    slices.append((tempo, slice))

    return TempoSlicedPattern(slices)


def make_bpm_timeline(
    initial_tempo: int,
    tempo_changes_by_pattern: dict[str, Optional[TempoChange]],
    pattern_sequence: list[str],
) -> list[hydrogen.BpmMarker]:
    bpm_timeline: list[hydrogen.BpmMarker] = []
    current_bpm = initial_tempo

    for i, pattern_name in enumerate(pattern_sequence):
        tempo_change = tempo_changes_by_pattern[pattern_name]

        if tempo_change is None:
            continue

        bpm = current_bpm  # To make Pyright happy
        if tempo_change.operation == BPMOp.DecreaseBPM:
            bpm = current_bpm - tempo_change.value
        elif tempo_change.operation == BPMOp.IncreaseBPM:
            bpm = current_bpm + tempo_change.value
        elif tempo_change.operation == BPMOp.SetBPM:
            bpm = tempo_change.value

        bpm_timeline.append(hydrogen.BpmMarker(i, bpm))
        current_bpm = bpm

    return bpm_timeline


def convert_track(track: mptm.Track) -> hydrogen.Song:
    track_pattern_names = track.mp_extensions.pattern_names or []
    extended_track_pattern_names = [
        (
            name
            if index < len(track_pattern_names) and (name := track_pattern_names[index])
            else f"Pattern {index}"
        )
        for index in range(0, len(track.patterns))
    ]

    # List of unique names. Same length as `track.patterns`.
    unique_pattern_names = uniquify_names(extended_track_pattern_names)
    named_patterns = zip(unique_pattern_names, track.patterns)

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

    def convert_slice(
        name: str, resolution: Fraction, rows: mptm.Pattern
    ) -> hydrogen.Pattern:
        size = round(Fraction(len(rows)) / resolution * hydrogen_ticks_per_beat)
        notes = [n for i, r in enumerate(rows) for n in convertRow(resolution, i, r)]
        return hydrogen.Pattern(name=name, size=size, notes=notes)

    def convert_pattern(
        name: str, resolution: Fraction, rows: mptm.Pattern
    ) -> list[Tuple[Optional[TempoChange], hydrogen.Pattern]]:
        slices = slice_pattern(rows).slices
        return [
            (
                bpm,
                convert_slice(
                    name if len(slices) == 1 else name + f"#{i}", resolution, slice
                ),
            )
            for i, (bpm, slice) in enumerate(slices)
        ]

    converted_sliced_patterns: list[
        list[Tuple[Optional[TempoChange], hydrogen.Pattern]]
    ] = [
        convert_pattern(name, get_pattern_resolution(i), pat)
        for i, (name, pat) in enumerate(named_patterns)
    ]

    patterns = [
        pattern for slices in converted_sliced_patterns for _, pattern in slices
    ]

    tempo_changes_by_pattern: dict[str, Optional[TempoChange]] = {
        pattern.name: tempo_change
        for slices in converted_sliced_patterns
        for tempo_change, pattern in slices
    }

    pattern_sequence = [
        pat.name for o in track.header.orders for _, pat in converted_sliced_patterns[o]
    ]

    bpm_timeline = make_bpm_timeline(
        track.header.initial_tempo, tempo_changes_by_pattern, pattern_sequence
    )

    return hydrogen.Song(
        name=track.header.songname,
        author="Automatically generated using Hydrogenesis",
        bpm=track.header.initial_tempo,
        patterns=patterns,
        pattern_sequence=pattern_sequence,
        bpm_timeline=bpm_timeline,
    )

from dataclasses import dataclass


@dataclass(frozen=True)
class Note:
    position: int  # Tick position within bar (fractional beat position * 48)
    instrument: int  # 0-based index
    velocity: float  # Range: [0.0, 1.0]
    key: int  # Range: [0, 11], corresponding to C, C#, D ... B
    octave: int  # 0 is the "normal octave". Negative values are allowed.


@dataclass(frozen=True)
class Pattern:
    size: int  # Number of ticks (= number of beats * 48)
    name: str  # Probably must be unique (used as identifier in `pattern_sequence`)
    notes: list[Note]


@dataclass(frozen=True)
class BpmMarker:
    bar: int  # 0-based index referencing pattern (= bar) in `pattern_sequence`
    bpm: int


@dataclass(frozen=True)
class Song:
    patterns: list[Pattern]
    pattern_sequence: list[str]  # Patterns referenced by name
    bpm_timeline: list[BpmMarker]

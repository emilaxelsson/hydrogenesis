from dataclasses import dataclass


@dataclass(frozen=True)
class Note:
    position: int  # Tick position within bar (fractional beat position * 48)
    # Finer granularity could be achieved using the `leadlag` property. It's a value in
    # the range [-1, 1], where -1 means delay by 5 (Hydrogen) ticks and 1 means advance by
    # 5 ticks. `leadlag` is a floating point value. Not sure how it's quantized, but at
    # least the UI shows two decimal places.

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

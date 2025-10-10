from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ITHeader:
    songname: str
    ordnum: int
    num_instruments: int
    num_samples: int
    num_patterns: int
    cwtv: int
    cmwt: int
    initial_speed: int  # ticks per row
    initial_tempo: int  # beats per minute
    orders: list[int]


@dataclass(frozen=True)
class MPExtensions:
    pattern_names: Optional[list[str]]


@dataclass(frozen=True)
class Command:
    c1: int
    c2: int


@dataclass(frozen=True)
class Cell:
    instrument: Optional[int]  # 1-based index
    note: Optional[int]  # 0-119 maps to C0 - B9
    vol_pan: Optional[int]  # 0-64 maps to volume 0-64; 128-192 maps to panning 0-64
    command: Optional[Command]


Channel = int

Row = dict[Channel, Cell]
Pattern = list[Row]


@dataclass(frozen=True)
class MPTMExtendedPattern:
    rows_per_beat: Optional[int]
    rows_per_measure: Optional[int]


@dataclass(frozen=True)
class MPTMExtensions:
    patterns: Optional[list[MPTMExtendedPattern]]


@dataclass(frozen=True)
class Track:
    header: ITHeader
    patterns: list[Pattern]
    mp_extensions: MPExtensions
    mptm_extensions: Optional[MPTMExtensions]

# Copyright (C) 2025 Emil Axelsson
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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

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
    name: Optional[str]
    author: Optional[str]
    bpm: int
    patterns: list[Pattern]
    pattern_sequence: list[str]  # Patterns referenced by name
    bpm_timeline: list[BpmMarker]

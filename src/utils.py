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

from typing import Tuple, TypeVar

T = TypeVar("T")
U = TypeVar("U")


def uniquify_names(names: list[str]) -> list[str]:
    """Return a new list of items with unique names by renaming duplicates."""
    seen: set[str] = set()
    result: list[str] = []

    for name in names:
        base_name = name
        new_name = base_name
        i = 1

        while new_name in seen:
            # if new_name == base_name
            new_name = f"{base_name}{i}"
            i += 1

        seen.add(new_name)
        result.append(new_name)

    return result


def require(val: T | None, what: str) -> T:
    if val is None:
        raise ValueError(f"missing {what}")
    return val


def unzip(pairs: list[Tuple[T, U]]) -> Tuple[list[T], list[U]]:
    ts: list[T] = []
    us: list[U] = []

    for (t, u) in pairs:
        ts.append(t)
        us.append(u)

    return (ts, us)

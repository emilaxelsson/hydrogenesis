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

import pprint
import textwrap


class Logger:
    def __init__(self, indent: int = 0):
        self.indent = indent

    def log(self, message: str = "", tag: str = ""):
        tag_len = 8
        padded_tag = (tag + (" " * tag_len))[:tag_len]
        print(textwrap.indent(f"{' ' * self.indent}{message}", padded_tag))

    def log_format(self, message: str, tag: str = ""):
        self.log(pprint.pformat(message, compact=True, sort_dicts=False), tag)

    def new(self, additional_indent: int) -> "Logger":
        return Logger(self.indent + additional_indent)


class SilentLogger(Logger):
    def log(self, message: str = "", tag: str = ""):
        pass

    def new(self, additional_indent: int) -> "SilentLogger":
        return SilentLogger()

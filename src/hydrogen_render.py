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

from xml.etree.ElementTree import Element, SubElement

import hydrogen_format as hydrogen
from utils import require


note_keys = [
    "C",
    "Cs",
    "D",
    "Ef",
    "E",
    "F",
    "Fs",
    "G",
    "Af",
    "A",
    "Bf",
    "B",
]


def get_instrument_ids(template: Element) -> list[int]:
    """
    Our Hydrogen format (hydrogen_format.py) refers to instrument by index rather than id.
    However, in the real Hydrogen format, notes refer to instrument by id, not index.

    The template contains a list of instruments, and each instrument has an id. Due to
    removal and re-ordering of instruments, the ids may be out of order and even contain
    gaps.

    The purpose of this function is to return the id of each instrument, so that we
    can translate from index to id.
    """
    instrument_ids: list[int] = []

    for instrument in template.findall(".//instrumentList/instrument"):
        id_elem = instrument.find("id")
        if id_elem is None or id_elem.text is None:
            continue
        try:
            instrument_ids.append(int(id_elem.text.strip()))
        except ValueError:
            continue

    return instrument_ids


def render_pattern(instrument_ids: list[int], pattern: hydrogen.Pattern) -> Element:
    pattern_elem = Element("pattern")

    name = SubElement(pattern_elem, "name")
    name.text = pattern.name

    size = SubElement(pattern_elem, "size")
    size.text = str(pattern.size)

    note_list = SubElement(pattern_elem, "noteList")
    for note in pattern.notes:
        note_elem = SubElement(note_list, "note")

        position = SubElement(note_elem, "position")
        position.text = str(note.position)

        velocity = SubElement(note_elem, "velocity")
        velocity.text = str(note.velocity)

        try:
            instrument_id = instrument_ids[note.instrument_index - 1]
        except ValueError:
            raise ValueError(f"no instrument with index {note.instrument_index} in template")

        instrument = SubElement(note_elem, "instrument")
        instrument.text = str(instrument_id)

        key = SubElement(note_elem, "key")
        key.text = note_keys[note.key] + str(note.octave)

    return pattern_elem


def graft(template: Element, song: hydrogen.Song) -> Element:
    name_element = require(template.find("name"), "name tag")
    name_element.text = song.name

    author_element = require(template.find("author"), "author tag")
    author_element.text = str(song.author)

    bpm_element = require(template.find("bpm"), "bpm tag")
    bpm_element.text = str(song.bpm)

    instrument_ids = get_instrument_ids(template)

    pattern_list = require(template.find("patternList"), "patternList tag")

    # Remove existing patterns from template
    pattern_list.clear()
    for p in song.patterns:
        pattern_list.append(render_pattern(instrument_ids, p))

    pattern_sequence = require(template.find("patternSequence"), "patternSequence tag")

    # Remove existing patterns from template
    pattern_sequence.clear()
    for pattern in song.pattern_sequence:
        group = Element("group")
        pattern_id = SubElement(group, "patternID")
        pattern_id.text = pattern
        pattern_sequence.append(group)

    bpm_timeline = require(template.find("BPMTimeLine"), "BPMTimeLine tag")

    if song.bpm_timeline:
        pattern_list = require(
            template.find("isTimelineActivated"), "isTimelineActivated tag"
        )
        pattern_list.text = "true"

        # Remove existing markers from template
        bpm_timeline.clear()
        for bpm_marker in song.bpm_timeline:
            new_bpm = Element("newBPM")
            bpm_bar = SubElement(new_bpm, "BAR")
            bpm_bar.text = str(bpm_marker.bar)
            bpm_bpm = SubElement(new_bpm, "BPM")
            bpm_bpm.text = str(bpm_marker.bpm)
            bpm_timeline.append(new_bpm)

    return template

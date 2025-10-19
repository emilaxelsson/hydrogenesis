from xml.etree.ElementTree import Element, SubElement

import hydrogen_format as hydrogen
from utils import require


def render_pattern(pattern: hydrogen.Pattern) -> Element:
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

        instrument = SubElement(note_elem, "instrument")
        instrument.text = str(note.instrument)

    return pattern_elem


def graft(template: Element, song: hydrogen.Song) -> Element:
    pattern_list = require(template.find("patternList"), "patternList tag")

    # Remove existing patterns from template
    pattern_list.clear()
    for p in song.patterns:
        pattern_list.append(render_pattern(p))

    pattern_sequence = require(template.find("patternSequence"), "patternSequence tag")
    pattern_sequence.clear()

    # Remove existing patterns from template
    pattern_sequence.clear()
    for pattern in song.pattern_sequence:
        group = Element("group")
        pattern_id = SubElement(group, "patternID")
        pattern_id.text = pattern
        pattern_sequence.append(group)

    return template

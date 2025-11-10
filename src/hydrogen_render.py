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

    pattern_list = require(template.find("patternList"), "patternList tag")

    # Remove existing patterns from template
    pattern_list.clear()
    for p in song.patterns:
        pattern_list.append(render_pattern(p))

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

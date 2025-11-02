import argparse
from pathlib import Path
from xml.dom import minidom
import xml.etree.ElementTree as xml
from xml.etree.ElementTree import Element

from conversion import convert_track
from logger import Logger, SilentLogger
from mptm_parser import Parser
from hydrogen_render import graft
from utils import require


def main(track_path: str, template_path: str, output_path: str, debug: bool):
    if debug:
        logger = Logger()
    else:
        logger = SilentLogger()

    with Path(track_path).open("rb") as f:
        pa = Parser(f, logger)
        track = pa.parse_track()

    h2song = convert_track(track)

    template_tree = xml.parse(template_path)
    template: Element = require(template_tree.getroot(), "template root element")

    rendered_song = graft(template, h2song)

    song_xml = xml.tostring(rendered_song)
    song_xml_str = minidom.parseString(song_xml).toprettyxml(indent="  ")

    # https://stackoverflow.com/questions/1662351/problem-with-newlines-when-i-use-toprettyxml#comment136233222_39984422
    song_xml_str = "\n".join([s for s in song_xml_str.splitlines() if s.strip()])

    with open(output_path, "w") as f:
        f.write(song_xml_str)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert OpenMPT tracks (.it/.mptm) to Hydrogen format (.h2song)."
    )
    parser.add_argument("input_file", help="Path to the input track")
    parser.add_argument("-t", "--template", help="Path to the template .h2song file", required=True)
    parser.add_argument("-o", "--output", help="Path to the output .h2song file", required=True)
    parser.add_argument(
        "--debug", action="store_true", help="Enable debug mode for verbose output"
    )

    args = parser.parse_args()

    main(
        track_path=args.input_file,
        template_path=args.template,
        output_path=args.output,
        debug=args.debug,
    )

from pathlib import Path
import pprint
import sys

from logger import Logger, SilentLogger
from mptm_parser import Parser

def main(path, debug):
    if debug:
        logger = Logger()
    else:
        logger = SilentLogger()

    p = Path(path)
    with p.open("rb") as f:
        pa = Parser(f, logger)
        parsed_track = pa.parse_track()

    pprint.pprint(parsed_track)


if __name__ == "__main__":
    usage = "Usage: python3 hydrogenesis.py [--debug] file.mptm"

    if len(sys.argv) < 2:
        print(usage)
        sys.exit(1)

    debug = False
    args = sys.argv[1:]
    if "--debug" in args:
        debug = True
        args.remove("--debug")

    if not args:
        print(f"Error: missing input file.\n{usage}")
        sys.exit(1)

    main(args[0], debug=debug)

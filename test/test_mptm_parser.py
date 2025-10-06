from pathlib import Path
import unittest

from logger import SilentLogger
from mptm_parser import (
    Cell,
    Command,
    ITHeader,
    MPExtensions,
    MPTMExtendedPattern,
    MPTMExtensions,
    Parser,
)


# Note: Empty 64-row patterns have a special representation (offset pointer = 0)
empty_pattern: list[dict[int, Cell]] = [{}] * 64


class TestMptmParser(unittest.TestCase):
    def test_can_parse_empty_it_module(self):
        with Path("test/empty.it").open("rb") as f:
            pa = Parser(f, SilentLogger())
            track = pa.parse_track()

            self.assertEqual(
                track.header,
                ITHeader(
                    cmwt=532,
                    cwtv=20786,
                    initial_speed=6,
                    initial_tempo=125,
                    num_instruments=0,
                    num_patterns=1,
                    num_samples=1,
                    orders=[0],
                    ordnum=2,
                    songname="",
                ),
            )

            self.assertEqual(track.mp_extensions, MPExtensions(pattern_names=None))
            self.assertEqual(track.mptm_extensions, None)
            self.assertEqual(track.patterns, [empty_pattern])

    def test_can_parse_test1(self):
        self.maxDiff = None
        with Path("test/test1.it").open("rb") as f:
            pa = Parser(f, SilentLogger())
            track = pa.parse_track()

            self.assertEqual(
                track.header,
                ITHeader(
                    cmwt=532,
                    cwtv=20786,
                    initial_speed=5,
                    initial_tempo=120,
                    num_instruments=0,
                    num_patterns=2,
                    num_samples=1,
                    orders=[0, 0, 1],
                    ordnum=4,
                    songname="Test1",
                ),
            )

            self.assertEqual(
                track.mp_extensions, MPExtensions(pattern_names=["Pattern 1"])
            )
            self.assertEqual(track.mptm_extensions, None)

            self.assertEqual(
                track.patterns,
                [
                    [
                        {0: Cell(instrument=2, note=60, vol_pan=None, command=None)},
                        {},
                        {},
                        {},
                        {
                            1: Cell(
                                instrument=3,
                                note=62,
                                vol_pan=None,
                                command=Command(20, 34),
                            ),
                            2: Cell(instrument=4, note=63, vol_pan=None, command=None),
                        },
                        {},
                        {},
                        {},
                        {1: Cell(instrument=5, note=74, vol_pan=None, command=None)},
                        {},
                        {},
                        {},
                        {},
                        {},
                        {},
                        {},
                    ],
                    empty_pattern,
                ],
            )

    def test_can_parse_test2(self):
        self.maxDiff = None
        with Path("test/test2.mptm").open("rb") as f:
            pa = Parser(f, SilentLogger())
            track = pa.parse_track()

            self.assertEqual(
                track.header,
                ITHeader(
                    cmwt=2184,
                    cwtv=2193,
                    initial_speed=5,
                    initial_tempo=120,
                    num_instruments=0,
                    num_patterns=2,
                    num_samples=1,
                    orders=[0, 0, 1],
                    ordnum=3,
                    songname="Test1",
                ),
            )

            self.assertEqual(track.mp_extensions, MPExtensions(pattern_names=["Intro"]))
            self.assertEqual(
                track.mptm_extensions,
                MPTMExtensions(
                    pattern=[
                        MPTMExtendedPattern(rows_per_beat=2, rows_per_measure=16),
                        MPTMExtendedPattern(rows_per_beat=None, rows_per_measure=None),
                    ]
                ),
            )

            self.assertEqual(
                track.patterns,
                [
                    [
                        {0: Cell(instrument=2, note=60, vol_pan=None, command=None)},
                        {},
                        {},
                        {},
                        {
                            1: Cell(
                                instrument=3,
                                note=62,
                                vol_pan=None,
                                command=Command(20, 34),
                            ),
                            2: Cell(instrument=4, note=63, vol_pan=None, command=None),
                        },
                        {},
                        {},
                        {},
                        {1: Cell(instrument=5, note=74, vol_pan=None, command=None)},
                        {},
                        {},
                        {},
                        {},
                        {},
                        {},
                        {},
                    ],
                    empty_pattern,
                ],
            )


if __name__ == "__main__":
    unittest.main()

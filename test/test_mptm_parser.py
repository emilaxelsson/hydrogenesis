from pathlib import Path
import unittest

from logger import SilentLogger
from mptm_parser import ITHeader, MPExtensions, Parser


class TestMptmParser(unittest.TestCase):
    def test_can_parse_empty_it_module(self):
        with Path("test/empty.it").open("rb") as f:
            pa = Parser(f, SilentLogger())
            track = pa.parse_track(mptm_extensions=False)

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
            self.assertEqual(track.patterns, [[{}] * 64])

    def test_can_parse_test1(self):
        with Path("test/test1.it").open("rb") as f:
            pa = Parser(f, SilentLogger())
            track = pa.parse_track(mptm_extensions=False)

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

            self.assertEqual(track.mp_extensions, MPExtensions(pattern_names=["Pattern 1"]))
            self.assertEqual(track.mptm_extensions, None)
            self.assertEqual(track.patterns, [[{}] * 16, [{}] * 64])


if __name__ == "__main__":
    unittest.main()

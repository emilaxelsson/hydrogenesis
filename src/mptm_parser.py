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
from io import BufferedReader
import os
import struct
from typing import Any, Callable, Tuple, cast, Optional, TypeVar

from logger import Logger


def read_u8(b: bytes) -> int:
    """
    >>> hex(read_u8(b'\x2a'))
    '0x2a'
    >>> hex(read_u8(b'\x2a\x22'))
    '0x2a'
    """
    return cast(int, struct.unpack_from("<B", b)[0])


def read_u16(b: bytes) -> int:
    """
    >>> hex(read_u16(b'\x23\x45'))
    '0x4523'
    >>> hex(read_u16(b'\x23\x45\x22'))
    '0x4523'
    """
    return cast(int, struct.unpack_from("<H", b)[0])


def read_u32(b: bytes) -> int:
    """
    >>> hex(read_u32(b'\x23\x34\x45\x56'))
    '0x56453423'
    >>> hex(read_u32(b'\x23\x34\x45\x56\x22'))
    '0x56453423'
    """
    return cast(int, struct.unpack_from("<I", b)[0])


def read_u64(b: bytes) -> int:
    """
    >>> hex(read_u64(b'\x23\x34\x45\x56\x23\x34\x45\x56'))
    '0x5645342356453423'
    >>> hex(read_u64(b'\x23\x34\x45\x56\x23\x34\x45\x56\x22'))
    '0x5645342356453423'
    """
    return cast(int, struct.unpack_from("<Q", b)[0])


# https://wiki.openmpt.org/Development:_228_Extensions#Adaptive_Integers
def read_auint16(f: BufferedReader) -> int:
    """
    >>> from io import BytesIO; bin(read_auint16(BufferedReader(BytesIO(bytes([0b10011000, 0b00111000])))))
    '0b1001100'
    >>> from io import BytesIO; bin(read_auint16(BufferedReader(BytesIO(bytes([0b10011001, 0b00111000])))))
    '0b1110001001100'
    """
    x = read_u8(f.peek(1)) & 0b00000001
    if x:
        return read_u16(f.read(2)) >> 1
    else:
        return read_u8(f.read(1)) >> 1


def read_auint32(f: BufferedReader) -> int:
    """
    >>> from io import BytesIO; bin(read_auint32(BufferedReader(BytesIO(bytes([0b10011000, 0b00111000, 0b01010101, 0xFF])))))
    '0b100110'
    >>> from io import BytesIO; bin(read_auint32(BufferedReader(BytesIO(bytes([0b10011001, 0b00111000, 0b01010101, 0xFF])))))
    '0b111000100110'
    >>> from io import BytesIO; bin(read_auint32(BufferedReader(BytesIO(bytes([0b10011010, 0b00111000, 0b01010101, 0xFF])))))
    '0b101010100111000100110'
    >>> from io import BytesIO; bin(read_auint32(BufferedReader(BytesIO(bytes([0b10011011, 0b00111000, 0b01010101, 0xFF])))))
    '0b111111110101010100111000100110'
    """
    size = read_u8(f.peek(1)) & 0b00000011
    if size == 0:
        return read_u8(f.read(1)) >> 2
    elif size == 1:
        return read_u16(f.read(2)) >> 2
    elif size == 2:
        x = f.read(3) + b"\x00"
        return read_u32(x) >> 2
    elif size == 3:
        return read_u32(f.read(4)) >> 2
    else:
        return 0  # cannot happen


def read_auint64(f: BufferedReader) -> int:
    """
    >>> from io import BytesIO; bin(read_auint64(BufferedReader(BytesIO(bytes([0b10011000, 0b00111000, 0b01010101, 0xFF])))))
    '0b100110'
    >>> from io import BytesIO; bin(read_auint64(BufferedReader(BytesIO(bytes([0b10011001, 0b00111000, 0b01010101, 0xFF])))))
    '0b111000100110'
    >>> from io import BytesIO; bin(read_auint64(BufferedReader(BytesIO(bytes([0b10011010, 0b00111000, 0b01010101, 0xFF])))))
    '0b111111110101010100111000100110'
    >>> from io import BytesIO; bin(read_auint64(BufferedReader(BytesIO(bytes([0b10011011, 0b00111000, 0b01010101, 0xFF, 0b11001100, 0b11100011, 0b11101110, 0b10000100])))))
    '0b10000100111011101110001111001100111111110101010100111000100110'
    """
    size = read_u8(f.peek(1)) & 0b00000011
    if size == 0:
        return read_u8(f.read(1)) >> 2
    elif size == 1:
        return read_u16(f.read(2)) >> 2
    elif size == 2:
        return read_u32(f.read(4)) >> 2
    elif size == 3:
        return read_u64(f.read(8)) >> 2
    else:
        return 0  # cannot happen


def read_cstr(b: bytes) -> str:
    """
    >>> read_cstr(b'hello  ')
    'hello'
    >>> read_cstr(b'hello  ' + bytes([0]) + b'rest')
    'hello'
    """
    # Decode up to first null byte, strip trailing whitespace
    return b.split(b"\x00", 1)[0].decode("latin1", errors="replace").rstrip()


T = TypeVar("T")


@dataclass(frozen=True)
class ITHeader:
    songname: str
    ordnum: int
    num_instruments: int
    num_samples: int
    num_patterns: int
    cwtv: int
    cmwt: int
    initial_speed: int  # ticks per row
    initial_tempo: int


@dataclass(frozen=True)
class OffsetTables:
    instrument_offsets: list[int]
    sample_offsets: list[int]
    pattern_offsets: list[int]


@dataclass(frozen=True)
class Command:
    c1: int
    c2: int


@dataclass(frozen=True)
class Cell:
    instrument: Optional[int]
    note: Optional[int]
    vol_pan: Optional[int]
    command: Optional[Command]


Channel = int

Row = dict[Channel, Cell]
Pattern = list[Row]


class Parser:
    def __init__(self, f: BufferedReader, logger: Logger):
        self.f = f
        self.logger = logger

    def log(self, message: str = "", pos: Optional[int] = None):
        tag = hex(pos) if pos is not None else "--"
        self.logger.log(message, tag)

    def log_format(self, message: str):
        self.logger.log_format(message)

    def sub(self, description: str, func: Callable[["Parser"], T]) -> T:
        self.log(f"---> {description}", self.f.tell())
        result = func(Parser(self.f, self.logger.new(3)))
        self.log(f"<--- {description}")
        return result

    def log_read(self, type: str, val: str, pos: Optional[int], var: Optional[str]):
        var_prefix = f"{var} = " if var else ""
        self.log(f"{var_prefix}reading {type} {val}", pos)

    def log_read_int(self, type: str, val: int, pos: int, var: Optional[str]):
        var_prefix = f"{var} = " if var else ""
        self.log(f"{var_prefix}reading {type} {hex(val)} (= {val})", pos)

    def read_u8(self, var: Optional[str] = None) -> int:
        pos = self.f.tell()
        i = read_u8(self.f.read(1))
        self.log_read_int("uint8", i, pos, var)
        return i

    def read_u16(self, var: Optional[str] = None) -> int:
        pos = self.f.tell()
        i = read_u16(self.f.read(2))
        self.log_read_int("uint16", i, pos, var)
        return i

    def read_u32(self, var: Optional[str] = None) -> int:
        pos = self.f.tell()
        i = read_u32(self.f.read(4))
        self.log_read_int("uint32", i, pos, var)
        return i

    def read_u64(self, var: Optional[str] = None) -> int:
        pos = self.f.tell()
        i = read_u64(self.f.read(8))
        self.log_read_int("uint64", i, pos, var)
        return i

    def read_auint16(self, var: Optional[str] = None) -> int:
        pos = self.f.tell()
        i = read_auint16(self.f)
        self.log_read_int("auint16", i, pos, var)
        return i

    def read_auint32(self, var: Optional[str] = None) -> int:
        pos = self.f.tell()
        i = read_auint32(self.f)
        self.log_read_int("auint32", i, pos, var)
        return i

    def read_auint64(self, var: Optional[str] = None) -> int:
        pos = self.f.tell()
        i = read_auint64(self.f)
        self.log_read_int("auint64", i, pos, var)
        return i

    def read_cstr(self, length: int, var: Optional[str] = None) -> str:
        pos = self.f.tell()
        str = read_cstr(self.f.read(length))
        self.log_read("string", f"'{str}'", pos, var)
        return str

    def read_bytes(self, length: int, var: Optional[str] = None) -> bytes:
        pos = self.f.tell()
        b = self.f.read(length)
        self.log_read("bytes", str(b), pos, var)
        return b

    def parse_it_header(self) -> Tuple[ITHeader, OffsetTables]:
        return self.sub("parse_it_header()", lambda sub: sub._parse_it_header())

    def _parse_it_header(self) -> Tuple[ITHeader, OffsetTables]:
        signature = self.read_bytes(4, "signature")

        if signature != b"IMPM":
            raise ValueError("not an IT/MPTM file (missing IMPM signature)")

        song_name = self.read_cstr(26)

        # Skipping two unused bytes
        self.f.read(2)

        ordnum = self.read_u16("ordnum")
        insnum = self.read_u16("insnum")
        smpnum = self.read_u16("smpnum")
        patnum = self.read_u16("patnum")
        cwtv = self.read_u16("cwtv")
        cmwt = self.read_u16("cmwt")

        self.f.seek(0x32)
        initial_speed = self.read_u8("initial_speed")
        initial_tempo = self.read_u8("initial_tempo")

        self.read_u8()
        self.read_u8()

        self.read_u16("message_length")
        self.read_u32("message_offset")

        # Skip orders, because they are replicated in the MPTM chunk
        self.f.seek(0xC0 + ordnum)

        instrument_offsets = list(
            struct.iter_unpack("<I", self.read_bytes(insnum * 4, "instrument_offsets"))
        )
        instrument_offsets_2 = [
            i[0] for i in instrument_offsets
        ]  # Get first component of tuple

        sample_offsets = list(
            struct.iter_unpack("<I", self.read_bytes(smpnum * 4, "sample_offsets"))
        )
        sample_offsets_2 = [i[0] for i in sample_offsets]

        pattern_offsets = list(
            struct.iter_unpack("<I", self.read_bytes(patnum * 4, "pattern_offsets"))
        )
        pattern_offsets_2 = [i[0] for i in pattern_offsets]

        return (
            ITHeader(
                songname=song_name,
                ordnum=ordnum,
                num_instruments=insnum,
                num_samples=smpnum,
                num_patterns=patnum,
                cwtv=cwtv,
                cmwt=cmwt,
                initial_speed=initial_speed,
                initial_tempo=initial_tempo,
            ),
            OffsetTables(
                instrument_offsets=instrument_offsets_2,
                sample_offsets=sample_offsets_2,
                pattern_offsets=pattern_offsets_2,
            ),
        )

    def parse_pnam(self) -> list[str]:
        magic_bytes = self.read_bytes(4, "magic_bytes")
        if magic_bytes != b"PNAM":
            raise ValueError("expected a PNAM chunk")
        size = self.read_u32("size")
        number_of_pattnern_names = int(size / 32)
        self.log(f"number_of_pattnern_names = {number_of_pattnern_names}")

        names: list[str] = []

        pos_before_list = self.f.tell()

        for i in range(0, number_of_pattnern_names):
            self.f.seek(pos_before_list + i * 32)
            name = self.read_cstr(32, "name")
            names.append(name)

        return names

    # Ideally, this function would just read the chunks it finds in sequence, stopping
    # when the data can no longer be parsed as a chunk of known type. However, it seems
    # that OpenMPT inserts extra data between the IT header and the first ModPlug
    # extension chunk. I don't know what this data is, so I cannot determine where the
    # extension chunks start.
    #
    # What we do know from the header is where the sample/instrument/pattern data starts
    # (the lowest offset pointer), so any ModPlug extensions must occur before that.
    # Hence, we simply search for extensions (by looking for magic bytes) in that region.
    #
    # Potential (but unlikely) problem with this approach: The region in which we search
    # for extension chunks includes some unrelated data (at least the leading unknown data
    # mentioned above). What if that data happens to contain the magic bytes we're looking
    # for?
    def parse_mp_extensions(self, offsets: OffsetTables) -> Optional[dict[str, Any]]:
        # `section_start` should be right after the header
        section_start = self.f.tell()

        self.log()
        self.log("parse_mp_extensions", section_start)

        # A pattern offset of 0 is a shorthand for an empty 64-row pattern
        pattern_offsets_without_0 = filter(lambda o: o != 0, offsets.pattern_offsets)

        all_offsets = (
            offsets.instrument_offsets
            + offsets.sample_offsets
            + list(pattern_offsets_without_0)
        )

        # The position right after the end of the region that may contain ModPlug
        # extension chunks, or `None` if no position can be determined
        pos_after_region: int | None = min(all_offsets, default=None)

        if pos_after_region is None:
            # If `pos_after_region` couldn't be determined, it means there isn't any
            # pattern data, so then it doesn't make sense to look for extensions anyway
            self.log(
                "could not determine size of ModPlug extensions region, skipping extensions"
            )
            return None

        self.log(f"pos_after_region: {hex(pos_after_region)}")

        region_size = pos_after_region - self.f.tell()
        self.log(f"region_size: {region_size}")

        if region_size < 0:
            raise ValueError("negative region size")

        # Note: Reading region into memory. I don't think there can be a massive amount of
        # data in the region, so this is probably fine.
        section = self.f.read(region_size)
        pnam_pos = section.find(b"PNAM")

        # If failed to find "PNAM"
        if pnam_pos == -1:
            return None

        self.f.seek(section_start + pnam_pos)
        names = self.parse_pnam()

        return {"names": names}

    def parse_packed_pattern_rows(self, num_rows: int) -> list[Row]:
        return self.sub(
            f"parse_packed_pattern_rows({num_rows})",
            lambda sub: sub._parse_packed_pattern_rows(num_rows),
        )

    # Follows the pseudo-code here:
    # https://github.com/schismtracker/schismtracker/wiki/ITTECH.TXT#impulse-pattern-format
    def _parse_packed_pattern_rows(self, num_rows: int) -> list[Row]:
        rows: list[Row] = []
        channel_masks: dict[int, Any] = {}
        channel_notes: dict[int, int] = {}
        channel_instrs: dict[int, int] = {}
        channel_volpans: dict[int, int] = {}
        channel_comms: dict[int, Any] = {}

        def mk_cell(cell: dict[str, Any]) -> Cell:
            return Cell(
                instrument=cell.get("instr"),
                note=cell.get("note"),
                vol_pan=cell.get("vol_pan"),
                command=cell.get("command"),
            )

        def parse_packed_pattern_row() -> None:
            self.sub(
                f"parse_packed_pattern_row()",
                lambda sub: _parse_packed_pattern_row(sub),
            )

        def _parse_packed_pattern_row(self: Parser):
            row: dict[int, dict[str, Any]] = {}

            def get_next_channel_marker() -> None:
                channel_variable = self.read_u8("channel_variable")
                self.log(f"channel_variable: {bin(channel_variable)}")
                if channel_variable == 0:
                    return
                channel = (channel_variable - 1) & 63
                self.log(f"channel = {channel}")
                if channel_variable & 128:
                    mask_variable = self.read_u8("mask_variable")
                    channel_masks[channel] = mask_variable
                    self.log(f"mask_variable: {bin(mask_variable)}")
                else:
                    mask_variable = channel_masks[channel]
                    self.log(f"previous mask_variable: {bin(mask_variable)}")
                if mask_variable & 1:
                    note = self.read_u8("note")
                    channel_notes[channel] = note
                    row.setdefault(channel, {})["note"] = note
                if mask_variable & 2:
                    instr = self.read_u8("instr")
                    channel_instrs[channel] = instr
                    row.setdefault(channel, {})["instr"] = instr
                if mask_variable & 4:
                    vol_pan = self.read_u8("vol_pan")
                    channel_volpans[channel] = vol_pan
                    row.setdefault(channel, {})["vol_pan"] = vol_pan
                if mask_variable & 8:
                    comm = self.read_u8("comm")
                    val = self.read_u8("val")
                    channel_comms[channel] = [comm, val]
                    row.setdefault(channel, {})["comm"] = [comm, val]
                if mask_variable & 16:
                    note = channel_notes[channel]
                    row.setdefault(channel, {})["note"] = note
                    self.log(f"   previous note: {note}")
                if mask_variable & 32:
                    instr = channel_instrs[channel]
                    row.setdefault(channel, {})["instr"] = instr
                    self.log(f"   previous instr: {instr}")
                if mask_variable & 64:
                    vol_pan = channel_volpans[channel]
                    row.setdefault(channel, {})["vol_pan"] = vol_pan
                    self.log(f"   previous vol_pan: {vol_pan}")
                if mask_variable & 128:
                    comm = channel_comms[channel]
                    row.setdefault(channel, {})["comm"] = comm
                    self.log(f"   previous comm: {comm}")

                get_next_channel_marker()

            get_next_channel_marker()

            row2 = {channel: mk_cell(note) for channel, note in row.items()}
            rows.append(row2)

        for i in range(0, num_rows):
            self.log(f"row {i}", self.f.tell())
            parse_packed_pattern_row()

        return rows

    # https://github.com/schismtracker/schismtracker/wiki/ITTECH.TXT#impulse-pattern-format
    def parse_patterns(self, offsets: list[int]) -> list[Pattern]:
        patterns: list[Pattern] = []

        for pos in offsets:
            if pos == 0:
                rows: list[Row] = [{}] * 64
            else:
                self.f.seek(pos)

                self.log()
                self.log(f"Parsing pattern", self.f.tell())

                # Skip length
                self.f.read(2)

                num_rows = self.read_u16()

                # Skip unused bytes
                self.f.read(4)

                rows = self.parse_packed_pattern_rows(num_rows)

            patterns.append(rows)

        return patterns

    def parse_mptm_chunk(self, expected_id: bytes) -> dict[Any, Any]:
        return self.sub(
            f"parse_mptm_chunk('{expected_id.decode('ascii')}')",
            lambda sub: sub._parse_mptm_chunk(expected_id),
        )

    def _parse_mptm_chunk(self, expected_id: bytes) -> dict[Any, Any]:
        chunk_start = self.f.tell()

        x228 = self.read_bytes(3, "x228")
        if x228 != b"228":
            raise ValueError("chunk is not a 228 container")

        id_len = self.read_u8("id_len")
        chunk_id = self.read_bytes(id_len, "chunk_id")

        if chunk_id != expected_id:
            raise ValueError(
                f"expected chunk id {str(expected_id)}; got {str(chunk_id)}"
            )

        header_constants = self.read_bytes(4, "header_constants")

        # We assume current OpenMPT which uses constant values for header byte and additional
        # header data; see
        # https://wiki.openmpt.org/Development:_228_Extensions#228_Chunks_in_MPTM_Files
        if header_constants != b"\x1f\x08\x00\x01":
            raise ValueError(f"unexpected header constants: {str(header_constants)}")

        # Numeric version number (exists because bit 4 of the header byte (1F) is set)
        self.read_auint64()

        custom_id_len = self.read_u8("custom_id_len")
        if not (custom_id_len & 0x01):
            raise ValueError('bit 0 of "custom ID length" not set')

        num_entries = self.read_auint64("num_entries")
        map_ptr = chunk_start + self.read_auint64("map_ptr")

        self.log(f"Header ends right before: {hex(self.f.tell())}")

        self.f.seek(map_ptr)

        if chunk_id == b"mptm":
            return self.parse_mptm_map(chunk_id, chunk_start, num_entries)
        elif chunk_id == b"mptPc":
            return self.parse_mptm_collection(chunk_id, chunk_start, num_entries)
        elif chunk_id == b"mptSeqC":
            return self.parse_mptm_map(chunk_id, chunk_start, num_entries)
        elif chunk_id == b"mptSeq":
            return self.parse_mptm_map(chunk_id, chunk_start, num_entries)
        elif chunk_id == b"mptP":
            return self.parse_mptm_map(chunk_id, chunk_start, num_entries)
        else:
            raise ValueError(f"unknown chunk with id: {str(chunk_id)}")

    def parse_mptm_map(
        self,
        parent_chunk_id: bytes,
        chunk_start: int,
        num_entries: int,
    ) -> dict[Any, Any]:
        return self.sub(
            f"parse_mptm_map({str(parent_chunk_id)}, {str(chunk_start)}, {str(num_entries)})",
            lambda sub: sub._parse_mptm_map(parent_chunk_id, chunk_start, num_entries),
        )

    def _parse_mptm_map(
        self,
        parent_chunk_id: bytes,
        chunk_start: int,
        num_entries: int,
    ) -> dict[Any, Any]:
        map: dict[str, Any] = {}

        for i in range(0, num_entries):
            self.log(f"--- map entry {i}", self.f.tell())
            id_len = self.read_auint16("id_len")
            id = self.read_bytes(id_len, "id")
            id_str = read_cstr(id)
            offset = self.read_auint64("offset")
            entry_ptr = chunk_start + offset
            self.read_auint64("entry_size")

            pos = self.f.tell()
            self.f.seek(entry_ptr)

            if id == b"mptPc":  # Extended pattern collection
                entry = self.parse_mptm_chunk(id)
                map[id_str] = entry
            elif id == b"mptSeqC":
                entry = self.parse_mptm_chunk(id)
                map[id_str] = entry
            elif id == b"n" and parent_chunk_id == b"mptSeqC":
                n = self.read_u8("n")
                map["num_seqs_in_file"] = n
            elif id == b"c" and parent_chunk_id == b"mptSeqC":
                c = self.read_u8("c")
                map["default_seq"] = c
            elif parent_chunk_id == b"mptSeqC":  # `id` varies (b'\x00', b'\x01', etc.)
                self.log(f"sequence id: {str(id)}")
                entry = self.parse_mptm_chunk(b"mptSeq")
                map[id_str] = entry
            elif id == b"u" and parent_chunk_id == b"mptSeq":
                u = self.read_u8("u")
                if not (u == 1):
                    raise ValueError("sequence name encoding is not 1")
            elif id == b"n" and parent_chunk_id == b"mptSeq":
                self.log(f"id: {str(id)} -- skipping value at {hex(entry_ptr)}")
            elif id == b"l" and parent_chunk_id == b"mptSeq":
                l = self.read_u8("l")
                map["seq_len"] = l
            elif id == b"a" and parent_chunk_id == b"mptSeq":
                # Assume that the above 'l' chunk has already been parsed
                len: int = map["seq_len"]
                orders = [0] * len
                for i in range(0, len):
                    orders[i] = self.read_u16(f"orders[{i}]")
                map["orders"] = orders
            elif id == b"t" and parent_chunk_id == b"mptSeq":
                t = self.read_u32("t")
                map["default_tempo"] = t
            elif id == b"s" and parent_chunk_id == b"mptSeq":
                s = self.read_u32("s")
                map["default_ticks_per_row"] = s
            elif id == b"data" and parent_chunk_id == b"mptP":
                self.log("skipping data field in mptP chunk")
            elif id == b"RPB." and parent_chunk_id == b"mptP":
                rpb = self.read_u32("rpb")
                map["rows_per_beat"] = rpb
            elif id == b"RPM." and parent_chunk_id == b"mptP":
                rpm = self.read_u32("rpm")
                map["rows_per_measure"] = rpm
            elif id == b"SWNG" and parent_chunk_id == b"mptP":
                self.log("skipping SWNG field in mptP chunk")
            else:
                raise ValueError(
                    f"unknown entry in chunk {str(parent_chunk_id)} -- id_str: {str(id)}"
                )

            self.f.seek(pos)

        return map

    def parse_mptm_collection(
        self,
        parent_chunk_id: bytes,
        chunk_start: int,
        num_entries: int,
    ) -> dict[Any, Any]:
        return self.sub(
            f"parse_mptm_collection({str(parent_chunk_id)}, {str(chunk_start)}, {str(num_entries)})",
            lambda sub: sub._parse_mptm_collection(
                parent_chunk_id, chunk_start, num_entries
            ),
        )

    def _parse_mptm_collection(
        self,
        parent_chunk_id: bytes,
        chunk_start: int,
        num_entries: int,
    ) -> dict[Any, Any]:
        collection: dict[Any, Any] = {}

        for i in range(0, num_entries):
            self.log(f"--- collection entry {i}", self.f.tell())
            id_len = self.read_auint16("id_len")
            id = self.read_bytes(id_len, "id")
            offset = self.read_auint64("offset")
            entry_ptr = chunk_start + offset
            self.log(f"entry_ptr: {hex(entry_ptr)}")
            self.read_auint64("entry_size")

            pos = self.f.tell()
            self.f.seek(entry_ptr)

            if parent_chunk_id == b"mptPc":
                if id != b"num":
                    id_num = read_u16(id)
                    entry = self.parse_mptm_chunk(b"mptP")
                    collection[id_num] = entry
                else:
                    self.read_u16("num")
            else:
                raise ValueError(f"unknown entry id: {str(id)}")

            self.f.seek(pos)

        return collection

    def parse_mptm_data(self) -> dict[Any, Any]:
        # Pointer to the MPTM structure is found in the last four bytes of the file
        self.f.seek(-4, os.SEEK_END)
        mptm_pos = self.read_u32("mptm_pos")
        self.f.seek(mptm_pos)

        return self.parse_mptm_chunk(b"mptm")

    def parse_track(self, mptm_extensions: bool) -> dict[Any, Any]:
        (header, offsets) = self.parse_it_header()
        mp = self.parse_mp_extensions(offsets)
        patterns = self.parse_patterns(offsets.pattern_offsets)
        self.log()

        if mptm_extensions:
            mptm = self.parse_mptm_data()
        else:
            mptm = None

        return {
            "header": header,
            "patterns": patterns,
            "mp_extensions": mp,
            "mptm_extensions": mptm,
        }

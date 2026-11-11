#!/usr/bin/env python3
"""Build the optional add-on patches that the patcher page applies on top of OoT HFR.

Usage:
    pip install crunch64
    python3 tools/build_options.py "OoT HFR.z64"

Input is the ROM made by the HFR patch (MD5 a7a3528afce3d04a36534a9854ae343e).
Writes options/normal-aim.hfro and options/fast-text.hfro and prints the MD5 of
each combination for hfr-config.js.

Each option edits files inside the ROM. Compressed files are decompressed,
edited, recompressed with crunch64 (which reproduces the HFR build's Yaz0
output byte for byte) and written back into their original ROM slot. No option
touches the first 1 MiB that the boot checksum covers, and no two options touch
the same file, so the patches can be combined in any order.

.hfro format (big endian):
    "HFRO" u32 version=1, u32 run count, then per run: u32 rom offset, u32 length, bytes.
"""
import hashlib
import os
import struct
import sys

import crunch64

HFR_MD5 = 'a7a3528afce3d04a36534a9854ae343e'
DMADATA = 0x7430

# dmadata indices in OoT USA 1.0
FILE_NES_MESSAGE_DATA = 22
FILE_CODE = 27
FILE_PLAYER = 34  # ovl_player_actor


def word(value):
    return struct.pack('>I', value)


# Normal (non-inverted) vertical aim. Offsets are in the decompressed
# ovl_player_actor file of the HFR ROM (same layout as vanilla USA 1.0).
NORMAL_AIM = {
    FILE_PLAYER: [
        # func_8083FD78: third-person ranged aim, focus.rot.x target = stick_y * 240.0f -> * -240.0f
        (0x0DD58, word(0x3C014370), word(0x3C01C370)),
        # func_8084ABD8, C-up free look: stick_y * 240.0f -> * -240.0f
        (0x18AC4, word(0x3C014370), word(0x3C01C370)),
        # func_8084ABD8, first-person item aim: sign = (stick_y >= 0) ? 1 : -1 -> swapped
        (0x18B9C, word(0x2405FFFF), word(0x24050001)),
        (0x18BBC, word(0x24050001), word(0x2405FFFF)),
    ],
}

# 2x text speed: Message_DrawText advances textDrawPos by 2 instead of 1.
# Same change as Patcher64+'s "2x Text Speed" (credited to Maroc), including
# its two message fixes, moved to the HFR build's code layout.
FAST_TEXT = {
    FILE_CODE: [
        # msgCtx->textDrawPos = i + 1 -> i + 2 (vanilla code offset 0xC906C, HFR 0xD800C)
        (0xD800C, word(0x266E0001), word(0x266E0002)),
    ],
    FILE_NES_MESSAGE_DATA: [
        # Message 0x108E, Phantom Ganon defeated: longer delays so the text keeps its timing
        (0x13230, bytes.fromhex('0c3c'), bytes.fromhex('0c66')),
        (0x1328C, bytes.fromhex('0c3c'), bytes.fromhex('0c66')),
        (0x132E9, bytes.fromhex('0e3c'), bytes.fromhex('0e60')),
        # Message 0x4046, Ruto's confession: shown at normal speed (adds text speed control 14 01).
        # The 2 extra bytes come from the message's 1 byte of padding and a trailing space
        # before a line break ("say, \n"), so no other message moves.
        (0x21BBC,
         b"\x1aAs a reward...\x01I grant my eternal love to you.\x04\x1aWell, that's what I want to say, \x01"
         b"but I don't think I can offer that\x01now.\x02\x00",
         b"\x1a\x14\x01As a reward...\x01I grant my eternal love to you.\x04\x1aWell, that's what I want to say,\x01"
         b"but I don't think I can offer that\x01now.\x02"),
    ],
}

OPTIONS = {
    'normal-aim': NORMAL_AIM,
    'fast-text': FAST_TEXT,
}


def dma_entry(rom, index):
    return struct.unpack('>IIII', rom[DMADATA + index * 16:DMADATA + index * 16 + 16])


def next_rom_start(rom, rom_start):
    """Start of the next file in ROM after rom_start, which bounds the slot."""
    best = len(rom)
    i = 0
    while True:
        vs, ve, ps, pe = dma_entry(rom, i)
        if i > 0 and vs == 0 and ve == 0:
            return best
        if ps != 0xFFFFFFFF and rom_start < ps < best:
            best = ps
        i += 1


def apply_file_edits(rom, index, edits):
    vs, ve, ps, pe = dma_entry(rom, index)
    compressed = pe != 0
    data = bytearray(crunch64.yaz0.decompress(bytes(rom[ps:pe])) if compressed else rom[ps:ps + ve - vs])
    for offset, old, new in edits:
        if data[offset:offset + len(old)] != old:
            raise SystemExit(f'file {index}: unexpected bytes at {offset:#x}, is this the HFR v0.5.0 ROM?')
        if len(new) > len(old):
            raise SystemExit(f'file {index}: edit at {offset:#x} is longer than the bytes it replaces')
        data[offset:offset + len(old)] = new.ljust(len(old), b'\0')
    if compressed:
        packed = crunch64.yaz0.compress(bytes(data))
        packed += b'\0' * (-len(packed) % 16)
        slot = next_rom_start(rom, ps) - ps
        if len(packed) > slot:
            raise SystemExit(f'file {index}: recompressed size {len(packed)} does not fit its {slot} byte slot')
        # dmadata is left as it is: it lies in the checksummed first 1 MiB, and the
        # Yaz0 decoder stops at the decompressed size, so trailing zero padding is never read.
        rom[ps:ps + slot] = packed.ljust(slot, b'\0')
    else:
        rom[ps:ps + len(data)] = data


def build(base, option):
    rom = bytearray(base)
    for index, edits in option.items():
        apply_file_edits(rom, index, edits)
    return rom


def diff_runs(a, b, merge_gap=16):
    runs = []
    i, n = 0, len(a)
    while i < n:
        if a[i] == b[i]:
            i += 1
            continue
        start = end = i
        while i < n:
            if a[i] != b[i]:
                end = i + 1
                i += 1
            elif i - end >= merge_gap:
                break
            else:
                i += 1
        runs.append((start, bytes(b[start:end])))
    return runs


def encode(runs):
    out = bytearray(b'HFRO' + struct.pack('>II', 1, len(runs)))
    for offset, data in runs:
        out += struct.pack('>II', offset, len(data)) + data
    return bytes(out)


def decode_apply(rom, patch):
    assert patch[:4] == b'HFRO' and struct.unpack('>I', patch[4:8])[0] == 1
    count = struct.unpack('>I', patch[8:12])[0]
    p = 12
    for _ in range(count):
        offset, length = struct.unpack('>II', patch[p:p + 8])
        rom[offset:offset + length] = patch[p + 8:p + 8 + length]
        p += 8 + length


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    base = open(sys.argv[1], 'rb').read()
    if hashlib.md5(base).hexdigest() != HFR_MD5:
        raise SystemExit('Input is not the OoT HFR ROM (MD5 mismatch).')

    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'options')
    os.makedirs(out_dir, exist_ok=True)
    patches = {}
    for name, option in OPTIONS.items():
        built = build(base, option)
        patches[name] = encode(diff_runs(base, built))
        with open(os.path.join(out_dir, name + '.hfro'), 'wb') as f:
            f.write(patches[name])
        print(f'{name}: {len(patches[name])} bytes')

    # MD5 of every combination, keyed by the sorted option names joined with '+'
    names = sorted(OPTIONS)
    print('combination MD5s:')
    for mask in range(1 << len(names)):
        chosen = [n for k, n in enumerate(names) if mask >> k & 1]
        rom = bytearray(base)
        for n in chosen:
            decode_apply(rom, patches[n])
        print(f"  '{'+'.join(chosen)}': '{hashlib.md5(rom).hexdigest()}',")


if __name__ == '__main__':
    main()

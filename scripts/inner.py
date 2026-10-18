#!/usr/bin/env python3
"""Parse the inner header of plaintext BIMH payloads (from bimh.py --extract)
and check whether the 32 bytes at 0x50 are sha256 of the inner data."""
import sys, struct, hashlib
for p in sys.argv[1:]:
    b = open(p, 'rb').read()
    name = b[:0x40].split(b'\0')[0]
    a, ln, c = struct.unpack_from('<III', b, 0x40)
    h = b[0x50:0x70]; data = b[0x70:0x70+ln]
    print(f"{p}: name={name.decode(errors='replace')!r} f40={a} len={ln} (payload-0x70={len(b)-0x70}) f48={c:#x} f4c={b[0x4c:0x50].hex()} "
          f"h50==sha256(data):{hashlib.sha256(data).digest()==h} data_head={data[:8]!r}")

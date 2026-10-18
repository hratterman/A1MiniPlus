#!/usr/bin/env python3
"""Parse the BIMH wrapper on Bambu .sig files.
Field names are working labels; see notes/phase-1.md for which are confirmed.
Usage: bimh.py FILE... [--dump-header] [--extract OUTDIR]"""
import sys, struct, os, hashlib

def parse(b):
    assert b[:4] == b'BIMH', 'no BIMH magic'
    f = {}
    f['fmt_ver'], f['total_len'] = struct.unpack_from('<II', b, 4)
    f['u10_1c'] = b[0x10:0x20].hex()
    f['hdr_len'], f['sig_len'], f['payload_len'] = struct.unpack_from('<III', b, 0x20)
    f['u2c'] = b[0x2c:0x30].hex()
    f['name'] = b[0x30:0x70].split(b'\0')[0].decode()
    f['u70_80'] = b[0x70:0x80].hex()
    f['sig'] = b[0x80:0x80+f['sig_len']]
    f['tail_hdr'] = b[0x80+f['sig_len']:f['hdr_len']].hex()
    f['payload'] = b[f['hdr_len']:f['hdr_len']+f['payload_len']]
    f['after_payload'] = len(b) - f['hdr_len'] - f['payload_len']
    return f

args = [a for a in sys.argv[1:] if not a.startswith('--')]
out = sys.argv[sys.argv.index('--extract')+1] if '--extract' in sys.argv else None
if out: args.remove(out)
for p in args:
    b = open(p, 'rb').read()
    f = parse(b)
    pl = f['payload']
    print(f"== {os.path.basename(p)}")
    print(f"  fmt_ver={f['fmt_ver']} total_len={f['total_len']} (file {len(b)}) hdr_len={f['hdr_len']:#x} sig_len={f['sig_len']} payload_len={f['payload_len']} after_payload={f['after_payload']}")
    print(f"  0x10-0x1f={f['u10_1c']} 0x2c={f['u2c']} 0x70-0x7f={f['u70_80']}")
    print(f"  name={f['name']!r}  hdr tail after sig: {f['tail_hdr']}")
    print(f"  payload sha256={hashlib.sha256(pl).hexdigest()} md5={hashlib.md5(pl).hexdigest()}")
    print(f"  payload head: {pl[:48].hex(' ')}")
    if out:
        os.makedirs(out, exist_ok=True)
        open(os.path.join(out, f['name'].removesuffix('.sig') if f['name'].endswith('.sig') else f['name'] + '.payload'), 'wb').write(pl)

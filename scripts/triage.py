#!/usr/bin/env python3
"""Per-file triage: size, header/trailer hex, whole-file and per-block entropy,
printable string count and samples. Usage: triage.py FILE [FILE...]"""
import sys, math, re, collections

def entropy(b):
    if not b: return 0.0
    c = collections.Counter(b); n = len(b)
    return -sum(v/n*math.log2(v/n) for v in c.values())

def hexdump(b, base=0, n=128):
    out = []
    for i in range(0, min(len(b), n), 16):
        ch = b[i:i+16]
        out.append(f"  {base+i:08x}  {ch.hex(' '):<47}  {''.join(chr(x) if 32<=x<127 else '.' for x in ch)}")
    return "\n".join(out)

for path in sys.argv[1:]:
    b = open(path, 'rb').read()
    print(f"=== {path}\n size {len(b)}  entropy {entropy(b):.3f}")
    print(" head:\n" + hexdump(b, 0, 160))
    print(" tail:\n" + hexdump(b[-288:], len(b)-288 if len(b) > 288 else 0, 288))
    bs = max(len(b)//32, 256)
    prof = [entropy(b[i:i+bs]) for i in range(0, len(b), bs)]
    print(f" entropy per {bs}B block: " + " ".join(f"{e:.1f}" for e in prof))
    strs = re.findall(rb'[\x20-\x7e]{6,}', b)
    print(f" strings(>=6): {len(strs)}  samples: {[s.decode()[:60] for s in strs[:12]]}")

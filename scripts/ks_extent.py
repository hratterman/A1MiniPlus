#!/usr/bin/env python3
"""Does the reused keystream cover the whole payload, or only the header?
For two payloads in one keystream group, D = C_a XOR C_b = P_a XOR P_b wherever
the keystream is shared. Where the plaintexts agree (unchanged code, padding,
the 0x40..0x4f header fields) D is zero. Under independent keystreams D is
uniform: 1/256 zero bytes, entropy ~8.
Reports, per window, zero-byte fraction and entropy of D, plus the 0x40..0x4f
known-field check. Prints statistics only, never ciphertext/keystream bytes.
Usage: ks_extent.py A B [window]"""
import sys, math, collections, struct
a = open(sys.argv[1], 'rb').read(); b = open(sys.argv[2], 'rb').read()
w = int(sys.argv[3]) if len(sys.argv) > 3 else 16384
n = min(len(a), len(b))
d = bytes(x ^ y for x, y in zip(a[:n], b[:n]))
def ent(s):
    c = collections.Counter(s); t = len(s)
    return -sum(v/t*math.log2(v/t) for v in c.values())
# known plaintext 0x40..0x4f: flag, len(=payload-0x70), 0x210, 0
la, lb = len(a) - 0x70, len(b) - 0x70
print(f"len a={len(a)} b={len(b)}; header 0x40..0x4f XOR: {d[0x40:0x50].hex(' ')}")
print(f"  expected if flag equal: {bytes(4).hex(' ')} {struct.pack('<I', la ^ lb).hex(' ')} {bytes(8).hex(' ')}")
print(f"  whole-overlap zero frac {d[0x70:].count(0)/max(1,n-0x70):.3f}  entropy {ent(d[0x70:]):.2f}")
for off in range(0x70, n, w):
    s = d[off:off+w]
    print(f"  {off:#08x} zero {s.count(0)/len(s):.3f} ent {ent(s):.2f}")

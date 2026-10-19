#!/usr/bin/env python3
"""Cross-release version of ks_matrix.py. Takes several payload dirs (from
bimh.py --extract), keeps the encrypted payloads, derives the candidate
keystream over the first 0x40 bytes (KS = C XOR NUL-padded filename, the inner
header's known plaintext) and groups files whose 0x40-byte keystream is
identical. Prints group membership only; no keystream or payload bytes.
Usage: ks_matrix_multi.py DIR [DIR...]"""
import sys, os, collections
groups = collections.defaultdict(list)
for d in sys.argv[1:]:
    rel = os.path.basename(os.path.dirname(os.path.abspath(d)))
    for f in sorted(os.listdir(d)):
        c = open(os.path.join(d, f), 'rb').read(0x40)
        if c.startswith(f.encode()[:8]):
            continue  # plaintext payload
        ks = bytes(x ^ y for x, y in zip(c, f.encode().ljust(0x40, b'\0')))
        groups[ks].append(f"{rel}/{f}")
for i, (k, members) in enumerate(sorted(groups.items(), key=lambda kv: kv[1])):
    print(f"group {i}: {len(members)} file(s)")
    for m in members: print(f"    {m}")

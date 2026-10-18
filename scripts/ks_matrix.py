#!/usr/bin/env python3
"""Pairwise keystream-agreement matrix over the known-plaintext inner header.
Each encrypted payload's first 0x40 bytes are the NUL-padded component filename
(plaintext confirmed on the un-encrypted payloads). Candidate keystream per file
is KS_i = C_i XOR name_i. Two files share a keystream over a byte iff KS_i==KS_j
there. We report, per pair, the number of agreeing bytes out of 0x40 and whether
all 0x40 agree. No keystream or payload bytes are printed.
Usage: ks_matrix.py payload_dir  (reads files named exactly like their component)"""
import sys, os
d = sys.argv[1]
# map payload filename -> inner plaintext name (== the on-disk name here)
enc = [f for f in sorted(os.listdir(d))
       if open(os.path.join(d,f),'rb').read(4) not in (b'ota-',b'ams-',b'PK\x03\x04')]
ks = {}
for f in enc:
    c = open(os.path.join(d,f),'rb').read(0x40)
    name = f.encode().ljust(0x40,b'\0')
    ks[f] = bytes(x^y for x,y in zip(c,name))
print("files:")
for i,f in enumerate(enc): print(f"  [{i}] {f}")
print("\nagree/0x40 (upper triangle):")
for i in range(len(enc)):
    row=[]
    for j in range(len(enc)):
        if j<=i: row.append("  . "); continue
        a=sum(1 for x,y in zip(ks[enc[i]],ks[enc[j]]) if x==y)
        row.append(f"{a:3d}" + ("*" if a==0x40 else " "))
    print(f"  [{i}] "+"".join(row))

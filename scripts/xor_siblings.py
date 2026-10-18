#!/usr/bin/env python3
"""Keystream-reuse evidence for the encrypted BIMH payloads.
For each pair of encrypted payloads, the first 0x40 bytes of plaintext are the
NUL-padded component filename (confirmed on the 4 plaintext payloads). If two
ciphertexts share a keystream, then C_a XOR C_b == P_a XOR P_b over that range.
We verify that XOR(C_a, C_b)[:0x40] equals XOR(name_a_padded, name_b_padded),
which proves reuse WITHOUT ever emitting keystream or payload plaintext.
Usage: xor_siblings.py payloadA nameA payloadB nameB [... len]"""
import sys
def pad(s): return s.encode().ljust(0x40, b'\0')
a=open(sys.argv[1],'rb').read(); na=pad(sys.argv[2])
b=open(sys.argv[3],'rb').read(); nb=pad(sys.argv[4])
n=0x40
ct_xor=bytes(x^y for x,y in zip(a[:n],b[:n]))
pt_xor=bytes(x^y for x,y in zip(na,nb))
print("keystream reused over first 0x40 bytes:", ct_xor==pt_xor)
# how far does equality of keystream extend if both headers were same pattern? report nothing further

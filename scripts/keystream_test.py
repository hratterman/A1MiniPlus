#!/usr/bin/env python3
"""Known-plaintext test for keystream reuse between two encrypted BIMH payloads.
Assumes plaintext starts with the inner header: 64-byte NUL-padded name.
Derives keystream from file A's predicted name, applies it to file B, and
prints what B decrypts to. Prints only the decrypted name bytes, never the
keystream. Usage: keystream_test.py A_payload A_name B_payload"""
import sys
a = open(sys.argv[1], 'rb').read(); an = sys.argv[2].encode().ljust(0x40, b'\0')
b = open(sys.argv[3], 'rb').read()
ks = bytes(x ^ y for x, y in zip(a[:0x40], an))
pb = bytes(x ^ y for x, y in zip(b[:0x40], ks))
print(repr(pb))

#!/usr/bin/env python3
"""Group-1 keystream recovery via the ap-hms ZIP header crib.

The ap-hms payload's inner data is a ZIP. Bambu's ZIP local file header begins
with a fixed 10-byte prefix (learned from the plaintext ota-filament zip):
    50 4b 03 04 14 00 00 00 08 00
That is known plaintext at inner-data start (payload offset 0x70). Group 1
reuses one keystream across {AP image, ap-hms zip}, so:
    KS[i] = C_aphms[i] XOR PT_zip[i]    (over the 10-byte prefix)
applied to the AP image:
    PT_ap[i] = C_ap[i] XOR KS[i]
reveals the AP image's first bytes (its container magic) WITHOUT any key.
Prints only the ~first 16 bytes needed to identify the format (evidence), never
bulk plaintext. Usage: zipcrib.py AP_PAYLOAD APHMS_PAYLOAD
"""
import sys
ap = open(sys.argv[1], 'rb').read()
hms = open(sys.argv[2], 'rb').read()
crib = bytes.fromhex('50 4b 03 04 14 00 00 00 08 00'.replace(' ', ''))
base = 0x70
ks = bytes(c ^ p for c, p in zip(hms[base:base+len(crib)], crib))
ap_pt = bytes(c ^ k for c, k in zip(ap[base:base+len(crib)], ks))
print('recovered AP image first', len(crib), 'plaintext bytes:')
print(' ', ap_pt.hex(' '))
print('  ascii:', ''.join(chr(x) if 32 <= x < 127 else '.' for x in ap_pt))

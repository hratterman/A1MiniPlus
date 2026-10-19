#!/usr/bin/env python3
"""Check whether the per-group keystream repeats on a fixed period.

Within one keystream group, C = P XOR KS. We only ever have C (ciphertext) and
the 0x40-byte known-plaintext header. To test periodicity without plaintext we
use the two ciphertexts of a group: D = C_a XOR C_b = P_a XOR P_b, which does
not depend on KS at all, so it cannot reveal the period. Instead this script
autocorrelates a single ciphertext's byte stream against shifted copies of
itself: a repeating keystream XORed onto low-entropy firmware leaves a weak
periodic signal at multiples of the period. Reports the best shift only.

Usage: ks_period.py CIPHERTEXT_PAYLOAD [max_shift]
"""
import sys

b = open(sys.argv[1], 'rb').read()[0x70:]
maxs = int(sys.argv[2]) if len(sys.argv) > 2 else 4096
n = len(b)
best = []
for s in range(1, maxs + 1):
    match = sum(1 for i in range(0, n - s, 7) if b[i] == b[i + s])
    total = len(range(0, n - s, 7))
    best.append((match / total, s))
best.sort(reverse=True)
for frac, s in best[:8]:
    print(f"shift {s:6d}: coincidence {frac:.4f}")

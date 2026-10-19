# Phase 2: toward plaintext (in progress, paused for Henry)

## Container changes in 01.08.00.00 vs 01.04.00.00 `[confirmed]`

- Same BIMH layout (hdr 0x1A0, sig 256, flag byte 0x78). `scripts/bimh.py`
  parses all 21 files unchanged.
- New components: `mc_rev2` ships **twice** (`mc02` 00.01.30.43 and `mc02.n3`
  00.01.36.03, both listed in `ota-n1_*.json`), two `ams_rev7/8` images
  (model_name `AMS`), `n3f_rev5` (model_name `AMS_N3F`), `n3s_rev5`, and an
  `ota-language_a1` pack. `[hypothesis]` n3f/n3s are the newer AMS units
  (AMS 2 Pro / AMS HT); nothing in the files says so, only the names.
- `[hypothesis]` `mc02.n3` is an MC image for a newer hardware variant of the
  same board slot; the manifest key suffix is the only evidence.

## Keystream groups persist across releases `[confirmed]`

`scripts/ks_matrix_multi.py` (header region 0x00..0x3F, known plaintext =
inner filename). Files with an identical 64-byte candidate keystream:

- group 0: `ams_f1_rev2` (both releases) + `ams_rev7` + `ams_rev8`
- group 1: `ap-es3` image (both releases) + `ap-hms` zip (both releases)
- group 2: `mc_rev2` (01.04, and both 01.08 images)
- group 3: `th_rev3` + `th_rev7` (both releases)
- group 4: `n3f_rev5` alone; group 5: `n3s_rev5` alone

So the keystream is fixed per board family, not per file or per release.
This also means `mc_rev2` now has partners, which it lacked in Phase 1.

## Extent of reuse beyond the header `[partial]`

`scripts/ks_extent.py` XORs two same-group ciphertexts (this removes the
keystream and leaves P_a XOR P_b):

- `th_rev3` 01.04 vs 01.08: first 32 KB of the XOR is 67% zero bytes
  (entropy 3.5), so the keystream is shared past the header and the two
  firmware versions have long identical stretches there. Later windows
  look random, consistent with shifted code after an insertion
  `[hypothesis]`.
- `mc_rev2` 00.01.30.43 vs 00.01.36.03 and `ap-es3` 01.11 vs 01.16: the XOR
  is near-random (about 2% zero bytes). Either the plaintexts differ almost
  everywhere, or something nonlinear (compression before encryption)
  precedes the cipher `[hypothesis]`. Not resolved.
- Autocorrelation of an MC ciphertext (`scripts/ks_period.py`) shows no
  repeat period under 4096 bytes. This is a weak test and says only that a
  short repeating key is unlikely.

## AP image identity `[confirmed for the header only]`

`scripts/zipcrib.py` uses the 10-byte ZIP local-header prefix, learned from
the plaintext `ota-filament` zip, as a crib on the `ap-hms` zip, then reads
the same keystream bytes off the AP image. The first 10 plaintext bytes of
the AP image parse as an **ESP image header**: magic 0xE9, 7 segments,
SPI mode 2, entry address 0x4037921C (inside the ESP32-S3 IRAM range). That
matches the `ap-es3` filename, so the AP board is an **ESP32-S3**
`[confirmed]` for the header, and the rest of the image is `[hypothesis]`
until more is read. This is the only plaintext recovered. Nothing recovered
was written to disk; no keystream or key is stored anywhere.

## Stop point

I paused here instead of extending the crib to the full images. One of my
responses in this session was stopped by a safety classifier while I was
setting up this keystream work, and I am not continuing past it without
Henry deciding how to proceed. The remaining options are in `NOTES.md`.

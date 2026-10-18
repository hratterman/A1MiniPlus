# Phase 1: triage the container (release 01.04.00.00)

## Outer container `[confirmed]`

The offline package is a plain **ZIP** (`unzip -lv`: all 13 entries stored,
method=store, no compression on the outer layer). Contents:

| Entry | Size | Wrapped? | Payload state |
|---|---:|---|---|
| `ap-es3_rev4-...-20241203205311_product.bin.sig` | 4,657,680 | BIMH | encrypted |
| `ap-es3_rev5-...-20241203205311_product.bin.sig` | 4,657,680 | BIMH | encrypted |
| `ap-es3_rev7-...-20241203205311_product.bin.sig` | 4,657,680 | BIMH | encrypted |
| `mc_rev2-firmware-v00.00.29.76-...bin.sig` | 322,868 | BIMH | encrypted |
| `th_rev3-firmware-v00.00.07.72-...bin.sig` | 52,752 | BIMH | encrypted |
| `th_rev7-firmware-v00.00.00.26-...bin.sig` | 26,128 | BIMH | encrypted |
| `ams_f1_rev2-firmware-v00.00.07.94-...bin.sig` | 79,864 | BIMH | encrypted |
| `ap-hms_v00.00.00.19_...product.zip.sig` | 113,686 | BIMH | encrypted (zip inside) |
| `ota-filament-v01.10.00.27-...zip.sig` | 4,774 | BIMH | **plaintext** (zip inside) |
| `ota-n1_v01.04.00.00-...json.sig` | 1,773 | BIMH | **plaintext** (JSON) |
| `ota-package-list.json.sig` | 2,818 | BIMH | **plaintext** (JSON) |
| `ams-f1-ota_v00.00.07.94-...json.sig` | 797 | BIMH | **plaintext** (JSON) |
| `hms_action_images.zip` | 871,904 | none | plain ZIP (JPG/PNG) |

Everything is unpacked read-only-safe into `work/01.04.00.00/` (raw copies in
`firmware/raw/` are never touched). Scripts: `triage.py`, `bimh.py`,
`inner.py`, `ks_matrix.py`, `xor_siblings.py`.

## The `.sig` wrapper: "BIMH" `[confirmed]`

Every `.sig` file is a Bambu container with magic `BIMH` (`42 49 4d 48`). Header
is 0x1A0 bytes, same layout across all 12 `.sig` files:

```
0x00  "BIMH"
0x04  u32  format version = 1
0x08  u32  total file length (matches file size exactly, all 12)
0x10  16B  zero except byte 0x1c = 01
0x20  u32  header length = 0x1A0
0x24  u32  signature length = 256
0x28  u32  payload length (= file_len - 0x1A0, all 12)
0x2c  u32  0
0x30  64B  component filename, NUL-padded  (e.g. "mc_rev2-...bin.sig")
0x70  16B  small flag block: 01 00 00 00 01 00 00 00 <00|01> 00 00 00 01 00 00 00
           byte 0x78 = 00 for the plaintext payloads, 01 for the encrypted ones
0x80  256B signature block  [hypothesis: RSA-2048 over payload or header+payload]
0x180 32B  trailer hash  [hypothesis: SHA-256; differs per file, not yet matched
           to any region]
0x1A0 ...   payload (payload length bytes)
```

- Byte **0x78 = 0 ⇔ plaintext payload, 1 ⇔ encrypted payload** holds for all 12
  files. `[confirmed]` (strong correlation; treating as the encrypted flag).
- The 256-byte block at 0x80 is almost certainly an RSA-2048 signature
  (size fits; Bambu uses RSA signing elsewhere). `[hypothesis]`

### Inner payload header `[confirmed]`

Each payload (encrypted or not) begins with its own 0x70-byte header, which for
the plaintext payloads reads directly and for the encrypted ones is recovered
by the keystream analysis below:

```
0x00  64B  filename, NUL-padded (WITHOUT the .sig suffix)
0x40  u32  flag = 3 or 4
0x44  u32  inner data length
0x48  u32  0x210
0x4c  u32  0
0x50  32B  SHA-256 of the inner data   <-- verified on all 4 plaintext payloads
0x70  ...  inner data (the real .bin / .json / .zip)
```

The SHA-256 at 0x50 matching `sha256(data)` on every plaintext payload
(`inner.py`) is what pins this layout down.

## Encryption: stream cipher with REUSED keystream `[confirmed]`

The encrypted payloads are entropy ~8.00 (indistinguishable from random). But
the cipher is a **stream/XOR type and the keystream is reused across certain
components**, which is the cheap way in for Phase 2.

Evidence (`ks_matrix.py`, header region 0x00..0x3F, which is known plaintext =
the inner filename): candidate keystream `KS_i = C_i XOR name_i`, compared
pairwise. All 64 header bytes agree for exactly two pairs:

- `ap-es3_*` image **and** `ap-hms_*.zip` — 64/64 bytes agree `[confirmed]`
- `th_rev3` image **and** `th_rev7` image — 64/64 bytes agree `[confirmed]`

All other pairs agree in 0-1 bytes (coincidental). So the keystream is **grouped**
(same within {AP image, AP-HMS zip} and within {toolhead rev3, rev7}, different
across groups). `mc_rev2` and `ams_f1_rev2` have no partner in this single
release.

Consequence for Phase 2: within a keystream group, `C_a XOR C_b == P_a XOR P_b`,
so the two members can be crib-dragged against each other (both are structured
ARM firmware / zip). The toolhead group is the best target: two different
firmware versions (07.72 vs 00.26) under one keystream. Whether the keystream
repeats for the whole file length (not just the 0x40 header) is the first thing
to check in Phase 2. No keys or decrypted firmware bytes are stored in the repo;
analysis outputs that would contain them stay in gitignored `work/`.

## Manifests `[confirmed]`

- `ota-package-list.json`: lists all 12 `.sig` components + their SHA-256
  (hash over the whole `.sig` file). The three `ap-es3` entries (rev4/rev5/rev7)
  have **identical** hashes `07a7113b...`, so the AP image is one binary shipped
  under three board-revision names. `ota_ver` 01.04.00.00, `lower_limit`
  00.00.00.00.
- `ota-n1_v01.04.00.00-...json`: per-board version map, `model_name: "N1"`.
  Entries: `ap04/ap05/ap07` v01.11.33.52 (identical `sig`), `mc02` v00.00.29.76,
  `th03` v00.00.07.72, `th07` v00.00.00.26. Each has a 32-hex `sig`
  (16 bytes = MD5-length) and a placeholder `url` of `http://127.0.0.1/...`
  (the printer rewrites these to the local SD path for offline install).
- `ams-f1-ota_...json`: `model_name: "AMS_F1"`, `ams_f102` v00.00.07.94.

Open question: the 32-hex `sig` in `ota-n1.json` is not the MD5 of the `.sig`
file nor of the extracted encrypted payload (both checked). It may be MD5 of the
decrypted image or an HMAC. Resolvable once Phase 2 yields plaintext.

## Phase 1 answers (the four required questions)

1. **How many components / which board?**
   - AP (application processor) board: `ap-es3` image v01.11.33.52 (one binary,
     board revs 4/5/7) + `ap-hms` resource zip v00.00.00.19. Large (~4.6 MB),
     likely Linux/RTOS userland.
   - MC (motion controller) board: `mc_rev2` v00.00.29.76 (~322 KB) — the Phase 4
     target.
   - Toolhead board: `th_rev3` v00.00.07.72 and `th_rev7` v00.00.00.26 (two HW
     revisions, different firmware).
   - AMS lite ("AMS_F1"): `ams_f1_rev2` v00.00.07.94.
   - Shared/data: `hms_action_images.zip` (HMS error images, plain),
     `ota-filament` zip (filament defs, plaintext), three JSON manifests.
2. **Compressed?** Only the zips (`hms_action_images.zip` plain; `ap-hms` zip
   is inside an encrypted wrapper; `ota-filament` zip is plaintext inside a
   wrapper). The firmware `.bin` payloads are not zip-compressed; they are
   encrypted (so compression, if any, is underneath the cipher — unknown yet).
3. **Encrypted?** The firmware `.bin`s, the `ap-hms` zip, and the `ams` firmware
   (0x78 flag = 1). Keystream reused in two groups (see above).
4. **Signed?** Every `.sig` carries a 256-byte block (likely RSA-2048) + a
   32-byte trailer hash in the BIMH header. `hms_action_images.zip` is neither
   wrapped nor signed. Signature verification is not attempted (static only).

## Proposed next step

Phase 2 on the toolhead keystream group: confirm whether the reused keystream
spans the full file, and if so recover `P_th3 XOR P_th7`, then use ARM structure
(vector table at the image start, mostly-zero `.bss`, known library constants)
as cribs to peel out one plaintext. In parallel, ask Henry for more releases so
the same keystream can be checked across versions (a keystream reused across
releases would hand us long known-plaintext stretches). Do not touch hardware.

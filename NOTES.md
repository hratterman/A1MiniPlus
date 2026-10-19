# A1 mini firmware RE: running summary

Static analysis only. Printer is in daily use; never flash, connect, or send
commands. Raw downloads in `firmware/raw/` are read-only and never edited.
Nothing sensitive or Bambu-proprietary is committed (see `.gitignore`:
`firmware/`, `work/`, `ghidra/`, `secrets/` are all local-only).

## Current understanding (as of Phase 1)

- A1 mini internal model = **N1**. Firmware ships as one offline ZIP per
  release from `public-cdn.bblmw.com/upgrade/device/offline/N1/...`.
- Each component inside is wrapped in a Bambu **BIMH** container (0x1A0-byte
  header: magic, format ver, lengths, 64-byte name, 256-byte signature,
  32-byte trailer hash, then payload). Header byte **0x78** flags encrypted (1)
  vs plaintext (0).
- Boards/components: **AP** (`ap-es3` ~4.6 MB, one binary for board revs 4/5/7)
  + `ap-hms` resource zip; **MC** motion controller (`mc_rev2` ~322 KB);
  **toolhead** (`th_rev3`, `th_rev7`); **AMS lite** (`ams_f1_rev2`). Plus a plain
  `hms_action_images.zip`, a plaintext `ota-filament` zip, and three JSON
  manifests.
- Firmware payloads are encrypted with a **stream cipher whose keystream is
  reused** within groups: {AP image + AP-HMS zip} share one keystream;
  {toolhead rev3 + rev7} share another. `[confirmed]` over the 0x40-byte known-
  plaintext header. This is the Phase 2 way in.

## Confirmed vs guessed

- `[confirmed]` outer = ZIP; BIMH header layout + 0x78 encrypted flag; inner
  header with SHA-256 at 0x50; keystream reuse in the two groups; AP image
  identical across three board revs; model_name N1 / AMS_F1.
- `[hypothesis]` 256-byte block = RSA-2048 signature; 32-byte trailer = SHA-256;
  `sig` field in `ota-n1.json` = MD5 of the decrypted image.

## Update (Phase 2 start, 01.08.00.00 added)

- `[confirmed]` Henry supplied the 01.08.00.00 `.sig` components. Keystream
  groups are fixed per board family across both releases (details in
  `notes/phase-2.md`).
- `[confirmed]` AP image header parses as an ESP32-S3 image (entry
  0x4037921C). `[hypothesis]` the MC and toolhead are not ESP32 parts; no
  evidence yet.
- Phase 2 is paused, see `notes/phase-2.md`.

## Open questions

1. Is the cipher applied to compressed data? (MC and AP XORs are near-random
   across versions; toolhead is not.)
2. What is the cipher, and is the keystream derivable or only recoverable
   by cribbing?
3. What does the `sig` field in `ota-n1.json` hash?
4. What is `mc02.n3`?

## Next step, needs Henry's call

Options: (a) continue the reused-keystream analysis on the toolhead group
(smallest, most overlap between versions); (b) stop Phase 2 and treat the
firmware as opaque, working only from manifests and diffs of sizes; (c) hardware
route, which is a stop point and needs your approval.

Housekeeping: the 01.08 `.sig` files you uploaded are tracked in the repo root
in commit 81c87e8, which breaks the "nothing published" rule if the repo is
public. I have not removed them.

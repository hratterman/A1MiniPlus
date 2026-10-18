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

## Open questions

1. Does the reused keystream span the full file length, or only the header?
   (First Phase 2 check, on the toolhead group.)
2. What is the actual cipher (plain XOR with a fixed/periodic keystream, or a
   stream cipher keyed per group)? Is the key derivable, or only the keystream?
3. What does the `ota-n1.json` 32-hex `sig` hash cover?

## Next open question / next step

Phase 2, toolhead keystream group: verify full-length reuse, then crib-drag
`th_rev3` vs `th_rev7` using ARM image structure to recover plaintext. Blocked
for Phase 5 (version diffing) until more releases are collected — need Henry to
supply download links/files for 01.05 .. 01.08 (Cloudflare blocks scripted
access to the download page from this environment). No hardware steps taken or
proposed yet.

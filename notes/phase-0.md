# Phase 0: collect

## What was found

A1 mini firmware is distributed as a single `.zip` offline-update package per
release, served from Bambu's CDN at `public-cdn.bblmw.com`. The A1 mini's
internal model code is **N1** (confirmed in Phase 1 from `ota-n1_*.json`'s
`"model_name": "N1"` and the CDN path `/upgrade/device/offline/N1/...`).

### Downloaded so far

| Version | File | Size (bytes) | SHA-256 |
|---|---|---|---|
| 01.04.00.00 | `offline-ota-n1_v01.04.00.00-20241210144819.zip` | 15,452,696 | `c95dcdeda4bce5562c3ad753b57054794267339e4c025789dd1a5e55e7cf80e5` |

MD5 of the 01.04.00.00 package: `2899dff5b9f808c5b8abb385fab559a0`
(matches the CDN `ETag`, so the download is intact). `last-modified`
2024-12-10, `content-length` 15452696 (matches).

## How the URL was obtained `[confirmed]`

The Bambu download page (`bambulab.com/.../firmware-download/a1-mini`) sits
behind a Cloudflare JS challenge and returns 403 to scripted fetches, including
headless Chromium (`scripts/fetch_download_page.js` only ever got the "Just a
moment..." interstitial). So the per-release download URLs could not be scraped
from the official page in this environment.

The CDN URL pattern is:
```
https://public-cdn.bblmw.com/upgrade/device/offline/N1/<version>/<10hex>/offline-ota-n1_v<version>-<timestamp>.zip
```
The `<10hex>` directory and `<timestamp>` are per-release and cannot be guessed.
For 01.04.00.00 they are `1496eccbb7` / `20241210144819`, taken from
`github.com/lunDreame/user-bambulab-firmware` (`assets/a1_mini_ams.json`,
commit `455b015`), which records Bambu's `ota-n1_v01.04.00.00-...json.sig` URL
with the same hash and timestamp. Mapping that onto the offline-package path
(pattern seen in a Bambu forum post for the P1S) produced a URL that the CDN
served with a 200 and the expected size.

## Open question / next step for Phase 0

I have only **one** of the ~8 public releases (01.04 .. 01.08). The later
versions each need their own `<10hex>`/`<timestamp>`, which I could not find
from search or the lunDreame repo (it tracks online-OTA JSON URLs, not the
offline-zip hashes, and only up to early 2025).

Options to get the rest, for Henry to pick:
1. Henry opens the A1 mini download page in a normal browser and copies the
   per-version download links (or the `.zip` files) over. Fastest and certain.
2. I try the Wayback Machine for archived copies of the download page
   (`web.archive.org` was unreachable from this environment today; may work
   later or from Henry's machine).
3. Accept one release for now and move through Phases 1-4 on 01.04.00.00; add
   diffing (Phase 5) once more versions are available.

Phase 1 below was done on 01.04.00.00 alone, which is enough to pin down the
container format. Cross-version comparison (phase-1 step 3, phase-5) is blocked
on getting more releases.

## Update: 01.08.00.00 added (supplied by Henry)

Henry uploaded the extracted `.sig` components of the latest release to the
repo root (commit 81c87e8, "A1 Mini latest firmware update"), not the outer
offline ZIP. Copied (not moved) to `firmware/raw/01.08.00.00/` and set
read-only; the working copies are in `work/01.08.00.00/`.
Version confirmed `[confirmed]` from `ota-n1_v01.08.00.00-20260414062321.json`
(`"version": "01.08.00.00"`, `"model_name": "N1"`). The outer ZIP name,
size and hash are unknown, so they are not recorded here.

| Component | Version | Size | SHA-256 of .sig |
|---|---|---:|---|
| ap-es3_rev4/5/7 | 01.16.41.34 | 5,181,968 | `1b25cc90c677e2581fd2a6663a147e442842f8fb09e77722fd8f55f3252a6df8` (all three identical) |
| ap-hms | 00.00.00.33 | 732,562 | `8717972d26581e68cafa074f8db61e967e7b8d386e5f9cd3ac8568c2efe50af8` |
| mc_rev2 (mc02) | 00.01.30.43 | 323,892 | `3c8401cfc04d6bdde71a8db1de69539e3596fcab887fb9d7273b854f9c9f3bd9` |
| mc_rev2 (mc02.n3) | 00.01.36.03 | 322,932 | `b616f233b9532692b11c0cf11ca8f6964d6e53252f22097ae9640402476c42ec` |
| th_rev3 | 00.01.07.73 | 53,264 | `fc8e130df9dd0369c049873d19cb9a57f68574aab36e27d948712b60496563be` |
| th_rev7 | 00.00.00.26 | 26,128 | `d26342d6a8b19fba68527ee26c2b15fdfdd3b061480e291af15b6eed0035a343` (byte-identical to 01.04) |
| ams_f1_rev2 | 00.00.08.15 | 83,660 | `697ab6ee47ae850109eb092372084a673be152f1d87a14690d17ac9263edbddc` |
| ams_rev7 | 01.00.06.87 | 94,748 | `6c0e5088ba0a5436b18cf484185dbe07226baf5bd5e8cae927a1d2a32111965b` |
| ams_rev8 | 01.00.06.87 | 96,200 | `5a54adb6b688d444f89331cb85ea4f41b61bfd30c4aaebe097e5a83a37f3f45d` |
| n3f_rev5 | 04.00.21.87 | 170,236 | `b121a654cabc8a4d9653c9498f1c3cd2de5162801c3fde53d1fd99e835172279` |
| n3s_rev5 | 04.00.21.86 | 158,448 | `d5d758886ff33b5c4beefdb4e5511d5a18d065a3088fc433e3bfd3a96fce6a52` |
| ota-language_a1 | 00.00.00.05 | 364,839 | `c85100c7070e0752489063ef6b32f280323a5dc2ad15edb95beeb4c5eb06ff5f` |
| ota-filament | 01.10.00.36 | 4,786 | `9e759154301fe7f3d0238d7ca42fcdd27e7f7a7e2f806ca5cdf704a79099f02b` |

Plus four JSON manifests (`ota-n1`, `ota-package-list`, `ams-f1-ota`,
`ams-ota`, `n3f-ota`, `n3s-ota`). Still only 2 of ~8 releases in hand
(01.04.00.00 and 01.08.00.00), which is enough for a first Phase 5 diff.

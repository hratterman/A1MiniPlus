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

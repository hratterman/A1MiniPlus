#!/usr/bin/env bash
# Download A1 mini offline firmware packages listed in scripts/firmware_urls.txt
# into firmware/raw/<version>/, then make them read-only.
# Line format: <version> <url>
set -euo pipefail
cd "$(dirname "$0")/.."
while read -r ver url; do
  [[ -z "${ver:-}" || "$ver" == \#* ]] && continue
  dest="firmware/raw/$ver/$(basename "$url")"
  if [[ -f "$dest" ]]; then echo "have $dest"; continue; fi
  mkdir -p "firmware/raw/$ver"
  curl -fSL --retry 4 -o "$dest.part" "$url"
  mv "$dest.part" "$dest"
  chmod a-w "$dest"
  echo "got $dest"
done < scripts/firmware_urls.txt

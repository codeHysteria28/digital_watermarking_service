"""Download the benchmark dataset into experiments/dataset/.

- Kodak True Color (24 PNGs from r0k.us)
- USC-SIPI Misc (Lena, Baboon, Peppers, Boat, House) — TIFF, converted to PNG

Idempotent: skips files already present.
"""
from __future__ import annotations

import io
import sys
import urllib.request
import urllib.error

from _common import DATASET

DATASET.mkdir(exist_ok=True)

KODAK_BASE = "https://r0k.us/graphics/kodak/kodak/"
KODAK_FILES = [f"kodim{i:02d}.png" for i in range(1, 25)]

# USC-SIPI Misc — public benchmark set, hosted as TIFF
SIPI = [
    ("https://sipi.usc.edu/database/misc/4.2.04.tiff", "sipi_lena.png"),
    ("https://sipi.usc.edu/database/misc/4.2.03.tiff", "sipi_baboon.png"),
    ("https://sipi.usc.edu/database/misc/4.2.07.tiff", "sipi_peppers.png"),
    ("https://sipi.usc.edu/database/misc/boat.512.tiff", "sipi_boat.png"),
    ("https://sipi.usc.edu/database/misc/house.tiff", "sipi_house.png"),
]

UA = {"User-Agent": "Mozilla/5.0 (thesis dataset downloader)"}


def _fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def download_kodak() -> None:
    print(f"== Kodak ({len(KODAK_FILES)} images) ==")
    for name in KODAK_FILES:
        out = DATASET / name
        if out.exists():
            print(f"  skip  {name} (exists)")
            continue
        try:
            data = _fetch(KODAK_BASE + name)
            out.write_bytes(data)
            print(f"  ok    {name} ({len(data)//1024} KB)")
        except urllib.error.URLError as e:
            print(f"  FAIL  {name}: {e}")


def download_sipi() -> None:
    print(f"== USC-SIPI ({len(SIPI)} images, TIFF -> PNG) ==")
    try:
        from PIL import Image
    except ImportError:
        print("  Pillow not installed — run: pip install pillow")
        return

    for url, out_name in SIPI:
        out = DATASET / out_name
        if out.exists():
            print(f"  skip  {out_name} (exists)")
            continue
        try:
            data = _fetch(url)
            img = Image.open(io.BytesIO(data))
            if img.mode != "RGB":
                img = img.convert("RGB")
            img.save(out, "PNG")
            print(f"  ok    {out_name} ({img.size[0]}x{img.size[1]})")
        except Exception as e:
            print(f"  FAIL  {out_name}: {e}")


def main() -> None:
    download_kodak()
    download_sipi()
    files = sorted(DATASET.glob("*.png"))
    total_mb = sum(p.stat().st_size for p in files) / (1024 * 1024)
    print(f"\nDataset: {len(files)} PNG files, {total_mb:.1f} MB total")
    print(f"Location: {DATASET}")


if __name__ == "__main__":
    sys.exit(main())

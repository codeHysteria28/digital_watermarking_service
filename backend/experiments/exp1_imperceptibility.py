"""Experiment 1 — Imperceptibility (PSNR & SSIM).

For each dataset image, embed a representative payload and measure how
visually different the watermarked image is from the original.
"""
from __future__ import annotations

import csv
import json

import cv2
import numpy as np
from skimage.metrics import peak_signal_noise_ratio, structural_similarity

from _common import RESULTS, PLOTS, list_images, read_bytes
from app.services.watermark_engine import embed_watermark, generate_payload


OUT_CSV = RESULTS / "exp1.csv"
OUT_PLOT = PLOTS / "exp1_psnr_distribution.png"


def _decode(img_bytes: bytes) -> np.ndarray:
    arr = np.frombuffer(img_bytes, dtype=np.uint8)
    return cv2.imdecode(arr, cv2.IMREAD_COLOR)  # BGR


def main() -> None:
    payload = generate_payload(user_id=1, image_id=1)
    rows = []
    print(f"{'image':30s}  {'WxH':>11s}  {'PSNR(dB)':>9s}  {'SSIM':>7s}")
    print("-" * 64)

    for img_path in list_images():
        original_bytes = read_bytes(img_path)
        try:
            watermarked_bytes = embed_watermark(original_bytes, payload)
        except ValueError as exc:
            print(f"{img_path.name:30s}  SKIPPED: {exc}")
            continue

        orig = _decode(original_bytes)
        wm = _decode(watermarked_bytes)
        if orig.shape != wm.shape:
            wm = cv2.resize(wm, (orig.shape[1], orig.shape[0]))

        psnr = peak_signal_noise_ratio(orig, wm, data_range=255)
        ssim = structural_similarity(orig, wm, channel_axis=2, data_range=255)
        h, w = orig.shape[:2]

        rows.append({
            "image": img_path.name,
            "width": w,
            "height": h,
            "psnr_db": round(float(psnr), 3),
            "ssim": round(float(ssim), 5),
            "passed_40db_threshold": bool(psnr >= 40.0),
        })
        print(f"{img_path.name:30s}  {w:>4d}x{h:<4d}  {psnr:>9.2f}  {ssim:>7.4f}")

    if not rows:
        print("No rows produced.")
        return

    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    psnrs = [r["psnr_db"] for r in rows]
    ssims = [r["ssim"] for r in rows]
    print("-" * 64)
    print(f"PSNR  mean={np.mean(psnrs):.2f}  median={np.median(psnrs):.2f}  "
          f"min={np.min(psnrs):.2f}  max={np.max(psnrs):.2f}")
    print(f"SSIM  mean={np.mean(ssims):.4f}  median={np.median(ssims):.4f}  "
          f"min={np.min(ssims):.4f}  max={np.max(ssims):.4f}")
    print(f"Pass rate (PSNR>=40dB): {sum(r['passed_40db_threshold'] for r in rows)}/{len(rows)}")
    print(f"Wrote {OUT_CSV}")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.hist(psnrs, bins=15, edgecolor="black")
        ax.axvline(40, color="red", linestyle="--", label="40 dB threshold")
        ax.set_xlabel("PSNR (dB)")
        ax.set_ylabel("Image count")
        ax.set_title("Imperceptibility: PSNR distribution")
        ax.legend()
        fig.tight_layout()
        fig.savefig(OUT_PLOT, dpi=150)
        print(f"Wrote {OUT_PLOT}")
    except ImportError:
        print("matplotlib not installed — skipping plot")


if __name__ == "__main__":
    main()

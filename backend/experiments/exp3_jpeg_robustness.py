"""Experiment 3 — Robustness to JPEG re-compression.

Embed watermark, re-save as JPEG at varying quality levels, attempt to
extract. Records bit-error rate and binary success.
"""
from __future__ import annotations

import csv

import cv2
import numpy as np

from _common import RESULTS, PLOTS, list_images, read_bytes
from app.services.watermark_engine import (
    embed_watermark,
    extract_watermark,
    generate_payload,
)


OUT_CSV = RESULTS / "exp3.csv"
OUT_PLOT = PLOTS / "exp3_ber_vs_quality.png"

QUALITIES = [95, 90, 80, 70, 50]


def _to_jpeg(png_bytes: bytes, quality: int) -> bytes:
    arr = np.frombuffer(png_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    ok, buf = cv2.imencode(".jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
    assert ok
    return buf.tobytes()


def _bit_error_rate(expected: str, recovered: str) -> float:
    e = expected.encode("utf-8")
    r = recovered.encode("utf-8") if recovered else b""
    n = max(len(e), len(r))
    if n == 0:
        return 0.0
    # Pad shorter one to compare bitwise
    if len(r) < len(e):
        r = r + b"\x00" * (len(e) - len(r))
    elif len(e) < len(r):
        e = e + b"\x00" * (len(r) - len(e))
    diff_bits = sum(bin(a ^ b).count("1") for a, b in zip(e, r))
    return diff_bits / (n * 8)


def main() -> None:
    payload = generate_payload(user_id=1, image_id=1)
    rows = []
    print(f"{'image':30s}  {'JPEG-Q':>7s}  {'extract':>8s}  {'BER':>7s}")
    print("-" * 60)

    for img_path in list_images():
        original = read_bytes(img_path)
        try:
            watermarked = embed_watermark(original, payload)
        except ValueError:
            continue

        # Baseline: lossless re-extract
        try:
            recovered = extract_watermark(watermarked)
            baseline_ok = recovered == payload
        except Exception:
            baseline_ok = False
        rows.append({
            "image": img_path.name, "jpeg_quality": "lossless",
            "extracted": baseline_ok, "ber": 0.0 if baseline_ok else 1.0,
        })
        print(f"{img_path.name:30s}  {'PNG':>7s}  {str(baseline_ok):>8s}  {0.0:>7.3f}")

        for q in QUALITIES:
            jpeg_bytes = _to_jpeg(watermarked, q)
            try:
                recovered = extract_watermark(jpeg_bytes)
                ok = recovered == payload
                ber = _bit_error_rate(payload, recovered)
            except Exception:
                ok = False
                ber = 1.0
            rows.append({
                "image": img_path.name, "jpeg_quality": q,
                "extracted": ok, "ber": round(ber, 4),
            })
            print(f"{img_path.name:30s}  {q:>7d}  {str(ok):>8s}  {ber:>7.3f}")

    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {OUT_CSV}")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(6, 4))
        for q in QUALITIES:
            bers = [r["ber"] for r in rows if r["jpeg_quality"] == q]
            if bers:
                ax.scatter([q] * len(bers), bers, alpha=0.5)
        # Mean line
        mean_bers = []
        for q in QUALITIES:
            bers = [r["ber"] for r in rows if r["jpeg_quality"] == q]
            mean_bers.append(np.mean(bers) if bers else 0)
        ax.plot(QUALITIES, mean_bers, color="red", marker="o", label="mean")
        ax.set_xlabel("JPEG quality")
        ax.set_ylabel("Bit-error rate")
        ax.set_title("Robustness: BER after JPEG re-compression")
        ax.invert_xaxis()
        ax.legend()
        fig.tight_layout()
        fig.savefig(OUT_PLOT, dpi=150)
        print(f"Wrote {OUT_PLOT}")
    except ImportError:
        pass


if __name__ == "__main__":
    main()

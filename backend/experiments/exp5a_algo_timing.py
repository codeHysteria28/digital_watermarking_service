"""Experiment 5a — Algorithm timing (in-process).

For increasing image sizes, time embed_watermark and extract_watermark.
Excludes API/network overhead — pure algorithm.
"""
from __future__ import annotations

import csv
import platform
import time

import cv2
import numpy as np

from _common import RESULTS, PLOTS
from app.services.watermark_engine import (
    embed_watermark,
    extract_watermark,
    generate_payload,
)


OUT_CSV = RESULTS / "exp5a.csv"
OUT_PLOT = PLOTS / "exp5a_timing.png"

SIZES = [(256, 256), (512, 512), (1024, 1024), (2048, 2048)]
RUNS = 10


def _make_image(w: int, h: int) -> bytes:
    rng = np.random.default_rng(0)
    img = rng.integers(0, 256, size=(h, w, 3), dtype=np.uint8)
    ok, buf = cv2.imencode(".png", img)
    assert ok
    return buf.tobytes()


def main() -> None:
    payload = generate_payload(user_id=1, image_id=1)
    print(f"Hardware: {platform.processor() or platform.machine()}, Python {platform.python_version()}")
    print(f"{'size':>11s}  {'embed mean(s)':>14s}  {'embed std':>10s}  "
          f"{'extract mean(s)':>16s}  {'extract std':>12s}")
    print("-" * 80)

    rows = []
    for (w, h) in SIZES:
        img = _make_image(w, h)

        # Warm-up
        wm = embed_watermark(img, payload)
        extract_watermark(wm)

        embed_times = []
        extract_times = []
        for _ in range(RUNS):
            t0 = time.perf_counter()
            wm = embed_watermark(img, payload)
            embed_times.append(time.perf_counter() - t0)

            t0 = time.perf_counter()
            extract_watermark(wm)
            extract_times.append(time.perf_counter() - t0)

        em_mean, em_std = float(np.mean(embed_times)), float(np.std(embed_times))
        ex_mean, ex_std = float(np.mean(extract_times)), float(np.std(extract_times))
        rows.append({
            "width": w, "height": h, "runs": RUNS,
            "embed_mean_s": round(em_mean, 4), "embed_std_s": round(em_std, 4),
            "extract_mean_s": round(ex_mean, 4), "extract_std_s": round(ex_std, 4),
        })
        print(f"{w}x{h:<4d}  {em_mean:>14.4f}  {em_std:>10.4f}  "
              f"{ex_mean:>16.4f}  {ex_std:>12.4f}")

    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w_ = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w_.writeheader()
        w_.writerows(rows)
    print(f"Wrote {OUT_CSV}")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        sizes_label = [f"{r['width']}x{r['height']}" for r in rows]
        x = np.arange(len(sizes_label))
        em = [r["embed_mean_s"] for r in rows]
        ex = [r["extract_mean_s"] for r in rows]
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(x - 0.2, em, width=0.4, label="embed")
        ax.bar(x + 0.2, ex, width=0.4, label="extract")
        ax.set_xticks(x); ax.set_xticklabels(sizes_label)
        ax.set_ylabel("Time (s)")
        ax.set_title(f"Algorithm timing (mean of {RUNS} runs)")
        ax.legend()
        fig.tight_layout()
        fig.savefig(OUT_PLOT, dpi=150)
        print(f"Wrote {OUT_PLOT}")
    except ImportError:
        pass


if __name__ == "__main__":
    main()

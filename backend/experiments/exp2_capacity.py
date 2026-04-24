"""Experiment 2 — Payload capacity vs image size.

For three synthetic image sizes, embed payloads of increasing size and
record success/failure plus PSNR.
"""
from __future__ import annotations

import csv

import cv2
import numpy as np
from skimage.metrics import peak_signal_noise_ratio

from _common import RESULTS, PLOTS
from app.services.watermark_engine import embed_watermark


OUT_CSV = RESULTS / "exp2.csv"
OUT_PLOT = PLOTS / "exp2_capacity.png"

SIZES = [(256, 256), (512, 512), (1024, 1024)]
PAYLOAD_BYTES = [16, 32, 64, 128, 256, 512, 1024, 2048]


def _make_test_image(w: int, h: int, seed: int = 42) -> bytes:
    """Generate a deterministic noisy test image so capacity is the only variable."""
    rng = np.random.default_rng(seed)
    img = rng.integers(0, 256, size=(h, w, 3), dtype=np.uint8)
    ok, buf = cv2.imencode(".png", img)
    assert ok
    return buf.tobytes()


def _decode(b: bytes) -> np.ndarray:
    arr = np.frombuffer(b, dtype=np.uint8)
    return cv2.imdecode(arr, cv2.IMREAD_COLOR)


def main() -> None:
    rows = []
    print(f"{'size':>11s}  {'payload(B)':>10s}  {'status':>10s}  {'PSNR':>8s}")
    print("-" * 50)

    for (w, h) in SIZES:
        original = _make_test_image(w, h)
        for nbytes in PAYLOAD_BYTES:
            payload = "A" * nbytes  # ASCII -> exactly nbytes after utf-8 encode
            try:
                wm_bytes = embed_watermark(original, payload)
                orig_arr = _decode(original)
                wm_arr = _decode(wm_bytes)
                psnr = float(peak_signal_noise_ratio(orig_arr, wm_arr, data_range=255))
                status = "ok"
            except ValueError as exc:
                psnr = float("nan")
                status = "fail"

            rows.append({
                "width": w, "height": h,
                "payload_bytes": nbytes,
                "status": status,
                "psnr_db": round(psnr, 3) if status == "ok" else "",
            })
            print(f"{w}x{h:<4d}  {nbytes:>10d}  {status:>10s}  "
                  f"{psnr:>8.2f}" if status == "ok" else
                  f"{w}x{h:<4d}  {nbytes:>10d}  {status:>10s}  {'-':>8s}")

    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w_ = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w_.writeheader()
        w_.writerows(rows)
    print(f"Wrote {OUT_CSV}")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(6, 4))
        for (w, h) in SIZES:
            xs = [r["payload_bytes"] for r in rows if r["width"] == w and r["status"] == "ok"]
            ys = [r["psnr_db"] for r in rows if r["width"] == w and r["status"] == "ok"]
            ax.plot(xs, ys, marker="o", label=f"{w}x{h}")
        ax.set_xscale("log", base=2)
        ax.set_xlabel("Payload size (bytes)")
        ax.set_ylabel("PSNR (dB)")
        ax.set_title("Capacity: PSNR vs payload size by image dimension")
        ax.axhline(40, color="red", linestyle="--", alpha=0.4, label="40 dB threshold")
        ax.legend()
        fig.tight_layout()
        fig.savefig(OUT_PLOT, dpi=150)
        print(f"Wrote {OUT_PLOT}")
    except ImportError:
        pass


if __name__ == "__main__":
    main()

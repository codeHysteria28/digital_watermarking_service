"""Experiment 5b — End-to-end API latency.

Times the full upload -> watermark -> verify chain against the deployed
FastAPI service. Requires:
  - BASE_URL env var (e.g. https://ca-...-azurecontainerapps.io)
  - AUTH_TOKEN env var (a valid JWT obtained via /api/v1/auth/login)

Uses the smallest dataset image so we measure overhead, not bandwidth.
Optionally deletes uploaded images at the end (DELETE /api/v1/images/{id}).
"""
from __future__ import annotations

import csv
import os
import statistics
import time

import httpx

from _common import RESULTS, list_images, read_bytes


OUT_CSV = RESULTS / "exp5b.csv"

BASE_URL = os.environ.get("BASE_URL", "").rstrip("/")
AUTH_TOKEN = os.environ.get("AUTH_TOKEN", "")
RUNS = 10
CLEANUP = os.environ.get("CLEANUP", "1") != "0"

API = "/api/v1/images"


def _pct(xs, p):
    if not xs:
        return 0.0
    xs = sorted(xs)
    k = int(round((p / 100) * (len(xs) - 1)))
    return xs[k]


def main():
    if not BASE_URL or not AUTH_TOKEN:
        raise SystemExit(
            "Set BASE_URL and AUTH_TOKEN environment variables."
        )

    images = sorted(list_images(), key=lambda p: p.stat().st_size)
    sample = images[0]
    image_bytes = read_bytes(sample)
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}

    upload_times, watermark_times, verify_times = [], [], []
    image_ids = []

    print(f"Target  : {BASE_URL}")
    print(f"Sample  : {sample.name} ({len(image_bytes)} bytes)")
    print(f"Runs    : {RUNS}")
    print(f"Cleanup : {CLEANUP}")
    print()

    with httpx.Client(timeout=120.0) as client:
        for i in range(RUNS):
            # Use a unique filename so re-running the experiment doesn't conflict
            fname = f"exp5b_{int(time.time()*1000)}_{i}.png"
            files = {"file": (fname, image_bytes, "image/png")}
            t0 = time.perf_counter()
            r = client.post(f"{BASE_URL}{API}/upload", headers=headers, files=files)
            dt = time.perf_counter() - t0
            upload_times.append(dt)
            if r.status_code >= 300:
                print(f"upload {i:2d}: HTTP {r.status_code} {r.text[:200]}")
                continue
            data = r.json()
            image_id = data.get("id") or data.get("image_id")
            image_ids.append(image_id)
            print(f"upload    {i:2d}: {dt*1000:8.1f} ms  -> id={image_id}")

        for i, image_id in enumerate(image_ids):
            t0 = time.perf_counter()
            r = client.post(f"{BASE_URL}{API}/{image_id}/watermark", headers=headers)
            dt = time.perf_counter() - t0
            watermark_times.append(dt)
            print(f"watermark {i:2d}: {dt*1000:8.1f} ms  -> HTTP {r.status_code}")

        for i, image_id in enumerate(image_ids):
            t0 = time.perf_counter()
            r = client.post(f"{BASE_URL}{API}/{image_id}/verify", headers=headers)
            dt = time.perf_counter() - t0
            verify_times.append(dt)
            print(f"verify    {i:2d}: {dt*1000:8.1f} ms  -> HTTP {r.status_code}")

        if CLEANUP:
            for image_id in image_ids:
                client.delete(f"{BASE_URL}{API}/{image_id}", headers=headers)
            print(f"cleanup: deleted {len(image_ids)} images")

    rows = []
    for label, ts in [
        ("POST /api/v1/images/upload", upload_times),
        ("POST /api/v1/images/{id}/watermark", watermark_times),
        ("POST /api/v1/images/{id}/verify", verify_times),
    ]:
        if not ts:
            continue
        rows.append({
            "endpoint": label, "n": len(ts),
            "mean_ms": round(statistics.mean(ts) * 1000, 1),
            "median_ms": round(statistics.median(ts) * 1000, 1),
            "p95_ms": round(_pct(ts, 95) * 1000, 1),
            "min_ms": round(min(ts) * 1000, 1),
            "max_ms": round(max(ts) * 1000, 1),
        })

    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print()
    for r in rows:
        print(f"{r['endpoint']:42s} n={r['n']:>2d}  mean={r['mean_ms']:>7.1f} ms  "
              f"median={r['median_ms']:>7.1f} ms  p95={r['p95_ms']:>7.1f} ms")
    print(f"Wrote {OUT_CSV}")


if __name__ == "__main__":
    main()

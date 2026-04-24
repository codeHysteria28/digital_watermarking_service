"""Experiment 4 — Tamper detection accuracy.

For each dataset image, build several tampered variants and measure
true/false positive rates from detect_tampering().

Conditions tested:
  Untampered:
    - control (identical bytes)
  Local tampers (3 sizes: 32, 64, 128 px):
    - paste_block        (object insertion)
    - copy_move          (region duplication)
    - blur_region        (object removal / anonymisation)
    - splice             (region from another image)
  Global tampers:
    - global_brightness  (subtle exposure shift)
    - salt_pepper_noise  (sensor noise / artefacts)
"""
from __future__ import annotations

import csv

from _common import RESULTS, list_images, read_bytes
from app.services.watermark_engine import (
    embed_watermark,
    detect_tampering,
    generate_payload,
)
from tampering_utils import (
    paste_block,
    global_brightness,
    copy_move,
    gaussian_blur_region,
    salt_pepper_noise,
    splice,
)


OUT_CSV = RESULTS / "exp4.csv"
LOCAL_SIZES = [32, 64, 128]


def main() -> None:
    payload = generate_payload(user_id=1, image_id=1)
    images = list_images()
    rows = []

    print(f"{'image':25s}  {'condition':>20s}  {'pred':>5s}  {'sev':>6s}  {'ratio':>7s}")
    print("-" * 75)

    # Pre-compute watermarked versions (also used as donors for splicing)
    wm_cache: dict = {}
    for img_path in images:
        try:
            wm_cache[img_path] = embed_watermark(read_bytes(img_path), payload)
        except ValueError:
            wm_cache[img_path] = None

    for idx, img_path in enumerate(images):
        watermarked = wm_cache[img_path]
        if watermarked is None:
            continue
        seed = hash(img_path.name) & 0xFFFF
        # Donor image for splicing: pick the next image in the list
        donor = wm_cache[images[(idx + 1) % len(images)]]

        # Build (condition, ground_truth_tampered, tampered_bytes)
        variants = [("untampered", False, watermarked)]
        for sz in LOCAL_SIZES:
            variants += [
                (f"paste_block_{sz}",  True, paste_block(watermarked, sz, seed)),
                (f"copy_move_{sz}",    True, copy_move(watermarked, sz, seed)),
                (f"blur_region_{sz}",  True, gaussian_blur_region(watermarked, sz, seed)),
            ]
            if donor is not None:
                variants.append((f"splice_{sz}", True,
                                 splice(watermarked, donor, sz, seed)))
        variants += [
            ("global_brightness", True, global_brightness(watermarked, delta=15)),
            ("salt_pepper_2pct",  True, salt_pepper_noise(watermarked, 0.02, seed)),
        ]

        for cond, gt, tampered_bytes in variants:
            r = detect_tampering(watermarked, tampered_bytes)
            rows.append({
                "image": img_path.name,
                "condition": cond,
                "ground_truth_tampered": gt,
                "predicted_tampered": r["is_tampered"],
                "severity": r["tampering_severity"] or "",
                "tamper_ratio": r["tamper_ratio"],
            })
            print(f"{img_path.name:25s}  {cond:>20s}  {str(r['is_tampered']):>5s}  "
                  f"{str(r['tampering_severity'] or '-'):>6s}  {r['tamper_ratio']:>7.4f}")

    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\nWrote {OUT_CSV}\n")

    # Confusion matrix per condition
    conditions = ["untampered"]
    for sz in LOCAL_SIZES:
        for kind in ("paste_block", "copy_move", "blur_region", "splice"):
            conditions.append(f"{kind}_{sz}")
    conditions += ["global_brightness", "salt_pepper_2pct"]

    print("Per-condition confusion matrix:")
    print(f"{'condition':>22s}  {'n':>3s}  {'TP':>3s}  {'FP':>3s}  {'TN':>3s}  "
          f"{'FN':>3s}  {'TPR':>5s}  {'FPR':>5s}  {'mean_ratio':>10s}")
    for cond in conditions:
        sub = [r for r in rows if r["condition"] == cond]
        if not sub:
            continue
        tp = sum(1 for r in sub if r["ground_truth_tampered"] and r["predicted_tampered"])
        fp = sum(1 for r in sub if not r["ground_truth_tampered"] and r["predicted_tampered"])
        tn = sum(1 for r in sub if not r["ground_truth_tampered"] and not r["predicted_tampered"])
        fn = sum(1 for r in sub if r["ground_truth_tampered"] and not r["predicted_tampered"])
        tpr = tp / (tp + fn) if (tp + fn) else 0
        fpr = fp / (fp + tn) if (fp + tn) else 0
        mean_ratio = sum(r["tamper_ratio"] for r in sub) / len(sub)
        print(f"{cond:>22s}  {len(sub):>3d}  {tp:>3d}  {fp:>3d}  {tn:>3d}  {fn:>3d}  "
              f"{tpr:>5.2f}  {fpr:>5.2f}  {mean_ratio:>10.4f}")

    # Aggregate by tamper kind (across sizes)
    print("\nAggregate by tamper family:")
    print(f"{'family':>22s}  {'n':>3s}  {'TPR':>5s}  {'FPR':>5s}")
    families = {
        "untampered (control)": ["untampered"],
        "paste_block (any size)": [f"paste_block_{s}" for s in LOCAL_SIZES],
        "copy_move (any size)": [f"copy_move_{s}" for s in LOCAL_SIZES],
        "blur_region (any size)": [f"blur_region_{s}" for s in LOCAL_SIZES],
        "splice (any size)": [f"splice_{s}" for s in LOCAL_SIZES],
        "global_brightness": ["global_brightness"],
        "salt_pepper_2pct": ["salt_pepper_2pct"],
    }
    for fam, conds in families.items():
        sub = [r for r in rows if r["condition"] in conds]
        if not sub:
            continue
        tp = sum(1 for r in sub if r["ground_truth_tampered"] and r["predicted_tampered"])
        fp = sum(1 for r in sub if not r["ground_truth_tampered"] and r["predicted_tampered"])
        tn = sum(1 for r in sub if not r["ground_truth_tampered"] and not r["predicted_tampered"])
        fn = sum(1 for r in sub if r["ground_truth_tampered"] and not r["predicted_tampered"])
        tpr = tp / (tp + fn) if (tp + fn) else 0
        fpr = fp / (fp + tn) if (fp + tn) else 0
        print(f"{fam:>22s}  {len(sub):>3d}  {tpr:>5.2f}  {fpr:>5.2f}")


if __name__ == "__main__":
    main()

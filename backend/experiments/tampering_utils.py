"""Synthetic tampering helpers for experiment 4.

All functions take and return PNG-encoded image bytes (so the watermark
detection pipeline can consume them directly). Each function uses a
seed for reproducibility.
"""
from __future__ import annotations

import cv2
import numpy as np


def _decode(img_bytes: bytes) -> np.ndarray:
    arr = np.frombuffer(img_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode image")
    return img


def _encode(img: np.ndarray) -> bytes:
    ok, buf = cv2.imencode(".png", img)
    assert ok
    return buf.tobytes()


def _safe_xy(img: np.ndarray, size: int, rng) -> tuple[int, int]:
    """Pick a top-left (x, y) so a `size`-square fits inside `img`."""
    h, w = img.shape[:2]
    x = int(rng.integers(0, max(1, w - size)))
    y = int(rng.integers(0, max(1, h - size)))
    return x, y


def paste_block(img_bytes: bytes, size: int, seed: int = 0) -> bytes:
    """Object insertion: paint a uniformly coloured rectangle."""
    img = _decode(img_bytes)
    rng = np.random.default_rng(seed)
    x, y = _safe_xy(img, size, rng)
    color = rng.integers(0, 256, size=3, dtype=np.uint8)
    img[y:y + size, x:x + size] = color
    return _encode(img)


def global_brightness(img_bytes: bytes, delta: int = 25) -> bytes:
    """Global edit: shift every pixel by a constant brightness delta."""
    img = _decode(img_bytes)
    img = np.clip(img.astype(np.int16) + delta, 0, 255).astype(np.uint8)
    return _encode(img)


def copy_move(img_bytes: bytes, size: int = 64, seed: int = 0) -> bytes:
    """Copy a square region from the image and paste it elsewhere."""
    img = _decode(img_bytes)
    rng = np.random.default_rng(seed)
    sx, sy = _safe_xy(img, size, rng)
    for _ in range(20):
        dx, dy = _safe_xy(img, size, rng)
        if abs(dx - sx) > size or abs(dy - sy) > size:
            break
    src = img[sy:sy + size, sx:sx + size].copy()
    img[dy:dy + size, dx:dx + size] = src
    return _encode(img)


def gaussian_blur_region(img_bytes: bytes, size: int = 64, seed: int = 0,
                         kernel: int = 15) -> bytes:
    """Blur a square region (object removal / face anonymisation)."""
    img = _decode(img_bytes)
    rng = np.random.default_rng(seed)
    x, y = _safe_xy(img, size, rng)
    region = img[y:y + size, x:x + size]
    img[y:y + size, x:x + size] = cv2.GaussianBlur(region, (kernel, kernel), 0)
    return _encode(img)


def salt_pepper_noise(img_bytes: bytes, amount: float = 0.02,
                      seed: int = 0) -> bytes:
    """Add salt-and-pepper noise across the entire image."""
    img = _decode(img_bytes)
    rng = np.random.default_rng(seed)
    h, w = img.shape[:2]
    n_pix = int(amount * h * w)
    ys = rng.integers(0, h, n_pix); xs = rng.integers(0, w, n_pix)
    img[ys, xs] = 255
    ys = rng.integers(0, h, n_pix); xs = rng.integers(0, w, n_pix)
    img[ys, xs] = 0
    return _encode(img)


def splice(img_bytes: bytes, donor_bytes: bytes, size: int = 64,
           seed: int = 0) -> bytes:
    """Paste a region from a different image (image splicing forgery)."""
    img = _decode(img_bytes)
    donor = _decode(donor_bytes)
    rng = np.random.default_rng(seed)
    dh, dw = donor.shape[:2]
    if dh < size or dw < size:
        scale = max(size / dh, size / dw) * 1.1
        donor = cv2.resize(donor, (int(dw * scale), int(dh * scale)))
    sx, sy = _safe_xy(donor, size, rng)
    region = donor[sy:sy + size, sx:sx + size]
    dx, dy = _safe_xy(img, size, rng)
    img[dy:dy + size, dx:dx + size] = region
    return _encode(img)

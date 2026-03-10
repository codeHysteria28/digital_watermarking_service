import numpy as np
import pywt
import cv2
import json
import hashlib
from datetime import datetime, timezone
from io import BytesIO

ALGORITHM_VERSION = "1.0.0"

# DWT embedding parameters
WAVELET = "haar"
EMBED_STRENGTH = 25  # Controls watermark strength vs image quality


def generate_payload(user_id: int, image_id: int) -> str:
    """Generate a JSON payload string containing watermark metadata."""
    payload = {
        "user_id": user_id,
        "image_id": image_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    return json.dumps(payload, separators=(",", ":"))


def _payload_to_bits(payload: str) -> list[int]:
    """Convert a string payload to a list of bits with a 32-bit length header."""
    payload_bytes = payload.encode("utf-8")
    length = len(payload_bytes)
    # 32-bit length header + payload bits
    length_bits = [(length >> (31 - i)) & 1 for i in range(32)]
    payload_bits = []
    for byte in payload_bytes:
        for i in range(7, -1, -1):
            payload_bits.append((byte >> i) & 1)
    return length_bits + payload_bits


def _bits_to_payload(bits: list[int]) -> str:
    """Convert a list of bits (with 32-bit length header) back to a string."""
    length = 0
    for i in range(32):
        length = (length << 1) | bits[i]
    payload_bits = bits[32 : 32 + length * 8]
    payload_bytes = bytearray()
    for i in range(0, len(payload_bits), 8):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | payload_bits[i + j]
        payload_bytes.append(byte)
    return payload_bytes.decode("utf-8")


def embed_watermark(image_bytes: bytes, payload: str) -> bytes:
    """Embed a watermark payload into an image using DWT.

    Args:
        image_bytes: Raw bytes of the original image.
        payload: String payload to embed.

    Returns:
        Watermarked image as PNG bytes.
    """
    img_array = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode image")

    # Work in YCrCb colour space — embed in luminance channel (Y)
    img_ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb).astype(np.float64)
    y_channel = img_ycrcb[:, :, 0]

    # Apply 2-level DWT
    coeffs = pywt.dwt2(y_channel, WAVELET)
    cA, (cH, cV, cD) = coeffs

    bits = _payload_to_bits(payload)
    total_bits = len(bits)

    if total_bits > cA.size:
        raise ValueError(
            f"Image too small for payload. Need {total_bits} coefficients, "
            f"have {cA.size}"
        )

    # Embed bits into LL subband coefficients using quantisation
    flat_cA = cA.flatten()
    for i in range(total_bits):
        coeff = flat_cA[i]
        quantised = int(coeff / EMBED_STRENGTH)
        if bits[i] == 1:
            # Make quantised value odd
            if quantised % 2 == 0:
                quantised += 1
        else:
            # Make quantised value even
            if quantised % 2 != 0:
                quantised += 1
        flat_cA[i] = quantised * EMBED_STRENGTH

    cA_modified = flat_cA.reshape(cA.shape)

    # Inverse DWT to reconstruct the Y channel
    y_reconstructed = pywt.idwt2((cA_modified, (cH, cV, cD)), WAVELET)

    # Handle size mismatch from DWT rounding
    y_reconstructed = y_reconstructed[: y_channel.shape[0], : y_channel.shape[1]]
    y_reconstructed = np.clip(y_reconstructed, 0, 255)

    img_ycrcb[:, :, 0] = y_reconstructed
    img_watermarked = cv2.cvtColor(img_ycrcb.astype(np.uint8), cv2.COLOR_YCrCb2BGR)

    # Encode as PNG (lossless) to preserve watermark
    _, buffer = cv2.imencode(".png", img_watermarked)
    return buffer.tobytes()


def extract_watermark(image_bytes: bytes, payload_bit_length: int | None = None) -> str:
    """Extract a watermark payload from a watermarked image.

    Args:
        image_bytes: Raw bytes of the watermarked image.
        payload_bit_length: If known, total number of bits to extract.
            If None, reads the 32-bit length header first.

    Returns:
        The extracted payload string.
    """
    img_array = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode image")

    img_ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb).astype(np.float64)
    y_channel = img_ycrcb[:, :, 0]

    coeffs = pywt.dwt2(y_channel, WAVELET)
    cA, _ = coeffs

    flat_cA = cA.flatten()

    # First read the 32-bit length header
    length_bits = []
    for i in range(32):
        quantised = int(flat_cA[i] / EMBED_STRENGTH + 0.5)
        length_bits.append(quantised % 2)

    length = 0
    for bit in length_bits:
        length = (length << 1) | bit

    total_bits = 32 + length * 8

    if total_bits > flat_cA.size:
        raise ValueError("Extracted length exceeds available coefficients — image may not be watermarked")

    # Extract all bits
    extracted_bits = []
    for i in range(total_bits):
        quantised = int(flat_cA[i] / EMBED_STRENGTH + 0.5)
        extracted_bits.append(quantised % 2)

    return _bits_to_payload(extracted_bits)


def detect_tampering(
    original_bytes: bytes, suspect_bytes: bytes, block_size: int = 16
) -> dict:
    """Detect tampering by comparing image blocks.

    Compares the original watermarked image against a suspect image
    using block-level correlation to identify modified regions.

    Args:
        original_bytes: Bytes of the original watermarked image.
        suspect_bytes: Bytes of the suspect image.
        block_size: Size of blocks to compare (pixels).

    Returns:
        Dict with is_tampered, confidence_score, tampered_regions, severity.
    """
    orig_arr = np.frombuffer(original_bytes, dtype=np.uint8)
    orig = cv2.imdecode(orig_arr, cv2.IMREAD_GRAYSCALE)

    susp_arr = np.frombuffer(suspect_bytes, dtype=np.uint8)
    suspect = cv2.imdecode(susp_arr, cv2.IMREAD_GRAYSCALE)

    if orig is None or suspect is None:
        raise ValueError("Could not decode one or both images")

    # Resize suspect to match original if needed
    if orig.shape != suspect.shape:
        suspect = cv2.resize(suspect, (orig.shape[1], orig.shape[0]))

    orig_f = orig.astype(np.float64)
    suspect_f = suspect.astype(np.float64)

    h, w = orig_f.shape
    tampered_regions = []
    total_blocks = 0
    tampered_blocks = 0

    for y in range(0, h - block_size + 1, block_size):
        for x in range(0, w - block_size + 1, block_size):
            total_blocks += 1
            orig_block = orig_f[y : y + block_size, x : x + block_size]
            susp_block = suspect_f[y : y + block_size, x : x + block_size]

            # Normalised cross-correlation
            orig_norm = orig_block - orig_block.mean()
            susp_norm = susp_block - susp_block.mean()

            denom = np.sqrt(
                np.sum(orig_norm**2) * np.sum(susp_norm**2)
            )

            if denom == 0:
                correlation = 1.0  # identical constant blocks
            else:
                correlation = np.sum(orig_norm * susp_norm) / denom

            # Threshold: correlation < 0.95 indicates tampering
            if correlation < 0.95:
                tampered_blocks += 1
                tampered_regions.append(
                    {
                        "x": int(x),
                        "y": int(y),
                        "width": block_size,
                        "height": block_size,
                        "correlation": round(float(correlation), 4),
                    }
                )

    tamper_ratio = tampered_blocks / total_blocks if total_blocks > 0 else 0
    is_tampered = tamper_ratio > 0.01  # More than 1% of blocks tampered

    # Confidence: how sure we are about the result
    if is_tampered:
        confidence = min(1.0, tamper_ratio * 10)  # Scale up low ratios
    else:
        confidence = 1.0 - tamper_ratio  # High confidence if very few blocks differ

    # Severity classification
    if tamper_ratio > 0.3:
        severity = "high"
    elif tamper_ratio > 0.1:
        severity = "medium"
    elif tamper_ratio > 0.01:
        severity = "low"
    else:
        severity = None

    return {
        "is_tampered": is_tampered,
        "confidence_score": round(confidence, 4),
        "tampered_regions": tampered_regions,
        "tampering_severity": severity,
        "tamper_ratio": round(tamper_ratio, 4),
    }


def calculate_psnr(original_bytes: bytes, watermarked_bytes: bytes) -> float:
    """Calculate PSNR between original and watermarked images.

    Returns:
        PSNR value in dB. Higher is better (>40dB is good).
    """
    orig_arr = np.frombuffer(original_bytes, dtype=np.uint8)
    orig = cv2.imdecode(orig_arr, cv2.IMREAD_COLOR)

    wm_arr = np.frombuffer(watermarked_bytes, dtype=np.uint8)
    wm = cv2.imdecode(wm_arr, cv2.IMREAD_COLOR)

    if orig is None or wm is None:
        raise ValueError("Could not decode one or both images")

    if orig.shape != wm.shape:
        wm = cv2.resize(wm, (orig.shape[1], orig.shape[0]))

    mse = np.mean((orig.astype(np.float64) - wm.astype(np.float64)) ** 2)
    if mse == 0:
        return float("inf")

    return round(float(10 * np.log10(255.0**2 / mse)), 2)

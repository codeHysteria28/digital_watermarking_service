import io
import json
import logging
import time

from fastapi import APIRouter, Depends, HTTPException, Request, status, File, UploadFile
from PIL import Image
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from core.security import get_current_user
from models.evidence_image import EvidenceImage
from models.user import User
from models.verification_log import VerificationLog
from schemas.verification_log import VerificationLogRead, VerificationLogSummary
from services.watermark_engine import extract_watermark, detect_tampering, ALGORITHM_VERSION
from services.watermark_service import verify_image, _download_blob

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/verification", tags=["Verification"])

ALLOWED_FORMATS = {"JPEG", "JPG", "PNG", "BMP", "TIFF", "WEBP"}


@router.post("/verify", response_model=VerificationLogRead)
async def verify_uploaded_image(
    request: Request,
    file: UploadFile = File(),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Accept an image file and verify its watermark authenticity.

    Extracts the embedded watermark payload and checks whether the image
    belongs to the authenticated user.
    """
    start_time = time.perf_counter()

    file_bytes = await file.read()

    # Validate image
    try:
        with Image.open(io.BytesIO(file_bytes)) as img:
            img.verify()
            img_format = img.format
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image file",
        )

    if img_format not in ALLOWED_FORMATS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported image format: {img_format}",
        )

    # Extract watermark
    is_authentic = False
    is_tampered = False
    extracted_payload = None
    payload_match = None
    confidence_score = 0.0
    error_message = None
    image_id = None
    tampered_regions = None
    tampering_severity = None

    try:
        extracted_str = extract_watermark(file_bytes)
        extracted_payload = extracted_str
        payload_data = json.loads(extracted_str)

        image_id = payload_data.get("image_id")
        payload_user_id = payload_data.get("user_id")

        # Verify the watermark belongs to the authenticated user
        payload_match = payload_user_id == user.id
        is_authentic = payload_match
        confidence_score = 1.0 if payload_match else 0.3
    except Exception as ex:
        is_authentic = False
        is_tampered = True
        confidence_score = 0.0
        tampering_severity = "high"
        error_message = f"Watermark extraction failed: {str(ex)}"

    processing_time = int((time.perf_counter() - start_time) * 1000)

    # If we found an image_id in the payload, look it up
    db_image_id = image_id
    image = None

    # Verify the referenced image exists and belongs to the user
    if image_id is not None:
        image = (
            db.query(EvidenceImage)
            .filter(EvidenceImage.id == image_id, EvidenceImage.user_id == user.id)
            .first()
        )
        if not image:
            payload_match = False
            is_authentic = False
            confidence_score = 0.3

    # Run block-level tamper detection if we have the original watermarked image
    if image and image.watermarked_path:
        try:
            original_bytes = _download_blob(image.watermarked_path)
            tamper_result = detect_tampering(original_bytes, file_bytes)
            is_tampered = tamper_result["is_tampered"]
            tampering_severity = tamper_result["tampering_severity"]
            tampered_regions = json.dumps(tamper_result["tampered_regions"])
            if tamper_result["is_tampered"]:
                confidence_score = tamper_result["confidence_score"]
        except Exception as ex:
            logger.warning("Tamper detection failed: %s", ex)

    processing_time = int((time.perf_counter() - start_time) * 1000)

    log = VerificationLog(
        image_id=db_image_id,
        is_authentic=is_authentic,
        is_tampered=is_tampered,
        confidence_score=round(confidence_score, 4),
        verification_type="full",
        tampered_regions=tampered_regions,
        tampering_severity=tampering_severity,
        extracted_payload=extracted_payload,
        payload_match=payload_match,
        verified_by_user_id=user.id,
        request_ip=request.client.host if request and request.client else None,
        user_agent=request.headers.get("user-agent") if request else None,
        processing_time_ms=processing_time,
        algorithm_version=ALGORITHM_VERSION,
        error_message=error_message,
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return log


@router.get("/history", response_model=List[VerificationLogSummary])
def get_verification_history(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the authenticated user's verification history, newest first."""
    logs = (
        db.query(VerificationLog)
        .filter(VerificationLog.verified_by_user_id == user.id)
        .order_by(VerificationLog.created_at.desc())
        .all()
    )
    return logs

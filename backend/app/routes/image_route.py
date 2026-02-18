import io
from models.evidence_image import *
from models.user import User
from schemas.evidence_image import *
from core.database import get_db
from core.security import get_current_user
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from PIL import Image
from core.blob_storage_auth import get_or_create_container
import hashlib
from PIL.ExifTags import TAGS
import json

router = APIRouter(prefix="/api/v1/images", tags=["Evidence Images"])

ALLOWED_FORMATS={"JPEG", "JPG", "PNG", "GIF", "WEBP", "BMP", "TIFF", "RAW", "DNG"}
MAX_FILE_SIZE = 50 * 1024 * 1024 # 50 MB

# Upload new image
@router.post("/upload", response_model=EvidenceImageResponse)
async def upload_image(
    file: UploadFile = File(), 
    user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)):

    # Read file bytes once
    file_bytes = await file.read()

    # File size check
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds 50 MB limit"
        )
    
    # Validate image type
    try:
        with Image.open(io.BytesIO(file_bytes)) as img:
            img.verify()
            img_format = img.format
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image file"
        )
    
    if img_format not in ALLOWED_FORMATS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Not allowed image type {img_format}. Allowed: JPEG/JPG, PNG, GIF, WEBP, BMP, TIFF, RAW, DNG",
        )
    
    # Generate SHA-256 hash of original image
    original_hash = hashlib.sha256(file_bytes).hexdigest()

    # Upload to blob storage
    blob_name = f"original/{user.id}/{file.filename}"
    container_client = get_or_create_container()
    blob_client = container_client.get_blob_client(blob_name)
    blob_client.upload_blob(file_bytes, overwrite=False)

    # Re-open to get dimensions (verify() invalidates the image)
    with Image.open(io.BytesIO(file_bytes)) as img:
        width, height = img.size
        exif_raw = img.getexif()

        if exif_raw:
            exif_dict = {TAGS.get(k, k): str(v) for k, v in exif_raw.items()}
            exif_json = json.dumps(exif_dict)
        else:
            exif_json = None

    # Upload to database
    db_image = EvidenceImage(
        user_id=user.id,
        filename=file.filename,
        original_path=blob_name,
        original_hash=original_hash,
        status=ImageStatus.PENDING,
        file_size=len(file_bytes),
        mime_type=file.content_type,
        image_width=width if width else None,
        image_height=height if height else None,
        exif_data=exif_json
    )

    db.add(db_image)
    db.commit()
    db.refresh(db_image)

    return db_image
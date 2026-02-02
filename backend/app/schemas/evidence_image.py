from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class ImageStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    VERIFIED = "verified"
    TAMPERED = "tampered"
    FAILED = "failed"

# Base schema with shared attributes
class EvidenceImageBase(BaseModel):
    filename: str = Field(..., max_length=255, examples=["crime_scene_001.jpg"])
    mime_type: Optional[str] = Field(None, max_length=100, examples=["image/jpeg"])

# Schema for creating a new image (what client sends)
class EvidenceImageCreate(EvidenceImageBase):
    pass

# Schema for updating an image
class EvidenceImageUpdate(BaseModel):
    status: Optional[ImageStatus] = None
    watermarked_path: Optional[str] = None
    watermarked_hash: Optional[str] = None

# Schema for reading/returning image data (what API returns)
class EvidenceImageRead(EvidenceImageBase):
    id: int
    user_id: int
    status: ImageStatus
    original_path: str
    watermarked_path: Optional[str] = None
    original_hash: str
    watermarked_hash: Optional[str] = None
    file_size: Optional[int] = None
    image_width: Optional[int] = None
    image_height: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True # Enables ORM mode

# Minimal schema for list responses
class EvidenceImageResponse(BaseModel):
    id: int
    filename: str
    status: ImageStatus
    created_at: datetime

    class Config:
        from_attributes = True

# Schema with verification info included
class EvidenceImageWithVerification(EvidenceImageRead):
    is_authentic: Optional[bool] = None
    is_tampered: Optional[bool] = None
    last_verified_at: Optional[datetime] = None
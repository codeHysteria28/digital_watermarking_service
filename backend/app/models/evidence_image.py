from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from .base import Base

class ImageStatus(str, Enum):
    PENDING = "pending" # uploaded, awaiting processing
    PROCESSING = "processing" # watermark being embedded
    COMPLETED = "completed" # Successfully watermarked
    VERIFIED = "verified" # Verified as authentic
    TAMPERED = "tampered" # Tampering detected
    FAILED = "failed" # Processing failed

class EvidenceImage(Base):
    __tablename__ = "evidence_images"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign key to User
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # File Information
    filename = Column(String(255), nullable=False) # original file name
    original_path = Column(String(512), nullable=False) # Path to original image
    watermarked_path = Column(String(512), nullable=True) # Path to watermarked image

    # Integrity hashes
    original_hash = Column(String(64), nullable=False) # SHA-256 of original
    watermarked_hash = Column(String(64), nullable=True) # SHA-256 of watermarked

    # Processing status
    status = Column(SQLAlchemyEnum(ImageStatus), default=ImageStatus.PENDING, nullable=False)

    # METADATA
    file_size = Column(Integer, nullable=True) # Size in bytes
    mime_type = Column(String(100), nullable=True) # e.g., image/jpef
    image_width = Column(Integer, nullable=True)
    image_height = Column(Integer, nullable=True)
    exif_data = Column(Text, nullable=True) # JSON string of EXIF medata

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="evidence_images")
    verification_logs = relationship("VerificationLog", back_populates="evidence_image")
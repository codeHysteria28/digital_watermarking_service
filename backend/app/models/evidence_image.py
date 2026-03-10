from datetime import datetime
from enum import Enum
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, ForeignKey, Text, Enum as SQLAlchemyEnum, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .base import Base

if TYPE_CHECKING:
    from .user import User
    from .verification_log import VerificationLog

class ImageStatus(str, Enum):
    PENDING = "pending"        # uploaded, awaiting processing
    PROCESSING = "processing"  # watermark being embedded
    COMPLETED = "completed"    # Successfully watermarked
    VERIFIED = "verified"      # Verified as authentic
    TAMPERED = "tampered"      # Tampering detected
    FAILED = "failed"          # Processing failed

class EvidenceImage(Base):
    __tablename__ = "evidence_images"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Foreign key to User
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    # File Information
    filename: Mapped[str] = mapped_column(String(255))
    original_path: Mapped[str] = mapped_column(String(512))
    watermarked_path: Mapped[Optional[str]] = mapped_column(String(512), default=None)

    # Integrity hashes
    original_hash: Mapped[str] = mapped_column(String(64))
    watermarked_hash: Mapped[Optional[str]] = mapped_column(String(64), default=None)

    # Processing status
    status: Mapped[ImageStatus] = mapped_column(
        SQLAlchemyEnum(ImageStatus), default=ImageStatus.PENDING
    )

    # Metadata
    file_size: Mapped[Optional[int]] = mapped_column(default=None)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100), default=None)
    image_width: Mapped[Optional[int]] = mapped_column(default=None)
    image_height: Mapped[Optional[int]] = mapped_column(default=None)
    exif_data: Mapped[Optional[str]] = mapped_column(Text, default=None)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), default=None
    )
    processed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), default=None
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="evidence_image")
    verification_logs: Mapped[List["VerificationLog"]] = relationship(
        back_populates="evidence_image"
    )
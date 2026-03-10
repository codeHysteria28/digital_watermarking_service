from datetime import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, ForeignKey, Text, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .base import Base

if TYPE_CHECKING:
    from .evidence_image import EvidenceImage
    from .user import User

class VerificationType(str, Enum):
    AUTHENTICITY = "authenticity"  # Verify watermark presence/ownership
    TAMPERING = "tampering"        # Check for image modifications
    FULL = "full"                  # Complete verification (both checks)


class VerificationLog(Base):
    __tablename__ = "verification_logs"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Foreign key to EvidenceImage (nullable for standalone file uploads)
    image_id: Mapped[Optional[int]] = mapped_column(ForeignKey("evidence_images.id"), index=True, default=None)

    # Verification results
    is_authentic: Mapped[bool] = mapped_column()
    is_tampered: Mapped[bool] = mapped_column()
    confidence_score: Mapped[float] = mapped_column(Float)

    # Additional verification details
    verification_type: Mapped[str] = mapped_column(
        String(50), default=VerificationType.FULL
    )

    # Tamper detection details
    tampered_regions: Mapped[Optional[str]] = mapped_column(Text, default=None)
    tampering_severity: Mapped[Optional[str]] = mapped_column(String(20), default=None)

    # Watermark extraction results
    extracted_payload: Mapped[Optional[str]] = mapped_column(Text, default=None)
    payload_match: Mapped[Optional[bool]] = mapped_column(default=None)

    # Request context (for audit trail)
    verified_by_user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"), index=True, default=None
    )
    request_ip: Mapped[Optional[str]] = mapped_column(String(45), default=None)
    user_agent: Mapped[Optional[str]] = mapped_column(String(512), default=None)

    # Processing metrics
    processing_time_ms: Mapped[Optional[int]] = mapped_column(default=None)
    algorithm_version: Mapped[Optional[str]] = mapped_column(String(50), default=None)

    # Error handling
    error_message: Mapped[Optional[str]] = mapped_column(Text, default=None)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    evidence_image: Mapped["EvidenceImage"] = relationship(
        back_populates="verification_logs"
    )
    verified_by: Mapped[Optional["User"]] = relationship(
        foreign_keys=[verified_by_user_id]
    )
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from .base import Base

class VerificationType(str, Enum):
    AUTHENTICITY = "authenticity"      # Verify watermark presence/ownership
    TAMPERING = "tampering"            # Check for image modifications
    FULL = "full"                      # Complete verification (both checks)


class VerificationLog(Base):
    __tablename__ = "verification_logs"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to EvidenceImage
    image_id = Column(Integer, ForeignKey("evidence_images.id"), nullable=False, index=True)
    
    # Verification results (as per issue requirements)
    is_authentic = Column(Boolean, nullable=False)        # Watermark verified successfully
    is_tampered = Column(Boolean, nullable=False)         # Tampering detected
    confidence_score = Column(Float, nullable=False)      # 0.0 to 1.0 confidence level
    
    # Additional verification details
    verification_type = Column(String(50), default=VerificationType.FULL, nullable=False)
    
    # Tamper detection details
    tampered_regions = Column(Text, nullable=True)        # JSON: regions where tampering detected
    tampering_severity = Column(String(20), nullable=True)  # low, medium, high
    
    # Watermark extraction results
    extracted_payload = Column(Text, nullable=True)       # Watermark data extracted during verification
    payload_match = Column(Boolean, nullable=True)        # Does extracted match original?
    
    # Request context (for audit trail)
    verified_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    request_ip = Column(String(45), nullable=True)        # IPv4 or IPv6
    user_agent = Column(String(512), nullable=True)
    
    # Processing metrics
    processing_time_ms = Column(Integer, nullable=True)   # How long verification took
    algorithm_version = Column(String(50), nullable=True) # Track algorithm changes
    
    # Error handling
    error_message = Column(Text, nullable=True)           # If verification failed
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    evidence_image = relationship("EvidenceImage", back_populates="verification_logs")
    verified_by = relationship("User", foreign_keys=[verified_by_user_id])
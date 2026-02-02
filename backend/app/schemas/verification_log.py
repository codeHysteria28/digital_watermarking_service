from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

class VerificationType(str, Enum):
    AUTHENTICITY = "authenticity"
    TAMPERING = "tampering"
    FULL = "full"

class TamperingSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

# Schema for requesting verification
class VerificationRequest(BaseModel):
    image_id: int
    verification_type: VerificationType = VerificationType.FULL

# Schema for API response (what client sees)
class VerificationLogRead(BaseModel):
    id: int
    image_id: int
    is_authentic: bool
    is_tampered: bool
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    verification_type: str
    tampering_severity: Optional[TamperingSeverity] = None
    tampered_regions: Optional[str] = None  # JSON string of regions
    payload_match: Optional[bool] = None
    processing_time_ms: Optional[int] = None
    algorithm_version: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Minimal schema for list/history views
class VerificationLogSummary(BaseModel):
    id: int
    image_id: int
    is_authentic: bool
    is_tampered: bool
    confidence_score: float
    created_at: datetime

    class Config:
        from_attributes = True

# Schema for verification result (used in service layer)
class VerificationResult(BaseModel):
    is_authentic: bool
    is_tampered: bool
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    tampered_regions: Optional[List[dict]] = None
    extracted_payload: Optional[str] = None
    payload_match: Optional[bool] = None
    processing_time_ms: int
    algorithm_version: str
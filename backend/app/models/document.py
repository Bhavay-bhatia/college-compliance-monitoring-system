import uuid
from datetime import datetime
from typing import Optional, Any, Dict
from sqlalchemy import String, DateTime, ForeignKey, Float, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, utc_now

class DocumentType:
    FIRE_NOC = "FIRE_NOC"
    LAND_DEED = "LAND_DEED"
    BUILDING_STABILITY = "BUILDING_STABILITY"
    FACULTY_ROSTER = "FACULTY_ROSTER"
    WATER_POTABILITY = "WATER_POTABILITY"
    COMMITTEE_MINUTES = "COMMITTEE_MINUTES"

class DocumentVerification(Base):
    __tablename__ = "document_verifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    application_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("applications.id"), nullable=True)
    institution_id: Mapped[str] = mapped_column(String(36), ForeignKey("institutions.id"), nullable=False)
    doc_type: Mapped[str] = mapped_column(String(64), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    ocr_status: Mapped[str] = mapped_column(String(32), default="COMPLETED")  # PENDING, PROCESSING, COMPLETED, FAILED
    extracted_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extracted_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    verification_status: Mapped[str] = mapped_column(String(32), default="VERIFIED")  # VERIFIED, FLAGGED, SUSPICIOUS, REJECTED
    confidence_score: Mapped[float] = mapped_column(Float, default=0.95)
    flag_reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    institution: Mapped["Institution"] = relationship("Institution")
    application: Mapped[Optional["Application"]] = relationship("Application")

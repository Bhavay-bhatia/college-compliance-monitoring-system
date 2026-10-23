import uuid
from datetime import datetime
from typing import Optional, Any
from sqlalchemy import String, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, utc_now

class Application(Base):
    __tablename__ = "applications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    institution_id: Mapped[str] = mapped_column(String(36), ForeignKey("institutions.id"), nullable=False)
    application_type: Mapped[str] = mapped_column(String(64), default="EXTENSION_OF_APPROVAL")  # EOA, NEW, EXPANSION
    programme: Mapped[str] = mapped_column(String(64), default="ENGINEERING_AND_TECHNOLOGY")
    academic_year: Mapped[str] = mapped_column(String(16), default="2026-2027")
    declared_student_intake: Mapped[int] = mapped_column(Integer, default=240)
    status: Mapped[str] = mapped_column(String(32), default="DRAFT")
    assigned_officer_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    payload_snapshot: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    version_number: Mapped[int] = mapped_column(Integer, default=1)

    institution: Mapped["Institution"] = relationship("Institution", back_populates="applications")
    compliance_runs: Mapped[list["ComplianceRun"]] = relationship("ComplianceRun", back_populates="application")

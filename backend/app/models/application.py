import uuid
from datetime import datetime
from typing import Optional, Any, List
from sqlalchemy import String, DateTime, ForeignKey, Integer, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, utc_now

class ApplicationStatus:
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    DEFICIENCY_ISSUED = "DEFICIENCY_ISSUED"
    RECTIFIED = "RECTIFIED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class Application(Base):
    __tablename__ = "applications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    institution_id: Mapped[str] = mapped_column(String(36), ForeignKey("institutions.id"), nullable=False)
    application_type: Mapped[str] = mapped_column(String(64), default="EXTENSION_OF_APPROVAL")
    programme: Mapped[str] = mapped_column(String(64), default="ENGINEERING_AND_TECHNOLOGY")
    academic_year: Mapped[str] = mapped_column(String(16), default="2026-2027")
    declared_student_intake: Mapped[int] = mapped_column(Integer, default=240)
    status: Mapped[str] = mapped_column(String(32), default=ApplicationStatus.DRAFT)
    assigned_officer_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    version_number: Mapped[int] = mapped_column(Integer, default=1)
    payload_snapshot: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    compliance_status: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    officer_remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    institution: Mapped["Institution"] = relationship("Institution", back_populates="applications")
    assigned_officer: Mapped[Optional["User"]] = relationship("User", foreign_keys=[assigned_officer_id])
    compliance_runs: Mapped[List["ComplianceRun"]] = relationship("ComplianceRun", back_populates="application", cascade="all, delete-orphan")
    revisions: Mapped[List["ApplicationRevision"]] = relationship("ApplicationRevision", back_populates="application", cascade="all, delete-orphan", order_by="ApplicationRevision.revision_number.asc()")

    @property
    def current_version(self) -> int:
        return self.version_number

    @current_version.setter
    def current_version(self, value: int):
        self.version_number = value


class ApplicationRevision(Base):
    __tablename__ = "application_revisions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    application_id: Mapped[str] = mapped_column(String(36), ForeignKey("applications.id"), nullable=False)
    revision_number: Mapped[int] = mapped_column(Integer, nullable=False)
    author_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    change_summary: Mapped[str] = mapped_column(String(500), default="Application updated")
    snapshot_data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    changed_fields: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    compliance_summary: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    application: Mapped["Application"] = relationship("Application", back_populates="revisions")
    author: Mapped[Optional["User"]] = relationship("User", back_populates="revisions_authored")

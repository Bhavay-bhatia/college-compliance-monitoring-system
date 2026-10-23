import uuid
from datetime import datetime
from typing import Optional, Any
from sqlalchemy import String, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, utc_now

class ComplianceRun(Base):
    __tablename__ = "compliance_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    application_id: Mapped[str] = mapped_column(String(36), ForeignKey("applications.id"), nullable=False)
    evaluated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    evaluation_period: Mapped[str] = mapped_column(String(32), default="2026-2027")
    input_snapshot: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    overall_status: Mapped[str] = mapped_column(String(32), default="COMPLIANT")  # COMPLIANT, DEFICIENT, NEEDS_REVIEW
    created_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    application: Mapped["Application"] = relationship("Application", back_populates="compliance_runs")
    results: Mapped[list["ComplianceResult"]] = relationship("ComplianceResult", back_populates="compliance_run", cascade="all, delete-orphan")


class ComplianceResult(Base):
    __tablename__ = "compliance_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    compliance_run_id: Mapped[str] = mapped_column(String(36), ForeignKey("compliance_runs.id"), nullable=False)
    rule_version_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("rule_versions.id"), nullable=True)
    rule_key: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)  # COMPLIANT, DEFICIENT, NEEDS_REVIEW, NOT_APPLICABLE
    severity: Mapped[str] = mapped_column(String(32), default="CRITICAL")
    required_value: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    actual_value: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    shortfall: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    explanation: Mapped[str] = mapped_column(String(2000), default="")
    evidence_refs: Mapped[list[str]] = mapped_column(JSON, default=list)

    compliance_run: Mapped["ComplianceRun"] = relationship("ComplianceRun", back_populates="results")
    deficiencies: Mapped[list["Deficiency"]] = relationship("Deficiency", back_populates="compliance_result")


class Deficiency(Base):
    __tablename__ = "deficiencies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    application_id: Mapped[str] = mapped_column(String(36), ForeignKey("applications.id"), nullable=False)
    compliance_result_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("compliance_results.id"), nullable=True)
    field_key: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    severity: Mapped[str] = mapped_column(String(32), default="CRITICAL")
    status: Mapped[str] = mapped_column(String(32), default="OPEN")  # OPEN, SUBMITTED_FOR_REVIEW, RESOLVED, ACCEPTED_WITH_REASON
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    compliance_result: Mapped[Optional["ComplianceResult"]] = relationship("ComplianceResult", back_populates="deficiencies")

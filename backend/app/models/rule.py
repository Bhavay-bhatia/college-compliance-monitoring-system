import uuid
from datetime import datetime
from typing import Optional, Any
from sqlalchemy import String, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, utc_now

class Rule(Base):
    __tablename__ = "rules"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    rule_key: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=True)
    scope: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    severity: Mapped[str] = mapped_column(String(32), default="CRITICAL")  # CRITICAL, HIGH, MEDIUM, LOW
    source_reference: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    versions: Mapped[list["RuleVersion"]] = relationship("RuleVersion", back_populates="rule", cascade="all, delete-orphan")


class RuleVersion(Base):
    __tablename__ = "rule_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    rule_id: Mapped[str] = mapped_column(String(36), ForeignKey("rules.id"), nullable=False)
    version_number: Mapped[str] = mapped_column(String(32), nullable=False)  # e.g. "2026.1"
    parameters: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    effective_to: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="APPROVED")  # DRAFT, APPROVED, RETIRED
    created_by: Mapped[str] = mapped_column(String(64), default="SYSTEM_INIT")
    approved_by: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    rule: Mapped["Rule"] = relationship("Rule", back_populates="versions")

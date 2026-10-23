import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, utc_now

class FacultyMember(Base):
    __tablename__ = "faculty_members"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    institution_id: Mapped[str] = mapped_column(String(36), ForeignKey("institutions.id"), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    designation: Mapped[str] = mapped_column(String(64), default="ASSISTANT_PROFESSOR")  # PROFESSOR, ASSOCIATE_PROFESSOR, ASSISTANT_PROFESSOR, PRINCIPAL
    department: Mapped[str] = mapped_column(String(128), default="Computer Science & Engineering")
    highest_qualification: Mapped[str] = mapped_column(String(64), default="Ph.D.")
    phd_awarded: Mapped[bool] = mapped_column(Boolean, default=True)
    pan_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    aadhaar_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    monthly_salary: Mapped[float] = mapped_column(Float, default=110000.0)
    bank_account_verified: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    joined_date: Mapped[str] = mapped_column(String(32), default="2022-08-01")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    institution: Mapped["Institution"] = relationship("Institution")

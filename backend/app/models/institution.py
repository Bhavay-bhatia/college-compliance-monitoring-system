import uuid
from datetime import datetime
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, utc_now

class Institution(Base):
    __tablename__ = "institutions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    institution_code: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    region: Mapped[str] = mapped_column(String(64), default="NORTH")
    address: Mapped[str] = mapped_column(String(500), nullable=True)
    institution_type: Mapped[str] = mapped_column(String(64), default="TECHNICAL")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    applications: Mapped[list["Application"]] = relationship("Application", back_populates="institution")

from sqlalchemy import String, Numeric, text, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.core.database import Base

class Equipment(Base):
    __tablename__ = "equipments"

    equipment_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(30), server_default="Available", nullable=False)
    total_used_hours: Mapped[float] = mapped_column(Numeric(10, 2), server_default=text("0"), nullable=False)
    maintenance_interval_hours: Mapped[float] = mapped_column(Numeric(10, 2), server_default=text("300"), nullable=False)
    last_maintenance_date: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"), nullable=False)

    bookings = relationship("Booking", back_populates="equipment", cascade="all, delete-orphan")
    maintenance_logs = relationship("MaintenanceLog", back_populates="equipment", cascade="all, delete-orphan")

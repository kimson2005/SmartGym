from sqlalchemy import ForeignKey, String, Text, Numeric, text, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.core.database import Base

class MaintenanceLog(Base):
    __tablename__ = "maintenance_logs"

    log_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipments.equipment_id", ondelete="CASCADE"), nullable=False)
    maintenance_date: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    type: Mapped[str] = mapped_column(String(30), server_default="Routine", nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    cost: Mapped[float] = mapped_column(Numeric(12, 2), server_default=text("0"), nullable=False)

    equipment = relationship("Equipment", back_populates="maintenance_logs")

from sqlalchemy import ForeignKey, String, Boolean, text, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from app.core.database import Base

class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    plan_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(150), server_default="Lịch tập tùy chỉnh", nullable=False)
    generated_by_ai: Mapped[bool] = mapped_column(Boolean, server_default=text("true"), nullable=False)
    plan_details: Mapped[dict] = mapped_column(JSONB, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("true"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"), nullable=False)

    user = relationship("User", back_populates="workout_plans")

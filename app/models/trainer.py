"""
============================================================================
TRAINER MODELS — SQLAlchemy 2.0 ORM cho tính năng Huấn luyện viên
============================================================================

Chứa 3 model tương ứng với 3 bảng mới trong PostgreSQL:
  1. Trainer         → trainers          (Hồ sơ HLV)
  2. TrainerBooking  → trainer_bookings  (Đặt lịch tập với HLV)
  3. TrainerReview   → trainer_reviews   (Đánh giá HLV)

Tất cả đều liên kết ngược về bảng `users` thông qua Foreign Key.
============================================================================
"""

from sqlalchemy import ForeignKey, String, Integer, Numeric, Text, Boolean, text, TIMESTAMP, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.core.database import Base


class Trainer(Base):
    """
    Hồ sơ Huấn luyện viên.
    Mỗi Trainer là một User có role='trainer' trong bảng users.
    Ràng buộc UNIQUE trên user_id: 1 user chỉ có 1 hồ sơ trainer.
    """
    __tablename__ = "trainers"

    trainer_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        unique=True, nullable=False
    )
    specialty: Mapped[str] = mapped_column(String(150), nullable=False)
    experience_years: Mapped[int] = mapped_column(Integer, server_default=text("0"), nullable=False)
    hourly_rate: Mapped[float] = mapped_column(Numeric(10, 2), server_default=text("0"), nullable=False)
    bio: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )

    # ── Relationships ──
    user = relationship("User", back_populates="trainer_profile")
    bookings = relationship("TrainerBooking", back_populates="trainer", cascade="all, delete-orphan")
    reviews = relationship("TrainerReview", back_populates="trainer", cascade="all, delete-orphan")


class TrainerBooking(Base):
    """
    Đặt lịch tập với Huấn luyện viên.
    Tách biệt hoàn toàn với bảng `bookings` (đặt thiết bị).
    member_id = hội viên đặt lịch, trainer_id = HLV được đặt.
    """
    __tablename__ = "trainer_bookings"

    booking_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    member_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    trainer_id: Mapped[int] = mapped_column(
        ForeignKey("trainers.trainer_id", ondelete="CASCADE"), nullable=False
    )
    start_time: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(30), server_default="Pending", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )

    # ── Relationships ──
    member = relationship("User", back_populates="trainer_bookings")
    trainer = relationship("Trainer", back_populates="bookings")


class TrainerReview(Base):
    """
    Đánh giá Huấn luyện viên bởi hội viên.
    Ràng buộc UNIQUE (trainer_id, member_id): mỗi member chỉ review 1 trainer 1 lần.
    Ràng buộc CHECK: rating phải từ 1 đến 5.
    """
    __tablename__ = "trainer_reviews"

    review_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    trainer_id: Mapped[int] = mapped_column(
        ForeignKey("trainers.trainer_id", ondelete="CASCADE"), nullable=False
    )
    member_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("trainer_id", "member_id", name="uq_trainer_reviews_unique_review"),
        CheckConstraint("rating >= 1 AND rating <= 5", name="chk_trainer_reviews_rating"),
    )

    # ── Relationships ──
    trainer = relationship("Trainer", back_populates="reviews")
    member = relationship("User", back_populates="trainer_reviews")

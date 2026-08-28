"""
============================================================================
TRAINER SCHEMAS — Pydantic v2 cho tính năng Huấn luyện viên
============================================================================

Schemas cho 3 nhóm:
  1. Trainer          — Hồ sơ HLV (CRUD)
  2. TrainerBooking   — Đặt lịch với HLV
  3. TrainerReview    — Đánh giá HLV

Mỗi nhóm có: Base, Create, Update, Response.
============================================================================
"""

from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Optional
from datetime import datetime, timedelta


# ═══════════════════════════════════════════════════════════════════════════
# TRAINER — Hồ sơ Huấn luyện viên
# ═══════════════════════════════════════════════════════════════════════════

class TrainerBase(BaseModel):
    """Thông tin cơ bản của HLV."""
    specialty: str = Field(..., max_length=150, description="Chuyên môn: Yoga, Gym, Cardio, ...")
    experience_years: int = Field(default=0, ge=0, description="Số năm kinh nghiệm")
    hourly_rate: float = Field(default=0.0, ge=0, description="Phí thuê theo giờ (VND)")
    bio: Optional[str] = Field(default=None, description="Giới thiệu về HLV")


class TrainerCreate(TrainerBase):
    """Schema tạo hồ sơ HLV mới — cần user_id."""
    user_id: int = Field(..., description="ID của user có role='trainer'")


class TrainerUpdate(BaseModel):
    """Schema cập nhật hồ sơ HLV — tất cả trường đều optional."""
    specialty: Optional[str] = Field(default=None, max_length=150)
    experience_years: Optional[int] = Field(default=None, ge=0)
    hourly_rate: Optional[float] = Field(default=None, ge=0)
    bio: Optional[str] = None


class TrainerResponse(TrainerBase):
    """Schema phản hồi hồ sơ HLV với đầy đủ thông tin."""
    trainer_id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ═══════════════════════════════════════════════════════════════════════════
# TRAINER BOOKING — Đặt lịch tập với Huấn luyện viên
# ═══════════════════════════════════════════════════════════════════════════

class TrainerBookingBase(BaseModel):
    """Thông tin cơ bản của lịch đặt HLV."""
    trainer_id: int = Field(..., description="ID hồ sơ trainer (bảng trainers)")
    start_time: datetime
    end_time: datetime

    @model_validator(mode="after")
    def validate_booking_time(self) -> "TrainerBookingBase":
        """Đảm bảo end_time > start_time ít nhất 30 phút (buổi tập tối thiểu)."""
        min_duration = timedelta(minutes=30)
        if self.end_time <= self.start_time:
            raise ValueError("Thời gian kết thúc phải sau thời gian bắt đầu")
        if (self.end_time - self.start_time) < min_duration:
            raise ValueError("Buổi tập với HLV phải tối thiểu 30 phút")
        return self


class TrainerBookingCreate(TrainerBookingBase):
    """Schema tạo booking HLV mới — cần member_id."""
    member_id: int = Field(..., description="ID của hội viên đặt lịch")


class TrainerBookingUpdate(BaseModel):
    """Schema cập nhật booking HLV."""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[str] = None


class TrainerBookingResponse(TrainerBookingBase):
    """Schema phản hồi booking HLV."""
    booking_id: int
    member_id: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ═══════════════════════════════════════════════════════════════════════════
# TRAINER REVIEW — Đánh giá Huấn luyện viên
# ═══════════════════════════════════════════════════════════════════════════

class TrainerReviewBase(BaseModel):
    """Thông tin cơ bản của đánh giá HLV."""
    trainer_id: int
    rating: int = Field(..., ge=1, le=5, description="Điểm đánh giá từ 1 đến 5 sao")
    comment: Optional[str] = None


class TrainerReviewCreate(TrainerReviewBase):
    """Schema tạo đánh giá mới — cần member_id."""
    member_id: int = Field(..., description="ID của hội viên đánh giá")


class TrainerReviewResponse(TrainerReviewBase):
    """Schema phản hồi đánh giá HLV."""
    review_id: int
    member_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

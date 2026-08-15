from pydantic import BaseModel, ConfigDict, model_validator
from typing import Optional
from datetime import datetime, timedelta


class BookingBase(BaseModel):
    """Schema cơ sở cho đặt lịch thiết bị."""
    equipment_id: int
    start_time: datetime
    end_time: datetime

    @model_validator(mode="after")
    def validate_booking_time(self) -> "BookingBase":
        """Đảm bảo end_time > start_time ít nhất 15 phút."""
        min_duration = timedelta(minutes=15)
        if self.end_time <= self.start_time:
            raise ValueError("Thời gian kết thúc phải sau thời gian bắt đầu")
        if (self.end_time - self.start_time) < min_duration:
            raise ValueError("Thời lượng đặt lịch phải tối thiểu 15 phút")
        return self


class BookingCreate(BookingBase):
    """Schema tạo booking mới - cần thêm user_id."""
    user_id: int


class BookingUpdate(BaseModel):
    """Schema cập nhật booking."""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[str] = None


class BookingResponse(BookingBase):
    """Schema phản hồi booking với đầy đủ thông tin."""
    booking_id: int
    user_id: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

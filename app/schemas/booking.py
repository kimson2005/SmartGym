from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class BookingBase(BaseModel):
    user_id: int
    equipment_id: int
    start_time: datetime
    end_time: datetime
    status: str = "Confirmed"

class BookingCreate(BookingBase):
    pass

class BookingUpdate(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[str] = None

class BookingResponse(BookingBase):
    booking_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

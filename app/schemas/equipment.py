from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class EquipmentBase(BaseModel):
    """Schema cơ sở cho thiết bị phòng Gym."""
    name: str
    category: str
    status: str = "Available"


class EquipmentCreate(EquipmentBase):
    """Schema để tạo thiết bị mới. Các trường mặc định do DB xử lý."""
    pass


class EquipmentUpdate(BaseModel):
    """Schema cập nhật thiết bị - tất cả trường đều optional."""
    name: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    total_used_hours: Optional[float] = None
    maintenance_interval_hours: Optional[float] = None
    last_maintenance_date: Optional[datetime] = None


class EquipmentResponse(EquipmentBase):
    """Schema phản hồi thiết bị với đầy đủ thông tin từ DB."""
    equipment_id: int
    total_used_hours: float
    maintenance_interval_hours: float
    last_maintenance_date: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

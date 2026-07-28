from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class EquipmentBase(BaseModel):
    name: str
    category: str
    status: str = "Available"
    total_used_hours: float = 0.0
    maintenance_interval_hours: float = 300.0

class EquipmentCreate(EquipmentBase):
    pass

class EquipmentUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    total_used_hours: Optional[float] = None
    maintenance_interval_hours: Optional[float] = None
    last_maintenance_date: Optional[datetime] = None

class EquipmentResponse(EquipmentBase):
    equipment_id: int
    last_maintenance_date: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

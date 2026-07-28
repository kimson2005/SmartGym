from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class MaintenanceLogBase(BaseModel):
    equipment_id: int
    type: str = "Routine"
    description: str
    cost: float = 0.0

class MaintenanceLogCreate(MaintenanceLogBase):
    pass

class MaintenanceLogUpdate(BaseModel):
    type: Optional[str] = None
    description: Optional[str] = None
    cost: Optional[float] = None

class MaintenanceLogResponse(MaintenanceLogBase):
    log_id: int
    maintenance_date: datetime

    model_config = ConfigDict(from_attributes=True)

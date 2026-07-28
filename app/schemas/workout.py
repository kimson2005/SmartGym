from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime

class WorkoutPlanBase(BaseModel):
    user_id: int
    title: str = "Lịch tập tùy chỉnh"
    generated_by_ai: bool = True
    plan_details: Dict[str, Any]
    is_active: bool = True

class WorkoutPlanCreate(WorkoutPlanBase):
    pass

class WorkoutPlanUpdate(BaseModel):
    title: Optional[str] = None
    generated_by_ai: Optional[bool] = None
    plan_details: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class WorkoutPlanResponse(WorkoutPlanBase):
    plan_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.equipment import EquipmentCreate, EquipmentResponse
from app.crud.crud_equipment import get_equipment, get_equipments, create_equipment

router = APIRouter(prefix="/equipments", tags=["equipments"])

@router.post("/", response_model=EquipmentResponse, status_code=status.HTTP_201_CREATED)
def create_equipment_endpoint(equipment: EquipmentCreate, db: Session = Depends(get_db)):
    return create_equipment(db=db, equipment=equipment)

@router.get("/", response_model=List[EquipmentResponse])
def read_equipments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    equipments = get_equipments(db, skip=skip, limit=limit)
    return equipments

@router.get("/{equipment_id}", response_model=EquipmentResponse)
def read_equipment(equipment_id: int, db: Session = Depends(get_db)):
    db_equipment = get_equipment(db, equipment_id=equipment_id)
    if db_equipment is None:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return db_equipment

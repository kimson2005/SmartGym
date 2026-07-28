from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.equipment import Equipment
from app.schemas.equipment import EquipmentCreate

def get_equipment(db: Session, equipment_id: int):
    return db.execute(select(Equipment).filter(Equipment.equipment_id == equipment_id)).scalars().first()

def get_equipments(db: Session, skip: int = 0, limit: int = 100):
    return db.execute(select(Equipment).offset(skip).limit(limit)).scalars().all()

def create_equipment(db: Session, equipment: EquipmentCreate):
    db_equipment = Equipment(**equipment.model_dump())
    db.add(db_equipment)
    db.commit()
    db.refresh(db_equipment)
    return db_equipment

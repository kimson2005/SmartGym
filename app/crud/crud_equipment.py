from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.equipment import Equipment
from app.schemas.equipment import EquipmentCreate, EquipmentUpdate

# --- Danh sách trạng thái hợp lệ ---
VALID_STATUSES = {"Available", "In_Use", "Maintenance"}


def get_equipment(db: Session, equipment_id: int) -> Equipment | None:
    """Lấy thông tin một thiết bị theo ID."""
    return db.execute(
        select(Equipment).filter(Equipment.equipment_id == equipment_id)
    ).scalar_one_or_none()


def get_equipments(db: Session, skip: int = 0, limit: int = 100) -> list[Equipment]:
    """Lấy danh sách thiết bị có phân trang."""
    result = db.execute(
        select(Equipment).offset(skip).limit(limit)
    )
    return list(result.scalars().all())


def create_equipment(db: Session, equipment: EquipmentCreate) -> Equipment:
    """Tạo thiết bị mới."""
    if equipment.status not in VALID_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Trạng thái không hợp lệ. Chỉ chấp nhận: {', '.join(VALID_STATUSES)}"
        )
    db_equipment = Equipment(**equipment.model_dump(exclude_unset=True))
    db.add(db_equipment)
    db.commit()
    db.refresh(db_equipment)
    return db_equipment


def update_equipment(db: Session, equipment_id: int, equipment_update: EquipmentUpdate) -> Equipment:
    """Cập nhật thông tin thiết bị (chỉ cập nhật các trường được gửi lên)."""
    db_equipment = get_equipment(db, equipment_id)
    if db_equipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy thiết bị"
        )

    update_data = equipment_update.model_dump(exclude_unset=True)

    # Kiểm tra trạng thái hợp lệ nếu có cập nhật status
    if "status" in update_data and update_data["status"] not in VALID_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Trạng thái không hợp lệ. Chỉ chấp nhận: {', '.join(VALID_STATUSES)}"
        )

    for field, value in update_data.items():
        setattr(db_equipment, field, value)

    db.commit()
    db.refresh(db_equipment)
    return db_equipment


def delete_equipment(db: Session, equipment_id: int) -> Equipment:
    """Xóa thiết bị theo ID. Trả về thiết bị đã xóa."""
    db_equipment = get_equipment(db, equipment_id)
    if db_equipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy thiết bị"
        )
    db.delete(db_equipment)
    db.commit()
    return db_equipment


def update_equipment_status(db: Session, equipment_id: int, new_status: str) -> Equipment:
    """Cập nhật trạng thái thiết bị sang 'Available', 'In_Use', hoặc 'Maintenance'."""
    if new_status not in VALID_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Trạng thái không hợp lệ. Chỉ chấp nhận: {', '.join(VALID_STATUSES)}"
        )

    db_equipment = get_equipment(db, equipment_id)
    if db_equipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy thiết bị"
        )

    db_equipment.status = new_status
    db.commit()
    db.refresh(db_equipment)
    return db_equipment

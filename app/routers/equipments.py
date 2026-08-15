from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.equipment import EquipmentCreate, EquipmentUpdate, EquipmentResponse
from app.crud.crud_equipment import (
    get_equipment, get_equipments, create_equipment,
    update_equipment, delete_equipment
)

router = APIRouter(prefix="/equipments", tags=["equipments"])


@router.post("/", response_model=EquipmentResponse, status_code=status.HTTP_201_CREATED)
def create_equipment_endpoint(equipment: EquipmentCreate, db: Session = Depends(get_db)):
    """Tạo thiết bị mới cho phòng Gym."""
    return create_equipment(db=db, equipment=equipment)


@router.get("/", response_model=List[EquipmentResponse])
def read_equipments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lấy danh sách tất cả thiết bị (có phân trang)."""
    return get_equipments(db, skip=skip, limit=limit)


@router.get("/{equipment_id}", response_model=EquipmentResponse)
def read_equipment(equipment_id: int, db: Session = Depends(get_db)):
    """Lấy chi tiết một thiết bị theo ID."""
    db_equipment = get_equipment(db, equipment_id=equipment_id)
    if db_equipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy thiết bị"
        )
    return db_equipment


@router.patch("/{equipment_id}", response_model=EquipmentResponse)
def update_equipment_endpoint(
    equipment_id: int,
    equipment_update: EquipmentUpdate,
    db: Session = Depends(get_db),
):
    """Cập nhật thông tin hoặc trạng thái thiết bị (partial update)."""
    return update_equipment(db=db, equipment_id=equipment_id, equipment_update=equipment_update)


@router.delete("/{equipment_id}", response_model=EquipmentResponse)
def delete_equipment_endpoint(equipment_id: int, db: Session = Depends(get_db)):
    """Xóa thiết bị khỏi hệ thống."""
    return delete_equipment(db=db, equipment_id=equipment_id)


@router.post("/analyze-maintenance/all")
def analyze_all_equipments_endpoint(db: Session = Depends(get_db)):
    """
    [Smart Feature] Quét toàn bộ thiết bị trong hệ thống và chạy AI dự báo bảo trì.
    Dành cho Admin hoặc CronJob gọi định kỳ.
    """
    from app.services.maintenance_ai import analyze_all_equipments
    return analyze_all_equipments(db)


@router.post("/{equipment_id}/analyze-maintenance")
def analyze_equipment_maintenance_endpoint(equipment_id: int, db: Session = Depends(get_db)):
    """
    [Smart Feature] Phân tích dữ liệu sử dụng của một thiết bị và tự động cảnh báo bảo trì.

    Logic Rule-based AI:
    - Quét lịch sử đặt lịch đã hoàn thành → tính tổng giờ hoạt động.
    - Nếu tổng giờ >= ngưỡng bảo trì → tự động khóa máy, ghi log, bắn thông báo cho Admin.
    """
    from app.services.maintenance_ai import analyze_and_trigger_maintenance
    result = analyze_and_trigger_maintenance(db, equipment_id)
    if result.get("status") == "error":
        raise HTTPException(status_code=404, detail=result.get("message"))
    return result



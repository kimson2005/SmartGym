from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.booking import BookingCreate, BookingResponse
from app.crud.crud_booking import (
    create_booking, get_booking, get_bookings,
    get_bookings_by_user, get_bookings_by_equipment, cancel_booking
)
from fastapi import HTTPException

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking_endpoint(booking: BookingCreate, db: Session = Depends(get_db)):
    """
    Tạo booking mới cho thiết bị.

    Logic chống Double Booking 2 lớp:
    - Lớp 1: Row-level Lock + Application-level overlap check
    - Lớp 2: Database constraint EXCLUDE USING gist (fallback)
    """
    return create_booking(db=db, booking=booking)


@router.get("/", response_model=List[BookingResponse])
def read_bookings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lấy danh sách tất cả booking (có phân trang)."""
    return get_bookings(db, skip=skip, limit=limit)


@router.get("/{booking_id}", response_model=BookingResponse)
def read_booking(booking_id: int, db: Session = Depends(get_db)):
    """Lấy chi tiết một booking theo ID."""
    db_booking = get_booking(db, booking_id=booking_id)
    if db_booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy booking"
        )
    return db_booking


@router.get("/user/{user_id}", response_model=List[BookingResponse])
def read_bookings_by_user(
    user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """Lấy danh sách booking của một user cụ thể."""
    return get_bookings_by_user(db, user_id=user_id, skip=skip, limit=limit)


@router.get("/equipment/{equipment_id}", response_model=List[BookingResponse])
def read_bookings_by_equipment(
    equipment_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """Lấy danh sách booking của một thiết bị cụ thể."""
    return get_bookings_by_equipment(db, equipment_id=equipment_id, skip=skip, limit=limit)


@router.patch("/{booking_id}/cancel", response_model=BookingResponse)
def cancel_booking_endpoint(booking_id: int, db: Session = Depends(get_db)):
    """Hủy một booking (chuyển status sang 'Cancelled')."""
    return cancel_booking(db=db, booking_id=booking_id)

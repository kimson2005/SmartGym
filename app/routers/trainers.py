"""
============================================================================
TRAINER ROUTER — API Endpoints cho tính năng Huấn luyện viên
============================================================================

Prefix: /api/v1/trainers

Endpoints:
  ── Trainer Profile ──
  POST   /                          Tạo hồ sơ HLV
  GET    /                          Danh sách tất cả HLV
  GET    /{trainer_id}              Chi tiết HLV (kèm rating trung bình)
  PUT    /{trainer_id}              Cập nhật hồ sơ HLV
  DELETE /{trainer_id}              Xóa hồ sơ HLV

  ── Trainer Bookings ──
  POST   /bookings/                 Hội viên đặt lịch với HLV
  GET    /bookings/                 Tất cả trainer bookings
  GET    /bookings/{booking_id}     Chi tiết một booking
  GET    /bookings/trainer/{id}     Bookings của 1 trainer
  GET    /bookings/member/{id}      Bookings HLV của 1 hội viên
  PATCH  /bookings/{id}/confirm     Trainer xác nhận
  PATCH  /bookings/{id}/reject      Trainer từ chối
  PATCH  /bookings/{id}/complete    Đánh dấu hoàn thành
  PATCH  /bookings/{id}/cancel      Hủy booking

  ── Trainer Reviews ──
  POST   /reviews/                  Hội viên đánh giá HLV
  GET    /reviews/trainer/{id}      Đánh giá của 1 trainer

============================================================================
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.trainer import (
    TrainerCreate, TrainerUpdate, TrainerResponse,
    TrainerBookingCreate, TrainerBookingResponse,
    TrainerReviewCreate, TrainerReviewResponse,
)
from app.crud.crud_trainer import (
    get_trainer, get_trainers, create_trainer, update_trainer, delete_trainer,
    get_trainer_booking, get_trainer_bookings, get_bookings_by_trainer,
    get_bookings_by_member, create_trainer_booking,
    confirm_trainer_booking, reject_trainer_booking,
    complete_trainer_booking, cancel_trainer_booking,
    get_reviews_by_trainer, get_trainer_average_rating, create_trainer_review,
)

router = APIRouter(prefix="/trainers", tags=["trainers"])


# ═══════════════════════════════════════════════════════════════════════════
# TRAINER PROFILE ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/", response_model=TrainerResponse, status_code=status.HTTP_201_CREATED)
def create_trainer_endpoint(trainer: TrainerCreate, db: Session = Depends(get_db)):
    """
    Tạo hồ sơ huấn luyện viên mới.
    User phải có role='trainer' trong bảng users.
    """
    return create_trainer(db=db, trainer=trainer)


@router.get("/", response_model=List[TrainerResponse])
def read_trainers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lấy danh sách tất cả huấn luyện viên (có phân trang)."""
    return get_trainers(db, skip=skip, limit=limit)


@router.get("/{trainer_id}")
def read_trainer(trainer_id: int, db: Session = Depends(get_db)):
    """
    Lấy chi tiết HLV theo ID, kèm theo điểm đánh giá trung bình.
    Response bổ sung field `average_rating` ngoài các field chuẩn.
    """
    db_trainer = get_trainer(db, trainer_id=trainer_id)
    if db_trainer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy huấn luyện viên"
        )

    # Tính rating trung bình
    avg_rating = get_trainer_average_rating(db, trainer_id)

    # Trả về response kèm average_rating
    trainer_data = TrainerResponse.model_validate(db_trainer).model_dump()
    trainer_data["average_rating"] = avg_rating
    return trainer_data


@router.put("/{trainer_id}", response_model=TrainerResponse)
def update_trainer_endpoint(
    trainer_id: int, trainer: TrainerUpdate, db: Session = Depends(get_db)
):
    """Cập nhật hồ sơ HLV."""
    return update_trainer(db=db, trainer_id=trainer_id, trainer_update=trainer)


@router.delete("/{trainer_id}", response_model=TrainerResponse)
def delete_trainer_endpoint(trainer_id: int, db: Session = Depends(get_db)):
    """Xóa hồ sơ HLV (cascade xóa bookings và reviews liên quan)."""
    return delete_trainer(db=db, trainer_id=trainer_id)


# ═══════════════════════════════════════════════════════════════════════════
# TRAINER BOOKING ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/bookings/", response_model=TrainerBookingResponse, status_code=status.HTTP_201_CREATED)
def create_trainer_booking_endpoint(
    booking: TrainerBookingCreate, db: Session = Depends(get_db)
):
    """
    Hội viên đặt lịch tập với HLV.
    Hệ thống tự động kiểm tra trùng lịch (overlap) trước khi tạo.
    Booking mới sẽ có status='Pending', chờ trainer xác nhận.
    """
    return create_trainer_booking(db=db, booking=booking)


@router.get("/bookings/", response_model=List[TrainerBookingResponse])
def read_trainer_bookings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lấy tất cả trainer bookings (có phân trang)."""
    return get_trainer_bookings(db, skip=skip, limit=limit)


@router.get("/bookings/{booking_id}", response_model=TrainerBookingResponse)
def read_trainer_booking(booking_id: int, db: Session = Depends(get_db)):
    """Lấy chi tiết một trainer booking."""
    db_booking = get_trainer_booking(db, booking_id=booking_id)
    if db_booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy booking"
        )
    return db_booking


@router.get("/bookings/trainer/{trainer_id}", response_model=List[TrainerBookingResponse])
def read_bookings_by_trainer(
    trainer_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """Lấy danh sách booking của một trainer cụ thể."""
    return get_bookings_by_trainer(db, trainer_id=trainer_id, skip=skip, limit=limit)


@router.get("/bookings/member/{member_id}", response_model=List[TrainerBookingResponse])
def read_bookings_by_member(
    member_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """Lấy danh sách booking HLV của một hội viên."""
    return get_bookings_by_member(db, member_id=member_id, skip=skip, limit=limit)


@router.patch("/bookings/{booking_id}/confirm", response_model=TrainerBookingResponse)
def confirm_booking_endpoint(
    booking_id: int,
    trainer_user_id: int = Query(..., description="user_id của trainer xác nhận"),
    db: Session = Depends(get_db),
):
    """
    Trainer xác nhận booking (Pending → Confirmed).
    Chỉ trainer sở hữu booking mới có quyền.
    """
    return confirm_trainer_booking(db=db, booking_id=booking_id, trainer_user_id=trainer_user_id)


@router.patch("/bookings/{booking_id}/reject", response_model=TrainerBookingResponse)
def reject_booking_endpoint(
    booking_id: int,
    trainer_user_id: int = Query(..., description="user_id của trainer từ chối"),
    db: Session = Depends(get_db),
):
    """
    Trainer từ chối booking (Pending → Rejected).
    Chỉ trainer sở hữu booking mới có quyền.
    """
    return reject_trainer_booking(db=db, booking_id=booking_id, trainer_user_id=trainer_user_id)


@router.patch("/bookings/{booking_id}/complete", response_model=TrainerBookingResponse)
def complete_booking_endpoint(booking_id: int, db: Session = Depends(get_db)):
    """Đánh dấu booking đã hoàn thành (Confirmed → Completed)."""
    return complete_trainer_booking(db=db, booking_id=booking_id)


@router.patch("/bookings/{booking_id}/cancel", response_model=TrainerBookingResponse)
def cancel_booking_endpoint(booking_id: int, db: Session = Depends(get_db)):
    """Hủy booking HLV (→ Cancelled)."""
    return cancel_trainer_booking(db=db, booking_id=booking_id)


# ═══════════════════════════════════════════════════════════════════════════
# TRAINER REVIEW ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/reviews/", response_model=TrainerReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review_endpoint(review: TrainerReviewCreate, db: Session = Depends(get_db)):
    """
    Hội viên đánh giá HLV (1-5 sao).
    Yêu cầu: Phải có ít nhất 1 booking 'Completed' với HLV này.
    Mỗi hội viên chỉ được đánh giá 1 lần cho mỗi HLV.
    """
    return create_trainer_review(db=db, review=review)


@router.get("/reviews/trainer/{trainer_id}", response_model=List[TrainerReviewResponse])
def read_reviews_by_trainer(trainer_id: int, db: Session = Depends(get_db)):
    """Lấy tất cả đánh giá của một trainer."""
    return get_reviews_by_trainer(db, trainer_id=trainer_id)

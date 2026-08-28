"""
============================================================================
TRAINER CRUD — Logic nghiệp vụ cho tính năng Huấn luyện viên
============================================================================

Xử lý toàn bộ truy vấn DB cho 3 bảng: trainers, trainer_bookings, trainer_reviews.

Logic nghiệp vụ phức tạp:
  1. Tạo hồ sơ HLV: Kiểm tra user phải có role='trainer'.
  2. Đặt lịch HLV: Chống trùng lịch (overlap check) giống booking thiết bị.
  3. Xác nhận/Từ chối booking: Chỉ trainer của booking đó mới có quyền.
  4. Đánh giá HLV: Chỉ cho phép khi đã hoàn thành ít nhất 1 buổi tập.
  5. Tính trung bình sao (average rating) cho trainer.
============================================================================
"""

from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.models.user import User
from app.models.trainer import Trainer, TrainerBooking, TrainerReview
from app.schemas.trainer import TrainerCreate, TrainerUpdate, TrainerBookingCreate, TrainerReviewCreate


# ═══════════════════════════════════════════════════════════════════════════
# TRAINER PROFILE CRUD
# ═══════════════════════════════════════════════════════════════════════════

def get_trainer(db: Session, trainer_id: int) -> Trainer | None:
    """Lấy hồ sơ HLV theo trainer_id."""
    return db.execute(
        select(Trainer).filter(Trainer.trainer_id == trainer_id)
    ).scalar_one_or_none()


def get_trainer_by_user_id(db: Session, user_id: int) -> Trainer | None:
    """Lấy hồ sơ HLV theo user_id (vì mỗi user chỉ có 1 trainer profile)."""
    return db.execute(
        select(Trainer).filter(Trainer.user_id == user_id)
    ).scalar_one_or_none()


def get_trainers(db: Session, skip: int = 0, limit: int = 100) -> list[Trainer]:
    """Lấy danh sách tất cả HLV có phân trang."""
    result = db.execute(
        select(Trainer).order_by(Trainer.trainer_id).offset(skip).limit(limit)
    )
    return list(result.scalars().all())


def create_trainer(db: Session, trainer: TrainerCreate) -> Trainer:
    """
    Tạo hồ sơ HLV mới.

    Logic nghiệp vụ:
      1. Kiểm tra user có tồn tại không.
      2. Kiểm tra user có role='trainer' không (chỉ trainer mới được tạo hồ sơ).
      3. Kiểm tra user chưa có hồ sơ trainer (UNIQUE constraint).
    """
    # Bước 1: Kiểm tra user tồn tại
    db_user = db.execute(
        select(User).filter(User.user_id == trainer.user_id)
    ).scalar_one_or_none()

    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người dùng"
        )

    # Bước 2: Kiểm tra role phải là 'trainer'
    if db_user.role != "trainer":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User này có role='{db_user.role}'. Chỉ user có role='trainer' mới được tạo hồ sơ HLV"
        )

    # Bước 3: Kiểm tra chưa có hồ sơ
    existing = get_trainer_by_user_id(db, trainer.user_id)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User này đã có hồ sơ huấn luyện viên"
        )

    db_trainer = Trainer(
        user_id=trainer.user_id,
        specialty=trainer.specialty,
        experience_years=trainer.experience_years,
        hourly_rate=trainer.hourly_rate,
        bio=trainer.bio,
    )
    db.add(db_trainer)
    db.commit()
    db.refresh(db_trainer)
    return db_trainer


def update_trainer(db: Session, trainer_id: int, trainer_update: TrainerUpdate) -> Trainer:
    """Cập nhật hồ sơ HLV. Chỉ cập nhật các trường được gửi lên (not None)."""
    db_trainer = get_trainer(db, trainer_id)
    if db_trainer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy hồ sơ huấn luyện viên"
        )

    update_data = trainer_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_trainer, field, value)

    db.commit()
    db.refresh(db_trainer)
    return db_trainer


def delete_trainer(db: Session, trainer_id: int) -> Trainer:
    """Xóa hồ sơ HLV (cascade xóa bookings và reviews liên quan)."""
    db_trainer = get_trainer(db, trainer_id)
    if db_trainer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy hồ sơ huấn luyện viên"
        )

    db.delete(db_trainer)
    db.commit()
    return db_trainer


# ═══════════════════════════════════════════════════════════════════════════
# TRAINER BOOKING CRUD
# ═══════════════════════════════════════════════════════════════════════════

def get_trainer_booking(db: Session, booking_id: int) -> TrainerBooking | None:
    """Lấy chi tiết một trainer booking."""
    return db.execute(
        select(TrainerBooking).filter(TrainerBooking.booking_id == booking_id)
    ).scalar_one_or_none()


def get_trainer_bookings(db: Session, skip: int = 0, limit: int = 100) -> list[TrainerBooking]:
    """Lấy tất cả trainer bookings."""
    result = db.execute(
        select(TrainerBooking).order_by(TrainerBooking.start_time.desc()).offset(skip).limit(limit)
    )
    return list(result.scalars().all())


def get_bookings_by_trainer(db: Session, trainer_id: int, skip: int = 0, limit: int = 100) -> list[TrainerBooking]:
    """Lấy danh sách booking của một trainer cụ thể."""
    result = db.execute(
        select(TrainerBooking)
        .filter(TrainerBooking.trainer_id == trainer_id)
        .order_by(TrainerBooking.start_time.desc())
        .offset(skip).limit(limit)
    )
    return list(result.scalars().all())


def get_bookings_by_member(db: Session, member_id: int, skip: int = 0, limit: int = 100) -> list[TrainerBooking]:
    """Lấy danh sách booking HLV của một hội viên."""
    result = db.execute(
        select(TrainerBooking)
        .filter(TrainerBooking.member_id == member_id)
        .order_by(TrainerBooking.start_time.desc())
        .offset(skip).limit(limit)
    )
    return list(result.scalars().all())


def create_trainer_booking(db: Session, booking: TrainerBookingCreate) -> TrainerBooking:
    """
    Tạo booking HLV mới với cơ chế chống trùng lịch (Overlap Check).

    Logic nghiệp vụ phức tạp:
      1. Kiểm tra member tồn tại.
      2. Kiểm tra trainer tồn tại.
      3. Kiểm tra member không tự đặt chính mình (nếu member cũng là trainer).
      4. Row-level Lock trên trainer record → ngăn race condition.
      5. Overlap Check: Kiểm tra trainer có rảnh vào khoảng thời gian đó không.
         Hai khoảng [A_start, A_end) và [B_start, B_end) bị overlap khi:
         A_start < B_end AND A_end > B_start
      6. Tạo booking với status='Pending' (chờ trainer xác nhận).
    """
    try:
        # Bước 1: Kiểm tra member tồn tại
        db_member = db.execute(
            select(User).filter(User.user_id == booking.member_id)
        ).scalar_one_or_none()
        if db_member is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy hội viên"
            )

        # Bước 2: Kiểm tra trainer tồn tại (với Row-level Lock)
        db_trainer = db.execute(
            select(Trainer)
            .filter(Trainer.trainer_id == booking.trainer_id)
            .with_for_update()
        ).scalar_one_or_none()
        if db_trainer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy huấn luyện viên"
            )

        # Bước 3: Member không được tự đặt chính mình
        if db_trainer.user_id == booking.member_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Huấn luyện viên không thể tự đặt lịch cho chính mình"
            )

        # Bước 4: Overlap Check — kiểm tra trainer có rảnh không
        # Chỉ kiểm tra các booking chưa bị Cancelled hoặc Rejected
        overlapping = db.execute(
            select(TrainerBooking).filter(
                and_(
                    TrainerBooking.trainer_id == booking.trainer_id,
                    TrainerBooking.status.in_(["Pending", "Confirmed"]),
                    TrainerBooking.start_time < booking.end_time,
                    TrainerBooking.end_time > booking.start_time,
                )
            )
        ).scalars().first()

        if overlapping is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Huấn luyện viên đã có lịch trong khoảng thời gian này"
            )

        # Bước 5: Tạo booking mới với status='Pending'
        db_booking = TrainerBooking(
            member_id=booking.member_id,
            trainer_id=booking.trainer_id,
            start_time=booking.start_time,
            end_time=booking.end_time,
            status="Pending",
        )
        db.add(db_booking)
        db.commit()
        db.refresh(db_booking)
        return db_booking

    except HTTPException:
        db.rollback()
        raise
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lỗi trùng lịch ở mức database"
        )
    except Exception:
        db.rollback()
        raise


def confirm_trainer_booking(db: Session, booking_id: int, trainer_user_id: int) -> TrainerBooking:
    """
    Trainer xác nhận booking.

    Logic nghiệp vụ:
      - Chỉ trainer sở hữu booking mới có quyền xác nhận.
      - Chỉ booking đang 'Pending' mới được xác nhận.
    """
    db_booking = get_trainer_booking(db, booking_id)
    if db_booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy booking"
        )

    # Kiểm tra quyền: trainer_user_id phải khớp với trainer của booking
    db_trainer = get_trainer(db, db_booking.trainer_id)
    if db_trainer is None or db_trainer.user_id != trainer_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền xác nhận booking này"
        )

    if db_booking.status != "Pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không thể xác nhận booking có trạng thái '{db_booking.status}'"
        )

    db_booking.status = "Confirmed"
    db.commit()
    db.refresh(db_booking)
    return db_booking


def reject_trainer_booking(db: Session, booking_id: int, trainer_user_id: int) -> TrainerBooking:
    """
    Trainer từ chối booking.

    Logic tương tự confirm nhưng chuyển status → 'Rejected'.
    """
    db_booking = get_trainer_booking(db, booking_id)
    if db_booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy booking"
        )

    db_trainer = get_trainer(db, db_booking.trainer_id)
    if db_trainer is None or db_trainer.user_id != trainer_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền từ chối booking này"
        )

    if db_booking.status != "Pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không thể từ chối booking có trạng thái '{db_booking.status}'"
        )

    db_booking.status = "Rejected"
    db.commit()
    db.refresh(db_booking)
    return db_booking


def complete_trainer_booking(db: Session, booking_id: int) -> TrainerBooking:
    """Đánh dấu booking đã hoàn thành (Completed). Dùng bởi admin hoặc hệ thống."""
    db_booking = get_trainer_booking(db, booking_id)
    if db_booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy booking"
        )

    if db_booking.status != "Confirmed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Chỉ booking 'Confirmed' mới có thể đánh dấu hoàn thành"
        )

    db_booking.status = "Completed"
    db.commit()
    db.refresh(db_booking)
    return db_booking


def cancel_trainer_booking(db: Session, booking_id: int) -> TrainerBooking:
    """Hủy booking HLV (chuyển status → 'Cancelled')."""
    db_booking = get_trainer_booking(db, booking_id)
    if db_booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy booking"
        )

    if db_booking.status in ("Completed", "Cancelled"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không thể hủy booking có trạng thái '{db_booking.status}'"
        )

    db_booking.status = "Cancelled"
    db.commit()
    db.refresh(db_booking)
    return db_booking


# ═══════════════════════════════════════════════════════════════════════════
# TRAINER REVIEW CRUD
# ═══════════════════════════════════════════════════════════════════════════

def get_reviews_by_trainer(db: Session, trainer_id: int) -> list[TrainerReview]:
    """Lấy tất cả đánh giá của một trainer."""
    result = db.execute(
        select(TrainerReview)
        .filter(TrainerReview.trainer_id == trainer_id)
        .order_by(TrainerReview.created_at.desc())
    )
    return list(result.scalars().all())


def get_trainer_average_rating(db: Session, trainer_id: int) -> float:
    """
    Tính điểm trung bình sao của trainer.
    Trả về 0.0 nếu chưa có đánh giá nào.
    """
    result = db.execute(
        select(func.avg(TrainerReview.rating))
        .filter(TrainerReview.trainer_id == trainer_id)
    ).scalar()
    return round(float(result), 1) if result else 0.0


def create_trainer_review(db: Session, review: TrainerReviewCreate) -> TrainerReview:
    """
    Tạo đánh giá HLV mới.

    Logic nghiệp vụ phức tạp:
      1. Kiểm tra trainer tồn tại.
      2. Kiểm tra member tồn tại.
      3. Member không được tự review chính mình (nếu member cũng là trainer).
      4. Kiểm tra member đã có ít nhất 1 booking 'Completed' với trainer này.
         → Chỉ cho phép review khi đã thực sự tập với HLV.
      5. Kiểm tra chưa review trước đó (UNIQUE constraint).
    """
    # Bước 1: Kiểm tra trainer tồn tại
    db_trainer = get_trainer(db, review.trainer_id)
    if db_trainer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy huấn luyện viên"
        )

    # Bước 2: Kiểm tra member tồn tại
    db_member = db.execute(
        select(User).filter(User.user_id == review.member_id)
    ).scalar_one_or_none()
    if db_member is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy hội viên"
        )

    # Bước 3: Không tự review mình
    if db_trainer.user_id == review.member_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Huấn luyện viên không thể tự đánh giá chính mình"
        )

    # Bước 4: Kiểm tra đã có booking 'Completed' chưa
    completed_booking = db.execute(
        select(TrainerBooking).filter(
            and_(
                TrainerBooking.trainer_id == review.trainer_id,
                TrainerBooking.member_id == review.member_id,
                TrainerBooking.status == "Completed",
            )
        )
    ).scalars().first()

    if completed_booking is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bạn cần hoàn thành ít nhất 1 buổi tập với HLV này trước khi đánh giá"
        )

    # Bước 5: Tạo review (UNIQUE constraint sẽ bắt nếu đã review trước đó)
    try:
        db_review = TrainerReview(
            trainer_id=review.trainer_id,
            member_id=review.member_id,
            rating=review.rating,
            comment=review.comment,
        )
        db.add(db_review)
        db.commit()
        db.refresh(db_review)
        return db_review

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Bạn đã đánh giá huấn luyện viên này rồi"
        )

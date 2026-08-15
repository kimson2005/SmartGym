from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.models.booking import Booking
from app.models.equipment import Equipment
from app.schemas.booking import BookingCreate


def get_booking(db: Session, booking_id: int) -> Booking | None:
    """Lấy thông tin một booking theo ID."""
    return db.execute(
        select(Booking).filter(Booking.booking_id == booking_id)
    ).scalar_one_or_none()


def get_bookings(db: Session, skip: int = 0, limit: int = 100) -> list[Booking]:
    """Lấy danh sách booking có phân trang."""
    result = db.execute(
        select(Booking).order_by(Booking.start_time.desc()).offset(skip).limit(limit)
    )
    return list(result.scalars().all())


def get_bookings_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> list[Booking]:
    """Lấy danh sách booking của một user cụ thể."""
    result = db.execute(
        select(Booking)
        .filter(Booking.user_id == user_id)
        .order_by(Booking.start_time.desc())
        .offset(skip).limit(limit)
    )
    return list(result.scalars().all())


def get_bookings_by_equipment(db: Session, equipment_id: int, skip: int = 0, limit: int = 100) -> list[Booking]:
    """Lấy danh sách booking của một thiết bị cụ thể."""
    result = db.execute(
        select(Booking)
        .filter(Booking.equipment_id == equipment_id)
        .order_by(Booking.start_time.desc())
        .offset(skip).limit(limit)
    )
    return list(result.scalars().all())


def create_booking(db: Session, booking: BookingCreate) -> Booking:
    """
    Tạo booking mới với cơ chế chống Double Booking 2 lớp:

    Lớp 1 (Application Level): Row-level Lock + Overlap Check
        - Sử dụng SELECT ... FOR UPDATE để khóa dòng thiết bị trong transaction.
        - Query kiểm tra overlap với các booking 'Confirmed' hiện tại.

    Lớp 2 (Database Level - Fallback): EXCLUDE USING gist constraint
        - Bắt IntegrityError từ ràng buộc prevent_double_booking.
        - Rollback và trả lỗi 400.
    """
    try:
        # ===== LỚP 1: APPLICATION-LEVEL LOCK & CHECK =====

        # Kiểm tra user có tồn tại không để tránh lỗi Foreign Key
        from app.models.user import User
        db_user = db.execute(select(User).filter(User.user_id == booking.user_id)).scalar_one_or_none()
        if db_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy người dùng"
            )

        # Bước 1: Khóa dòng thiết bị bằng Row-level Lock (FOR UPDATE)
        # Điều này ngăn mọi transaction khác đọc/ghi vào dòng này cho đến khi commit
        db_equipment = db.execute(
            select(Equipment)
            .filter(Equipment.equipment_id == booking.equipment_id)
            .with_for_update()
        ).scalar_one_or_none()

        if db_equipment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy thiết bị"
            )

        # Kiểm tra thiết bị có đang ở trạng thái Maintenance không
        if db_equipment.status == "Maintenance":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Thiết bị đang trong trạng thái bảo trì, không thể đặt lịch"
            )

        # Bước 2: Kiểm tra xung đột thời gian (Overlap Check)
        # Hai khoảng thời gian [A_start, A_end) và [B_start, B_end) bị overlap khi:
        # A_start < B_end AND A_end > B_start
        overlapping_booking = db.execute(
            select(Booking).filter(
                and_(
                    Booking.equipment_id == booking.equipment_id,
                    Booking.status == "Confirmed",
                    Booking.start_time < booking.end_time,
                    Booking.end_time > booking.start_time,
                )
            )
        ).scalars().first()

        if overlapping_booking is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Thiết bị đã được đặt trong khoảng thời gian này"
            )

        # Bước 3: Tạo booking mới
        db_booking = Booking(
            user_id=booking.user_id,
            equipment_id=booking.equipment_id,
            start_time=booking.start_time,
            end_time=booking.end_time,
            status="Confirmed",
        )
        db.add(db_booking)
        db.commit()
        db.refresh(db_booking)
        return db_booking

    except HTTPException:
        # Cho phép HTTPException được raise lên mà không rollback
        db.rollback()
        raise

    except IntegrityError:
        # ===== LỚP 2: DATABASE-LEVEL FALLBACK =====
        # Bắt lỗi từ ràng buộc EXCLUDE USING gist (prevent_double_booking)
        # Trường hợp này xảy ra khi 2 request đồng thời vượt qua Lớp 1
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Thiết bị đã được đặt trong khoảng thời gian này (xung đột ở mức database)"
        )

    except Exception:
        # Bắt mọi lỗi không mong muốn khác
        db.rollback()
        raise


def cancel_booking(db: Session, booking_id: int) -> Booking:
    """Hủy một booking (chuyển status sang 'Cancelled')."""
    db_booking = get_booking(db, booking_id)
    if db_booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy booking"
        )

    if db_booking.status != "Confirmed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không thể hủy booking có trạng thái '{db_booking.status}'"
        )

    db_booking.status = "Cancelled"
    db.commit()
    db.refresh(db_booking)
    return db_booking

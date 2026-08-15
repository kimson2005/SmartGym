from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.booking import Booking
from app.models.equipment import Equipment
from app.models.maintenance import MaintenanceLog
from app.models.notification import Notification
from app.models.user import User


def _ensure_aware_utc(dt: datetime) -> datetime:
    """
    Đảm bảo datetime luôn có timezone (aware).
    Nếu DB trả về naive datetime (không có tz), gắn mặc định là UTC.
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def analyze_and_trigger_maintenance(db: Session, equipment_id: int) -> dict:
    """
    Logic thông minh (AI Rule-based) cho một thiết bị:
    1. Tự động chuyển các booking quá hạn sang 'Completed'.
    2. Tính toán tổng số giờ hoạt động thực tế của thiết bị.
    3. Đối chiếu với ngưỡng maintenance_interval_hours.
    4. Tự động chuyển status sang 'Maintenance', cập nhật last_maintenance_date,
       ghi log và bắn Notification cho Admin nếu vượt ngưỡng.
    """
    now_utc = datetime.now(timezone.utc)

    # 1. Lấy thông tin thiết bị
    equipment = db.execute(
        select(Equipment).filter(Equipment.equipment_id == equipment_id)
    ).scalar_one_or_none()

    if not equipment:
        return {"status": "error", "message": "Không tìm thấy thiết bị"}

    # 2. Quét và cập nhật các booking trong quá khứ thành 'Completed'
    past_bookings = db.execute(
        select(Booking)
        .filter(Booking.equipment_id == equipment_id)
        .filter(Booking.status == "Confirmed")
        .filter(Booking.end_time <= now_utc)
    ).scalars().all()

    for b in past_bookings:
        b.status = "Completed"

    if past_bookings:
        db.commit()

    # 3. Tính tổng số giờ hoạt động từ các booking đã Completed
    completed_bookings = db.execute(
        select(Booking)
        .filter(Booking.equipment_id == equipment_id)
        .filter(Booking.status == "Completed")
    ).scalars().all()

    total_seconds = 0.0
    for b in completed_bookings:
        start = _ensure_aware_utc(b.start_time)
        end = _ensure_aware_utc(b.end_time)
        total_seconds += (end - start).total_seconds()

    total_hours = round(total_seconds / 3600.0, 2)

    # 4. Cập nhật tổng số giờ vào thiết bị
    equipment.total_used_hours = total_hours
    db.commit()

    actions_taken = []
    completed_count = len(past_bookings)

    if completed_count > 0:
        actions_taken.append(
            f"Auto-completed {completed_count} past booking(s)"
        )

    # 5. Rule-based AI: Kiểm tra ngưỡng bảo trì
    if total_hours >= equipment.maintenance_interval_hours and equipment.status != "Maintenance":
        # Đổi trạng thái thiết bị để chặn đặt lịch mới
        equipment.status = "Maintenance"

        # Cập nhật ngày bảo trì gần nhất trên bảng Equipments
        equipment.last_maintenance_date = now_utc

        # Tạo nhật ký bảo trì dự đoán (Predictive)
        log = MaintenanceLog(
            equipment_id=equipment.equipment_id,
            maintenance_date=now_utc,
            type="Predictive",
            description=(
                f"Hệ thống SmartGym AI tự động phát hiện: "
                f"Thiết bị '{equipment.name}' đã hoạt động {total_hours:.2f} giờ "
                f"(vượt ngưỡng an toàn {equipment.maintenance_interval_hours} giờ). "
                f"Cần bảo trì ngay để tránh hỏng hóc."
            ),
            cost=0.0,
        )
        db.add(log)

        # Bắn thông báo (Notification) cho toàn bộ Quản trị viên (Admin)
        admins = db.execute(
            select(User).filter(User.role == "admin")
        ).scalars().all()

        for admin in admins:
            notif = Notification(
                user_id=admin.user_id,
                title="🚨 Cảnh báo bảo trì khẩn cấp (AI Predictive)",
                message=(
                    f"Thiết bị '{equipment.name}' (ID: {equipment.equipment_id}) "
                    f"đã đạt {total_hours:.1f}/{equipment.maintenance_interval_hours} giờ hoạt động. "
                    f"Hệ thống tự động khóa thiết bị và chuyển sang chế độ bảo trì. "
                    f"Vui lòng kiểm tra và xử lý."
                ),
            )
            db.add(notif)

        actions_taken.append(
            "Triggered predictive maintenance alert "
            "(Status → Maintenance, last_maintenance_date updated, Notification sent to admins)"
        )
        db.commit()
        db.refresh(equipment)

    return {
        "equipment_id": equipment_id,
        "equipment_name": equipment.name,
        "total_used_hours": total_hours,
        "maintenance_interval_hours": float(equipment.maintenance_interval_hours),
        "remaining_hours": round(
            float(equipment.maintenance_interval_hours) - total_hours, 2
        ),
        "status": equipment.status,
        "last_maintenance_date": (
            equipment.last_maintenance_date.isoformat()
            if equipment.last_maintenance_date
            else None
        ),
        "actions": actions_taken,
    }


def analyze_all_equipments(db: Session) -> dict:
    """
    Quét toàn bộ thiết bị trong hệ thống và chạy AI dự báo bảo trì.
    Dùng cho Admin gọi thủ công hoặc CronJob gọi định kỳ.
    """
    equipments = db.execute(select(Equipment)).scalars().all()

    results = []
    triggered_count = 0

    for eq in equipments:
        result = analyze_and_trigger_maintenance(db, eq.equipment_id)
        results.append(result)
        if result.get("actions"):
            triggered_count += 1

    return {
        "total_equipments_scanned": len(equipments),
        "triggered_maintenance_count": triggered_count,
        "details": results,
    }

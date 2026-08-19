"""
Router Workouts — API tạo lịch tập Gym bằng AI.

Endpoint chính:
    POST /api/v1/workouts/generate/{user_id}
        → Đọc physical_info từ User → Gọi Gemini AI → Lưu WorkoutPlan vào DB.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.database import get_db
from app.models.user import User
from app.models.workout import WorkoutPlan
from app.schemas.workout import WorkoutPlanResponse

router = APIRouter(prefix="/workouts", tags=["workouts"])


@router.post(
    "/generate/{user_id}",
    response_model=WorkoutPlanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="AI tạo lịch tập cá nhân hóa",
    description=(
        "[Smart Feature] Phân tích `physical_info` của người dùng bằng Gemini AI "
        "để tự động thiết kế lịch tập Gym cá nhân hóa. "
        "Kết quả được lưu vào bảng `workout_plans` với `generated_by_ai = True`."
    ),
)
def generate_workout_plan_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
):
    """
    Tạo lịch tập Gym bằng AI cho một người dùng cụ thể.

    Logic:
    1. Tìm User theo user_id → 404 nếu không tồn tại.
    2. Kiểm tra physical_info → 400 nếu chưa cập nhật thông tin thể chất.
    3. Gọi Gemini AI để tạo lịch tập → 503 nếu AI gặp lỗi.
    4. Lưu kết quả vào bảng workout_plans → Trả về WorkoutPlanResponse.
    """

    # ===== Bước 1: Tìm User =====
    db_user = db.execute(
        select(User).filter(User.user_id == user_id)
    ).scalar_one_or_none()

    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy người dùng với ID {user_id}",
        )

    # ===== Bước 2: Kiểm tra physical_info =====
    if not db_user.physical_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Người dùng chưa cập nhật thông tin thể chất (physical_info). "
                "Vui lòng cập nhật chiều cao, cân nặng, mục tiêu tập luyện trước khi sử dụng tính năng này."
            ),
        )

    # ===== Bước 3: Gọi Gemini AI =====
    try:
        from app.services.ai_service import generate_workout_plan

        plan_details = generate_workout_plan(physical_info=db_user.physical_info)
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Dịch vụ AI tạm thời không khả dụng: {e}",
        )

    # ===== Bước 4: Lưu vào Database =====
    # Tạo title tự động dựa trên mục tiêu (nếu có) trong physical_info
    goal = db_user.physical_info.get("goal", "Cải thiện sức khỏe")
    ai_title = f"Lịch tập AI — {goal} — {db_user.full_name}"

    db_plan = WorkoutPlan(
        user_id=user_id,
        title=ai_title[:150],  # Giới hạn 150 ký tự theo constraint DB
        generated_by_ai=True,
        plan_details=plan_details,
        is_active=True,
    )

    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)

    return db_plan

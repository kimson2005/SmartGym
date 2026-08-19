"""
Pydantic Schemas cho AI Structured Output — Lịch tập Gym cá nhân hóa.

Các class này đóng vai trò "khuôn đúc" (response_schema) để ép Gemini LLM
trả về đúng định dạng JSON chuyên nghiệp, map thẳng vào cột `plan_details` (JSONB)
của bảng `workout_plans`.

Cấu trúc phân cấp:
    WorkoutPlanAISchema
    ├── overview: str (tổng quan lịch tập)
    ├── fitness_level: str (đánh giá thể lực)
    ├── weekly_schedule: list[DailyPlanSchema]
    │   ├── day: str (Thứ Hai, Thứ Ba, ...)
    │   ├── focus: str (nhóm cơ chính)
    │   ├── estimated_duration_minutes: int
    │   ├── warmup: WarmupCooldownSchema
    │   ├── exercises: list[ExerciseSchema]
    │   │   ├── name, sets, reps, rest_seconds, tempo, notes ...
    │   │   └── muscle_group, equipment_needed
    │   └── cooldown: WarmupCooldownSchema
    └── nutrition_tips: list[str]
"""

from pydantic import BaseModel, Field


class ExerciseSchema(BaseModel):
    """Chi tiết một bài tập trong buổi tập."""

    name: str = Field(
        description="Tên bài tập (ví dụ: Barbell Bench Press, Squat, Deadlift)"
    )
    muscle_group: str = Field(
        description="Nhóm cơ chính được kích hoạt (ví dụ: Ngực, Lưng, Chân, Vai)"
    )
    sets: int = Field(
        description="Số hiệp (set) cần thực hiện"
    )
    reps: str = Field(
        description="Số lần lặp mỗi hiệp. Có thể là số cụ thể '12' hoặc khoảng '8-12' hoặc thời gian '30 giây'"
    )
    rest_seconds: int = Field(
        description="Thời gian nghỉ giữa các hiệp (đơn vị: giây)"
    )
    tempo: str = Field(
        description="Nhịp thực hiện (ví dụ: '3-1-2-0' nghĩa là 3s hạ - 1s giữ - 2s nâng - 0s nghỉ)"
    )
    equipment_needed: str = Field(
        description="Thiết bị cần dùng (ví dụ: Barbell, Dumbbell, Cable Machine, Bodyweight)"
    )
    notes: str = Field(
        description="Lưu ý kỹ thuật hoặc mẹo quan trọng cho bài tập này"
    )


class WarmupCooldownSchema(BaseModel):
    """Phần khởi động hoặc giãn cơ."""

    description: str = Field(
        description="Mô tả hoạt động khởi động/giãn cơ"
    )
    duration_minutes: int = Field(
        description="Thời lượng (phút)"
    )


class DailyPlanSchema(BaseModel):
    """Lịch tập cho một ngày cụ thể trong tuần."""

    day: str = Field(
        description="Ngày trong tuần (ví dụ: Thứ Hai, Thứ Ba, ... hoặc 'Nghỉ ngơi')"
    )
    focus: str = Field(
        description="Nhóm cơ/mục tiêu chính của buổi tập (ví dụ: Ngực + Tay trước, Lưng + Tay sau, Chân, Nghỉ phục hồi)"
    )
    estimated_duration_minutes: int = Field(
        description="Tổng thời gian ước tính cho buổi tập (phút), bao gồm khởi động và giãn cơ"
    )
    warmup: WarmupCooldownSchema = Field(
        description="Phần khởi động trước khi tập"
    )
    exercises: list[ExerciseSchema] = Field(
        description="Danh sách các bài tập chính trong buổi tập"
    )
    cooldown: WarmupCooldownSchema = Field(
        description="Phần giãn cơ/thả lỏng sau khi tập"
    )


class WorkoutPlanAISchema(BaseModel):
    """
    Schema tổng thể cho lịch tập Gym được AI tạo ra.
    Đây là cấu trúc chính được lưu vào cột `plan_details` (JSONB).
    """

    overview: str = Field(
        description="Tổng quan về chương trình tập: phân tích thể trạng, mục tiêu, và lý do thiết kế lịch tập này"
    )
    fitness_level: str = Field(
        description="Đánh giá mức độ thể lực hiện tại (Beginner / Intermediate / Advanced)"
    )
    program_duration_weeks: int = Field(
        description="Số tuần khuyến nghị áp dụng chương trình này trước khi đánh giá lại"
    )
    weekly_schedule: list[DailyPlanSchema] = Field(
        description="Lịch tập chi tiết cho 7 ngày trong tuần (bao gồm cả ngày nghỉ)"
    )
    nutrition_tips: list[str] = Field(
        description="3-5 lời khuyên dinh dưỡng phù hợp với mục tiêu và thể trạng của người tập"
    )
    important_warnings: list[str] = Field(
        description="Các cảnh báo an toàn hoặc lưu ý y tế quan trọng dựa trên thông tin thể chất"
    )

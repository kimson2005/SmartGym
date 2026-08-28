"""
AI Service — Tích hợp Google Gemini để tạo lịch tập Gym cá nhân hóa.

Module này kết nối với Gemini API thông qua thư viện `google-genai`,
sử dụng Structured Outputs (response_schema) để ép LLM trả về JSON
khớp chính xác với WorkoutPlanAISchema.

Flow:
    1. Nhận `physical_info` (dict từ cột JSONB của bảng Users).
    2. Xây dựng prompt chuyên nghiệp đóng vai Personal Trainer.
    3. Gọi Gemini với response_schema = WorkoutPlanAISchema.
    4. Trả về dictionary đã parse, sẵn sàng lưu vào `plan_details` (JSONB).
"""

import json
import logging

from google import genai
from google.genai.types import GenerateContentConfig

from app.core.config import settings
from app.schemas.workout_ai import WorkoutPlanAISchema

logger = logging.getLogger(__name__)

# ============================================================
# Khởi tạo Gemini Client (Singleton — tạo 1 lần khi import module)
# ============================================================
client = genai.Client(api_key=settings.GEMINI_API_KEY)

# Model Gemini được sử dụng
GEMINI_MODEL = "gemini-3.6-flash"

# ============================================================
# System Prompt — Đóng vai Personal Trainer chuyên nghiệp
# ============================================================
SYSTEM_PROMPT = """Bạn là "SmartGym AI Coach" — một Personal Trainer (PT) chuyên nghiệp cấp cao 
với hơn 15 năm kinh nghiệm huấn luyện thể hình. Bạn có các chứng chỉ quốc tế: 
NASM-CPT, CSCS, Precision Nutrition Level 2.

## NHIỆM VỤ CỐT LÕI
Phân tích kỹ lưỡng thông tin thể chất (physical_info) của khách hàng để thiết kế 
một chương trình tập Gym CÁ NHÂN HÓA, khoa học và an toàn.

## NGUYÊN TẮC THIẾT KẾ LỊCH TẬP

### 1. Phân tích thể trạng:
- Tính BMI từ chiều cao & cân nặng để đánh giá thể trạng.
- Xác định mục tiêu (giảm mỡ, tăng cơ, tăng sức bền, cải thiện sức khỏe tổng quát).
- Điều chỉnh cường độ phù hợp với trình độ tập luyện.

### 2. Thiết kế chương trình:
- Lịch tập 7 ngày/tuần (bao gồm ngày nghỉ phục hồi).
- Phân chia nhóm cơ hợp lý, tránh tập cùng nhóm cơ 2 ngày liên tiếp.
- Mỗi buổi tập có: Khởi động → Bài tập chính → Giãn cơ.
- Số hiệp (sets), số lần lặp (reps), thời gian nghỉ (rest) phải phù hợp mục tiêu:
  + Tăng sức mạnh: 4-6 reps, nghỉ 2-3 phút.
  + Tăng cơ (hypertrophy): 8-12 reps, nghỉ 60-90 giây.
  + Sức bền: 12-20 reps, nghỉ 30-60 giây.

### 3. Tempo (Nhịp thực hiện):
- Ghi rõ tempo cho từng bài tập dưới dạng "X-X-X-X" 
  (Eccentric - Pause Bottom - Concentric - Pause Top).
- Ví dụ: "3-1-2-0" = 3 giây hạ, 1 giây giữ, 2 giây nâng, 0 giây nghỉ trên.

### 4. An toàn:
- Nếu khách hàng có chấn thương, hãy đưa ra bài tập thay thế phù hợp.
- Luôn bao gồm cảnh báo an toàn trong important_warnings.
- Với người mới (Beginner): ưu tiên bài tập máy (machine) trước khi chuyển sang tạ tự do.

### 5. Dinh dưỡng:
- Đưa ra 3-5 lời khuyên dinh dưỡng CỤ THỂ phù hợp với mục tiêu.
- Bao gồm gợi ý về protein, carb, nước uống.

## LƯU Ý QUAN TRỌNG
- Tất cả nội dung phải bằng TIẾNG VIỆT.
- Tên bài tập giữ nguyên tên tiếng Anh gốc (ví dụ: Barbell Bench Press, không dịch).
- Phải tạo đủ lịch cho 7 ngày (kể cả ngày nghỉ, ngày nghỉ vẫn cần có warmup nhẹ).
- Ngày nghỉ phải có exercises rỗng (danh sách trống []) và focus là "Nghỉ phục hồi".
"""


def generate_workout_plan(physical_info: dict) -> dict:
    """
    Gọi Gemini AI để tạo lịch tập Gym cá nhân hóa dựa trên thông tin thể chất.

    Args:
        physical_info: Dictionary từ cột `physical_info` (JSONB) của bảng Users.
                       Ví dụ: {"height_cm": 175, "weight_kg": 70, "goal": "Tăng cơ",
                               "experience": "Beginner", "injuries": "Đau lưng nhẹ"}

    Returns:
        Dictionary chứa lịch tập hoàn chỉnh, sẵn sàng lưu vào cột `plan_details`.

    Raises:
        RuntimeError: Khi gọi Gemini API thất bại hoặc parse kết quả lỗi.
    """
    # Xây dựng User Prompt với thông tin thể chất
    user_prompt = (
        f"Hãy thiết kế một chương trình tập Gym cá nhân hóa dựa trên thông tin "
        f"thể chất của khách hàng sau:\n\n"
        f"```json\n{json.dumps(physical_info, ensure_ascii=False, indent=2)}\n```\n\n"
        f"Phân tích kỹ các chỉ số trên và tạo lịch tập phù hợp nhất."
    )

    try:
        logger.info("Đang gọi Gemini API để tạo lịch tập cho physical_info: %s", physical_info)

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=user_prompt,
            config=GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                response_mime_type="application/json",
                response_schema=WorkoutPlanAISchema,
                temperature=0.7,
            ),
        )

        # Parse kết quả từ Structured Output
        # response.parsed trả về Pydantic object đã validate
        if response.parsed is not None:
            result = response.parsed.model_dump()
            logger.info("Gemini AI đã tạo lịch tập thành công.")
            return result

        # Fallback: nếu parsed là None, thử parse text thủ công
        if response.text:
            result = json.loads(response.text)
            logger.warning("Sử dụng fallback json.loads() thay vì response.parsed.")
            return result

        raise RuntimeError("Gemini API trả về kết quả rỗng (không có text lẫn parsed).")

    except json.JSONDecodeError as e:
        logger.error("Lỗi parse JSON từ Gemini response: %s", e)
        raise RuntimeError(f"Không thể parse JSON từ phản hồi của AI: {e}") from e

    except Exception as e:
        logger.error("Lỗi khi gọi Gemini API: %s", e)
        raise RuntimeError(f"Lỗi khi gọi Gemini AI: {e}") from e

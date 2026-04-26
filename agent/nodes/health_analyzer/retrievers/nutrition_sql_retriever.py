"""
路3：结构化营养聚合查询（SQL）
================================
数据源：food_logs 表
用途：给 LLM 提供精确数字，避免幻觉
      例："你本周平均每天摄入1800kcal，蛋白质仅45g，低于建议量60g"

查询维度：
  - 近 N 天每日热量 / 三大营养素均值
  - 各餐次出现频率（早餐缺失率）
  - 热量最高的 Top5 食物
  - 每日营养素与目标的差距（需 JOIN nutrition_goals）
"""

from dataclasses import dataclass


@dataclass
class NutritionSQLResult:
    avg_daily_calories: float | None
    avg_protein_g: float | None
    avg_fat_g: float | None
    avg_carb_g: float | None
    breakfast_skip_rate: float | None   # 0.0~1.0
    top_high_calorie_foods: list[str]   # ["炸鸡 x3次", "奶茶 x2次"]
    calorie_gap: float | None           # 实际 - 目标，正数=超标，负数=不足
    protein_gap: float | None
    summary_text: str                   # 供直接拼入 Prompt 的文字摘要


async def retrieve(
    user_id: str,
    days: int = 7,
    db_session=None,
) -> NutritionSQLResult:
    """
    Args:
        user_id:    用户 ID
        days:       统计近几天，默认7天
        db_session: AsyncSession，由 runtime.context 传入

    Returns:
        NutritionSQLResult

    TODO 实现步骤：
      1. 查 food_logs 聚合近 days 天数据
         SELECT AVG(calories), AVG(protein_g), AVG(fat_g), AVG(carb_g),
                COUNT(DISTINCT date(logged_at)) as log_days
         WHERE user_id=? AND logged_at >= now()-{days}days
      2. 查 nutrition_goals 取用户目标值
      3. 计算 gap = 实际均值 - 目标值
      4. 查 Top5 高热量食物（GROUP BY food_name ORDER BY SUM(calories) DESC）
      5. 统计早餐缺失率（某天无 meal_type='breakfast' 记录即算缺失）
      6. 拼 summary_text 供 Prompt 直接引用
    """
    # TODO
    return NutritionSQLResult(
        avg_daily_calories=None,
        avg_protein_g=None,
        avg_fat_g=None,
        avg_carb_g=None,
        breakfast_skip_rate=None,
        top_high_calorie_foods=[],
        calorie_gap=None,
        protein_gap=None,
        summary_text="暂无营养统计数据",
    )

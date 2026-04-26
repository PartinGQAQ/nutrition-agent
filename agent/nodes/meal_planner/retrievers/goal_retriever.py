"""
路3：用户营养目标 & 缺口计算（DB 查询）
=========================================
数据源：nutrition_goals 表 + food_logs 表
用途：给 LLM 提供精确的目标值与缺口数字，
      确保生成的饮食计划热量/营养素符合用户设定，而非拍脑袋

计算逻辑：
  缺口 = 近7天实际均值 - 用户目标值
  正数 = 超标（需减少）
  负数 = 不足（需补充）
"""

from dataclasses import dataclass


@dataclass
class GoalResult:
    # 目标值
    target_calories: float | None
    target_protein_g: float | None
    target_fat_g: float | None
    target_carb_g: float | None
    # 近7天实际均值
    actual_calories: float | None
    actual_protein_g: float | None
    actual_fat_g: float | None
    actual_carb_g: float | None
    # 缺口（实际 - 目标）
    calorie_gap: float | None
    protein_gap: float | None
    fat_gap: float | None
    carb_gap: float | None
    # 供 Prompt 直接引用
    gap_summary: str            # "热量超标200kcal，蛋白质不足15g，脂肪达标"
    plan_days: int = 7


async def retrieve(
    user_id: str,
    plan_days: int = 7,
    db_session=None,
) -> GoalResult:
    """
    Args:
        user_id:   用户 ID
        plan_days: 饮食计划天数（同时也是历史参考天数）
        db_session: AsyncSession

    Returns:
        GoalResult

    TODO 实现步骤：
      1. 查 nutrition_goals 取 target_* 字段
      2. 查 food_logs 聚合近 plan_days 天 AVG(calories/protein_g/fat_g/carb_g)
      3. 计算各维度 gap
      4. 拼 gap_summary 文字（超标/不足/达标 三态描述）
    """
    # TODO
    return GoalResult(
        target_calories=None,
        target_protein_g=None,
        target_fat_g=None,
        target_carb_g=None,
        actual_calories=None,
        actual_protein_g=None,
        actual_fat_g=None,
        actual_carb_g=None,
        calorie_gap=None,
        protein_gap=None,
        fat_gap=None,
        carb_gap=None,
        gap_summary="暂无营养目标数据",
        plan_days=plan_days,
    )

"""
三路召回结果合并
=================
合并策略：
  路3（目标&缺口） → 最高优先级，给 LLM 明确的数字约束
  路1（偏好历史）  → 口味约束，确保计划用户愿意吃
  路2（食谱推荐）  → 具体可用食材/菜品池，供 LLM 选取

LLM 生成计划时的期望行为：
  "你需要生成满足缺口数字（路3）、符合用户口味（路1）、
   优先从推荐食谱（路2）中选取的7天饮食计划"
"""

from agent.nodes.meal_planner.retrievers.preference_retriever import PreferenceResult
from agent.nodes.meal_planner.retrievers.recipe_retriever import RecipeResult
from agent.nodes.meal_planner.retrievers.goal_retriever import GoalResult


def merge(
    goal_result: GoalResult,
    preference_result: PreferenceResult,
    recipe_result: RecipeResult,
) -> str:
    """
    Returns:
        merged_context: 直接拼入饮食计划 Prompt 的多段上下文
    """
    sections: list[str] = []

    # ── 路3：营养目标与缺口（优先级最高）────────────────────────────
    sections.append(f"【营养目标与缺口（{goal_result.plan_days}天计划）】")
    sections.append(goal_result.gap_summary or "暂无目标数据")

    # ── 路1：用户饮食偏好 ─────────────────────────────────────────
    sections.append("\n【用户饮食偏好】")
    sections.append(preference_result.summary_text or "暂无偏好数据")
    if preference_result.liked_foods:
        sections.append("高频食物：" + "、".join(preference_result.liked_foods[:10]))

    # ── 路2：推荐食谱池 ───────────────────────────────────────────
    sections.append("\n【推荐食谱参考】")
    if recipe_result.recipes:
        for r in recipe_result.recipes:
            name = r.get("name", "未知")
            cal = r.get("calories", "?")
            tags = "、".join(r.get("tags", []))
            sections.append(f"• {name}（{cal}kcal）[{tags}]")
    else:
        sections.append(recipe_result.summary_text or "暂无食谱数据")

    return "\n".join(sections)

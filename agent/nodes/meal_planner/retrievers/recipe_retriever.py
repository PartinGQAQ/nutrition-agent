"""
路2：食谱知识库语义检索
========================
数据源：Chroma 食谱集合（rag/knowledge_base/recipes 离线入库）
用途：根据用户的营养缺口和口味偏好，召回最合适的食谱推荐
      例：
        - 蛋白质不足 + 偏好中式 → "鸡胸肉炒西兰花食谱"
        - 热量超标 + 需减脂   → "低卡饱腹沙拉食谱"
        - 早餐缺失率高         → "10分钟快手早餐食谱"

食谱知识库建议字段：
  name, calories, protein_g, fat_g, carb_g,
  prep_time_min, cuisine_type, tags (["高蛋白", "减脂", "快手"])
"""

from dataclasses import dataclass


@dataclass
class RecipeResult:
    recipes: list[dict]         # 食谱列表，含名称/营养/做法摘要
    summary_text: str           # 供 Prompt 引用的食谱推荐摘要


async def retrieve(
    nutrition_gap_summary: str,     # 路3 计算出的营养缺口描述
    preference_summary: str,        # 路1 得出的偏好摘要
    days: int = 7,
    k: int = 14,                    # 默认返回14个（7天×2餐参考）
) -> RecipeResult:
    """
    Args:
        nutrition_gap_summary: 例 "蛋白质不足15g，热量超标200kcal"
        preference_summary:    例 "偏好中式，常吃米饭面条"
        days:                  计划天数，影响召回数量
        k:                     返回食谱数

    Returns:
        RecipeResult

    TODO 实现步骤：
      1. 拼接 query = nutrition_gap_summary + " " + preference_summary
      2. 对 Chroma collection="recipes" 做向量检索
      3. 按 tags 过滤（如热量超标时过滤 tag="高热量"）
      4. 返回 top-k 食谱及摘要
    """
    # TODO
    return RecipeResult(recipes=[], summary_text="暂无食谱推荐")

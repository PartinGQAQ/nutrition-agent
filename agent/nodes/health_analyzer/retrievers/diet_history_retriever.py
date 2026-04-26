"""
路1：历史饮食语义检索
========================
数据源：Chroma 饮食记录集合（food_db_writer 写入的语义化文本）
用途：找出近期高热量餐食、高频食物、某类营养素不足的具体例证，
      给 LLM 分析提供有据可查的真实记录，避免幻觉。

Query 策略：
  - 用 LLM 把用户原始问题扩展成多个子查询
    例："最近饮食健康吗" →
        ["近期高热量食物", "蔬菜摄入记录", "高脂肪饮食记录"]
  - 多个子查询结果 union 后去重，取 top-k
"""

from dataclasses import dataclass


@dataclass
class DietHistoryResult:
    records: list[str]          # 语义化文本列表，直接拼入 Prompt
    query_keywords: list[str]   # 扩展后的子查询（调试用）


async def retrieve(
    user_id: str,
    question: str,
    k: int = 10,
) -> DietHistoryResult:
    """
    Args:
        user_id:  用于向量库过滤（where user_id == ?）
        question: 用户原始问题
        k:        最终返回的语义文本条数

    Returns:
        DietHistoryResult

    TODO 实现步骤：
      1. 用 LLM 扩展 question → query_keywords (list[str])
         参考 intent_router 的 chain 写法，输出 JSON 数组
      2. asyncio.gather 并行对每个 keyword 做 Chroma 向量检索
         collection = "diet_history"，filter = {"user_id": user_id}
      3. 去重 + 按相似度排序，截取 top-k
      4. 返回 DietHistoryResult
    """
    # TODO
    return DietHistoryResult(records=[], query_keywords=[])

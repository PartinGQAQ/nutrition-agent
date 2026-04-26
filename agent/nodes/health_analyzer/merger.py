"""
三路召回结果合并
=================
职责：把三路异构结果统一拼装成可直接注入 Prompt 的上下文字符串。

合并策略：
  路3（SQL精确数字）→ 最高优先级，放在 Prompt 最前面，给 LLM 数字锚点
  路1（历史语义）   → 具体饮食例证，中间
  路2（知识库）     → 专业知识背书，最后

这样 LLM 在生成分析时会优先引用精确数字，
再用历史记录佐证，最后用知识作为建议依据。
"""

from agent.nodes.health_analyzer.retrievers.diet_history_retriever import DietHistoryResult
from agent.nodes.health_analyzer.retrievers.knowledge_retriever import KnowledgeResult
from agent.nodes.health_analyzer.retrievers.nutrition_sql_retriever import NutritionSQLResult


def merge(
    sql_result: NutritionSQLResult,
    diet_result: DietHistoryResult,
    knowledge_result: KnowledgeResult,
) -> str:
    """
    将三路召回结果合并为 Prompt 上下文字符串。

    Returns:
        merged_context: 直接拼入健康分析 Prompt 的多段文本
    """
    sections: list[str] = []

    # ── 路3：精确营养统计（优先级最高）────────────────────────────────
    sections.append("【近期营养统计（结构化数据）】")
    sections.append(sql_result.summary_text or "暂无统计数据")

    # ── 路1：历史饮食语义记录 ─────────────────────────────────────────
    if diet_result.records:
        sections.append("\n【相关饮食记录（语义检索）】")
        for i, record in enumerate(diet_result.records, 1):
            sections.append(f"{i}. {record}")
    else:
        sections.append("\n【相关饮食记录】暂无匹配记录")

    # ── 路2：营养知识库 ───────────────────────────────────────────────
    if knowledge_result.docs:
        sections.append("\n【营养知识参考】")
        for doc, title in zip(knowledge_result.docs, knowledge_result.source_titles):
            sections.append(f"[{title}] {doc}")
    else:
        sections.append("\n【营养知识参考】暂无匹配知识")

    return "\n".join(sections)

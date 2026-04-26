"""
路2：营养知识库语义检索
========================
数据源：Chroma 营养知识集合（rag/knowledge_base/ 文档离线入库）
用途：给分析报告提供专业知识背书，例如：
      - 用户碳水偏高 → 召回"低GI饮食建议"
      - 用户蛋白质不足 → 召回"成年人每日蛋白质推荐量"
      - 用户缺乏蔬菜 → 召回"膳食纤维与肠道健康"

知识库文档建议来源：
  - 中国居民膳食指南（2022）
  - USDA Dietary Guidelines
  - 常见营养素 RDA 标准
  - 常见饮食误区 FAQ
"""

from dataclasses import dataclass


@dataclass
class KnowledgeResult:
    docs: list[str]             # 相关知识片段列表，直接拼入 Prompt
    source_titles: list[str]    # 来源标题（引用用）


async def retrieve(
    question: str,
    diet_summary: str,          # 路3 SQL 聚合结果的文本摘要，辅助召回更精准
    k: int = 5,
) -> KnowledgeResult:
    """
    Args:
        question:      用户原始问题
        diet_summary:  路3 返回的营养统计摘要（如"近7天均热量1800kcal，蛋白质45g"）
                       拼进 query 让知识检索更有针对性
        k:             返回知识片段数

    Returns:
        KnowledgeResult

    TODO 实现步骤：
      1. 拼接 query = question + " " + diet_summary
      2. 对 Chroma collection="nutrition_knowledge" 做向量检索
      3. 返回 top-k 文档片段及来源标题
    """
    # TODO
    return KnowledgeResult(docs=[], source_titles=[])

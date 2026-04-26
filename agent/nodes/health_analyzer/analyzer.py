"""
health_analyzer 主节点
========================
流程：
  1. asyncio.gather 并行触发三路检索
     路1 diet_history_retriever  → 历史饮食语义召回
     路2 knowledge_retriever     → 营养知识库语义召回
     路3 nutrition_sql_retriever → 结构化SQL聚合查询
  2. merger.merge() 将三路结果拼成统一上下文
  3. 注入现有 LLM Prompt 生成分析报告（原 health_anazlizer 逻辑保留不动）
"""

import asyncio

from langgraph.runtime import Runtime
from loguru import logger

from agent.context import DataAgentContext
from agent.llm import llm
from agent.state import AgentState
from agent.nodes.health_analyzer.merger import merge
from agent.nodes.health_analyzer.retrievers import (
    diet_history_retriever,
    knowledge_retriever,
    nutrition_sql_retriever,
)


async def run(state: AgentState, runtime: Runtime[DataAgentContext]) -> AgentState:
    user_id = state["user_id"]
    question = state["question"]
    db_session = None  # TODO: 从 runtime.context 取 AsyncSession

    logger.info(f"[health_analyzer] 开始三路并行召回 user={user_id}")

    # ── Step 1：三路并行检索 ──────────────────────────────────────────
    sql_result, diet_result, _ = await asyncio.gather(
        nutrition_sql_retriever.retrieve(user_id=user_id, days=7, db_session=db_session),
        diet_history_retriever.retrieve(user_id=user_id, question=question),
        asyncio.sleep(0),   # 占位，等 sql_result 出来再做知识检索（需要 summary_text）
    )

    # 路2 依赖路3 的 summary_text 做更精准的知识召回，单独等一步
    knowledge_result = await knowledge_retriever.retrieve(
        question=question,
        diet_summary=sql_result.summary_text,
    )

    logger.info(
        f"[health_analyzer] 召回完成 "
        f"diet={len(diet_result.records)}条 "
        f"knowledge={len(knowledge_result.docs)}条"
    )

    # ── Step 2：合并三路结果 ──────────────────────────────────────────
    merged_context = merge(sql_result, diet_result, knowledge_result)

    # ── Step 3：LLM 生成健康分析（原 health_anazlizer 逻辑，未改动）────
    try:
        health_information = await runtime.context["food_log_repository"].get_health_information(user_id)

        prompt = """
你是一个营养助手，根据用户的问题，分析用户健康信息，并给出建议。不要给出任何负面评价，客观给出分析结果，并给出建议，一定要结合过去一周的食品记录来关联分析。输出类型为markdown格式，尽量简洁
用户的问题：{question}
用户健康信息：{health_information}
三路召回上下文：
{merged_context}
分析结果：
""".format(
            question=question,
            health_information=health_information,
            merged_context=merged_context,
        )

        response = await llm.ainvoke(prompt)
        logger.info(f"[health_analyzer] LLM 生成完成")
        return {"response": response.content}

    except Exception as e:
        logger.error(f"[health_analyzer] 分析失败: {e}")
        return {"response": f"分析失败：{e}"}

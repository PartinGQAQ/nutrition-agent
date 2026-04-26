"""
meal_planner 主节点
=====================
流程：
  1. asyncio.gather 并行触发三路检索
     路1 preference_retriever → 用户饮食偏好语义召回
     路2 recipe_retriever     → 食谱知识库语义召回（依赖路3的缺口，串行）
     路3 goal_retriever       → 营养目标与缺口 DB 查询
  2. merger.merge() 拼装上下文
  3. LLM 生成 N 天个性化饮食计划
"""

import asyncio

from langgraph.runtime import Runtime
from loguru import logger

from agent.context import DataAgentContext
from agent.llm import llm
from agent.state import AgentState
from agent.nodes.meal_planner.merger import merge
from agent.nodes.meal_planner.retrievers import (
    preference_retriever,
    recipe_retriever,
    goal_retriever,
)

DEFAULT_PLAN_DAYS = 7


async def run(state: AgentState, runtime: Runtime[DataAgentContext]) -> AgentState:
    user_id = state["user_id"]
    question = state["question"]
    db_session = None  # TODO: 从 runtime.context 取 AsyncSession

    logger.info(f"[meal_planner] 开始三路并行召回 user={user_id}")

    # ── Step 1：路1 & 路3 并行（路2 依赖路3缺口，后串行）────────────
    goal_result, preference_result = await asyncio.gather(
        goal_retriever.retrieve(user_id=user_id, plan_days=DEFAULT_PLAN_DAYS, db_session=db_session),
        preference_retriever.retrieve(user_id=user_id),
    )

    # 路2 拿到缺口摘要后再召回，食谱方向更精准
    recipe_result = await recipe_retriever.retrieve(
        nutrition_gap_summary=goal_result.gap_summary,
        preference_summary=preference_result.summary_text,
        days=DEFAULT_PLAN_DAYS,
    )

    logger.info(
        f"[meal_planner] 召回完成 "
        f"recipes={len(recipe_result.recipes)}个 "
        f"liked_foods={len(preference_result.liked_foods)}个"
    )

    # ── Step 2：合并三路结果 ──────────────────────────────────────────
    merged_context = merge(goal_result, preference_result, recipe_result)

    # ── Step 3：LLM 生成饮食计划 ──────────────────────────────────────
    try:
        prompt = """
你是一个专业营养师，根据用户需求和以下三路召回的上下文，生成一份{days}天的个性化饮食计划。

要求：
1. 每天包含早餐、午餐、晚餐，可含加餐
2. 热量和营养素尽量满足目标，弥补缺口
3. 优先使用用户偏好食物，避免强迫用户吃不喜欢的东西
4. 优先从推荐食谱池中选取，食谱不足时可自行补充
5. 输出格式为 Markdown，每天一个标题，简洁清晰

用户需求：{question}

{merged_context}

饮食计划：
""".format(
            days=DEFAULT_PLAN_DAYS,
            question=question,
            merged_context=merged_context,
        )

        response = await llm.ainvoke(prompt)
        logger.info(f"[meal_planner] LLM 生成完成")
        return {"response": response.content}

    except Exception as e:
        logger.error(f"[meal_planner] 生成失败: {e}")
        return {"response": f"饮食计划生成失败：{e}"}

from __future__ import annotations

import asyncio
import logging

from langgraph.graph import END, StateGraph

from agent.state import AgentState
from agent.nodes import (
    food_logger,
    health_anazlizer,
    history_query,
    intent_router,
    meal_planner,
)
from client.db_client import db_client
from db.repositories import FoodLogRepository

_compiled_graph = None


def _route_intent(state: AgentState) -> str:
    """将 intent_router 产出（或历史别名）映射到条件边 key。"""
    raw = (state.intent or "other").strip().lower()
    aliases = {
        "food_logger": "log_food",
        "log_food": "log_food",
        "history_query": "query_history",
        "query_history": "query_history",
        "meal_planner": "plan_meal",
        "plan_meal": "plan_meal",
        "analyze_health": "analyze_health",
        "health": "analyze_health",
        "other": "other",
    }
    mapped = aliases.get(raw, raw)
    allowed = frozenset(
        {"log_food", "query_history", "plan_meal", "analyze_health", "other"}
    )
    return mapped if mapped in allowed else "other"


def _build_state_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("intent_router", intent_router.run)
    graph.add_node("food_logger", food_logger.run)
    graph.add_node("history_query", history_query.run)
    graph.add_node("meal_planner", meal_planner.run)
    graph.add_node("health_anazlizer", health_anazlizer.run)
    graph.set_entry_point("intent_router")

    graph.add_conditional_edges(
        "intent_router",
        _route_intent,
        {
            "log_food": "food_logger",
            "query_history": "history_query",
            "plan_meal": "meal_planner",
            "analyze_health": "health_anazlizer",
            "other": END,
        },
    )

    for node in ("food_logger", "history_query", "meal_planner", "health_anazlizer"):
        graph.add_edge(node, END)

    return graph


def get_compiled_graph():
    """编译后的图单例，避免每个 HTTP 请求重复 compile。"""
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = _build_state_graph().compile()
    return _compiled_graph

def create_short_term_memory(db_path: str = "checkpoints.db") -> AsyncSqliteSaver:
    """
    创建短期记忆（会话级别 Checkpointer）。
    
    Args:
        db_path: SQLite 文件路径。生产环境换成 AsyncPostgresSaver。
    
    Returns:
        AsyncSqliteSaver 实例，传给 graph.compile() 使用。
    
    用法：
        async with create_short_term_memory() as memory:
            graph = builder.compile(checkpointer=memory)
    """
    return AsyncSqliteSaver.from_conn_string(db_path)


def build_graph():
    """兼容旧调用名，等价于 get_compiled_graph。"""
    return get_compiled_graph()


if __name__ == "__main__":
    compiled = build_graph()

    async def _smoke_test() -> None:
        await db_client.init_db()
        async with db_client.session_scope() as session:
            # ainvoke 第一个位置参数是 input，不能写 state=
            result = await compiled.ainvoke(
                AgentState(user_id="1", session_id="1", question="请帮我分析我的身体报告"),
                context={
                    "food_log_repository": FoodLogRepository(session),
                },
            )
            logging.info(f"Smoke Test Result: {result}")

    asyncio.run(_smoke_test())
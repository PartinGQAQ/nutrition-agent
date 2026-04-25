from __future__ import annotations

import asyncio
import logging

from langgraph.graph import END, StateGraph

from agent.state import AgentState
from agent.nodes import (
    food_db_writer,
    food_logger,
    health_anazlizer,
    history_query,
    intent_router,
    meal_planner,
    memory_load,
)
from client.db_client import db_client
from db.repositories import FoodLogRepository

_compiled_graph = None


def _route_after_food_logger(state) -> str:
    """
    food_logger 完成后的路由：
      - slot_list 存在且 status == "ok" → 进 food_db_writer 落库
      - 其他情况（图片模糊、提取失败、reply 已含错误） → 直接结束
    """
    slot_list = state.get("slot_list")
    if slot_list and getattr(slot_list, "status", None) == "ok" and slot_list.items:
        return "write"
    return "end"


def _build_state_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("intent_router", intent_router.run)
    graph.add_node("food_logger", food_logger.run)
    graph.add_node("food_db_writer", food_db_writer.run)
    graph.add_node("history_query", history_query.run)
    graph.add_node("meal_planner", meal_planner.run)
    graph.add_node("health_anazlizer", health_anazlizer.run)
    graph.add_node("memory_load", memory_load.run)
    graph.set_entry_point("memory_load")

    graph.add_edge("memory_load", "intent_router")
    graph.add_conditional_edges(
        "intent_router",
        lambda state: (state["intent"] or "other").strip(),
        {
            "food_logger": "food_logger",
            "history_query": "history_query",
            "meal_planner": "meal_planner",
            "health_anazlizer": "health_anazlizer",
            "other": END,
        },
    )

    # food_logger 提取完 slot_list 后，交给 food_db_writer 落库
    graph.add_conditional_edges(
        "food_logger",
        _route_after_food_logger,
        {
            "write": "food_db_writer",
            "end": END,             # 图片模糊 / 提取失败时直接结束
        },
    )
    graph.add_edge("food_db_writer", END)

    for node in ("history_query", "meal_planner", "health_anazlizer"):
        graph.add_edge(node, END)

    return graph


def get_compiled_graph(checkpointer=None):
    """编译后的图单例；传入 checkpointer 时重新编译（仅首次）。"""
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = _build_state_graph().compile(checkpointer=checkpointer)
    return _compiled_graph



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
                AgentState(user_id="1", session_id="1", question="今天吃了什么，根据我的图片记录食物信息"),
                context={
                    "food_log_repository": FoodLogRepository(session),
                },
            )
            logging.info(f"Smoke Test Result: {result}")

    asyncio.run(_smoke_test())
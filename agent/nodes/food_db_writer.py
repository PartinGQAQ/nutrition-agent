"""
food_db_writer — 饮食记录写入节点
===================================
职责：
  1. 从 state.slot_list 取出 food_logger 提取的多食物结果
  2. 逐条查 food 表做名称标准化（模糊匹配 / USDA API）
  3. 生成 FoodLog 对象并批量写入 DB
  4. 生成语义化文本（供向量库检索）并写入 Chroma/Qdrant
  5. 组织自然语言回复写入 state.reply

上游依赖：food_logger（state.slot_list 必须已被填充）
"""


from datetime import datetime, timezone

from langgraph.runtime import Runtime
from loguru import logger

from agent.context import DataAgentContext
from agent.state import AgentState
from client.embedding_client import embedding_client
from db.models import FoodLog
from memory.slot import FoodSlot, FoodSlotList
from db.repositories import FoodLogRepository
from db.repositories import QdrantVectorStoreRepository


async def run(state: AgentState, runtime: Runtime[DataAgentContext]) -> AgentState:
    slot_list: FoodSlotList | None = state.get("slot_list")
    food_log_repository: FoodLogRepository = runtime.context["food_log_repository"]
    vector_store_repository: QdrantVectorStoreRepository = runtime.context["vector_store_repository"]
    
    # ── 防御：上游没有成功提取时直接返回错误 ──────────────────────────
    if slot_list is None or slot_list.status != "ok" or not slot_list.items:
        reason = slot_list.message if slot_list else "slot_list 为空"
        return {"reply": f"无法记录饮食：{reason}", "error": reason}

    # ── 1. 逐条标准化 & 写 DB ─────────────────────────────────────────
    saved_logs = []
    for slot in slot_list.items:
        # TODO: 查 food 表 / USDA API，把 slot.food_name 映射到规范 food_id
        food_id = await _lookup_food_id(slot, food_log_repository)
        if food_id is None:
            return {"reply": f"无法记录饮食：{slot.food_name} 未找到", "error": f"无法记录饮食：{slot.food_name} 未找到"}

        food_log = _build_food_log(slot, food_id, state["user_id"], state["dialog_timestamp"], food_log_repository)
        saved_logs.append(food_log)
        logger.info(f"[food_db_writer] saved: {slot.food_name} {slot.food_amount}{slot.food_unit}")
    
    # 批量写入DB
    food_logs = await food_log_repository.create_food_logs(saved_logs)
    ids = [food_log.id for food_log in food_logs]


    return {"reply": reply, "ids": ids}


# ── 辅助函数（占位，逻辑自己填） ──────────────────────────────────────

async def _lookup_food_id(slot: FoodSlot, food_log_repository: FoodLogRepository) -> int | None:
    """
    按 food_name 模糊匹配 food 表，返回 food_id。
    找不到时返回 None（后续可以走 USDA API 兜底）。

    建议策略：
      1. 先查本地 food 表（LIKE / pg_trgm）
      2. 命中率低时调 tools/usda_api.py search_food()
      3. 都没有时插入一条新 Food 记录并返回新 id
    """
    foods = await food_log_repository.get_food_by_name_like(slot.food_name)
    if foods:
        return foods[0].id
    else:
        return None


def _build_food_log(
    slot: FoodSlot,
    food_id: int,
    user_id: str,
    dialog_timestamp: str | None,
) -> FoodLog:
    """把 FoodSlot 转成 FoodLog ORM 对象。confidence 对应 slot.uncertainty。"""
    return FoodLog(
        user_id=user_id,
        food_id=food_id,
        food_name=slot.food_name or "",
        amount_g=float(slot.food_amount or 0),
        meal_type=slot.meal_type or "snack",
        calories=float(slot.food_calories or 0),
        protein_g=float(slot.food_protein or 0),
        fat_g=float(slot.food_fat or 0),
        carb_g=float(slot.food_carb or 0),
        logged_at=datetime.now(timezone.utc),
        confidence=slot.uncertainty or "low",
        dialog_timestamp=dialog_timestamp or "",
    )






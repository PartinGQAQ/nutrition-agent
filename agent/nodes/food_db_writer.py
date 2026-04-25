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


from langgraph.runtime import Runtime
from loguru import logger

from agent.context import DataAgentContext
from agent.state import AgentState
from memory.slot import FoodSlot, FoodSlotList


async def run(state: AgentState, runtime: Runtime[DataAgentContext]) -> AgentState:
    slot_list: FoodSlotList | None = state.get("slot_list")

    # ── 防御：上游没有成功提取时直接返回错误 ──────────────────────────
    if slot_list is None or slot_list.status != "ok" or not slot_list.items:
        reason = slot_list.message if slot_list else "slot_list 为空"
        return {"reply": f"无法记录饮食：{reason}", "error": reason}

    # ── 1. 逐条标准化 & 写 DB ─────────────────────────────────────────
    saved_logs = []
    for slot in slot_list.items:
        # TODO: 查 food 表 / USDA API，把 slot.food_name 映射到规范 food_id
        food_id = _lookup_food_id(slot)

        # TODO: 调用 crud.create_food_log 写入 DB
        food_log = _build_food_log(slot, food_id, state["user_id"], state["dialog_timestamp"])
        # await runtime.context["food_log_repository"].create(food_log)
        saved_logs.append(food_log)
        logger.info(f"[food_db_writer] saved: {slot.food_name} {slot.food_amount}{slot.food_unit}")

    # ── 2. 语义化文本 → 向量库 ────────────────────────────────────────
    for slot in slot_list.items:
        semantic_text = _build_semantic_text(slot, state["user_id"], state["dialog_timestamp"])
        # TODO: embedding(semantic_text) → vector_store.upsert(...)
        logger.debug(f"[food_db_writer] semantic: {semantic_text}")

    # ── 3. 生成自然语言回复 ────────────────────────────────────────────
    reply = _build_reply(slot_list, notes=slot_list.notes)

    return {"reply": reply}


# ── 辅助函数（占位，逻辑自己填） ──────────────────────────────────────

def _lookup_food_id(slot: FoodSlot) -> int | None:
    """
    按 food_name 模糊匹配 food 表，返回 food_id。
    找不到时返回 None（后续可以走 USDA API 兜底）。

    建议策略：
      1. 先查本地 food 表（LIKE / pg_trgm）
      2. 命中率低时调 tools/usda_api.py search_food()
      3. 都没有时插入一条新 Food 记录并返回新 id
    """
    # TODO
    return None


def _build_food_log(slot: FoodSlot, food_id: int | None, user_id: str, dialog_timestamp: str | None):
    """
    把 FoodSlot 转成 FoodLog ORM 对象。
    注意：FoodLog.confidence 字段对应 slot.uncertainty。
    """
    # TODO: 返回 FoodLog(...)
    return {
        "user_id": user_id,
        "food_id": food_id,
        "food_name": slot.food_name,
        "amount_g": slot.food_amount,
        "meal_type": slot.meal_type,
        "calories": slot.food_calories,
        "protein_g": slot.food_protein,
        "fat_g": slot.food_fat,
        "carb_g": slot.food_carb,
        "confidence": slot.uncertainty,
        "dialog_timestamp": dialog_timestamp,
    }


def _build_semantic_text(slot: FoodSlot, user_id: str, dialog_timestamp: str | None) -> str:
    """
    生成便于向量检索的语义化文本。
    示例："用户(user_123)在2024-01-01T12:00:00午餐吃了100g米饭，约350kcal，
          蛋白质7g，脂肪1g，碳水78g。"

    建议：
      - 包含 user_id（检索时按用户过滤）
      - 包含 dialog_timestamp（支持时间范围查询）
      - 包含营养摘要（支持"上周高热量食物"类语义查询）
    """
    ts = dialog_timestamp or "未知时间"
    return (
        f"用户({user_id})在{ts}{slot.meal_type or ''}吃了"
        f"{slot.food_amount}{slot.food_unit} {slot.food_name}，"
        f"约{slot.food_calories or '未知'}kcal，"
        f"蛋白质{slot.food_protein or '?'}g，"
        f"脂肪{slot.food_fat or '?'}g，"
        f"碳水{slot.food_carb or '?'}g。"
    )


def _build_reply(slot_list: FoodSlotList, notes: str) -> str:
    """
    把多条记录拼成自然语言回复。
    TODO: 可以换成 LLM 生成更自然的文案。
    """
    lines = []
    total_cal = 0.0
    for slot in slot_list.items:
        cal = slot.food_calories or 0
        total_cal += cal
        lines.append(
            f"• {slot.food_name} {slot.food_amount}{slot.food_unit}"
            f"（{slot.meal_type}，约{cal:.0f} kcal）"
        )
    summary = "\n".join(lines)
    result = f"已记录以下饮食：\n{summary}\n合计约 {total_cal:.0f} kcal"
    if notes:
        result += f"\n备注：{notes}"
    return result

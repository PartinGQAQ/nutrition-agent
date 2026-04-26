from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from agent.llm import llm
from agent.prompts import food_logger_prompt
from agent.state import AgentState
from agent.context import DataAgentContext
from langgraph.runtime import Runtime

from db.repositories import QdrantVectorStoreRepository
from client.embedding_client import embedding_client
from loguru import logger
from memory.slot import FoodSlot, FoodSlotList

async def run(state: AgentState, runtime: Runtime[DataAgentContext]) -> AgentState:
    """将食物记录向量化并写入向量库"""
    vector_store_repository: QdrantVectorStoreRepository = runtime.context["vector_store_repository"]
    slot_list = state["slot_list"]
    user_id = state["user_id"]
    ids = state["ids"]
    
    food_log_vectors = []
    payloads = []
    # ── 2. 语义化文本 → 向量库 ────────────────────────────────────────
    for index, slot in enumerate(slot_list.items):
        # 生成语义text
        semantic_text = await _build_semantic_text(slot, user_id, state["dialog_timestamp"])
        # 向量化
        embedding_text = await embedding_client.embed_documents([semantic_text])
        # 存入数组
        food_log_vectors.append(embedding_text[0])
        # 转为dict 作为payload存入向量库
        payload = slot.model_dump()
        payload["id"] = ids[index]
        logger.debug(f"[food_vector_writer] semantic: {semantic_text}")
        payloads.append(payload)
        
    await vector_store_repository.upsert(ids,food_log_vectors, payloads)

    # ── 3. 生成自然语言回复 ────────────────────────────────────────────
    reply = _build_reply(slot_list, notes=slot_list.notes)
    
    
    return {"reply": reply}

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
    # LLM 生成自然文案
    summary = "\n".join(lines)
    result = f"已记录以下饮食：\n{summary}\n合计约 {total_cal:.0f} kcal"
    if notes:
        result += f"\n备注：{notes}"
    return result

async def _build_semantic_text(slot: FoodSlot, user_id: str, dialog_timestamp: str | None) -> str:
    """
    生成便于向量检索的语义化文本。
    示例："用户(user_123)在2024-01-01T12:00:00午餐吃了100g米饭，约350kcal，
          蛋白质7g，脂肪1g，碳水78g。"

    建议：
      - 包含 user_id（检索时按用户过滤）
      - 包含 dialog_timestamp（支持时间范围查询）
      - 包含营养摘要（支持"上周高热量食物"类语义查询）
    """
    
    prompt = PromptTemplate.from_template(
        template = food_logger_prompt.semantic_text_prompt,
        input_variables = ["user_id", "dialog_timestamp"]
    )
    
    chain = prompt | llm | StrOutputParser()
    
    result = await chain.ainvoke({"user_id": user_id, "dialog_timestamp": dialog_timestamp})
    
    return result
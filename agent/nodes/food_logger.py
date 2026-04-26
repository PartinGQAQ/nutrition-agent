import json
import re
from datetime import datetime, timezone

from langchain_core.prompts import ChatPromptTemplate
from loguru import logger
from langgraph.runtime import Runtime
from langchain_openai import ChatOpenAI

from agent.context import DataAgentContext
from agent.prompts.food_logger_prompt import extract_food_info_prompt
from agent.state import AgentState
from memory.slot import FoodSlotList
from vision.food_recognizer import image_bytes_to_base64, preprocess_image


def _parse_llm_json(raw: str) -> dict:
    """从 LLM 文本中取出 JSON 对象（兼容首尾 Markdown 代码块）。"""
    text = (raw or "").strip()
    if text.startswith("```"):
        m = re.search(r"\{[\s\S]*\}", text)
        if m:
            text = m.group(0)
    return json.loads(text)


async def run(state: AgentState, runtime: Runtime[DataAgentContext]) -> AgentState:
    """提取食物信息并写入数据库"""
    logger.info("Extracting food information...")
    question = state["question"]
    image_bytes = state["image"]
    llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0)

    compressed = preprocess_image(image_bytes)
    b64_image = image_bytes_to_base64(compressed)

    dialog_timestamp = state.get("dialog_timestamp") or datetime.now(timezone.utc).isoformat()

    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个饮食信息提取助手，严格按要求输出 JSON。"),
        (
            "human",
            [
                {"type": "text", "text": extract_food_info_prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "data:image/jpeg;base64,{b64_image}",
                        "detail": "auto",
                    },
                },
            ],
        ),
    ])

    message = prompt.format_messages(
        b64_image=b64_image,
        question=question,
        multimodal_info="用户上传了一张食物图片",
        dialog_timestamp=dialog_timestamp,
    )

    response = await llm.ainvoke(message)
    logger.info(f"Food Logger Response: {response.content}")

    try:
        payload = _parse_llm_json(response.content)
        # model 可以直接json(对象)! 转成model，不需要model_validate_json
        food_slot_list = FoodSlotList.model_validate(payload)
    except Exception as e:
        logger.error(f"Failed to parse LLM response: {e}")
        return {"error": f"食物识别解析失败: {e}"}

    logger.info(f"Food Logger Slot List: {food_slot_list}")
    return {
        "slot_list": food_slot_list,
        "dialog_timestamp": dialog_timestamp,
        "reply": f"已识别 {len(food_slot_list.items)} 种食物，正在记录...",
    }

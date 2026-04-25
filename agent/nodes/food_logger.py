from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from agent.state import AgentState
from agent.context import DataAgentContext
from langgraph.runtime import Runtime
from loguru import logger

from langchain_openai import ChatOpenAI
from agent.prompts.food_logger_prompt import extract_food_info_prompt

from db.models import FoodLog
from memory.slot import FoodSlot
from vision.food_recognizer import image_bytes_to_base64, preprocess_image


async def run(state: AgentState, runtime: Runtime[DataAgentContext]) -> AgentState:
    """提取食物信息并写入数据库"""
    # TODO: 多模态提取食物信息
    logger.info("Extracting food information...")
    question = state["question"]
    image_bytes = state["image"]
    llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0, )
    
    compressed = preprocess_image(image_bytes)
    b64_image = image_bytes_to_base64(compressed)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个饮食信息提取助手，严格按要求输出 JSON。"),
        (
            "human",
            [
                {
                    "type": "text",
                    "text": extract_food_info_prompt,
                },
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
        dialog_timestamp=state["dialog_timestamp"],
    )
    
    response = await llm.ainvoke(message)
    logger.info(f"Food Logger Response: {response.content}")
    
    # TODO: 提取食物信息
    slot = FoodSlot.model_validate_json(response.content)
    if slot.missing_required():
        return {"error": "缺少必要信息"}

    food_log: list[FoodLog] = []
    # TODO: 从food表中召回规范的食物id或信息
    
    
    # TODO: 生成食物log
    
    
    # TODO: 生成语义化食物信息
    
    prompt = """
"""
    
    # TODO：存语义化食物信息到向量库
    
    
    return {"reply": "（占位）记录食物功能开发中"}

def generate_food_log(slot: FoodSlot) -> FoodLog:
    return FoodLog(
        
    )
from agent.state import AgentState
from agent.context import DataAgentContext
from langgraph.runtime import Runtime
from loguru import logger

from langchain_openai import ChatOpenAI
def run(state: AgentState, runtime: Runtime[DataAgentContext]) -> AgentState:
    """提取食物信息并写入数据库"""
    # TODO: 多模态提取食物信息
    
    logger.info(f"Food Logger State: {state}")
    llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0, )
    
    
    
    # TODO: 提取食物信息

    
    # TODO: 生成语义化食物信息
    
    prompt = """
"""
    
    # TODO：存语义化食物信息到向量库
    
    
    return {"reply": "（占位）记录食物功能开发中"}
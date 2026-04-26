from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from agent.context import DataAgentContext
from agent.llm import llm
from agent.state import AgentState
from loguru import logger
from memory.short_term import make_thread_id


async def run(state: AgentState, runtime: Runtime[DataAgentContext]) -> AgentState:
    question = state["question"]
    config = {"configurable": {"thread_id": make_thread_id(state['user_id'], state['session_id'])}}
    history_info = "\n".join(
        [str(m) for m in (state["messages"][-6:] if state["messages"] else [])]
    ) or "无"
    prompt = """
你是一个营养助手，根据用户的问题识别意图。根据用户历史信息，给出最合适的意图。
用户问题：{question}
用户历史信息：{history_info}

只输出下面三个字符串之一，不要输出其它任何字符（不要 markdown、不要解释）：
- food_logger
- meal_planner
- other

含义：
  food_logger  = 用户想记录自己吃了什么（含上传图片、描述食物、补录餐食等）
  meal_planner = 用户想获取饮食计划、食谱推荐、下一餐吃什么建议等
  other        = 其他问题（健康分析、历史查询等功能请使用页面按钮操作）
"""
    tmpl = PromptTemplate(template=prompt, input_variables=["question", "history_info"])
    chain = tmpl | llm | StrOutputParser()
    response = (
        await chain.ainvoke(
            {"question": question, "history_info": history_info},
            config=config,
        )
    ).strip()
    logger.info(f"Intent: {response}")
    return {"intent": response}

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from agent.context import DataAgentContext
from agent.llm import llm
from agent.state import AgentState
from loguru import logger


async def run(state: AgentState, runtime: Runtime[DataAgentContext]) -> AgentState:
    question = state.question
    config = {"configurable": {"thread_id": state.user_id}}
    prompt = """
你是一个营养助手，根据用户的问题识别意图。根据用户历史信息，给出最合适的意图。
用户问题：{question}
用户历史信息：{history_info}

只输出下面五个字符串之一，不要输出其它任何字符（不要 markdown、不要解释）：
- log_food
- query_history
- plan_meal
- analyze_health
- other

含义：log_food=记录食物；query_history=查历史饮食；plan_meal=生成饮食计划；analyze_health=分析健康；other=其它。
"""
    # 读用户历史信息，嵌入到state中，用于后续的分析:
    
    tmpl = PromptTemplate(template=prompt, input_variables=["question"])
    chain = tmpl | llm | StrOutputParser()
    response = (await chain.ainvoke({"question": question}, config=config)).strip()
    logger.info(f"Intent: {response}")
    return {"intent": response}

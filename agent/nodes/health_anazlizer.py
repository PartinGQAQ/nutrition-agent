from langgraph.runtime import Runtime

from agent.context import DataAgentContext
from agent.llm import llm
from agent.state import AgentState
from loguru import logger

async def run(state: AgentState, runtime: Runtime[DataAgentContext]) -> AgentState:
    """分析健康信息并写入数据库"""
    user_id = state.user_id
    repo = runtime.context["food_log_repository"]

    try:
        health_information = await repo.get_health_information(user_id)
        food_logs = await repo.get_food_logs(user_id)

        prompt = """
你是一个营养助手，根据用户的问题，分析用户健康信息，并给出建议。不要给出任何负面评价，客观给出分析结果，并给出建议，一定要结合过去一周的食品记录来关联分析。输出类型为markdown格式，尽量简洁
用户的问题：{question}
用户健康信息：{health_information}
用户饮食记录：{food_logs}
分析结果：
"""
        prompt = prompt.format(
            question=state.question,
            health_information=health_information,
            food_logs=food_logs,
        )

        response = await llm.ainvoke(prompt)
        logger.info(f"Health Analyzer Response: {response.content}")
        return {"response": response.content}

    except Exception as e:
        return {"response": f"分析失败：{e}"}

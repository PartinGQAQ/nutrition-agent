from agent.state import AgentState
from agent.context import DataAgentContext
from langgraph.runtime import Runtime


def run(state: AgentState, runtime: Runtime[DataAgentContext]) -> AgentState:
    """生成个性化饮食计划"""
    return {"reply": "（占位）饮食计划功能开发中"}

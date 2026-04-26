from agent.state import AgentState
from agent.context import DataAgentContext
from langgraph.runtime import Runtime


def run(state: AgentState, runtime: Runtime[DataAgentContext]) -> AgentState:
    """查询历史饮食记录并组织回复"""
    return {"reply": "（占位）历史查询功能开发中"}

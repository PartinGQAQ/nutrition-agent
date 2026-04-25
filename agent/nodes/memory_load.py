from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from agent.context import DataAgentContext
from agent.llm import llm
from agent.state import AgentState
from loguru import logger

from memory.short_term import trim_conversation


async def run(state: AgentState, runtime: Runtime[DataAgentContext]) -> AgentState:
    # 读用户历史信息，嵌入到state中，用于后续的分析:
    user_id = state.user_id
    
    messages = state.messages
    
    trimmed = trim_conversation(messages, max_tokens=4000, llm=llm)
    
    return state
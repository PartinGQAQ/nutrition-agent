from typing import Annotated, Any

from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
from langgraph.graph import MessagesState
from langchain_core.messages import trim_messages, BaseMessage


class AgentState(MessagesState):
    user_id: str
    session_id: str
    question: str
    keyword: str 
    messages: Annotated[list, add_messages] = Field(default_factory=list)
    intent: str | None = None
    food_context: dict[str, Any] = Field(default_factory=dict)
    retrieved_docs: list[str] = Field(default_factory=list)
    # 以下字段必须在模型上声明，否则节点 return 的键会被 Pydantic 丢弃，ainvoke 结果里看不到
    response: str | None = None
    reply: str | None = None
    error: str | None = None

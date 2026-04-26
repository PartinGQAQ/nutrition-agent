from typing import Annotated, Any

from langgraph.graph import MessagesState
from langgraph.graph.message import add_messages
from pydantic import Field

from memory.slot import FoodSlot, FoodSlotList

class AgentState(MessagesState):
    user_id: str
    session_id: str
    question: str
    keyword: str = ""
    slot: FoodSlot | None = None
    slot_list: FoodSlotList | None = None   # food_logger 提取的多食物结果，传给 food_db_writer
    image: bytes | None = None
    messages: Annotated[list, add_messages] = Field(default_factory=list)
    intent: str | None = None
    food_context: dict[str, Any] = Field(default_factory=dict)
    retrieved_docs: list[str] = Field(default_factory=list)
    dialog_timestamp: str | None = None
    ids: list[int] = Field(default_factory=list)
    # 以下字段必须在模型上声明，否则节点 return 的键会被 Pydantic 丢弃，ainvoke 结果里看不到
    response: str | None = None
    reply: str | None = None
    error: str | None = None

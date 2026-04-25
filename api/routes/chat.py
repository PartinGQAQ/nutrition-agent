from typing import Any, Optional, cast
import uuid

from fastapi import APIRouter, Depends, File, Request, UploadFile
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from agent.context import DataAgentContext
from agent.graph import get_compiled_graph
from agent.state import AgentState
from client.db_client import db_client
from db.repositories import FoodLogRepository
from memory.short_term import make_thread_id

router = APIRouter()


class ChatRequest(BaseModel):
    user_id: str
    session_id: str
    message: str


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    intent: Optional[str] = None


def _final_state_to_dict(final: Any) -> dict[str, Any]:
    if hasattr(final, "model_dump"):
        return cast(dict[str, Any], final.model_dump())
    if isinstance(final, dict):
        return final
    return dict(final)


@router.post("/message", response_model=ChatResponse)
async def send_message(
    req: ChatRequest,
    session: AsyncSession = Depends(db_client.get_session),
):
    """发送文字消息，返回 agent 回复"""
    state = AgentState(
        user_id=req.user_id,
        session_id=req.session_id,
        question=req.message,
    )
    context: DataAgentContext = {
        "food_log_repository": FoodLogRepository(session),
    }

    # 启动graph
    graph = get_compiled_graph()
    config = {"configurable": {"thread_id": make_thread_id(req.user_id, req.session_id)}}
    final = await graph.ainvoke(state, config=config, context=context)
    data = _final_state_to_dict(final)

    if data.get("error"):
        reply = str(data["error"])
    else:
        reply = (data.get("response") or data.get("reply") or "").strip() or "暂无回复"

    return ChatResponse(
        session_id=req.session_id,
        reply=reply,
        intent=data.get("intent"),
    )


@router.post("/image", response_model=ChatResponse)
async def send_image(
    request: Request,
    user_id: str,
    session_id: str,
    image: UploadFile = File(...),
    message: Optional[str] = None,
    session: AsyncSession = Depends(db_client.get_session),
):
    """上传食物图片，agent 识别并记录"""
    session_id = session_id or str(uuid.uuid4())
    image_bytes = await image.read()
    state = AgentState(
        user_id=user_id,
        session_id=session_id,
        question=message or "",
        image=image_bytes,
    )
    context: DataAgentContext = {
        "food_log_repository": FoodLogRepository(session),
    }
    
    # 注入的memoryserver（）sqlite版本
    checkpointer = getattr(request.app.state, "short_memory", None)
    
    graph = get_compiled_graph(checkpointer=checkpointer)
    config = {"configurable": {"thread_id": make_thread_id(user_id, session_id)}}
    final = await graph.ainvoke(state, config=config, context=context)
    data = _final_state_to_dict(final)

    if data.get("error"):
        reply = str(data["error"])
    else:
        reply = (data.get("response") or data.get("reply") or "").strip() or "暂无回复"

    return ChatResponse(
        session_id=session_id,
        reply=reply,
        intent=data.get("intent"),
    )


@router.get("/history/{session_id}")
async def get_session_history(session_id: str):
    """获取指定会话的对话历史"""
    pass


@router.delete("/history/{session_id}")
async def clear_session_history(session_id: str):
    """清空指定会话的对话历史"""
    pass

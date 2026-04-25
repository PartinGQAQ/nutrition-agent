"""
短期记忆模块 — 基于 LangGraph Checkpointer
===============================================
职责：管理单次会话内的对话上下文。
生命周期：会话级别，同一个 thread_id 下自动恢复。
存储位置：SQLite（开发） / PostgreSQL（生产）
"""
 
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.graph import MessagesState
from langchain_core.messages import trim_messages, BaseMessage
from langchain_openai import ChatOpenAI
from typing import Annotated
import operator

 
# ─────────────────────────────────────────────
# 2. 短期记忆工厂
#    返回一个 AsyncSqliteSaver 实例，作为
#    graph.compile(checkpointer=memory) 的参数。
#    LangGraph 在每个节点执行后自动保存 State 快照，
#    下次用同一个 thread_id 进来时自动恢复。
# ─────────────────────────────────────────────
def create_short_term_memory(db_path: str = "checkpoints.db") -> AsyncSqliteSaver:
    """
    创建短期记忆（会话级别 Checkpointer）。
    
    Args:
        db_path: SQLite 文件路径。生产环境换成 AsyncPostgresSaver。
    
    Returns:
        AsyncSqliteSaver 实例，传给 graph.compile() 使用。
    
    用法：
        async with create_short_term_memory() as memory:
            graph = builder.compile(checkpointer=memory)
    """
    return AsyncSqliteSaver.from_conn_string(db_path)
 
 
# ─────────────────────────────────────────────
# 3. 消息裁剪工具
#    对话越来越长时，messages 会撑爆 context window。
#    每次调用 LLM 前先裁剪，只保留最近 N 个 token。
# ─────────────────────────────────────────────
def trim_conversation(
    messages: list[BaseMessage],
    max_tokens: int = 4000,
    llm: ChatOpenAI | None = None,
) -> list[BaseMessage]:
    """
    裁剪对话历史，防止 context window 溢出。
    
    策略 "last"：保留最新的消息，从尾部往前数到 max_tokens 为止。
    这样可以保留最近的上下文，丢弃很久之前的对话。
    
    Args:
        messages:   完整消息列表（来自 State）
        max_tokens: 保留的最大 token 数（默认 4000）
        llm:        用于计算 token 数的模型实例，None 则用字符估算
    
    Returns:
        裁剪后的消息列表，直接传给 LLM
    
    示例：
        trimmed = trim_conversation(state["messages"])
        response = llm.invoke(trimmed)
    """
    return trim_messages(
        messages,
        max_tokens=max_tokens,
        strategy="last",          # 保留最新的，丢弃最旧的
        token_counter=llm,        # 用 LLM 实例精确计算 token 数
        include_system=True,      # 始终保留 system prompt
        allow_partial=False,      # 不截断单条消息的中间
    )
 
 
# ─────────────────────────────────────────────
# 4. thread_id 规范
#    thread_id 决定"哪些消息属于同一个会话"。
#    规范：{user_id}_{session_id}
#    - 同一 session_id → 继续上次对话（上下文自动恢复）
#    - 新 session_id   → 全新对话（上下文清空）
# ─────────────────────────────────────────────
def make_thread_id(user_id: str, session_id: str) -> str:
    """
    生成规范的 thread_id。
    
    Args:
        user_id:    用户唯一标识（从 JWT / API Key 获取）
        session_id: 会话唯一标识（前端每次新建对话时生成 UUID）
    
    Returns:
        格式为 "user_123_session_abc" 的字符串
    
    示例：
        config = {
            "configurable": {
                "thread_id": make_thread_id("user_123", "session_abc"),
                "user_id": "user_123",   # 节点查 DB 时用这个
            }
        }
        await graph.ainvoke({"messages": [msg]}, config)
    """
    return f"{user_id}_{session_id}"
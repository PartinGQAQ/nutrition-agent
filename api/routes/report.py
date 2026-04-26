from fastapi import APIRouter, Query, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from client.db_client import db_client
from db.repositories import FoodLogRepository
from agent.nodes.health_analyzer.analyzer import run as health_analyzer_run
from agent.state import AgentState

router = APIRouter()


class WeeklyReportResponse(BaseModel):
    user_id: str
    week_start: str
    week_end: str
    avg_daily_calories: float
    avg_protein_g: float
    avg_fat_g: float
    avg_carb_g: float
    goal_completion_rate: float  # 0.0 ~ 1.0
    highlights: list[str]
    suggestions: list[str]


class NutritionGoal(BaseModel):
    user_id: str
    daily_calories: Optional[float] = None
    daily_protein_g: Optional[float] = None
    daily_fat_g: Optional[float] = None
    daily_carb_g: Optional[float] = None


# ── Button 触发：健康分析 ─────────────────────────────────────────────
@router.get("/analysis")
async def get_health_analysis(
    user_id: str = Query(...),
    question: str = Query("帮我分析最近的饮食健康状况", description="分析问题，可自定义"),
    session: AsyncSession = Depends(db_client.get_session),
):
    """
    Button 触发：三路召回 + LLM 生成健康分析报告。
    直接调用 health_analyzer，不走 LangGraph。
    """
    from langgraph.runtime import Runtime
    from agent.context import DataAgentContext

    state = AgentState(
        user_id=user_id,
        session_id="button",
        question=question,
    )

    class _MockRuntime:
        context: DataAgentContext = {
            "food_log_repository": FoodLogRepository(session)
        }

    result = await health_analyzer_run(state, _MockRuntime())
    return {"user_id": user_id, "analysis": result.get("response", "")}


# ── Button 触发：营养周报 ─────────────────────────────────────────────
@router.get("/weekly", response_model=WeeklyReportResponse)
async def get_weekly_report(
    user_id: str = Query(...),
    week_start: date = Query(..., description="周一日期"),
):
    """Button 触发：生成指定周的结构化营养周报"""
    # TODO: 查 food_logs 聚合 + 对比 nutrition_goals
    pass


# ── Button 触发：营养趋势 ─────────────────────────────────────────────
@router.get("/trend")
async def get_nutrition_trend(
    user_id: str = Query(...),
    start_date: date = Query(...),
    end_date: date = Query(...),
    metric: str = Query("calories", description="calories / protein / fat / carb"),
):
    """Button 触发：返回指定时间段某项营养指标的每日趋势数据（供前端画折线图）"""
    # TODO: 按天聚合 food_logs，返回 [{date, value}] 列表
    pass


# ── 营养目标管理 ──────────────────────────────────────────────────────
@router.post("/goal")
async def set_nutrition_goal(goal: NutritionGoal):
    """设置或更新用户的营养目标"""
    # TODO: crud.upsert_nutrition_goal
    pass


@router.get("/goal/{user_id}")
async def get_nutrition_goal(user_id: str):
    """查询用户当前营养目标"""
    # TODO: crud.get_nutrition_goal
    pass

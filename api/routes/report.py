from contextlib import asynccontextmanager
from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from agent.graph import build_graph
from client.db_client import db_client
from db.repositories import FoodLogRepository

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



@router.get("/weekly", response_model=WeeklyReportResponse)
async def get_weekly_report(
    user_id: str = Query(...),
    week_start: date = Query(..., description="周一日期"),
):
    """生成指定周的营养周报"""
    pass

@router.get("/last_week_health_report")
async def get_last_week_health_report(
    user_id: str = Query(...),
    session: AsyncSession = Depends(db_client.get_session)
):
    """获取上周的健康报告"""
    graph = build_graph()
    
    

@router.get("/trend")
async def get_nutrition_trend(
    user_id: str = Query(...),
    start_date: date = Query(...),
    end_date: date = Query(...),
    metric: str = Query("calories", description="calories / protein / fat / carb"),
):
    """获取指定时间段内某项营养指标的每日趋势数据"""
    pass


@router.get("/meal-plan")
async def get_meal_plan(
    user_id: str = Query(...),
    days: int = Query(7, ge=1, le=30),
):
    """基于用户目标和历史，生成未来 N 天的饮食计划"""
    pass


@router.post("/goal")
async def set_nutrition_goal(goal: NutritionGoal):
    """设置或更新用户的营养目标"""
    pass


@router.get("/goal/{user_id}")
async def get_nutrition_goal(user_id: str):
    """查询用户当前营养目标"""
    pass


@router.get("/analysis")
async def get_nutrition_analysis(
    user_id: str = Query(...),
    start_date: date = Query(...),
    end_date: date = Query(...),
):
    """对指定时间段的饮食数据做 AI 分析，返回洞察与建议"""
    pass

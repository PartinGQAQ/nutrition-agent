from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional
from datetime import date

router = APIRouter()


class FoodLogRequest(BaseModel):
    user_id: str
    food_name: str
    amount_g: float
    meal_type: str  # breakfast / lunch / dinner / snack
    logged_at: Optional[str] = None  # ISO datetime，默认当前时间


class FoodLogResponse(BaseModel):
    log_id: str
    food_name: str
    calories: float
    protein_g: float
    fat_g: float
    carb_g: float
    meal_type: str
    logged_at: str
    meal_time: str


class FoodLogUpdateRequest(BaseModel):
    amount_g: Optional[float] = None
    meal_type: Optional[str] = None
    logged_at: Optional[str] = None


@router.post("/log", response_model=FoodLogResponse)
async def log_food(req: FoodLogRequest):
    """手动记录一条饮食"""
    pass


@router.get("/log/{log_id}", response_model=FoodLogResponse)
async def get_food_log(log_id: str):
    """查询单条饮食记录"""
    pass


@router.put("/log/{log_id}", response_model=FoodLogResponse)
async def update_food_log(log_id: str, req: FoodLogUpdateRequest):
    """更新一条饮食记录"""
    pass


@router.delete("/log/{log_id}")
async def delete_food_log(log_id: str):
    """删除一条饮食记录"""
    pass


@router.get("/logs")
async def list_food_logs(
    user_id: str = Query(...),
    start_date: date = Query(...),
    end_date: date = Query(...),
    meal_type: Optional[str] = Query(None),
):
    """查询用户在日期范围内的饮食记录列表"""
    pass


@router.get("/search")
async def search_food(
    query: str = Query(..., description="食物名称关键词"),
    limit: int = Query(10),
):
    """从 USDA / 本地数据库模糊搜索食物及营养信息"""
    pass


@router.get("/nutrition/daily")
async def get_daily_nutrition(user_id: str = Query(...), day: date = Query(...)):
    """获取用户某天的营养摄入汇总（热量、三大营养素等）"""
    pass

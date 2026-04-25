from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional
from datetime import date
from pydantic import Field

router = APIRouter()

class HealthInformationRequest(BaseModel):
    user_id: str
    height_cm: float
    weight_kg: float
    age: int = Field(..., ge=0, le=120)
    gender: str = Field(..., min_length=1, max_length=10)
    activity_level: str = Field(..., min_length=1, max_length=10)
    target_weight_kg: float = Field(..., ge=0)
    

@router.post("/health-information")
async def create_health_information(req: HealthInformationRequest):
    """创建健康信息"""
    pass

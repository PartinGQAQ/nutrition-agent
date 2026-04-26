from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    password: str
    created_at: datetime
    updated_at: datetime

class HealthInformation(SQLModel, table=True):
    __tablename__ = "health_information"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str
    height_cm: float
    weight_kg: float
    age: int
    gender: str
    activity_level: str
    target_weight_kg: float
    
class Food(SQLModel, table=True):
    __tablename__ = "foods"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    calories: float
    protein_g: float
    fat_g: float
    carb_g: float


class FoodLog(SQLModel, table=True):
    __tablename__ = "food_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str
    food_id: int
    food_name: str
    amount_g: float
    meal_type: str
    calories: float
    protein_g: float
    fat_g: float
    carb_g: float
    logged_at: datetime
    confidence: str
    dialog_timestamp: str


class NutritionGoal(SQLModel, table=True):
    __tablename__ = "nutrition_goals"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str
    daily_calories: float
    daily_protein_g: float
    daily_fat_g: float
    daily_carb_g: float
    updated_at: datetime

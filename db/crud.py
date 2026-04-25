from db.models import FoodLog, NutritionGoal, HealthInformation
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

def upsert_health_information(db, user_id: str, data: dict) -> HealthInformation:
    pass

def create_food_log(db, data: dict) -> FoodLog:
    pass


def get_food_log(db, log_id: str) -> FoodLog | None:
    pass


def update_food_log(db, log_id: str, data: dict) -> FoodLog | None:
    pass


def delete_food_log(db, log_id: str) -> bool:
    pass


def list_food_logs(db, user_id: str, start_date, end_date, meal_type=None) -> list[FoodLog]:
    pass


def upsert_nutrition_goal(db, data: dict) -> NutritionGoal:
    pass


def get_nutrition_goal(db, user_id: str) -> NutritionGoal | None:
    pass

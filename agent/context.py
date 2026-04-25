from typing import TypedDict
from db.repositories import FoodLogRepository


class DataAgentContext(TypedDict):
    food_log_repository: FoodLogRepository
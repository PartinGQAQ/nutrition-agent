from pydantic import BaseModel


class FoodSlot(BaseModel):
    food_name: str | None = None
    food_amount: float | None = None
    food_unit: str = "g"
    meal_type: str | None = None          # breakfast/lunch/dinner/snack
    meal_time: str | None = None          # ISO string，默认当前时间
    # LLM 返回字段名与 prompt 保持一致
    food_calories: float | None = None
    food_protein: float | None = None
    food_fat: float | None = None
    food_carb: float | None = None
    food_fiber: float | None = None
    uncertainty: str = "low"              # low / medium / high

    def missing_required(self) -> list[str]:
        required = {
            "food_name": self.food_name,
            "food_amount": self.food_amount,
            "meal_type": self.meal_type,
        }
        return [k for k, v in required.items() if v is None]


class FoodSlotList(BaseModel):
    """LLM 多模态提取结果的顶层包装，对应 prompt 的完整输出结构。"""
    status: str                           # "ok" | "image_blur"
    items: list[FoodSlot] = []
    notes: str = ""
    message: str = ""                     # image_blur 时的提示文案
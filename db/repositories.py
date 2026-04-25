import asyncio
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from client.db_client import db_client
from db.models import FoodLog, HealthInformation


class FoodLogRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_health_information(self, user_id: str) -> HealthInformation | None:
        stmt = select(HealthInformation).where(HealthInformation.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_food_logs(self, user_id: str, days: int = 7) -> list[FoodLog]:
        stmt = select(FoodLog).where(FoodLog.user_id == user_id)
        start_date = datetime.now() - timedelta(days=days)
        stmt = stmt.where(FoodLog.logged_at >= start_date).order_by(FoodLog.logged_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


if __name__ == "__main__":
    async def main() -> None:
        await db_client.init_db()
        async with db_client.session_scope() as session:
            repository = FoodLogRepository(session)
            health_information = await repository.get_health_information("1")
            food_logs = await repository.get_food_logs("1")
            print(health_information)
            print(food_logs)

    asyncio.run(main())
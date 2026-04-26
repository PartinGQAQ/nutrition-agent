import asyncio
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from client.db_client import db_client
from db.models import Food, FoodLog, HealthInformation
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct



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
    
    async def get_food_by_name_like(self, name: str) -> Food | None:
        stmt = select(Food).where(Food.name.ilike(f"%{name}%"))
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def create_food_logs(self, food_logs: list[FoodLog]) -> list[FoodLog]:
        """写入后每条记录的 ``id``（自增）会回填到对象上，可直接用于 Qdrant 等。"""
        self.session.add_all(food_logs)
        await self.session.flush()  # 执行 INSERT，数据库生成 id 并写回实例
        await self.session.commit()
        return food_logs


class QdrantVectorStoreRepository:
    def __init__(self, client: AsyncQdrantClient, vector_size: int = 1024):
        self.client = client
        self.collection = "foods"
        self.vector_size = vector_size

    async def upsert(self, ids: list[str], embeddings: list[list[float]], metadatas: list[dict]) -> None:
        await self.client.upsert(
            collection_name=self.collection,
            points=[
                PointStruct(
                    id=id,
                    vector=embedding,
                    payload=metadata,
                )
                for id, embedding, metadata in zip(ids, embeddings, metadatas)
            ],
        )
        
        
    async def query(self, query_embedding: list[float], k: int = 5) -> list[dict]:
        results = await self.client.query_points(
            collection_name=self.collection,
            query_vector=query_embedding,
            limit=k,
        )
        return [result.payload for result in results.points]
    
    
    async def ensure_collection(self) -> None:
        if not await self.client.collection_exists(self.collection):
            await self.client.create_collection(
                self.collection,
                vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
            )
          
            
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
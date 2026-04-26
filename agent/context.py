from typing import TypedDict
from db.repositories import FoodLogRepository
from db.repositories import QdrantVectorStoreRepository
from client.embedding_client import EmbeddingClient


class DataAgentContext(TypedDict):
    embedding_client: EmbeddingClient
    food_log_repository: FoodLogRepository
    vector_store_repository: QdrantVectorStoreRepository
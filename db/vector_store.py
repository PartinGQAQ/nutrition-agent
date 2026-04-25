


class VectorStore:
    def upsert(self, collection: str, ids: list[str], embeddings: list, metadatas: list) -> None:
        pass

    def query(self, collection: str, query_embedding: list, k: int = 5) -> list[dict]:
        pass

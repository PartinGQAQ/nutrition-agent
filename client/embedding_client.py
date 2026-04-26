from langchain_openai import OpenAIEmbeddings
import dotenv
import os
import asyncio

dotenv.load_dotenv()


class EmbeddingClient:
    def __init__(self):
        self.client = None
    
    async def connect(self):
        self.clients = OpenAIEmbeddings(
            model="text-embedding-3-large",
            api_key=os.getenv("OPENAI_API_KEY"),
            dimensions=1024 
        )
        
    async def embed_documents(self, documents: list[str]) -> list[list[float]]:
        return await self.clients.aembed_documents(documents)
        
embedding_client = EmbeddingClient()
    
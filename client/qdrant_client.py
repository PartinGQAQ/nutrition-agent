from qdrant_client import AsyncQdrantClient, QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

class QdrantClient:
    def __init__(self, vector_size: int):
        self.client = QdrantClient(
            url="https://ae3c7b2d-5e90-478a-9ac0-3a73ab79adaf.us-east4-0.gcp.cloud.qdrant.io:6333", 
            api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6NmU1OWJhMDktNWVlNy00MWFhLTlhZWItNGI5YTdkNTNkM2M1In0.9I4Xo6LU9i0o6hz29rwBRrbEQ7SktDgXLAOmTUX5O48",
        )
        self.client = None
        self.collection = "foods"

    def init_client_cloud(self):
        self.client = AsyncQdrantClient(
            url="https://ae3c7b2d-5e90-478a-9ac0-3a73ab79adaf.us-east4-0.gcp.cloud.qdrant.io:6333", 
            api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6NmU1OWJhMDktNWVlNy00MWFhLTlhZWItNGI5YTdkNTNkM2M1In0.9I4Xo6LU9i0o6hz29rwBRrbEQ7SktDgXLAOmTUX5O48",
        )
        if not self.client.collection_exists(self.collection):
            self.client.create_collection(self.collection)
        
    def init_client_local(self):
        self.client = AsyncQdrantClient(
            url="http://localhost:6333",
        )
        
        
qdrant_client = QdrantClient()
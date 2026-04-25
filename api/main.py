from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from client.db_client import DBClient
from api.routes import chat, food, report
from memory.short_term import short_term_memory

db_client = DBClient()  # 全局单例

@asynccontextmanager
async def lifespan(app: FastAPI):
    await db_client.init_db()
    async with short_term_memory as short_memory:
        app.state.short_memory = short_memory
        yield


app = FastAPI(title="Nutrition Agent API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(food.router, prefix="/api/food", tags=["food"])
app.include_router(report.router, prefix="/api/report", tags=["report"])


@app.get("/health")
async def health_check():
    return {"status": "ok"}

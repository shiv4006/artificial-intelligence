from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import pool
from app.routers import chat, conversations, models

SCHEMA = Path(__file__).parent / "schema.sql"

@asynccontextmanager
async def lifespan(app:FastAPI):
    await pool.open(wait=True, timeout=5)
    async with pool.connection() as conn:
        await conn.execute(SCHEMA.read_text())
    yield
    await pool.close()
    
app = FastAPI(title="Chat API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(conversations.router)
app.include_router(chat.router)
app.include_router(models.router)

@app.get("/health")
async def health():
    async with pool.connection() as conn:
        await conn.execute("SELECT 1")
    return {"status": "ok"}
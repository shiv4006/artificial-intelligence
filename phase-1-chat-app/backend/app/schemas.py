from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import AfterValidator, BaseModel, Field

from app.pricing import model_prices

def known_model(model: str) -> str:
    if model not in model_prices():
        raise ValueError(f"Unknown model. Choose one of: {', '.join(model_prices())}")
    return model

# A model name that must be one the app offers (Groq models plus OLLAMA_MODELS from .env).
ModelName = Annotated[str, AfterValidator(known_model)]

class ConversationCreate(BaseModel):
    title: str = "New chat"
    model: ModelName = "openai/gpt-oss-20b"
    system_prompt: str = "You are a helpful assistant."
    
class ConversationUpdate(BaseModel):
    title: str | None = None
    model: ModelName | None = None

class Conversation(BaseModel):
    id: UUID
    title: str
    model: str
    system_prompt: str
    created_at: datetime
    updated_at: datetime
    
class Message(BaseModel):
    id: int
    role: Literal["user", "assistant"]
    content: str
    model: str | None
    prompt_tokens: int | None
    completion_tokens: int | None
    reasoning_tokens: int | None
    cost_usd: float | None
    created_at: datetime
    
class ConversationDetail(Conversation):
    summary: str | None = None
    messages: list[Message]
    
class ChatRequest(BaseModel):
    content: str = Field(min_length=1)
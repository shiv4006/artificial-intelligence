from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

# Keep in sync with PRICES in pricing.py
ModelName = Literal["openai/gpt-oss-20b", "openai/gpt-oss-120b"]

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
    messages: list[Message]
    
class ChatRequest(BaseModel):
    content: str = Field(min_length=1)
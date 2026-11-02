from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    groq_api_key: str
    groq_base_url: str = "https://api.groq.com/openai/v1"
    ollama_base_url: str = "http://localhost:11434/v1"
    ollama_models: list[str] = []          # local models to offer; empty = Ollama off
    database_url: str = "postgresql://chat:chat@localhost:5433/chat"
    cors_origins: list[str] = ["http://localhost:3000"]
    context_strategy: Literal["none", "window", "summary"] = "window"
    context_max_tokens: int = 3000 # history sent to the model per call, system prompt not counted
    utility_model: str = "openai/gpt-oss-20b" # cheap model for summaries and titles

settings = Settings()
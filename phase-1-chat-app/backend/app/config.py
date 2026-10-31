from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    groq_api_key: str
    groq_base_url: str = "https://api.groq.com/openai/v1"
    database_url: str = "postgresql://chat:chat@localhost:5433/chat"
    cors_origins: list[str] = ["http://localhost:3000"]

settings = Settings()
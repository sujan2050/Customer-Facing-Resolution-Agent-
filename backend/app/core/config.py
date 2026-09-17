import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Resolve - SkyRoute Resolution Agent"
    VERSION: str = "1.0.0"
    
    # LLM Settings
    LLM_PROVIDER: str = "gemini"
    LLM_MODEL: str = "gemini-2.5-flash"
    GOOGLE_API_KEY: Optional[str] = None
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/resolution_agent_db"
    
    # Server Ports
    BACKEND_PORT: int = 8000
    FRONTEND_PORT: int = 3000
    
    # Mock/Fallback mode if API key is not provided (allows tests to pass offline)
    MOCK_LLM: bool = False

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

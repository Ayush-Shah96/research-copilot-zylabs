"""Configuration management for the application."""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings."""

    # API Configuration
    API_TITLE: str = "AI Research Copilot API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Production-grade AI Research Copilot using LangGraph"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
        os.getenv("FRONTEND_URL", "http://localhost:3000"),
    ]

    # Database Configuration
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./copilot.db"
    )
    SQLALCHEMY_ECHO: bool = os.getenv("SQLALCHEMY_ECHO", "False").lower() == "true"

    # LLM Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "2000"))

    # Research Configuration
    RESEARCH_TIMEOUT: int = int(os.getenv("RESEARCH_TIMEOUT", "300"))
    WEB_SEARCH_ENABLED: bool = os.getenv("WEB_SEARCH_ENABLED", "True").lower() == "true"
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    
    # Search Provider Configuration
    SEARCH_PROVIDER: str = os.getenv("SEARCH_PROVIDER", "mock")  # tavily, brave, mock
    SEARCH_API_KEY: str = os.getenv("SEARCH_API_KEY", "")
    MAX_SEARCH_RESULTS: int = int(os.getenv("MAX_SEARCH_RESULTS", "10"))

    # Workflow Configuration
    WORKFLOW_TIMEOUT: int = int(os.getenv("WORKFLOW_TIMEOUT", "600"))
    ENABLE_STREAMING: bool = os.getenv("ENABLE_STREAMING", "True").lower() == "true"

    # Session Configuration
    SESSION_TIMEOUT: int = int(os.getenv("SESSION_TIMEOUT", "3600"))  # 1 hour
    MAX_SESSIONS_PER_USER: int = int(os.getenv("MAX_SESSIONS_PER_USER", "100"))

    # WebSocket Configuration
    WEBSOCKET_ENABLED: bool = os.getenv("WEBSOCKET_ENABLED", "True").lower() == "true"
    PING_INTERVAL: int = int(os.getenv("PING_INTERVAL", "30"))

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Feature Flags
    ENABLE_CHAT: bool = os.getenv("ENABLE_CHAT", "True").lower() == "true"
    ENABLE_REPORT_EXPORT: bool = os.getenv("ENABLE_REPORT_EXPORT", "True").lower() == "true"
    ENABLE_BATCH_PROCESSING: bool = os.getenv("ENABLE_BATCH_PROCESSING", "False").lower() == "true"


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()


settings = get_settings()
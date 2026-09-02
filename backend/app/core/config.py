import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    PROJECT_NAME: str = "LeadForge"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # AI Engine (Perplexity / Gemini / Hugging Face / Ollama)
    ACTIVE_AI_PROVIDER: str = "auto"  # auto | perplexity | gemini | huggingface | ollama | mock
    AI_SEARCH_PROVIDER: str = "auto"  # auto | perplexity | gemini | huggingface | mock

    PERPLEXITY_API_KEY: str = Field(default="", description="Perplexity API Key for Real-time Search")
    PERPLEXITY_MODEL: str = "sonar"  # sonar | sonar-pro | sonar-reasoning
    
    GEMINI_API_KEY: str = Field(default="", description="Google Gemini API Key")
    GEMINI_MODEL: str = "gemini-2.0-flash"  # gemini-2.0-flash | gemini-1.5-pro | gemini-1.5-flash

    HF_TOKEN: str = Field(default="", description="Hugging Face API Token")
    HF_MODEL: str = "mistralai/Mistral-7B-Instruct-v0.3"
    HF_OUTREACH_MODEL: str = "mistralai/Mistral-7B-Instruct-v0.3"
    HF_AUDIT_MODEL: str = "Qwen/Qwen2.5-Coder-7B-Instruct"
    HF_CLASSIFICATION_MODEL: str = "meta-llama/Meta-Llama-3-8B-Instruct"
    HF_EXTRACTION_MODEL: str = "meta-llama/Meta-Llama-3-8B-Instruct"
    HF_PROVIDER: str = "huggingface"  # huggingface | ollama | mock
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    AI_TEMPERATURE: float = 0.3
    AI_MAX_TOKENS: int = 1024
    ENABLE_AI_ANALYSIS: bool = True
    ENABLE_AI_EMAIL_GEN: bool = True
    ENABLE_AI_REPLY_CLASSIFICATION: bool = True
    ENABLE_AI_SEARCH_DISCOVERY: bool = True
    
    # External APIs (Google Maps / SerpApi)
    GOOGLE_MAPS_API_KEY: str = Field(default="", description="Google Places / Maps API Key")
    SERPAPI_KEY: str = Field(default="", description="SerpApi Key for Google Maps & Search")
    ENABLE_GOOGLE_MAPS_DISCOVERY: bool = True
    
    # Database (Supports Local SQLite, Serverless /tmp, and Managed PostgreSQL)
    DATABASE_URL: str = Field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL",
            "sqlite+aiosqlite:////tmp/leadforge.db" if os.getenv("VERCEL") else "sqlite+aiosqlite:///./leadforge.db"
        )
    )
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = "leadforge-secret-key-production-ready-2026-v1"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    ENCRYPTION_KEY: str = "leadforge-secure-enc-key-32ch!"
    
    # SMTP Defaults
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "prospecting@leadforge.io"
    SMTP_FROM_NAME: str = "LeadForge Outreach"
    SMTP_USE_TLS: bool = True
    
    # Crawl / Scrape Settings
    CRAWL_MAX_PAGES_PER_DOMAIN: int = 10
    CRAWL_TIMEOUT_SECONDS: int = 15
    CRAWL_MAX_RESPONSE_SIZE: int = 5 * 1024 * 1024  # 5MB
    CRAWL_RATE_LIMIT_PER_MINUTE: int = 60
    
    # Freshness Thresholds (in days)
    FRESHNESS_FRESH_DAYS: int = 7
    FRESHNESS_RECENT_DAYS: int = 30
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3005",
        "http://127.0.0.1:3005",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

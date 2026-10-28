from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application configuration loaded from environment or .env file."""
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_ENV: str = Field(default="local", description="Environment: local, test, staging, production")
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./researchforge.db",
        description="Database connection URL"
    )
    REDIS_URL: str = Field(default="redis://localhost:6379/0", description="Redis queue and cache URL")
    SESSION_SECRET: str = Field(
        default="rf-dev-secret-key-at-least-32-bytes-long-for-testing!",
        description="Session encryption secret"
    )
    
    # Access Model & Authentication (ADR-009 & Blueprint 17)
    ACCESS_MODE: str = Field(default="single_owner", description="single_owner or multi_user")
    REGISTRATION_POLICY: str = Field(default="closed", description="closed, invite_only, or open")
    WEBAUTHN_RP_ID: str = Field(default="localhost", description="Relying party ID for WebAuthn")
    WEBAUTHN_RP_NAME: str = Field(default="ResearchHub", description="Relying party name")
    DEMO_DATA: bool = Field(default=True, description="Enable demo seed datasets (behind demo flag per P13)")
    DEMO_MODE: bool = Field(default=False, description="Display demo banner when using seeded data")

    # Open Scholarly API Keys & Mailto
    OPENALEX_MAILTO: Optional[str] = "researchforge@example.org"
    OPENALEX_API_KEY: Optional[str] = None
    CROSSREF_MAILTO: Optional[str] = "researchforge@example.org"
    NCBI_API_KEY: Optional[str] = None
    UNPAYWALL_EMAIL: Optional[str] = "researchforge@example.org"

    # LLM Settings
    LLM_PROVIDER: Optional[str] = None
    LLM_API_KEY: Optional[str] = None
    LLM_MODEL_SYNTHESIS: str = "gemini-3.8-flash"
    LLM_MODEL_VERIFY: str = "gemini-3.1-pro-preview"
    LLM_EMBEDDING_MODEL: str = "gemini-embedding-001"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    
    # Quota & Budgets
    QUOTA_WEEKLY_CREDITS_FREE: int = 50
    GLOBAL_MONTHLY_LLM_BUDGET_USD: float = 100.0


settings = Settings()

"""
Configuration management using pydantic-settings
Loads from environment variables with validation
"""

from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment"""

    # Application
    app_name: str = Field(default="llm-router", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # Server
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    workers: int = Field(default=4, alias="WORKERS")

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://router:router@localhost:5432/router_db",
        alias="DATABASE_URL",
    )

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    # Pinecone
    pinecone_api_key: Optional[str] = Field(default=None, alias="PINECONE_API_KEY")
    pinecone_environment: str = Field(default="us-west1-gcp", alias="PINECONE_ENVIRONMENT")
    pinecone_index_name: str = Field(default="llm-router", alias="PINECONE_INDEX_NAME")

    # Model APIs
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")
    openai_base_url: str = Field(default="https://api.openai.com/v1", alias="OPENAI_BASE_URL")
    anthropic_base_url: str = Field(
        default="https://api.anthropic.com/v1",
        alias="ANTHROPIC_BASE_URL",
    )
    local_llama_endpoint: str = Field(
        default="http://localhost:8001",
        alias="LOCAL_LLAMA_ENDPOINT",
    )

    # Model configuration
    default_model: str = Field(default="llama-7b", alias="DEFAULT_MODEL")
    fallback_model: str = Field(default="gpt-4", alias="FALLBACK_MODEL")

    # Feature flags
    enable_ml_routing: bool = Field(default=False, alias="ENABLE_ML_ROUTING")
    enable_rag_routing: bool = Field(default=False, alias="ENABLE_RAG_ROUTING")
    enable_caching: bool = Field(default=True, alias="ENABLE_CACHING")

    # Phase 5 / 6 runtime
    ml_complexity_model_path: str = Field(
        default="src/training/models/complexity",
        alias="ML_COMPLEXITY_MODEL_PATH",
    )
    ml_domain_model_path: str = Field(
        default="src/training/models/domain",
        alias="ML_DOMAIN_MODEL_PATH",
    )
    rag_top_k: int = Field(default=10, alias="RAG_TOP_K")
    rag_min_similarity: float = Field(default=0.7, alias="RAG_MIN_SIMILARITY")
    rag_namespace: str = Field(default="routing-logs", alias="RAG_NAMESPACE")

    # Performance
    request_timeout: int = Field(default=30, alias="REQUEST_TIMEOUT")
    max_retries: int = Field(default=3, alias="MAX_RETRIES")
    circuit_breaker_threshold: int = Field(default=5, alias="CIRCUIT_BREAKER_THRESHOLD")

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

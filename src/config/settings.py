"""Application configuration settings."""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings."""
    
    # API Keys
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/resume_ai"
    redis_url: str = "redis://localhost:6379/0"
    
    # Vector Database
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""
    qdrant_collection_name: str = "cv_embeddings"
    
    # Application
    app_env: str = "development"
    log_level: str = "INFO"
    max_upload_size_mb: int = 10
    allowed_extensions: List[str] = [".pdf", ".docx", ".txt"]
    
    # Agent Configuration
    max_parser_agents: int = 5
    llm_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    max_tokens: int = 4000
    temperature: float = 0.1
    
    # Scoring Weights
    weight_skills: float = 0.4
    weight_experience: float = 0.3
    weight_education: float = 0.15
    weight_career: float = 0.1
    weight_other: float = 0.05
    
    # Storage
    data_dir: str = "data"
    cv_dir: str = "data/cvs"
    report_dir: str = "data/reports"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()


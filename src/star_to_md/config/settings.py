from pydantic_settings import BaseSettings
from typing import Dict, Optional
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings"""
    app_name: str = "star_to_md"
    debug: bool = False
    
    # API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # LLM Settings
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.1
    
    # Ell Settings
    ell_store_path: str = "./logs/ell"
    ell_autocommit: bool = True
    ell_verbose: bool = False
    
    # Processing Settings
    max_chunk_size: int = 4
    confidence_threshold: float = 0.8
    
    # Pandoc Settings
    pandoc_path: Optional[str] = None
    
    class Config:
        env_prefix = "STAR_TO_MD_"
        env_file = ".env"
        extra = "allow"  # Allow extra fields from environment variables

@lru_cache
def get_settings() -> Settings:
    """Cached settings instance"""
    return Settings()
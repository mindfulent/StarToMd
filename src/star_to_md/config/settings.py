from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Dict, Optional, Any
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings"""
    app_name: str = "star_to_md"
    debug: bool = False
    
    # OpenAI Settings
    openai_api_key: str = Field(env='OPENAI_API_KEY')
    
    # LLM Settings
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.1
    
    # Processing Settings
    max_chunk_size: int = 4
    confidence_threshold: float = 0.8
    
    # Pandoc Settings
    pandoc_path: Optional[str] = None
    
    class Config:
        env_prefix = "STAR_TO_MD_"
        env_file = ".env"

@lru_cache
def get_settings() -> Settings:
    """Cached settings instance"""
    return Settings()
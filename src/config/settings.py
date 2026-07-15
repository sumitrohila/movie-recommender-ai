from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # LLM
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field("gpt-4o-mini", env="OPENAI_MODEL")
    
    # Optional other LLMs
    anthropic_api_key: str | None = Field(None, env="ANTHROPIC_API_KEY")
    
    # Database
    database_url: str = Field("sqlite:///./movies.db", env="DATABASE_URL")
    
    # Redis
    redis_url: str | None = Field(None, env="REDIS_URL")
    
    # External APIs
    tmdb_api_key: str | None = Field(None, env="TMDB_API_KEY")
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
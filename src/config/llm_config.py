from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from functools import lru_cache
from .settings import settings

@lru_cache(maxsize=1)
def get_llm(temperature: float = 0.0):
    """Singleton LLM instance (OpenAI by default)."""
    return ChatOpenAI(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
        temperature=temperature,
    )

# Optional: get different models
def get_anthropic_llm():
    if settings.anthropic_api_key:
        return ChatAnthropic(api_key=settings.anthropic_api_key, model="claude-3-sonnet-20240229")
    return None
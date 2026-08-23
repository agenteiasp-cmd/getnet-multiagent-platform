from functools import lru_cache

from openai import AsyncOpenAI

from app.config import get_settings


@lru_cache
def get_openai_client() -> AsyncOpenAI:
    """Single shared AsyncOpenAI client, built from settings.

    Cached so agents/tools share one HTTP connection pool instead of each
    constructing their own client.
    """
    settings = get_settings()
    return AsyncOpenAI(api_key=settings.openai_api_key)

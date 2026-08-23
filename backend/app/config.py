from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables / .env.

    All five variables are required: the app should fail fast at startup
    rather than fail confusingly deep inside a request when a client is
    first constructed.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: str = Field(alias="OPENAI_API_KEY")
    pinecone_api_key: str = Field(alias="PINECONE_API_KEY")
    pinecone_environment: str = Field(alias="PINECONE_ENVIRONMENT")
    pinecone_index_name: str = Field(alias="PINECONE_INDEX_NAME")
    tavily_api_key: str = Field(alias="TAVILY_API_KEY")

    router_model: str = Field(default="gpt-4o-mini", alias="ROUTER_MODEL")
    knowledge_model: str = Field(default="gpt-4o-mini", alias="KNOWLEDGE_MODEL")
    support_model: str = Field(default="gpt-4o-mini", alias="SUPPORT_MODEL")
    escalation_model: str = Field(default="gpt-4o-mini", alias="ESCALATION_MODEL")

    data_dir: str = Field(default="data_store", alias="DATA_DIR")


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor.

    Raises pydantic.ValidationError with a clear message listing every
    missing environment variable if required settings are absent.
    """
    return Settings()  # type: ignore[call-arg]

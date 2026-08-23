import pytest
from pydantic import ValidationError


def test_settings_load_from_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("PINECONE_API_KEY", "pc-test")
    monkeypatch.setenv("PINECONE_ENVIRONMENT", "us-east-1-aws")
    monkeypatch.setenv("PINECONE_INDEX_NAME", "test-index")
    monkeypatch.setenv("TAVILY_API_KEY", "tvly-test")

    from app.config import Settings

    settings = Settings(_env_file=None)  # type: ignore[call-arg]
    assert settings.openai_api_key == "sk-test"
    assert settings.pinecone_index_name == "test-index"


def test_settings_missing_required_var_raises(monkeypatch):
    for var in (
        "OPENAI_API_KEY",
        "PINECONE_API_KEY",
        "PINECONE_ENVIRONMENT",
        "PINECONE_INDEX_NAME",
        "TAVILY_API_KEY",
    ):
        monkeypatch.delenv(var, raising=False)

    from app.config import Settings

    with pytest.raises(ValidationError) as exc_info:
        Settings(_env_file=None)  # type: ignore[call-arg]

    missing_fields = {error["loc"][0] for error in exc_info.value.errors()}
    assert missing_fields == {
        "OPENAI_API_KEY",
        "PINECONE_API_KEY",
        "PINECONE_ENVIRONMENT",
        "PINECONE_INDEX_NAME",
        "TAVILY_API_KEY",
    }

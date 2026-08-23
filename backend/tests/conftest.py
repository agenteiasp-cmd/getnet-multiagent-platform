import pytest

from app.config import get_settings


def has_real_credentials() -> bool:
    try:
        get_settings()
        return True
    except Exception:
        return False


requires_live_credentials = pytest.mark.skipif(
    not has_real_credentials(),
    reason="Live external-API test requires OPENAI/PINECONE/TAVILY credentials in backend/.env",
)

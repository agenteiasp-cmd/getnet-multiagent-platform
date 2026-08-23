import json

import pytest
from fastapi.testclient import TestClient

from app.config_store.agent_config import AgentConfigStore, DEFAULT_AGENT_CONFIGS
from app.dependencies import get_agent_config_store
from app.main import app


@pytest.fixture
def config_store(tmp_path):
    store = AgentConfigStore(tmp_path / "agent_config.json")
    app.dependency_overrides[get_agent_config_store] = lambda: store
    yield store
    app.dependency_overrides.pop(get_agent_config_store, None)


def test_default_configs_have_sane_defaults_for_all_four_agents():
    assert set(DEFAULT_AGENT_CONFIGS.keys()) == {"router", "knowledge", "support", "escalation"}
    for agent, config in DEFAULT_AGENT_CONFIGS.items():
        assert "prompt" in config
        assert "tools" in config
        assert config["enabled"] is True


def test_get_all_agent_configs(config_store):
    client = TestClient(app)
    response = client.get("/agents/config")
    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {"router", "knowledge", "support", "escalation"}


def test_save_persists_prompt_edit(config_store):
    client = TestClient(app)
    response = client.put("/agents/config/support", json={"prompt": "novo prompt de teste"})
    assert response.status_code == 200
    assert response.json()["prompt"] == "novo prompt de teste"

    # Persisted: a fresh read reflects the saved value.
    assert config_store.get("support")["prompt"] == "novo prompt de teste"


def test_restore_default_reverts_prompt(config_store):
    client = TestClient(app)
    client.put("/agents/config/support", json={"prompt": "prompt temporário"})
    assert config_store.get("support")["prompt"] == "prompt temporário"

    response = client.post("/agents/config/support/restore-default")
    assert response.status_code == 200
    assert response.json()["prompt"] == DEFAULT_AGENT_CONFIGS["support"]["prompt"]


def test_unknown_agent_returns_404(config_store):
    client = TestClient(app)
    response = client.put("/agents/config/does-not-exist", json={"prompt": "x"})
    assert response.status_code == 404


def test_stale_persisted_file_missing_new_keys_is_backfilled(tmp_path):
    path = tmp_path / "agent_config.json"
    stale = {
        agent: {k: v for k, v in cfg.items() if k not in ("max_tokens", "disabled_features")}
        for agent, cfg in DEFAULT_AGENT_CONFIGS.items()
    }
    path.write_text(json.dumps(stale), encoding="utf-8")

    store = AgentConfigStore(path)
    all_configs = store.get_all()

    for agent_config in all_configs.values():
        assert "max_tokens" in agent_config
        assert "disabled_features" in agent_config

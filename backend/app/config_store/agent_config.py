import copy
import json
from pathlib import Path

from app.llm.router_llm import CHITCHAT_SYSTEM_PROMPT, ROUTER_SYSTEM_PROMPT
from app.llm.support_llm import SUPPORT_SYSTEM_PROMPT
from app.agents.knowledge import RAG_SYSTEM_PROMPT
from app.tools.support_tools import SUPPORT_TOOL_NAMES

DEFAULT_AGENT_CONFIGS: dict[str, dict] = {
    "router": {
        "prompt": f"{ROUTER_SYSTEM_PROMPT}\n\n---\n{CHITCHAT_SYSTEM_PROMPT}",
        "model": "gpt-4o-mini",
        "temperature": 0.0,
        "tools": ["classify_intent"],
        "enabled": True,
        "max_tokens": None,
        "disabled_features": [],
    },
    "knowledge": {
        "prompt": RAG_SYSTEM_PROMPT,
        "model": "gpt-4o-mini",
        "temperature": 0.3,
        "tools": ["pinecone_retrieval", "tavily_web_search"],
        "enabled": True,
        "max_tokens": None,
        "disabled_features": [],
    },
    "support": {
        "prompt": SUPPORT_SYSTEM_PROMPT,
        "model": "gpt-4o-mini",
        "temperature": 0.0,
        "tools": list(SUPPORT_TOOL_NAMES),
        "enabled": True,
        "max_tokens": None,
        "disabled_features": [],
    },
    "escalation": {
        "prompt": "",
        "model": None,
        "temperature": None,
        "tools": ["mock_handoff_call"],
        "enabled": True,
        "max_tokens": None,
        "disabled_features": [],
    },
}


class AgentConfigStore:
    """JSON-file-backed store for per-agent settings (prompt, model,
    temperature, tools, enabled), separate from the live orchestration's
    hardcoded agent wiring - see design.md's Settings UI decision."""

    def __init__(self, path: Path):
        self._path = path
        if not self._path.exists():
            self._write(copy.deepcopy(DEFAULT_AGENT_CONFIGS))

    def _read(self) -> dict:
        data = json.loads(self._path.read_text(encoding="utf-8"))
        # Backfill any keys missing from a file persisted by an older
        # version of DEFAULT_AGENT_CONFIGS (e.g. max_tokens/disabled_features
        # added in a later revision) so callers never see a partial record.
        for agent, defaults in DEFAULT_AGENT_CONFIGS.items():
            if agent in data:
                data[agent] = {**defaults, **data[agent]}
        return data

    def _write(self, data: dict) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def get_all(self) -> dict:
        return self._read()

    def get(self, agent: str) -> dict | None:
        return self._read().get(agent)

    def update(self, agent: str, updates: dict) -> dict:
        data = self._read()
        if agent not in data:
            raise KeyError(agent)
        data[agent] = {**data[agent], **updates}
        self._write(data)
        return data[agent]

    def restore_default(self, agent: str) -> dict:
        if agent not in DEFAULT_AGENT_CONFIGS:
            raise KeyError(agent)
        data = self._read()
        data[agent] = copy.deepcopy(DEFAULT_AGENT_CONFIGS[agent])
        self._write(data)
        return data[agent]

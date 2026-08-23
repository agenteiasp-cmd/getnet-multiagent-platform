import json
import sqlite3
from pathlib import Path

from app.observability.models import StepRecord
from app.observability.pricing import estimate_cost_usd

SCHEMA = """
CREATE TABLE IF NOT EXISTS conversations (
    conversation_id TEXT PRIMARY KEY,
    trace_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    message TEXT NOT NULL,
    response TEXT NOT NULL,
    agent_used TEXT NOT NULL,
    intent TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL,
    trace_id TEXT NOT NULL,
    step TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    input_data TEXT,
    output_data TEXT,
    model TEXT,
    prompt_tokens INTEGER NOT NULL DEFAULT 0,
    completion_tokens INTEGER NOT NULL DEFAULT 0,
    latency_ms REAL NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'ok'
);

CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trace_id TEXT NOT NULL,
    agent_used TEXT NOT NULL,
    rating INTEGER NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_steps_conversation_id ON steps(conversation_id);
CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at);
CREATE INDEX IF NOT EXISTS idx_feedback_created_at ON feedback(created_at);
"""


def _serialize(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, default=str)


class ObservabilityStore:
    def __init__(self, db_path: Path):
        self._db_path = db_path
        db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.executescript(SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def upsert_conversation(
        self,
        *,
        conversation_id: str,
        trace_id: str,
        user_id: str,
        message: str,
        response: str,
        agent_used: str,
        intent: str,
        status: str,
        created_at: str,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO conversations
                    (conversation_id, trace_id, user_id, message, response, agent_used, intent, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(conversation_id) DO UPDATE SET
                    response=excluded.response,
                    agent_used=excluded.agent_used,
                    intent=excluded.intent,
                    status=excluded.status
                """,
                (conversation_id, trace_id, user_id, message, response, agent_used, intent, status, created_at),
            )

    def insert_step(self, record: StepRecord) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO steps
                    (conversation_id, trace_id, step, timestamp, input_data, output_data, model,
                     prompt_tokens, completion_tokens, latency_ms, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.conversation_id,
                    record.trace_id,
                    record.step,
                    record.timestamp,
                    _serialize(record.input),
                    _serialize(record.output),
                    record.model,
                    record.prompt_tokens,
                    record.completion_tokens,
                    record.latency_ms,
                    record.status,
                ),
            )

    def list_conversations(
        self,
        *,
        start: str | None = None,
        end: str | None = None,
        agent: str | None = None,
        status: str | None = None,
        limit: int = 100,
    ) -> list[dict]:
        query = "SELECT * FROM conversations WHERE 1=1"
        params: list = []
        if start:
            query += " AND created_at >= ?"
            params.append(start)
        if end:
            query += " AND created_at <= ?"
            params.append(end)
        if agent:
            query += " AND agent_used = ?"
            params.append(agent)
        if status:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    def get_conversation(self, conversation_id: str) -> dict | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM conversations WHERE conversation_id = ?", (conversation_id,)
            ).fetchone()
        return dict(row) if row else None

    def get_steps(self, conversation_id: str) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM steps WHERE conversation_id = ? ORDER BY id ASC", (conversation_id,)
            ).fetchall()
        return [dict(row) for row in rows]

    def metrics_summary(self, *, start: str | None = None, end: str | None = None) -> dict:
        query = "SELECT status, COUNT(*) as count FROM conversations WHERE 1=1"
        params: list = []
        if start:
            query += " AND created_at >= ?"
            params.append(start)
        if end:
            query += " AND created_at <= ?"
            params.append(end)
        query += " GROUP BY status"
        with self._connect() as conn:
            status_rows = conn.execute(query, params).fetchall()

            latency_query = "SELECT AVG(latency_ms) as avg_latency, SUM(latency_ms) as total_latency, COUNT(*) as step_count FROM steps WHERE 1=1"
            latency_params: list = []
            if start:
                latency_query += " AND timestamp >= ?"
                latency_params.append(start)
            if end:
                latency_query += " AND timestamp <= ?"
                latency_params.append(end)
            latency_row = conn.execute(latency_query, latency_params).fetchone()

        by_status = {row["status"]: row["count"] for row in status_rows}
        total = sum(by_status.values())
        errors = sum(count for status, count in by_status.items() if status != "ok")
        return {
            "total_conversations": total,
            "by_status": by_status,
            "error_rate": (errors / total) if total else 0.0,
            "avg_step_latency_ms": latency_row["avg_latency"] or 0.0,
            "total_step_latency_ms": latency_row["total_latency"] or 0.0,
            "step_count": latency_row["step_count"] or 0,
        }

    def agent_usage(self, *, start: str | None = None, end: str | None = None) -> dict[str, int]:
        query = "SELECT agent_used, COUNT(*) as count FROM conversations WHERE 1=1"
        params: list = []
        if start:
            query += " AND created_at >= ?"
            params.append(start)
        if end:
            query += " AND created_at <= ?"
            params.append(end)
        query += " GROUP BY agent_used"
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return {row["agent_used"]: row["count"] for row in rows}

    def token_usage(self, *, start: str | None = None, end: str | None = None) -> dict:
        query = """
            SELECT
                s.model as model,
                c.agent_used as agent_used,
                SUM(s.prompt_tokens) as prompt_tokens,
                SUM(s.completion_tokens) as completion_tokens
            FROM steps s
            JOIN conversations c ON c.conversation_id = s.conversation_id
            WHERE s.model IS NOT NULL
        """
        params: list = []
        if start:
            query += " AND s.timestamp >= ?"
            params.append(start)
        if end:
            query += " AND s.timestamp <= ?"
            params.append(end)
        query += " GROUP BY s.model, c.agent_used"
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        breakdown = []
        for row in rows:
            entry = dict(row)
            entry["estimated_cost_usd"] = estimate_cost_usd(
                entry["model"], entry["prompt_tokens"] or 0, entry["completion_tokens"] or 0
            )
            breakdown.append(entry)
        total_prompt = sum(row["prompt_tokens"] or 0 for row in breakdown)
        total_completion = sum(row["completion_tokens"] or 0 for row in breakdown)
        total_cost = sum(row["estimated_cost_usd"] for row in breakdown)
        return {
            "total_prompt_tokens": total_prompt,
            "total_completion_tokens": total_completion,
            "total_estimated_cost_usd": total_cost,
            "breakdown": breakdown,
        }

    def insert_feedback(self, *, trace_id: str, agent_used: str, rating: int, created_at: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO feedback (trace_id, agent_used, rating, created_at) VALUES (?, ?, ?, ?)",
                (trace_id, agent_used, rating, created_at),
            )

    def agent_feedback(self, *, start: str | None = None, end: str | None = None) -> dict[str, dict]:
        query = """
            SELECT
                agent_used,
                COUNT(*) as total,
                SUM(CASE WHEN rating > 0 THEN 1 ELSE 0 END) as positive,
                AVG(rating) as avg_score
            FROM feedback
            WHERE 1=1
        """
        params: list = []
        if start:
            query += " AND created_at >= ?"
            params.append(start)
        if end:
            query += " AND created_at <= ?"
            params.append(end)
        query += " GROUP BY agent_used"
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        result = {}
        for row in rows:
            total = row["total"]
            result[row["agent_used"]] = {
                "total": total,
                "positive_rate": (row["positive"] / total) if total else 0.0,
                "avg_score": row["avg_score"] or 0.0,
            }
        return result

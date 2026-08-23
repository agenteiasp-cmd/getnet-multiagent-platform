import json
import subprocess
import sys
import tempfile
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent

TEST_CATEGORIES: dict[str, list[str]] = {
    "guardrails": ["tests/test_guardrails.py"],
    "router": ["tests/test_router.py", "tests/test_orchestrator.py"],
    "knowledge": [
        "tests/test_knowledge_agent.py",
        "tests/test_retrieval_tool.py",
        "tests/test_web_search_tool.py",
        "tests/test_rag_ingest.py",
        "tests/test_rag_upsert.py",
    ],
    "support": ["tests/test_support_agent.py"],
    "escalation": ["tests/test_escalation_agent.py"],
    "chat_api": ["tests/test_chat_endpoint.py"],
    "observability": ["tests/test_observability.py", "tests/test_observability_api.py"],
    "config": ["tests/test_agent_config_api.py", "tests/test_config.py"],
    "e2e": ["tests/test_e2e_examples.py"],
    "all": ["tests"],
}


class TestRunRequest(BaseModel):
    category: str


class TestCaseResult(BaseModel):
    name: str
    outcome: str
    duration_seconds: float
    error: str | None = None


class TestRunResult(BaseModel):
    category: str
    passed: int
    failed: int
    total: int
    duration_seconds: float
    tests: list[TestCaseResult]


@router.get("/tests/categories")
def list_test_categories() -> list[str]:
    return sorted(TEST_CATEGORIES.keys())


@router.post("/tests/run", response_model=TestRunResult)
def run_tests(request: TestRunRequest) -> TestRunResult:
    if request.category not in TEST_CATEGORIES:
        raise HTTPException(status_code=404, detail=f"Unknown test category: {request.category}")

    paths = TEST_CATEGORIES[request.category]

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        report_path = Path(tmp.name)

    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                *paths,
                "-q",
                "--json-report",
                f"--json-report-file={report_path}",
            ],
            cwd=BACKEND_ROOT,
            capture_output=True,
            text=True,
            timeout=300,
        )
        report = json.loads(report_path.read_text(encoding="utf-8"))
    finally:
        report_path.unlink(missing_ok=True)

    tests = []
    for test in report.get("tests", []):
        error = None
        if test.get("outcome") == "failed":
            error = test.get("call", {}).get("longrepr")
        tests.append(
            TestCaseResult(
                name=test["nodeid"],
                outcome=test["outcome"],
                duration_seconds=test.get("duration", 0.0),
                error=error,
            )
        )

    summary = report.get("summary", {})
    return TestRunResult(
        category=request.category,
        passed=summary.get("passed", 0),
        failed=summary.get("failed", 0),
        total=summary.get("total", 0),
        duration_seconds=report.get("duration", 0.0),
        tests=tests,
    )

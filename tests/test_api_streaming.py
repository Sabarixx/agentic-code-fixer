"""Unit tests for FastAPI streaming SSE endpoints (/repair/stream and /duck_chat/stream)."""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from ui.api_server import app


@pytest.fixture
def client():
    return TestClient(app)


def test_repair_stream_endpoint(client):
    """Verify /repair/stream streams SSE events without blocking."""
    mock_events = [
        {"stage": "diagnosing", "bug_category": "Null Pointer", "root_cause": "User is null"},
        {"stage": "generating_tests", "generated_tests": "def test(): pass"},
        {"stage": "fixing", "iteration": 1, "corrected_code": "def foo(): return 1"},
        {"stage": "testing", "iteration": 1, "test_results": {"passed": 1, "total": 1}},
        {"stage": "done", "status": "passed", "corrected_code": "def foo(): return 1", "iterations_taken": 1},
    ]

    with patch("ui.api_server.run_custom_fix", return_value=iter(mock_events)):
        response = client.post(
            "/repair/stream",
            json={"code": "def foo(): pass", "language": "python", "tests": ""},
        )
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
        body = response.text
        assert "data: " in body
        assert "diagnosing" in body
        assert "generating_tests" in body
        assert "fixing" in body
        assert "testing" in body
        assert "done" in body
        assert "[DONE]" in body


def test_duck_chat_stream_endpoint(client):
    """Verify /duck_chat/stream streams SSE events including pondering and chunks."""
    mock_response = MagicMock()
    mock_response.response_text = "Let's check the function arguments."
    mock_response.current_level = 1
    mock_response.is_solution_unlocked = False
    mock_response.critic_monologue = "User seems confused by null handling."

    mock_llm = MagicMock()
    mock_structured = MagicMock()
    mock_structured.invoke.return_value = mock_response
    mock_llm.with_structured_output.return_value = mock_structured

    with patch("ui.api_server.get_llm", return_value=mock_llm):
        response = client.post(
            "/duck_chat/stream",
            json={
                "code": "def foo(x): return x.y",
                "tests": "",
                "user_message": "Why does it crash?",
                "language": "python",
            },
        )
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
        body = response.text
        assert "pondering" in body
        assert "chunk" in body
        assert "done" in body
        assert "[DONE]" in body

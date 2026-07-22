from unittest.mock import patch

@patch("app.agent.agent_service.is_safe", return_value=True)
@patch("app.agent.agent_service.client")
def test_run_agent_basic(mock_client, mock_safe):
    mock_client.chat.completions.create.return_value.choices = [
        type("obj", (), {"message": type("m", (), {"content": "Hello", "tool_calls": None})()})()
    ]
    from app.agent.agent_service import run_agent
    result = run_agent("hi")
    assert result["answer"] == "Hello"
"""
Checks how each provider translates our messages into its SDK's format.
These tests don't call any real API.
"""

from app.providers.claude_provider import ClaudeProvider
from app.providers.gemini_provider import to_gemini_contents
from app.schemas.chat import ChatMessage

CONVERSATION = [
    ChatMessage(role="user", content="Hi"),
    ChatMessage(role="assistant", content="Hello!"),
    ChatMessage(role="user", content="How are you?"),
]


def test_gemini_calls_the_assistant_role_model():
    contents = to_gemini_contents(CONVERSATION)

    assert [c.role for c in contents] == ["user", "model", "user"]
    assert contents[1].parts[0].text == "Hello!"


def test_claude_request_contains_the_conversation_and_system_prompt():
    provider = ClaudeProvider(api_key="test-key", model_id="claude-opus-5-5")

    request = provider.build_request(CONVERSATION, system_prompt="Be brief")

    assert request["model"] == "claude-opus-5-5"
    assert request["system"] == "Be brief"
    assert [m["role"] for m in request["messages"]] == ["user", "assistant", "user"]


def test_claude_request_leaves_out_an_empty_system_prompt():
    provider = ClaudeProvider(api_key="test-key", model_id="claude-opus-5-5")

    request = provider.build_request(CONVERSATION, system_prompt="   ")

    assert "system" not in request


def test_claude_fallbacks_are_only_sent_to_models_that_support_them():
    supported = ClaudeProvider(api_key="test-key", model_id="claude-opus-5-5")
    unsupported = ClaudeProvider(api_key="test-key", model_id="claude-haiku-5-5")

    assert supported.build_request(CONVERSATION, "")["fallbacks"] == "default"
    assert "fallbacks" not in unsupported.build_request(CONVERSATION, "")

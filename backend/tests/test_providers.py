"""
Checks how each provider translates our messages into its SDK's format.
These tests don't call any real API.
"""

from app.providers.claude_provider import ClaudeProvider
from app.providers.groq_provider import GroqProvider
from app.schemas.chat import ChatMessage

CONVERSATION = [
    ChatMessage(role="user", content="Hi"),
    ChatMessage(role="assistant", content="Hello!"),
    ChatMessage(role="user", content="How are you?"),
]


def test_groq_puts_the_system_prompt_first_as_a_message():
    provider = GroqProvider(api_key="test-key", model_id="openai/gpt-oss-120b")

    request = provider.build_request(CONVERSATION, system_prompt="Be brief")

    assert request["stream"] is True
    assert request["messages"][0] == {"role": "system", "content": "Be brief"}
    assert [m["role"] for m in request["messages"]] == ["system", "user", "assistant", "user"]


def test_groq_leaves_out_an_empty_system_prompt():
    provider = GroqProvider(api_key="test-key", model_id="openai/gpt-oss-120b")

    request = provider.build_request(CONVERSATION, system_prompt="")

    assert [m["role"] for m in request["messages"]] == ["user", "assistant", "user"]


def test_groq_reasoning_effort_is_only_sent_to_gpt_oss_models():
    gpt_oss = GroqProvider(api_key="test-key", model_id="openai/gpt-oss-120b")
    llama = GroqProvider(api_key="test-key", model_id="llama-3.3-70b-versatile")

    assert gpt_oss.build_request(CONVERSATION, "")["reasoning_effort"] == "low"
    assert "reasoning_effort" not in llama.build_request(CONVERSATION, "")


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

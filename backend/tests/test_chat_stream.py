from collections.abc import AsyncIterator

from app.api.routes import chat
from app.providers.base import ChatChunk, ChatProvider, ProviderError
from tests.helpers import parse_sse


def ask(client, question: str, model: str = "demo", system_prompt: str = ""):
    """Send one question to the streaming endpoint."""
    return client.post(
        "/api/chat/stream",
        json={
            "model": model,
            "system_prompt": system_prompt,
            "messages": [{"role": "user", "content": question}],
        },
    )


def test_demo_reply_streams_tokens_then_done(client):
    response = ask(client, "Hello there")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")

    events = parse_sse(response.text)
    tokens = [e for e in events if e["type"] == "token"]
    done = events[-1]

    # Many small pieces, then exactly one "done" event at the end.
    assert len(tokens) > 10
    assert done["type"] == "done"
    assert "Hello there" in "".join(t["text"] for t in tokens)

    # The stats shown under each answer.
    assert done["output_tokens"] == len(tokens)
    assert done["input_tokens"] == 2  # "Hello there" is two words
    assert done["total_ms"] >= 0
    assert done["first_token_ms"] is not None


def test_system_prompt_reaches_the_model(client):
    response = ask(client, "Hi", system_prompt="Talk like a pirate")

    text = "".join(e["text"] for e in parse_sse(response.text) if e["type"] == "token")
    assert "Talk like a pirate" in text


def test_unknown_model_returns_404(client):
    response = ask(client, "Hi", model="no-such-model")

    assert response.status_code == 404


def test_last_message_must_be_from_user(client):
    response = client.post(
        "/api/chat/stream",
        json={"model": "demo", "messages": [{"role": "assistant", "content": "Hi"}]},
    )

    assert response.status_code == 422


def test_empty_conversation_is_rejected(client):
    response = client.post("/api/chat/stream", json={"model": "demo", "messages": []})

    assert response.status_code == 422


class BrokenProvider(ChatProvider):
    """Starts replying, then fails — like a model whose connection drops."""

    async def stream_reply(self, messages, system_prompt) -> AsyncIterator[ChatChunk]:
        yield ChatChunk(text="Partial ")
        raise ProviderError("The model is overloaded.")


def test_provider_error_becomes_an_error_event(client, monkeypatch):
    monkeypatch.setattr(chat, "get_provider", lambda model_id: BrokenProvider())

    events = parse_sse(ask(client, "Hi").text)

    assert events[0] == {"type": "token", "text": "Partial "}
    assert events[-1] == {"type": "error", "message": "The model is overloaded."}

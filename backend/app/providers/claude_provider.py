"""
Talks to Anthropic's Claude models through the official `anthropic` SDK.

Get an API key at https://platform.claude.com
Docs: https://platform.claude.com/docs
"""

from collections.abc import AsyncIterator
from typing import Any

import anthropic

from app.providers.base import ChatChunk, ChatProvider, ProviderError
from app.schemas.chat import ChatMessage

# Models that support automatic fallbacks: if Claude's safety filter declines a
# request, Anthropic retries it on a suitable other model instead of failing.
MODELS_WITH_FALLBACK = {"claude-fable-5-1", "claude-opus-5-5", "claude-opus-5", "claude-sonnet-5-5"}


class ClaudeProvider(ChatProvider):
    def __init__(self, api_key: str, model_id: str):
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.model_id = model_id

    async def stream_reply(
        self, messages: list[ChatMessage], system_prompt: str
    ) -> AsyncIterator[ChatChunk]:
        try:
            # `**request` spreads the dictionary out as keyword arguments (model=..., messages=...).
            # `.beta` is needed because the fallbacks feature is still in beta.
            async with self.client.beta.messages.stream(**self.build_request(messages, system_prompt)) as stream:
                async for text in stream.text_stream:
                    yield ChatChunk(text=text)
                final = await stream.get_final_message()
        except anthropic.APIError as error:
            raise ProviderError(self.describe_error(error)) from error

        if final.stop_reason == "refusal":
            raise ProviderError("Claude declined to answer this request.")

        yield ChatChunk(
            input_tokens=final.usage.input_tokens,
            output_tokens=final.usage.output_tokens,
        )

    def build_request(self, messages: list[ChatMessage], system_prompt: str) -> dict[str, Any]:
        """Everything we send to Claude, as a dictionary."""
        request: dict[str, Any] = {
            "model": self.model_id,
            # Upper limit on the reply length, in tokens. Kept generous: a reply that gets
            # cut off is worse than a long one, and you only pay for tokens actually written.
            "max_tokens": 64000,
            # Claude uses the same "user" / "assistant" roles as we do, so no renaming needed.
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            # How much Claude thinks before answering. "low" keeps chat replies quick.
            "output_config": {"effort": "low"},
        }
        if system_prompt.strip():
            request["system"] = system_prompt
        if self.model_id in MODELS_WITH_FALLBACK:
            request["betas"] = ["server-side-fallback-2026-07-01"]
            request["fallbacks"] = "default"
        return request

    def describe_error(self, error: anthropic.APIError) -> str:
        """Turn an SDK error into a sentence the user can act on (most specific first)."""
        if isinstance(error, anthropic.AuthenticationError):
            return "Claude rejected the API key. Check ANTHROPIC_API_KEY in backend/.env."
        if isinstance(error, anthropic.NotFoundError):
            return f"Claude doesn't know the model '{self.model_id}'. Check CLAUDE_MODEL in backend/.env."
        if isinstance(error, anthropic.RateLimitError):
            return "Claude's rate limit was reached. Wait a moment and try again."
        if isinstance(error, anthropic.APIConnectionError):
            return "Couldn't reach the Claude API. Check your internet connection."
        if isinstance(error, anthropic.APIStatusError):
            # e.g. 400 "Your credit balance is too low", 529 "Overloaded"
            return f"Claude error {error.status_code}: {api_error_message(error)}"
        return f"Claude error: {error}"


def api_error_message(error: anthropic.APIStatusError) -> str:
    """The human-readable message inside an API error response, if there is one."""
    body = error.body
    if isinstance(body, dict) and isinstance(body.get("error"), dict):
        return body["error"].get("message", str(error))
    return str(error)

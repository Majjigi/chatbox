"""
Talks to models hosted by Groq (open models such as gpt-oss and Llama) through
the official `groq` SDK. Groq runs them on its own very fast chips, and its API
has a free plan.

Get a free API key at https://console.groq.com/keys
Docs: https://console.groq.com/docs
"""

from collections.abc import AsyncIterator
from typing import Any

import groq

from app.providers.base import ChatChunk, ChatProvider, ProviderError
from app.schemas.chat import ChatMessage


class GroqProvider(ChatProvider):
    def __init__(self, api_key: str, model_id: str):
        self.client = groq.AsyncGroq(api_key=api_key)
        self.model_id = model_id

    async def stream_reply(
        self, messages: list[ChatMessage], system_prompt: str
    ) -> AsyncIterator[ChatChunk]:
        usage = None

        try:
            # `await` sends the request; `stream=True` makes the reply arrive in chunks.
            stream = await self.client.chat.completions.create(**self.build_request(messages, system_prompt))
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield ChatChunk(text=chunk.choices[0].delta.content)
                # The last chunk carries the token counts. Groq puts them in its own
                # `x_groq` field; newer API versions also fill the standard `usage` field.
                if chunk.usage:
                    usage = chunk.usage
                elif chunk.x_groq and chunk.x_groq.usage:
                    usage = chunk.x_groq.usage
        except groq.APIError as error:
            raise ProviderError(self.describe_error(error)) from error

        if usage is not None:
            yield ChatChunk(input_tokens=usage.prompt_tokens, output_tokens=usage.completion_tokens)

    def build_request(self, messages: list[ChatMessage], system_prompt: str) -> dict[str, Any]:
        """Everything we send to Groq, as a dictionary."""
        # Groq uses the "chat completions" format: the system prompt is simply the
        # first message, with role "system".
        chat: list[dict[str, str]] = []
        if system_prompt.strip():
            chat.append({"role": "system", "content": system_prompt})
        chat += [{"role": m.role, "content": m.content} for m in messages]

        request: dict[str, Any] = {
            "model": self.model_id,
            "messages": chat,
            "stream": True,
            # Upper limit on the reply length. Groq's free plan counts this against your
            # tokens-per-minute allowance, so it's kept modest.
            "max_completion_tokens": 4096,
        }
        # gpt-oss models think before answering; "low" keeps chat replies quick.
        if self.model_id.startswith("openai/gpt-oss"):
            request["reasoning_effort"] = "low"
        return request

    def describe_error(self, error: groq.APIError) -> str:
        """Turn an SDK error into a sentence the user can act on (most specific first)."""
        if isinstance(error, groq.AuthenticationError):
            return "Groq rejected the API key. Check GROQ_API_KEY in backend/.env."
        if isinstance(error, groq.NotFoundError):
            return f"Groq doesn't know the model '{self.model_id}'. Check GROQ_MODEL in backend/.env."
        if isinstance(error, groq.RateLimitError):
            return "Groq's free rate limit was reached. Wait a minute and try again."
        if isinstance(error, groq.APIConnectionError):
            return "Couldn't reach the Groq API. Check your internet connection."
        if isinstance(error, groq.APIStatusError):
            return f"Groq error {error.status_code}: {api_error_message(error)}"
        return f"Groq error: {error}"


def api_error_message(error: groq.APIStatusError) -> str:
    """The human-readable message inside an API error response, if there is one."""
    body = error.body
    if isinstance(body, dict) and isinstance(body.get("error"), dict):
        return body["error"].get("message", str(error))
    return str(error)

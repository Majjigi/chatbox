"""
Talks to Google's Gemini models through the official `google-genai` SDK.

Get an API key at https://aistudio.google.com/apikey
Docs: https://ai.google.dev/gemini-api/docs
"""

from collections.abc import AsyncIterator

from google import genai
from google.genai import errors, types

from app.providers.base import ChatChunk, ChatProvider, ProviderError
from app.schemas.chat import ChatMessage


class GeminiProvider(ChatProvider):
    def __init__(self, api_key: str, model_id: str):
        self.client = genai.Client(api_key=api_key)
        self.model_id = model_id

    async def stream_reply(
        self, messages: list[ChatMessage], system_prompt: str
    ) -> AsyncIterator[ChatChunk]:
        # None (rather than "") tells Gemini there is no system prompt.
        config = types.GenerateContentConfig(system_instruction=system_prompt.strip() or None)
        usage = None

        try:
            # `client.aio` is the async version of the client: it waits without blocking the server.
            stream = await self.client.aio.models.generate_content_stream(
                model=self.model_id,
                contents=to_gemini_contents(messages),
                config=config,
            )
            async for chunk in stream:
                if chunk.text:
                    yield ChatChunk(text=chunk.text)
                # Chunks carry running token totals; the last one has the final numbers.
                if chunk.usage_metadata:
                    usage = chunk.usage_metadata
        except errors.APIError as error:
            raise ProviderError(self.describe_error(error)) from error

        if usage is not None:
            yield ChatChunk(
                input_tokens=usage.prompt_token_count,
                # Gemini counts its hidden "thinking" tokens separately. They are billed as
                # output, so we add them in (Claude's output count already includes them).
                output_tokens=(usage.candidates_token_count or 0) + (usage.thoughts_token_count or 0),
            )

    def describe_error(self, error: errors.APIError) -> str:
        """Turn an SDK error into a sentence the user can act on."""
        if "API key" in (error.message or ""):
            return "Gemini rejected the API key. Check GEMINI_API_KEY in backend/.env."
        if error.code == 404:
            return f"Gemini doesn't know the model '{self.model_id}'. Check GEMINI_MODEL in backend/.env."
        if error.code == 429:
            return "Gemini's rate limit or free quota was reached. Wait a minute and try again."
        return f"Gemini error {error.code}: {error.message}"


def to_gemini_contents(messages: list[ChatMessage]) -> list[types.Content]:
    """Convert our messages to Gemini's format. Gemini calls the assistant role "model"."""
    return [
        types.Content(
            role="model" if message.role == "assistant" else "user",
            parts=[types.Part.from_text(text=message.content)],
        )
        for message in messages
    ]

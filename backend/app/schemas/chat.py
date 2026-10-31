"""
The shapes of the data that travels between the Angular app and this API.

Each class lists its fields with a type. FastAPI uses them to check incoming
requests automatically: a request with a missing or wrong field is rejected
with a 422 error before our code even runs.
"""

from typing import Literal

from pydantic import BaseModel, Field, field_validator

# ---------------------------------------------------------------------------
# Requests
# ---------------------------------------------------------------------------


class ChatMessage(BaseModel):
    """One message in the conversation."""

    # Literal means "only these exact values are allowed".
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1)


class ChatRequest(BaseModel):
    """Body of POST /api/chat/stream."""

    # Which model should answer — one of the ids from GET /api/models.
    model: str
    # Instructions that steer the model ("You are a pirate…"). Empty means none.
    system_prompt: str = Field(default="", max_length=10_000)
    # The whole conversation so far, oldest first. The last one is the new question.
    # Models don't remember earlier requests, so the history is sent every time.
    messages: list[ChatMessage] = Field(min_length=1)

    # A validator is extra checking code that runs after the field types are checked.
    @field_validator("messages")
    @classmethod
    def last_message_is_from_user(cls, messages: list[ChatMessage]) -> list[ChatMessage]:
        if messages[-1].role != "user":
            raise ValueError("the last message must come from the user")
        return messages


# ---------------------------------------------------------------------------
# Responses
# ---------------------------------------------------------------------------


class ModelInfo(BaseModel):
    """One choice in the model dropdown (returned by GET /api/models)."""

    id: str
    label: str
    provider: Literal["demo", "gemini", "claude"]
    # False when the model's API key isn't set in .env — the dropdown greys it out.
    available: bool


# ---------------------------------------------------------------------------
# Stream events
#
# The reply is not sent as one JSON response. It is sent as a stream of small
# events, and every event has a `type` so the browser knows what it holds.
# ---------------------------------------------------------------------------


class TokenEvent(BaseModel):
    """The next piece of the reply text."""

    type: Literal["token"] = "token"
    text: str


class DoneEvent(BaseModel):
    """The reply is finished. Carries the stats shown under the answer."""

    type: Literal["done"] = "done"
    # Tokens are the word-pieces models read and write (and bill by).
    # None means the model didn't report a count.
    input_tokens: int | None
    output_tokens: int | None
    # Milliseconds from receiving the request until the reply finished.
    total_ms: int
    # Milliseconds until the first piece of text arrived (how long you stared at "…").
    first_token_ms: int | None


class ErrorEvent(BaseModel):
    """Something went wrong while the reply was streaming."""

    type: Literal["error"] = "error"
    message: str

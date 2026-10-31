"""
POST /api/chat/stream — sends the conversation to a model and streams the reply back.

How the streaming works
-----------------------
A normal endpoint builds the whole answer, then returns it in one go. This one
returns a `StreamingResponse`: every string our generator `yield`s is sent to the
browser straight away, while the model is still writing the rest.

The strings use the Server-Sent Events (SSE) format: each event is a line that
starts with `data: ` followed by JSON, and a blank line marks the end of the event.

    data: {"type": "token", "text": "Hel"}

    data: {"type": "token", "text": "lo!"}

    data: {"type": "done", "input_tokens": 12, "output_tokens": 3, "total_ms": 840, ...}

The event types are defined in app/schemas/chat.py.
"""

import logging
import time
from collections.abc import AsyncIterator

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.providers.base import ChatProvider, ProviderError
from app.providers.registry import ModelUnavailableError, UnknownModelError, get_provider
from app.schemas.chat import ChatRequest, DoneEvent, ErrorEvent, TokenEvent

logger = logging.getLogger(__name__)

# Every route in this file starts with /chat (main.py adds /api in front).
router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/stream")
async def stream_chat(request: ChatRequest) -> StreamingResponse:
    # Problems we can spot *before* streaming starts become normal HTTP errors.
    try:
        provider = get_provider(request.model)
    except UnknownModelError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(error))
    except ModelUnavailableError as error:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(error))

    return StreamingResponse(
        stream_reply_events(provider, request),
        media_type="text/event-stream",
        # Ask browsers and proxies to pass each event on immediately, not cache or buffer it.
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


async def stream_reply_events(provider: ChatProvider, request: ChatRequest) -> AsyncIterator[str]:
    """Run the model and turn its output into SSE events, timing it along the way.

    If the browser disconnects (the user pressed Stop), FastAPI stops this
    generator, which also closes the connection to the model.
    """
    started_at = time.perf_counter()  # a precise stopwatch reading, in seconds
    first_token_ms: int | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None

    try:
        async for chunk in provider.stream_reply(request.messages, request.system_prompt):
            if chunk.text:
                if first_token_ms is None:
                    first_token_ms = elapsed_ms(started_at)
                yield to_sse(TokenEvent(text=chunk.text))

            # The provider's final chunk carries the token counts.
            if chunk.input_tokens is not None:
                input_tokens = chunk.input_tokens
            if chunk.output_tokens is not None:
                output_tokens = chunk.output_tokens

    # The HTTP status (200 OK) was sent with the first event, so from here on
    # errors can't become an HTTP error code — they travel as an "error" event.
    except ProviderError as error:
        yield to_sse(ErrorEvent(message=str(error)))
        return
    except Exception:
        logger.exception("Unexpected error while streaming a reply")
        yield to_sse(ErrorEvent(message="Unexpected server error. See the backend terminal for details."))
        return

    yield to_sse(
        DoneEvent(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_ms=elapsed_ms(started_at),
            first_token_ms=first_token_ms,
        )
    )


def to_sse(event: BaseModel) -> str:
    """Format one event the SSE way: `data: <json>` followed by a blank line."""
    return f"data: {event.model_dump_json()}\n\n"


def elapsed_ms(started_at: float) -> int:
    """Milliseconds since `started_at`."""
    return round((time.perf_counter() - started_at) * 1000)

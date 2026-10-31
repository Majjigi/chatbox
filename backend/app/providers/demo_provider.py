"""
A pretend model that runs inside the backend. It needs no API key and no internet.

It lets you try the whole streaming pipeline (backend → browser) for free, and
the automated tests use it too.
"""

import asyncio
import re
import textwrap
from collections.abc import AsyncIterator

from app.providers.base import ChatChunk, ChatProvider
from app.schemas.chat import ChatMessage

# Pause between words so you can watch the reply appear. (Tests set this to 0.)
WORD_DELAY_SECONDS = 0.04


class DemoProvider(ChatProvider):
    """Streams a canned reply word by word."""

    # `async def` + `yield` makes an *async generator*: a function that hands out
    # values one at a time and can wait (`await`) in between without blocking the server.
    async def stream_reply(
        self, messages: list[ChatMessage], system_prompt: str
    ) -> AsyncIterator[ChatChunk]:
        reply = build_demo_reply(question=messages[-1].content, system_prompt=system_prompt)

        # Split into words, keeping the space after each one: "Hi there" → ["Hi ", "there"].
        words = re.findall(r"\S+\s*", reply)
        for word in words:
            await asyncio.sleep(WORD_DELAY_SECONDS)
            yield ChatChunk(text=word)

        # Real models count tokens (pieces of words). The demo simply counts words.
        input_words = len(system_prompt.split()) + sum(len(m.content.split()) for m in messages)
        yield ChatChunk(input_tokens=input_words, output_tokens=len(words))


def build_demo_reply(question: str, system_prompt: str) -> str:
    """The text the demo model "says" — it repeats back what it received."""
    if system_prompt.strip():
        prompt_line = f'Your system prompt is: "{shorten(system_prompt)}". A real model would follow it.'
    else:
        prompt_line = "No system prompt was sent with this message."

    return (
        "Hi! I'm the demo model. I live inside the backend, so I work without an API key.\n\n"
        f'You said: "{shorten(question)}"\n\n'
        f"{prompt_line}\n\n"
        "Each word of this answer was sent to you separately, so you can watch streaming "
        "work from end to end. Add an API key in backend/.env to talk to a real model."
    )


def shorten(text: str) -> str:
    """Trim long text to about 200 characters so the demo reply stays readable."""
    return textwrap.shorten(text, width=200, placeholder="…")

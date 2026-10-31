"""
The common shape that every model "provider" follows.

A provider is the piece of code that knows how to talk to one AI service
(Groq, Claude, or the offline demo). They all offer the same method,
`stream_reply(...)`, so the chat route can use any of them without knowing
which one it has. Each provider file translates that one call into its own SDK.
"""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass

from app.schemas.chat import ChatMessage


@dataclass
class ChatChunk:
    """One piece of a streamed reply.

    Most chunks carry `text`. The provider's final chunk carries the token
    counts instead (models only know the totals once they've finished).
    """

    text: str = ""
    input_tokens: int | None = None
    output_tokens: int | None = None


class ProviderError(Exception):
    """A problem worth showing to the user, such as "your API key is invalid"."""


class ChatProvider(ABC):
    """Base class for every provider. ABC = "abstract base class": a template
    that can't be used directly, only through a subclass that fills in the methods."""

    @abstractmethod
    def stream_reply(
        self, messages: list[ChatMessage], system_prompt: str
    ) -> AsyncIterator[ChatChunk]:
        """Yield the reply piece by piece, ending with a chunk that has the token counts.

        Raise `ProviderError` with a friendly message if the model call fails.
        """

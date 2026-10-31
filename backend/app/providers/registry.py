"""
The list of models the app offers, and a way to get the provider for one of them.

To add another model (e.g. OpenAI), write a provider class like the ones in this
folder, then add it to `list_models()` and `_create_provider()` below.
"""

from app.core.config import settings
from app.providers.base import ChatProvider
from app.providers.claude_provider import ClaudeProvider
from app.providers.demo_provider import DemoProvider
from app.providers.groq_provider import GroqProvider
from app.schemas.chat import ModelInfo

DEMO_MODEL_ID = "demo"


class UnknownModelError(Exception):
    """The requested model id isn't in the list."""


class ModelUnavailableError(Exception):
    """The model is in the list, but its API key isn't set."""


def list_models() -> list[ModelInfo]:
    """Every model for the dropdown, in display order.

    The app pre-selects the first available one, so real models come first.
    """
    return [
        ModelInfo(
            id=settings.groq_model,
            label=f"Groq · {settings.groq_model}",
            provider="groq",
            available=bool(settings.groq_api_key),
        ),
        ModelInfo(
            id=settings.claude_model,
            label=f"Claude · {settings.claude_model}",
            provider="claude",
            available=bool(settings.anthropic_api_key),
        ),
        ModelInfo(id=DEMO_MODEL_ID, label="Demo model (offline)", provider="demo", available=True),
    ]


# Providers are created the first time they're needed and then reused,
# because each one keeps its own network connection pool.
_providers: dict[str, ChatProvider] = {}


def get_provider(model_id: str) -> ChatProvider:
    """Return the provider for `model_id`, or raise if it can't be used."""
    # Find the first model with a matching id, or None if there isn't one.
    model = next((m for m in list_models() if m.id == model_id), None)

    if model is None:
        raise UnknownModelError(f"Unknown model '{model_id}'.")
    if not model.available:
        raise ModelUnavailableError(f"{model.label} has no API key. Add it to backend/.env.")

    if model_id not in _providers:
        _providers[model_id] = _create_provider(model)
    return _providers[model_id]


def _create_provider(model: ModelInfo) -> ChatProvider:
    if model.provider == "groq":
        return GroqProvider(api_key=settings.groq_api_key, model_id=model.id)
    if model.provider == "claude":
        return ClaudeProvider(api_key=settings.anthropic_api_key, model_id=model.id)
    if model.provider == "demo":
        return DemoProvider()
    raise UnknownModelError(f"No provider for '{model.provider}'.")

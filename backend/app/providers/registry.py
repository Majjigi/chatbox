"""
The list of models the app offers, and a way to get the provider for one of them.

To add another model, write a provider class (see demo_provider.py) and add it
to `list_models()` and `_create_provider()` below.
"""

from app.providers.base import ChatProvider
from app.providers.demo_provider import DemoProvider
from app.schemas.chat import ModelInfo

DEMO_MODEL_ID = "demo"


class UnknownModelError(Exception):
    """The requested model id isn't in the list."""


class ModelUnavailableError(Exception):
    """The model is in the list, but its API key isn't set."""


def list_models() -> list[ModelInfo]:
    """Every model for the dropdown, in display order."""
    return [
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
    if model.provider == "demo":
        return DemoProvider()
    raise UnknownModelError(f"No provider for '{model.provider}'.")

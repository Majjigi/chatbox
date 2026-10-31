"""
Shared test setup. pytest loads this file automatically before running the tests.

A *fixture* is a helper that pytest runs for a test. A test asks for one simply
by naming it as a parameter, e.g. `def test_something(client): ...`.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.providers import demo_provider


@pytest.fixture
def client() -> TestClient:
    """Calls the app directly in memory — no running server needed."""
    return TestClient(app)


@pytest.fixture(autouse=True)  # autouse = applies to every test without asking
def instant_demo_model(monkeypatch):
    """Make the demo model reply without its pause between words, so tests run fast."""
    monkeypatch.setattr(demo_provider, "WORD_DELAY_SECONDS", 0)

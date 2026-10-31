from app.core.config import settings


def find(models: list[dict], provider: str) -> dict:
    return next(m for m in models if m["provider"] == provider)


def test_models_list_includes_the_demo_model(client):
    response = client.get("/api/models")

    assert response.status_code == 200
    demo = find(response.json(), "demo")
    assert demo["id"] == "demo"
    assert demo["available"] is True


def test_models_without_an_api_key_are_unavailable(client):
    models = client.get("/api/models").json()

    assert find(models, "groq")["available"] is False
    assert find(models, "claude")["available"] is False


def test_models_with_an_api_key_are_available(client, monkeypatch):
    monkeypatch.setattr(settings, "groq_api_key", "test-key")
    monkeypatch.setattr(settings, "anthropic_api_key", "test-key")

    models = client.get("/api/models").json()

    assert find(models, "groq")["available"] is True
    assert find(models, "groq")["id"] == settings.groq_model
    assert find(models, "claude")["available"] is True
    assert find(models, "claude")["id"] == settings.claude_model

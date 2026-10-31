def test_models_list_includes_the_demo_model(client):
    response = client.get("/api/models")

    assert response.status_code == 200
    demo = next(m for m in response.json() if m["id"] == "demo")
    assert demo["provider"] == "demo"
    assert demo["available"] is True

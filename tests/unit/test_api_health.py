from bna_market.web.app import create_app


def test_health_endpoint_registered():
    app = create_app({"TESTING": True})
    client = app.test_client()

    response = client.get("/api/health")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "healthy"
    assert "/api/health" in payload.get("endpoints", [])

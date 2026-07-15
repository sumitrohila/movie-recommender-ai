from fastapi.testclient import TestClient

def test_recommend_endpoint(client: TestClient):
    response = client.post("/api/v1/recommend", json={
        "user_input": "I love sci-fi",
        "mode": "chain"
    })
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
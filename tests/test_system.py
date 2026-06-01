from fastapi.testclient import TestClient


def test_metadata_endpoint(client: TestClient) -> None:
    response = client.get("/metadata")

    assert response.status_code == 200
    assert response.json() == {
        "name": "FinPilot",
        "version": "0.1.0",
        "docs_url": "/docs",
    }

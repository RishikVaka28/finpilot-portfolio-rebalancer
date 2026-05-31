from fastapi.testclient import TestClient


def test_portfolio_crud_requires_owner_token(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    unauthenticated = client.get("/api/v1/portfolios")
    assert unauthenticated.status_code == 401

    created = client.post(
        "/api/v1/portfolios",
        json={"name": "Long Term"},
        headers=auth_headers,
    )
    assert created.status_code == 201
    portfolio_id = created.json()["id"]

    listed = client.get("/api/v1/portfolios", headers=auth_headers)
    assert listed.status_code == 200
    assert listed.json()[0]["name"] == "Long Term"

    updated = client.put(
        f"/api/v1/portfolios/{portfolio_id}",
        json={"name": "Retirement"},
        headers=auth_headers,
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Retirement"

    deleted = client.delete(f"/api/v1/portfolios/{portfolio_id}", headers=auth_headers)
    assert deleted.status_code == 204


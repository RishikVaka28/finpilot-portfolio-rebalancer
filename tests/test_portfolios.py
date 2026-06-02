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


def test_portfolio_summary_reports_value_and_allocation(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    created = client.post(
        "/api/v1/portfolios",
        json={"name": "Allocation Check"},
        headers=auth_headers,
    )
    portfolio_id = created.json()["id"]

    client.post(
        f"/api/v1/portfolios/{portfolio_id}/holdings",
        json={"symbol": "VTI", "quantity": "8", "price": "100"},
        headers=auth_headers,
    )
    client.post(
        f"/api/v1/portfolios/{portfolio_id}/holdings",
        json={"symbol": "BND", "quantity": "2", "price": "100"},
        headers=auth_headers,
    )

    response = client.get(
        f"/api/v1/portfolios/{portfolio_id}/summary",
        headers=auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["portfolio_name"] == "Allocation Check"
    assert body["total_value"] == "1000.00"
    assert body["holdings_count"] == 2
    allocations = {item["symbol"]: item for item in body["allocations"]}
    assert allocations["VTI"]["market_value"] == "800.00"
    assert allocations["VTI"]["current_percent"] == "80.0000"
    assert allocations["BND"]["market_value"] == "200.00"
    assert allocations["BND"]["current_percent"] == "20.0000"


def test_empty_portfolio_summary_returns_zero_total(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    created = client.post(
        "/api/v1/portfolios",
        json={"name": "Empty"},
        headers=auth_headers,
    )
    portfolio_id = created.json()["id"]

    response = client.get(
        f"/api/v1/portfolios/{portfolio_id}/summary",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["total_value"] == "0.00"
    assert response.json()["allocations"] == []

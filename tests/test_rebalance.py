from fastapi.testclient import TestClient


def _create_portfolio(client: TestClient, headers: dict[str, str]) -> int:
    response = client.post("/api/v1/portfolios", json={"name": "Core"}, headers=headers)
    assert response.status_code == 201
    return int(response.json()["id"])


def test_rebalance_recommendations(client: TestClient, auth_headers: dict[str, str]) -> None:
    portfolio_id = _create_portfolio(client, auth_headers)

    client.post(
        f"/api/v1/portfolios/{portfolio_id}/holdings",
        json={"symbol": "VTI", "quantity": "10", "price": "100"},
        headers=auth_headers,
    )
    client.post(
        f"/api/v1/portfolios/{portfolio_id}/holdings",
        json={"symbol": "BND", "quantity": "5", "price": "100"},
        headers=auth_headers,
    )
    client.post(
        f"/api/v1/portfolios/{portfolio_id}/targets",
        json={"symbol": "VTI", "target_percent": "60"},
        headers=auth_headers,
    )
    client.post(
        f"/api/v1/portfolios/{portfolio_id}/targets",
        json={"symbol": "BND", "target_percent": "40"},
        headers=auth_headers,
    )

    response = client.get(f"/api/v1/portfolios/{portfolio_id}/rebalance", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["total_value"] == "1500.00"
    assert body["total_buy_value"] == "100.00"
    assert body["total_sell_value"] == "100.00"
    assert body["is_balanced"] is False
    recommendations = {item["symbol"]: item for item in body["recommendations"]}
    assert recommendations["VTI"]["action"] == "SELL"
    assert recommendations["VTI"]["drift_percent"] == "6.6667"
    assert recommendations["VTI"]["difference_value"] == "-100.00"
    assert recommendations["BND"]["action"] == "BUY"
    assert recommendations["BND"]["drift_percent"] == "-6.6667"
    assert recommendations["BND"]["difference_value"] == "100.00"


def test_rebalance_rejects_targets_that_do_not_sum_to_100(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    portfolio_id = _create_portfolio(client, auth_headers)
    client.post(
        f"/api/v1/portfolios/{portfolio_id}/holdings",
        json={"symbol": "VTI", "quantity": "1", "price": "100"},
        headers=auth_headers,
    )
    client.post(
        f"/api/v1/portfolios/{portfolio_id}/targets",
        json={"symbol": "VTI", "target_percent": "80"},
        headers=auth_headers,
    )

    response = client.get(f"/api/v1/portfolios/{portfolio_id}/rebalance", headers=auth_headers)

    assert response.status_code == 422
    assert "sum to 100" in response.json()["detail"]


def test_rebalance_identifies_balanced_portfolio(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    portfolio_id = _create_portfolio(client, auth_headers)
    client.post(
        f"/api/v1/portfolios/{portfolio_id}/holdings",
        json={"symbol": "VTI", "quantity": "6", "price": "100"},
        headers=auth_headers,
    )
    client.post(
        f"/api/v1/portfolios/{portfolio_id}/holdings",
        json={"symbol": "BND", "quantity": "4", "price": "100"},
        headers=auth_headers,
    )
    client.post(
        f"/api/v1/portfolios/{portfolio_id}/targets",
        json={"symbol": "VTI", "target_percent": "60"},
        headers=auth_headers,
    )
    client.post(
        f"/api/v1/portfolios/{portfolio_id}/targets",
        json={"symbol": "BND", "target_percent": "40"},
        headers=auth_headers,
    )

    response = client.get(f"/api/v1/portfolios/{portfolio_id}/rebalance", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["is_balanced"] is True
    assert response.json()["total_buy_value"] == "0.00"
    assert response.json()["total_sell_value"] == "0.00"
    assert all(item["action"] == "HOLD" for item in response.json()["recommendations"])

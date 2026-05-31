from fastapi.testclient import TestClient


def test_register_and_login(client: TestClient) -> None:
    register_response = client.post(
        "/api/v1/auth/register",
        json={"email": "person@example.com", "password": "strongpassword"},
    )

    assert register_response.status_code == 201
    assert register_response.json()["email"] == "person@example.com"

    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": "person@example.com", "password": "strongpassword"},
    )

    assert login_response.status_code == 200
    assert login_response.json()["token_type"] == "bearer"
    assert login_response.json()["access_token"]


def test_duplicate_registration_is_rejected(client: TestClient) -> None:
    payload = {"email": "person@example.com", "password": "strongpassword"}

    assert client.post("/api/v1/auth/register", json=payload).status_code == 201
    assert client.post("/api/v1/auth/register", json=payload).status_code == 409


import json
from typing import Dict

from fastapi.testclient import TestClient

from core.configs import settings
from tests.utils.utils import random_email, random_lower_string


def test_create_token():
    pass


def test_login_for_access_token():
    pass


def test_get_current_user_from_token():
    pass


def test_get_current_user_from_token(client: TestClient) -> None:
    test_email = random_email()
    test_password = random_lower_string()

    # Create a new user
    user_response = client.post(
        f"{settings.API_V1_STR}/users/register",
        json.dumps({"email": test_email, "password": test_password}),
    )
    assert user_response.status_code == 200

    # We used 'username' instead of 'email' field for OAuth2PasswordRequestForm
    login_data = {
        "username": test_email,
        "password": test_password,
    }
    r = client.post(
        f"{settings.API_V1_STR}/auth/access-token", data=json.dumps(login_data)
    )
    tokens = r.json()
    assert r.status_code == 200
    assert "access_token" in tokens
    assert tokens["access_token"]


def test_use_access_token(
    client: TestClient, superuser_token_headers: Dict[str, str]
) -> None:
    r = client.post(
        f"{settings.API_V1_STR}/login/test-token",
        headers=superuser_token_headers,
    )
    result = r.json()
    assert r.status_code == 200
    assert "email" in result

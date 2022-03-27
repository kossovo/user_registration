import json

import pytest

from backend.core.configs import settings
from backend.tests.conftest import normal_user_token_headers
from backend.tests.utils.utils import random_email, random_lower_string


@pytest.mark.skip
def test_login_for_access_token(client):  # FXIME

    data = {
        "email": random_email(),
        "password": random_lower_string(),
    }
    response = client.post(f"{settings.API_V1_STR}/auth/access-token", json.dumps(data))

    assert response.status_code == 200
    assert response.token_type == "bearer"


@pytest.mark.skip
def test_get_current_user_from_token(client):  # FXIME
    """
    Check user login using API
    """
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
        f"{settings.API_V1_STR}/auth/access-token",
        data=json.dumps(login_data),
        headers=normal_user_token_headers,
    )
    tokens = r.json()
    assert r.status_code == 200
    assert "access_token" in tokens
    assert tokens["access_token"]

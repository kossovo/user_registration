import json

from backend.core.configs import settings
from backend.tests.utils.utils import random_email, random_lower_string


def test_create_user_ok(client):
    data = {
        "email": random_email(),
        "password": random_lower_string(),
    }
    response = client.post(f"{settings.API_V1_STR}/users/register", json.dumps(data))
    assert response.status_code == 200
    assert response.json().get("email") == data.get("email")
    assert response.json().get("is_active") is True
    assert not response.json().get("password")


def test_create_user_can_send_email(client):
    pass


def test_we_can_create_user_withoud_send_email(client):
    pass

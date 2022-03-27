import json

import pytest

from backend.core.configs import settings
from backend.db.repository.users import get_user_by_email
from backend.schemas.users import UserCreate
from backend.tests.utils.utils import random_email, random_lower_string


def test_api_register(client):
    data = {
        "email": random_email(),
        "password": random_lower_string(),
    }
    response = client.post(f"{settings.API_V1_STR}/users/register", json.dumps(data))
    assert response.status_code == 200
    assert response.json().get("email") == data.get("email")
    assert response.json().get("is_active") is True
    assert not response.json().get("password")


def test_api_get_user(client):
    data = {
        "email": random_email(),
        "password": random_lower_string(),
    }
    response = client.post(f"{settings.API_V1_STR}/users/register", json.dumps(data))
    assert response.status_code == 200


def test_api_all_users(client):
    # Check actual users store in the database
    first_response = client.get(f"{settings.API_V1_STR}/users/all")
    assert first_response.status_code == 200
    first_len = len(first_response.json())

    # Create 10 users
    for i in range(10):
        data = {
            "email": random_email(),
            "password": random_lower_string(),
        }
        client.post(
            f"{settings.API_V1_STR}/users/register",
            json.dumps(data),
        )
    response = client.get(f"{settings.API_V1_STR}/users/all")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 10 + first_len


def test_api_update_user(client, db):
    data = {
        "email": random_email(),
        "password": random_lower_string(),
    }
    new_password = random_lower_string()
    assert new_password != data.get("password")

    response = client.post(f"{settings.API_V1_STR}/users/register", json.dumps(data))
    assert response.status_code == 200
    created_user = get_user_by_email(email=data.get("email"), db=db)

    response_up = client.put(
        f"{settings.API_V1_STR}/users/update/{created_user.id}",
        data=json.dumps({"password": new_password}),
    )
    assert response_up.status_code == 200
    assert response_up.json().get("detail") == "Successfully updated"


@pytest.mark.skip
def test_api_delete_user(client, db, verified_user_token_headers):  # FIXME
    """
    Only users which have verified their email address can delete a record
    """
    data = {
        "email": random_email(),
        "password": random_lower_string(),
    }

    response = client.post(f"{settings.API_V1_STR}/users/register", json.dumps(data))
    user_to_delete = get_user_by_email(email=data.get("email"), db=db)

    response = client.post(
        f"{settings.API_V1_STR}/users/delete/{user_to_delete.id}",
        json.dumps(data),
        headers=verified_user_token_headers,
    )
    assert response.status_code == 200

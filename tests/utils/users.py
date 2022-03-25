from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from core.configs import settings
from db.models.users import Users
from db.repository.users import (create_new_user, get_user_by_email,
                                 update_user_by_id)
from schemas.users import UserCreate, UserUpdate
from tests.utils.utils import random_email, random_lower_string


def user_authentication_headers(
    *, client: TestClient, email: str, password: str
) -> Dict[str, str]:
    data = {"email": email, "password": password}

    response = client.post(f"{settings.API_V1_STR}/login/access-token", data=data)
    auth_token = response.json().get("access_token")
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers


def create_random_user(db: Session) -> Users:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = create_new_user(user=user_in, db=db)
    return user


def authentication_token_from_email(
    *, client: TestClient, email: str, db: Session
) -> Dict[str, str]:
    """
    Return a valid token for the user with given email.
    If the user doesn't exist it is created first.
    """
    password = random_lower_string()
    user = get_user_by_email(email=email, db=db)
    if not user:
        user_in_create = UserCreate(email=email, password=password)
        user = create_new_user(user=user_in_create, db=db)
    else:
        user_in_update = UserUpdate(password=password)
        user = update_user_by_id(user_id=user.id, user=user_in_update, db=db)

    return user_authentication_headers(client=client, email=email, password=password)

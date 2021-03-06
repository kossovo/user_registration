from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.core.configs import settings
from backend.db.models.users import Users
from backend.db.repository.users import (
    create_new_user,
    get_user_by_email,
    update_user_by_id,
)
from backend.schemas.users import UserCreate, UserUpdate
from backend.tests.utils.utils import random_email, random_lower_string


def user_authentication_headers(
    *, client: TestClient, email: str, password: str
) -> Dict[str, str]:
    data = {"email": email, "password": password}

    response = client.post(f"{settings.API_V1_STR}/auth/access-token", data=data)
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
    *, client: TestClient, email: str, db: Session, **kwargs
) -> Dict[str, str]:
    """
    Return a valid token for the user with given email.
    If the user doesn't exist it is created first.
    """
    password = random_lower_string()
    user = get_user_by_email(email=email, db=db)
    user_up = UserUpdate()

    if not user:
        user_in_create = UserCreate(email=email, password=password)
        user = create_new_user(user=user_in_create, db=db)
    else:
        if "is_verify" in kwargs:
            user_up.is_verified = True

        user_up.password = password
        user = update_user_by_id(user_id=user.id, user=user_up, db=db)
    return user_authentication_headers(client=client, email=email, password=password)

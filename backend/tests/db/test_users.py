import pytest
from sqlalchemy.orm import Session

from backend.core.hashing import Hasher
from backend.db.repository.users import (
    authenticate,
    create_new_user,
    get_user_by_id,
    is_active,
    update_user_by_id,
)
from backend.schemas.users import UserCreate, UserUpdate
from backend.tests.utils.utils import random_email, random_lower_string


def test_create_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = create_new_user(user=user_in, db=db)
    assert user.email == email
    assert hasattr(user, "hashed_password")


def test_authenticate_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = create_new_user(user=user_in, db=db)
    authenticated_user = authenticate(email=email, password=password, db=db)
    assert authenticated_user
    assert user.email == authenticated_user.email


def test_not_authenticate_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user = authenticate(email=email, password=password, db=db)
    assert user is None


def test_check_if_user_is_active(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = create_new_user(user=user_in, db=db)
    activate_user = is_active(user)
    assert activate_user is True


def test_check_if_user_is_active_inactive(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password, disabled=True)
    user = create_new_user(user=user_in, db=db)

    activate_user = is_active(user)
    assert activate_user


def test_user_isnt_automatically_verified(db: Session) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    user = create_new_user(user=user_in, db=db)
    assert user.is_verified is False


@pytest.mark.skip  # FIXME
def test_update_user(db: Session) -> None:
    password = random_lower_string()
    email = random_email()
    user_in = UserCreate(email=email, password=password)
    user = create_new_user(user=user_in, db=db)
    assert user

    new_password = random_lower_string()
    user_in_update = UserUpdate(password=new_password)
    update_user_by_id(user_id=user.id, user=user_in_update, db=db)

    user_2 = get_user_by_id(user_id=user.id, db=db)

    assert user_2
    assert user.email == user_2.email
    assert Hasher.verify_password(new_password, user_2.hashed_password)


def test_verify_user(db: Session):
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    user = create_new_user(user=user_in, db=db)
    assert user.is_verified is False

    # FIXME

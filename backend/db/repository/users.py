from typing import Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from backend.core.hashing import Hasher
from backend.db.models.users import Users
from backend.schemas.users import UserCreate, UserUpdate


def create_new_user(user: UserCreate, db: Session) -> Users:
    created_user = Users(
        email=user.email,
        hashed_password=Hasher.get_password_hash(user.password),
        is_active=user.is_active,
    )
    db.add(created_user)
    db.commit()
    db.refresh(created_user)

    return created_user


def get_user_by_email(email: str, db: Session) -> Users:
    return db.query(Users).filter(Users.email == email).first()


def get_user_by_id(user_id: int, db: Session) -> Users:
    return db.query(Users).filter(Users.id == user_id).first()


def update_user_by_id(user_id: int, user: UserUpdate, db: Session):
    existing_user = db.query(Users).filter(Users.id == user_id)
    if not existing_user.first():
        return None

    update_data = jsonable_encoder(user.dict(exclude_unset=True))
    existing_user.update(update_data)
    db.commit()
    return existing_user.first()


def authenticate(email: str, password: str, db: Session) -> Optional[Users]:
    user = get_user_by_email(email=email, db=db)
    if not user:
        return None
    if not Hasher.verify_password(
        plain_password=password, hash_password=user.hashed_password
    ):
        return None
    return user


def is_active(user: Users) -> bool:
    return user.is_active


def is_verified(user: Users) -> bool:
    return user.is_verified

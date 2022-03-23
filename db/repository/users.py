from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from core.hashing import Hasher
from db.models.users import Users
from schemas.users import UserCreate, UserValidation


def create_new_user(user: UserCreate, db: Session) -> Users:
    created_user = Users(
        # TODO: Add a uuid field
        # username=user.username,
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


def update_user_by_id(user_id: int, user: UserValidation, db: Session):
    existing_user = db.query(Users).filter(Users.id == user_id)
    if not existing_user.first():
        return 0

    update_data = jsonable_encoder(user.dict(exclude_unset=True))
    existing_user.update(update_data)
    db.commit()
    return 1

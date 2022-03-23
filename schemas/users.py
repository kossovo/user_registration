import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import UUID4, BaseModel, EmailStr, Field


class CreateUpdateDictModel(BaseModel):
    def create_update_dict(self):
        return self.dict(
            exclude_unset=True,
            exclude={
                "id",
                "is_active",
                "is_verified",
                "is_validation_mail_send",
                "validation_date",
            },
        )


class BaseUser(CreateUpdateDictModel):
    """Base User model."""

    id: UUID4 = Field(default_factory=uuid.uuid4)
    email: EmailStr
    is_active: bool = True
    is_verified: bool = False


class UserCreate(CreateUpdateDictModel):
    email: EmailStr
    password: str
    is_active: Optional[bool] = True


class UserValidation(CreateUpdateDictModel):
    email: EmailStr
    is_active: Optional[bool] = True
    is_verified: Optional[bool] = True
    is_validation_mail_send: Optional[bool] = True
    validation_date: Optional[datetime] = datetime.now()


class UserShow(BaseModel):
    email: EmailStr
    is_active: bool
    is_verified: bool = False

    class Config:
        orm_mode = True

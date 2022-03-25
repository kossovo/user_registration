from datetime import datetime
from typing import Optional

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

    email: EmailStr
    is_active: Optional[bool] = True
    is_verified: bool = False


class UserCreate(BaseUser):
    """Create User model"""

    email: EmailStr
    password: str


# Properties to receive via API on update
class UserUpdate(CreateUpdateDictModel):
    """Update User model"""

    is_active: Optional[bool] = True
    password: Optional[str] = None


# In some case, we can verified users without sending email (eg. existing users)
class UserValidation(BaseUser):
    is_validation_mail_send: bool = True
    validation_date: datetime = datetime.now()


# To return via api (token)
class UserAPI(BaseUser):
    id: Optional[int] = None

    class Config:
        orm_mode = True


class UserShow(BaseUser):
    email: EmailStr
    is_active: bool
    is_verified: Optional[bool] = False

    class Config:
        orm_mode = True

from sqlalchemy import Column, DateTime, Integer, String, Boolean

from db.base import Base


class Users(Base):
    """
    Model represent a User
    """

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_validation_mail_send = Column(Boolean, default=False)
    validation_date = Column(DateTime)

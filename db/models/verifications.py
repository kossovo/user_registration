from sqlalchemy import Column, Integer, String

from db.base import Base


class CodeVerification(Base):
    """
    The objective of this model is to simulate a user code verification system
    sent by mail by storing these temporarily in the database.

    For a project in production, I would strongly recommend using a third-party system like Twilio,
    which offers a complete and secure API for validating codes by email and SMS.
    """

    # This should normally be a temporary data !
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, nullable=False, unique=True, index=True)
    hashed_code = Column(String, nullable=False)

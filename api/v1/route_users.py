from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.utils import (
    check_verify_code_token,
    generate_random_code,
    send_verification_email,
)
from core.configs import settings
from db.repository.users import create_new_user, get_user_by_email
from db.session import get_db
from schemas.mails import MessageSchema
from schemas.users import UserCreate, UserShow

router = APIRouter()


def get_verification_msg(verification_code):
    return f"""<p>Your verification code is {verification_code}</p>"""


@router.post("/register", response_model=UserShow, description="Create a new user")
async def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
) -> Any:

    user = get_user_by_email(email=user_in.email, db=db)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{user.email}' already exist",
        )

    created_user = create_new_user(user_in, db)
    if not created_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Can't create user {user_in.email}, please contact your admin",
        )

    # For a production env, I advice to use a service provider like twilio API for account validation by sms or email
    if settings.EMAILS_ENABLED and user_in.email:
        verification_code = generate_random_code(size=4)

        send_verification_email(
            email_to=user_in.email,
            verification_code=verification_code,
        )
    return created_user


@router.post("/verify-code/{email}", response_model=MessageSchema)
def verify_code(
    token: str = Body(...), code: str = Body(...), db: Session = Depends(get_db)
) -> Any:

    token_code = check_verify_code_token(token)

    if not token_code:
        raise HTTPException(status_code=400, detail="Invalid token")

    if token_code != code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification code"
        )

    return {"message": "Code successfully verified"}

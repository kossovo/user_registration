from datetime import datetime
from typing import Any, List

from fastapi import APIRouter, Depends, Form, HTTPException, status
from jose import JWTError
from sqlalchemy.orm import Session

from backend.api.utils import (
    generate_random_code,
    get_current_user_from_token,
    send_verification_email,
)
from backend.core.configs import settings
from backend.core.security import decode_jwt
from backend.db.models.users import Users
from backend.db.repository.users import (
    create_new_user,
    delete_user_by_id,
    get_user_by_email,
    get_user_by_id,
    retrieve_all_users,
    update_user_by_id,
)
from backend.db.session import get_db
from backend.schemas.users import UserCreate, UserShow, UserUpdate

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

        verify_link = send_verification_email(
            email_to=user_in.email,
            verification_code=verification_code,
        )
        print(
            f"\n *********** Verification CODE (): '{verification_code}' ******************* \n "
        )
        print(
            f"\n *********** Activation LINK (send by mail): '{verify_link}' ******************* \n \n "
        )

    return created_user


@router.post("/verify/{token}", status_code=status.HTTP_200_OK)
async def verify_email_token_code(
    token: str, code: str = Form(...), db: Session = Depends(get_db)
) -> Any:

    try:
        token_data = decode_jwt(token_string=token)
        # {'exp': 1648409190.684334, 'nbf': 1648344390, 'sub': 'TLFN', 'email': 'user3@example.com'}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can't decode the given JWT token.",
        )

    if token_data.get("sub") != code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification code"
        )

    user = get_user_by_email(email=token_data.get("email"), db=db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid token"
        )

    # Update user informations
    user_in = UserUpdate(
        is_active=True,
        is_validation_mail_send=True,
        is_verified=True,
        validation_date=datetime.now(),
    )
    update_user_by_id(user_id=user.id, user=user_in, db=db)

    return {"message": "Code successfully verified"}


@router.get("/get/{user_id}", response_model=UserShow)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = get_user_by_id(user_id=user_id, db=db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The user with id {user_id} doesn't exist",
        )
    return user


@router.get("/all", response_model=List[UserShow])
def retrieve_available_users(db: Session = Depends(get_db)):
    users = retrieve_all_users(db=db)
    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No users found in the database",
        )
    return users


@router.delete("/delete/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user_from_token),
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Access denied",
        )

    # Only authentificate user can make this action
    # If the user access rules were implemented, here we should have to check the current user access right
    # For this first version, only verified users can delete a record
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Only verified user can delete data",
        )

    user = get_user_by_id(user_id=user_id, db=db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No user with id {user_id} found",
        )

    assert delete_user_by_id(user_id=user_id, db=db)
    return {"detail": "Successfully deleted"}


@router.put("/update/{user_id}", status_code=status.HTTP_200_OK)
async def update_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
):

    # Only user owner or super admin user can delete a user
    user_search = get_user_by_id(user_id=user_id, db=db)
    if not user_search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{user_id}' not found",
        )
    update_user_by_id(user_id=user_id, user=user, db=db)
    return {"detail": "Successfully updated"}

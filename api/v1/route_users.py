from email.errors import MessageError

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.utils import create_token, generate_random_code
from core.configs import settings
from core.email import sendmail
from db.repository.users import (create_new_user, get_user_by_email,
                                 update_user_by_id)
from db.repository.verifications import (save_verification_code,
                                         verification_check)
from db.session import get_db
from schemas.token import TokenData
from schemas.users import UserCreate, UserShow, UserValidation

router = APIRouter()


def get_verification_msg(verification_code):
    return f"""<p>Your verification code is {verification_code}</p>"""


@router.post("/register", response_model=UserShow)
def create_user(
    user: UserCreate,
    response: Response,
    db: Session = Depends(get_db),
    realy_send_mail: bool = False,
):  # realy_send_mail - just for debugging

    existing_user = get_user_by_email(email=user.email, db=db)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email '{user.email}' already exist",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        created_user = create_new_user(user, db)

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Can't create user {user.email}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Send verification code by mail
    verification_code = generate_random_code(size=4)
    print(f"***************** {verification_code} ****************")

    if realy_send_mail:
        try:
            sendmail(
                mailto=user.email,
                subject="DM verification code",
                message=get_verification_msg(verification_code),
            )
        except MessageError:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Can't send verification code",
                headers={"WWW-Authenticate": "Bearer"},
            )

    # As mentioned in Code verification model, this is just for a PoC. I recommend to use twilio
    save_verification_code(TokenData(email=user.email, code=verification_code), db=db)

    # Create a token for email verification
    create_token(
        data={"sub": "register", "email": user.email, "code": verification_code},
        response=response,
        expire_minute=settings.JWT_EMAIL_TOKEN_EXPIRE_MINUTES,
    )
    return created_user


@router.post("/verify")
def verify_code(data: TokenData, db: Session = Depends(get_db)):
    """The verify token of emails have a short live (1m), if token is not anymore valid,
    we skip all and clean the Code Validation linked to this token in the data base

    Args:
        data (TokenData): Validation data
        db (Session, optional): Data base session. Defaults to Depends(get_db).

    Raises:
        HTTPException: _description_
        HTTPException: _description_
        HTTPException: _description_

    Returns:
        bool: return true if the code was verified
    """
    print(f"---------------- TOKEN: {data.code, data.email} -------------------")
    import pdb

    pdb.set_trace
    check = verification_check(data=data, db=db)

    if not check:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong verification code",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Update related user
    user = get_user_by_email(email=data.email, db=db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Can't find user {data.email}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    validation_data = UserValidation(email=data.email, is_verified=True)
    up_user = update_user_by_id(user_id=user.id, user=validation_data, db=db)
    if not up_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"You don't have the permission to update user {user.email}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return True if check else False

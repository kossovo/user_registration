from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import Response
from jose.exceptions import JWTError
from sqlalchemy.orm import Session

from api.utils import OAuth2PasswordBearerWithCookie
from core.configs import settings
from core.hashing import Hasher
from core.security import generate_jwt, decode_jwt
from db.session import get_db
from db.repository.users import get_user_by_email
from schemas.token import Token, TokenData
from schemas.users import UserCreate
from core.validators import is_valid_email

router = APIRouter()


@router.post("/token", response_model=Token)
async def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):

    # 'OAuth2PasswordRequestForm' object has no attribute 'email', so we used username file as email field
    if not is_valid_email(form_data.username):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid email address",
            headers={"WWW-Authenticate": "Bearer"},
        )

    existing_user = get_user_by_email(email=form_data.username, db=db)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{form_data.username}' already exist",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expire = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = generate_jwt(
        data={"email": existing_user.email}, expires_delta=access_token_expire
    )  # FIXME: Store user.uuid instead of user.email

    # Store access token as cookies, activate httponly for more safety
    response.set_cookie(
        key="access_token", value=f"Bearer {access_token}", httponly=True
    )

    return Token(access_token=access_token, token_type="bearer")


# Overrided class to store token in cookie
oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/auth/token")


async def get_current_user_from_token(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):

    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credential",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_jwt(token=token)
        email: str = payload.get("email")
        code: str = payload.get("code")  # FIXME - The code manageùent has changed
        if email is None or code is None:
            raise credential_exception

        token_data = TokenData(email=email, code=code)  # Store to TokenData schema
    except JWTError:
        raise credential_exception

    # FIXE - Check code (?)
    user = get_user_by_email(email == token_data.email, db=db)
    if user is None:
        raise credential_exception
    return user

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.api.utils import create_token, get_current_user_from_token
from backend.core.configs import settings
from backend.db.models.users import Users
from backend.db.repository.users import authenticate
from backend.db.session import get_db
from backend.schemas.token import Token
from backend.schemas.users import UserAPI

router = APIRouter()


@router.post("/access-token", response_model=Token, description="Authentification")
async def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    # 'OAuth2PasswordRequestForm' object has no attribute 'email', so we used username file as email field
    user = authenticate(email=form_data.username, password=form_data.password, db=db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="This email address isn't active, please contact your admin",
        )
    token_data = {"sub": "login", "email": user.email}

    access_token = create_token(
        data=token_data,
        response=response,
        expire_minute=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    return access_token


@router.post("/login/test-token", response_model=UserAPI)
def test_token(current_user: Users = Depends(get_current_user_from_token)) -> Any:
    """
    Test access token
    """
    return current_user

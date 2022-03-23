import random
import string
from datetime import timedelta
from typing import Dict, Optional

from fastapi import HTTPException, Request, Response, status
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security.oauth2 import OAuth2
from fastapi.security.utils import get_authorization_scheme_param

from core.configs import settings
from core.security import generate_jwt
from schemas.token import Token


def generate_random_code(size: int = 4) -> str:
    return "".join(random.choices(string.ascii_uppercase, k=size))


def create_token(data: Dict, response: Response, expire_minute: int):
    """Generic function to create a JWT

    Args:
        data (Dict): Token data
        response (Response): FastAPI Response
        expire_minute (int): Token live time in minute

    Returns:
        Token: JW Token
    """
    access_token_expire = timedelta(minutes=expire_minute)
    access_token = generate_jwt(data=data, expires_delta=access_token_expire)

    # Store access token as cookies, activate httponly for more safety
    response.set_cookie(
        key="access_token", value=f"Bearer {access_token}", httponly=True
    )

    return Token(access_token=access_token, token_type="bearer")


class OAuth2PasswordBearerWithCookie(OAuth2):
    """
    Create a new class based on OAuth2PasswordBearer default to allow getting token
    from cookies instead of header.

    Her, we just replace the line
    ...
        authorization: str = request.headers.get("Authorization")
    ... by ...

    """

    def __init__(
        self,
        tokenUrl: str,
        scheme_name: Optional[str] = None,
        scopes: Optional[Dict[str, str]] = None,
        description: Optional[str] = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(
            flows=flows,
            scheme_name=scheme_name,
            description=description,
            auto_error=auto_error,
        )

    async def __call__(self, request: Request) -> Optional[str]:
        # Get the token from cookies
        authorization: str = request.cookies.get("access_token")

        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param

import logging
import random
import string
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

import emails
from emails.template import JinjaTemplate
from fastapi import Depends, HTTPException, Request, Response, status
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security.oauth2 import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from jose import jwt
from jose.exceptions import JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from backend.core.configs import settings
from backend.core.security import decode_jwt, generate_jwt
from backend.db.models.users import Users
from backend.db.repository.users import get_user_by_email
from backend.db.session import get_db
from backend.schemas.token import Token


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


def generate_code_verification_token(code: str) -> str:
    delta = timedelta(hours=settings.JWT_EMAIL_TOKEN_EXPIRE_MINUTES)
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()

    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": code},
        key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def send_email(
    email_to: str,
    subject_template: str = "",
    html_template: str = "",
    environment: Dict[str, Any] = {},
) -> None:

    smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
    if not settings.EMAILS_ENABLED:
        raise NotImplementedError("no provided configuration for email variables")
    if not smtp_options.get("host"):
        raise ValueError("Invalid hostname")

    message = emails.Message(
        subject=JinjaTemplate(subject_template),
        html=JinjaTemplate(html_template),
        mail_from=(settings.MAIL_FROM_NAME, settings.MAIL_FROM),
    )
    if settings.SMTP_TLS:
        smtp_options["tls"] = True
    if settings.SMTP_USERNAME:
        smtp_options["user"] = settings.SMTP_USERNAME
    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD

    response = message.send(to=email_to, render=environment, smtp=smtp_options)
    logging.info(f"send email result: {response}")
    return response


def send_verification_email(email_to: str, verification_code: str) -> None:

    project_name = settings.PROJECT_TITLE
    link = f"{settings.APPS_HOST}/{settings.API_V1_STR}/verify-code/{email_to}"
    subject = f"{project_name} - Activate your account"

    BASE_DIR = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    template_filepath = os.path.join(BASE_DIR, settings.EMAIL_TEMPLATES_DIR)

    with open(Path(template_filepath) / "new_account.html") as f:
        template_str = f.read()

    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": settings.PROJECT_TITLE,
            "verification_code": verification_code,
            "email": email_to,
            "link": link,
        },
    )
    # Generate token
    return generate_code_verification_token(verification_code)


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


# Overrided class to store token in cookie
oauth2_scheme = OAuth2PasswordBearerWithCookie(
    tokenUrl=f"{settings.API_V1_STR}/auth/access-token"
)


def get_current_user_from_token(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> Users:

    try:
        payload = decode_jwt(token=token)

    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credential",
        )
    user = get_user_by_email(email=payload.get("email"))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def check_verify_code_token(token: str) -> Optional[str]:
    try:
        decoded_token = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=settings.JWT_ALGORITHM
        )

        return decoded_token.get("sub")

    except (JWTError, ValidationError):
        raise jwt.ExpiredSignatureError("Invalid token")

from lib2to3.pgen2.token import tok_name
from typing import Any, Dict, List, Optional

from datetime import datetime, timedelta
from jose import jwt

from core.configs import settings


def generate_jwt(
    data: dict,
    secret_key: str = settings.JWT_SECRET_KEY,
    algorithm: str = settings.JWT_ALGORITHM,
    expires_delta: Optional[timedelta] = None,
) -> str:

    payload = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
    payload["exp"] = expire
    encoded_jwt = jwt.encode(payload, secret_key, algorithm=algorithm)

    return encoded_jwt


def decode_jwt(
    token: str,
    key: str = settings.JWT_SECRET_KEY,
    algorithms: List[str] = settings.JWT_ALGORITHM,
) -> Dict[str, Any]:
    return jwt.decode(token=tok_name, key=key, algorithms=algorithms)

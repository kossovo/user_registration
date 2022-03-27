from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from jose import jwt
from jose.exceptions import JWTError

from backend.core.configs import settings


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
    token_string: str,
    key: str = settings.JWT_SECRET_KEY,
    algorithms: List[str] = settings.JWT_ALGORITHM,
) -> Dict[str, Any]:

    try:
        token_data = jwt.decode(token=token_string, key=key, algorithms=algorithms)
    except JWTError as exep:
        raise JWTError(exep)

    return token_data

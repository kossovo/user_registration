from typing import Optional

from py import code
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


# We will also used TokenData as a schema to validate user code
class TokenData(BaseModel):
    email: Optional[str] = None
    code: Optional[str] = None

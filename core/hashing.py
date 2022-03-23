from typing import Tuple

from passlib import pwd
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Hasher:
    @staticmethod
    def get_password_hash(plain_password: str) -> str:
        return pwd_context.hash(plain_password)

    @staticmethod
    def generate_password() -> str:
        return pwd.genword()

    @staticmethod
    def verify_password(plain_password: str, hash_password: str) -> Tuple[bool, str]:
        return pwd_context.verify(plain_password, hash_password)

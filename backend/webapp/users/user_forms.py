from typing import List, Optional

from fastapi import Request

from backend.webapp.utils.validators import is_valid_email


class UserCreateForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.email: Optional[str] = None
        self.password: Optional[str] = None
        self.errors: List = []

    async def load_data(self):
        form = await self.request.form()
        self.email = form.get("email")
        self.password = form.get("password")

    def clean_code(self):
        if not self.email or not (is_valid_email(self.email)):
            self.errors.append("Invalid email address")
        if not self.password or len(self.password) < 8:
            self.errors.append("Password must have at least 8 chars")

    async def is_valid(self):
        self.clean_code()
        if not self.errors:
            return True
        return False

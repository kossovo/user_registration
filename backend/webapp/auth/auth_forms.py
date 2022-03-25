from typing import List, Optional

from fastapi import Request

from backend.webapp.utils.validators import is_valid_email


class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.email: Optional[str] = None
        self.password: Optional[str] = None
        self.errors: List = []

    async def load_data(self):
        form = await self.request.form()
        self.username = form.get("email")
        self.password = form.get("password")

    async def is_valid(self):
        # username is supposed to be email, so we have to check it
        if not self.username or not (is_valid_email(self.username)):
            self.errors.append("Invalid email address")
        if not self.errors:
            return True
        return False

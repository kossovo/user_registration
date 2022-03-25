from fastapi import APIRouter

from webapp.auth import route_logins
from webapp.users import route_users

webapps_router = APIRouter(include_in_schema=False)

webapps_router.include_router(router=route_users.router, prefix="", tags=["Sign Up"])
webapps_router.include_router(router=route_logins.router, prefix="", tags=["Sign In"])

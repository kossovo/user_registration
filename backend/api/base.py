from fastapi import APIRouter

from backend.api.v1 import route_auth, route_users
from backend.core.configs import settings

api_router = APIRouter()

api_router.include_router(
    route_users.router, prefix=f"{settings.API_V1_STR}/users", tags=["Users"]
)
api_router.include_router(
    route_auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Login"]
)

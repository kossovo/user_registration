from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.api.base import api_router
from backend.core.configs import settings
from backend.db.base import Base
from backend.db.session import engine
from backend.webapp.base import webapps_router


def create_tables():
    # Connect FastAPI to the database engine, so the DB will automatically creating when destruct the project.
    Base.metadata.create_all(bind=engine)


def include_router(app):
    app.include_router(api_router)
    app.include_router(webapps_router)


def start_application():
    start_app = FastAPI(
        title=settings.PROJECT_TITLE,
        version=settings.PROJECT_VERSION,
        description=settings.PROJECT_DESCRIPTION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
    )
    create_tables()
    include_router(start_app)
    return start_app


app = start_application()

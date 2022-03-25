import os

from dotenv import find_dotenv, load_dotenv
from pydantic import BaseSettings, EmailStr

load_dotenv(find_dotenv())


class Settings:

    PROJECT_TITLE: str = "Users registration API"
    PROJECT_VERSION: str = "1.0.1"
    PROJECT_DESCRIPTION: str = "Building a user registration API"
    API_V1_STR: str = "/api/v1"

    APPS_HOST: str = os.getenv("APPS_HOST")

    DATABASE_HOST: str = os.getenv("POSTGRES_HOST")
    DATABASE_NAME: str = os.getenv("POSTGRES_DB")
    DATABASE_PORT: str = os.getenv("POSTGRES_PORT")
    DATABASE_USER: str = os.getenv("POSTGRES_USER")
    DATABASE_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    DATABASE_URL = str = os.getenv("DATABASE_URL")

    # Getting JWT params
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30

    JWT_EMAIL_TOKEN_EXPIRE_MINUTES = 1
    EMAILS_ENABLED: bool = False

    # Mails & SMTP
    MAIL_FROM: str = os.getenv("MAIL_FROM")
    MAIL_FROM_NAME: str = os.getenv("MAIL_FROM_NAME")

    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD")
    SMTP_PORT: int = os.getenv("SMTP_PORT")
    SMTP_HOST: str = os.getenv("SMTP_HOST")
    SMTP_TLS: bool = os.getenv("SMTP_TLS")
    SMTP_SSL: bool = os.getenv("SMTP_SSL")
    SMTP_USE_CREDENTIALS: bool = os.getenv("SMTP_USE_CREDENTIALS")
    SMTP_VALIDATE_CERTS: bool = os.getenv("SMTP_VALIDATE_CERTS")

    # Test
    EMAIL_TEST_USER: EmailStr = "test@dailymotion.local"


settings = Settings()

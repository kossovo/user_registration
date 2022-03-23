import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


class Settings:
    PROJECT_TITLE: str = "Users registration API"
    PROJECT_VERSION: str = "1.0.1"
    PROJECT_DESCRIPTION: str = "Building a user registration API"

    DATABASE_HOST: str = os.getenv("DB_HOST")
    DATABASE_NAME: str = os.getenv("DB_NAME")
    DATABASE_PORT: str = os.getenv("DB_PORT")
    DATABASE_USER: str = os.getenv("DB_USER")
    DATABASE_PASSWORD: str = os.getenv("DB_PASSWORD")
    DATABASE_URL = str = os.getenv("DATABASE_URL")

    # Getting JWT params
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 1

    # Mail
    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD")
    MAIL_FROM: str = os.getenv("MAIL_FROM")
    MAIL_FROM_NAME: str = os.getenv("MAIL_FROM_NAME")
    MAIL_PORT: int = os.getenv("MAIL_PORT")
    MAIL_SERVER: str = os.getenv("MAIL_SERVER")
    MAIL_TLS: bool = os.getenv("MAIL_TLS")
    MAIL_SSL: bool = os.getenv("MAIL_SSL")
    USE_CREDENTIALS: bool = os.getenv("USE_CREDENTIALS")
    VALIDATE_CERTS: bool = os.getenv("VALIDATE_CERTS")


settings = Settings()

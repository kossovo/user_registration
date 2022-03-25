import os
import sys
from typing import Dict, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# this is to include backend dir in sys.path so that we can import from db,main.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from core.configs import settings
from db.session import SessionLocal
from main import app
from tests.utils.users import authentication_token_from_email


@pytest.fixture(scope="session")
def db() -> Generator:
    yield SessionLocal()


@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def normal_user_token_headers(client: TestClient, db: Session) -> Dict[str, str]:
    return authentication_token_from_email(client=client, email=settings.m, db=db)

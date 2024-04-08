import logging
import os

import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv(".env")
engine = create_engine(url=os.environ["DATABASE_URL"])

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def create_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="session", autouse=True)
def logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    yield logger


@pytest.fixture(scope="session", autouse=True)
def db(logger):
    logger.info("SETUP session")
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
    logger.info("TEARDOWN session")

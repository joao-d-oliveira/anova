from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
import os

from app.config import Config


CONFIG = None
ENGINE = None
SESSION_FACTORY = None
SQLALCHEMY_DATABASE_URL = None

def get_sqlalchemy_database_url():
    global CONFIG
    global SQLALCHEMY_DATABASE_URL
    if CONFIG is None:
        CONFIG = Config()
    if SQLALCHEMY_DATABASE_URL is None:
        SQLALCHEMY_DATABASE_URL = f"postgresql://{CONFIG.db_user}:{CONFIG.db_password}@{CONFIG.db_host}:{CONFIG.db_port}/{CONFIG.db_name}"
    return SQLALCHEMY_DATABASE_URL

def get_engine():
    global ENGINE
    if ENGINE is None:
        ENGINE = create_engine(
            get_sqlalchemy_database_url(),
            poolclass=QueuePool,
            pool_size=10,  # Number of permanent connections
            max_overflow=10,  # Number of additional connections when pool_size is reached
            pool_timeout=30,  # Seconds to wait before giving up on getting a connection
            pool_recycle=1800,  # Recycle connections after 30 minutes
        )
    return ENGINE


def get_session_factory():
    global SESSION_FACTORY
    if SESSION_FACTORY is None:
        SESSION_FACTORY = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return SESSION_FACTORY


@contextmanager
def database_context():
    with get_session_factory()() as session:
        yield session


# Dependency
def get_db():
    with get_session_factory()() as session:
        yield session

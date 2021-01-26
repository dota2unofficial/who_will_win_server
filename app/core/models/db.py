from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import sessionmaker

from ..setting import Settings


engine = create_engine(
    Settings.SQLALCHEMY_DB_URI,
    pool_pre_ping=True
)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


@as_declarative()
class Base:
    id: Any

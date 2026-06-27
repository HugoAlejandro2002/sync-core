from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import DateTime, String
from sqlalchemy.dialects.mysql import CHAR as MYSQL_CHAR
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import Numeric, TypeEngine

# CHAR(36) on MySQL (per AGENTS.md), VARCHAR(36) elsewhere (e.g. SQLite for tests).
UUID_TYPE: TypeEngine[str] = String(36).with_variant(MYSQL_CHAR(36), "mysql")

# DECIMAL(14, 2) for money, DECIMAL(5, 4) for confidence scores. Never float.
MONEY_TYPE: TypeEngine[Decimal] = Numeric(14, 2, asdecimal=True)
CONFIDENCE_TYPE: TypeEngine[Decimal] = Numeric(5, 4, asdecimal=True)


def new_uuid() -> str:
    return str(uuid4())


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
    )

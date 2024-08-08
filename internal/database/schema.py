"""
Manager from database
"""

from datetime import datetime

from sqlalchemy import ForeignKey, func, Integer, DateTime, JSON
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column


class AbstractAsyncEntity(AsyncAttrs, DeclarativeBase):
    pass


class User(AbstractAsyncEntity):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now)
    requested_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    processed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    data: Mapped[list["Data"]] = relationship()


class Data(AbstractAsyncEntity):
    __tablename__ = "users_data"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    user: Mapped["User"] = relationship()
    requested_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    data: Mapped[dict] = mapped_column(JSON, nullable=False)

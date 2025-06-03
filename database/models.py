from datetime import datetime
from typing import Annotated, Optional
from pydantic import HttpUrl
from sqlalchemy import MetaData, ForeignKey, DateTime, func, String, TypeDecorator
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.sql import expression

int_pk = Annotated[int, mapped_column(primary_key=True)]
created_time = Annotated[datetime, mapped_column(DateTime(timezone=True), server_default=func.now())]
updated_time = Annotated[datetime, mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())]

class HttpUrlType(TypeDecorator):
    impl = String(2083)
    cache_ok = True
    python_type = HttpUrl

    def process_bind_param(self, value, dialect) -> str:
        return str(value)

    def process_result_value(self, value, dialect) -> HttpUrl:
        return HttpUrl(url=value)

    def process_literal_param(self, value, dialect) -> str:
        return str(value)
class Base(AsyncAttrs, DeclarativeBase):
    """Базовый класс для всех моделей."""
    __abstract__ = True
    metadata = MetaData()

    repr_cols_num = 3
    repr_cols = tuple()
    
    def __repr__(self):
        """Relationships не используются в repr(), т.к. могут вести к неожиданным подгрузкам"""
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {', '.join(cols)}>"
    
    created_at: Mapped[created_time] 
    updated_at: Mapped[updated_time] 

class User(Base):
    """Модель пользователя для хранения информации об учетных записях."""
    __tablename__ = 'users'

    id: Mapped[int_pk]
    username: Mapped[str] = mapped_column(nullable=False, index=True, unique=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=False)
    is_admin: Mapped[bool] = mapped_column(server_default=expression.false(), nullable=False)

class Link(Base):
    __tablename__ = 'links'

    id: Mapped[int_pk]
    link: Mapped[str] = mapped_column(nullable=False, index=True, unique=True)
    original_link: Mapped[HttpUrl] = mapped_column(HttpUrlType, nullable=False, unique=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    activated: Mapped[bool] = mapped_column(server_default=expression.true(), nullable=False)
    expired_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

class Click(Base):
    __tablename__ = 'clicks'

    id: Mapped[int_pk]
    link_id: Mapped[int] = mapped_column(ForeignKey("links.id", ondelete="CASCADE"), nullable=False)
    ip: Mapped[str] = mapped_column(nullable=False)
    user_agent: Mapped[str] = mapped_column(nullable=False)

  
   
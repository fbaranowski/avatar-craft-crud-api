import uuid
from typing import List

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


class User(Base):
    __tablename__ = "user"

    mail: Mapped[str] = mapped_column(String(50), unique=True)
    avatars: Mapped[List["Avatar"]] = relationship(back_populates="user", lazy="joined")


class Avatar(Base):
    __tablename__ = "avatar"

    uuid: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(), nullable=True)
    type: Mapped[str] = mapped_column(String(), nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="avatars")

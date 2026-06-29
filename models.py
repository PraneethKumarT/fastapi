from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    image_file: Mapped[str] = mapped_column(String(255), default="default.jpg")
    password_hash: Mapped[str] = mapped_column(String(200), nullable=False)

    posts: Mapped[list["Post"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), index=True)
    content: Mapped[str] = mapped_column(Text)
    date_posted: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="posts")

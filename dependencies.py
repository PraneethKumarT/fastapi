from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models
from auth import oauth2_scheme, verify_access_token
from database import get_db

templates = Jinja2Templates(directory="templates")

DbSession = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: DbSession,
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = verify_access_token(token)
    if payload is None:
        raise credentials_exception
    user = await db.get(models.User, int(payload["sub"]))
    if user is None:
        raise credentials_exception
    return user


CurrentUser = Annotated[models.User, Depends(get_current_user)]


async def find_post(db: AsyncSession, post_id: int) -> models.Post:
    post = await db.scalar(
        select(models.Post)
        .where(models.Post.id == post_id)
        .options(selectinload(models.Post.user))
    )
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


async def find_user(db: AsyncSession, user_id: int) -> models.User:
    user = await db.get(models.User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

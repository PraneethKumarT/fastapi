from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import selectinload

import models
from dependencies import CurrentUser, DbSession, find_user
from schemas import PostResponse, UserCreate, UserUpdate, UserPrivate, Token
from auth import hash_password, create_access_token, verify_password


router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("", response_model=UserPrivate, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: DbSession):
    existing_user = await db.scalar(
        select(models.User).where(
            (models.User.username == user.username) | (models.User.email == user.email)
        )
    )
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    new_user = models.User(
        username=user.username,
        email=user.email,
        password_hash=hash_password(user.password),
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.post("/token", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: DbSession):
    user = await db.scalar(select(models.User).where(models.User.username == form_data.username))
    if user is None or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=access_token)


@router.get("/me", response_model=UserPrivate)
async def read_current_user(current_user: CurrentUser):
    return current_user


@router.get("/{user_id}", response_model=UserPrivate)
async def get_user(user_id: int, db: DbSession):
    return await find_user(db, user_id)


@router.get("/{user_id}/posts", response_model=list[PostResponse])
async def get_user_posts(user_id: int, db: DbSession):
    await find_user(db, user_id)
    return (await db.scalars(
        select(models.Post)
        .where(models.Post.user_id == user_id)
        .options(selectinload(models.Post.user))
    )).all()


@router.patch("/{user_id}", response_model=UserPrivate)
async def update_user(user_id: int, user_update: UserUpdate, db: DbSession):
    user = await find_user(db, user_id)
    updates = user_update.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(user, field, value)
    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: DbSession):
    user = await find_user(db, user_id)
    await db.delete(user)
    await db.commit()

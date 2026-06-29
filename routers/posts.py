from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

import models
from dependencies import DbSession, find_post
from schemas import PostCreate, PostUpdate, PostResponse

router = APIRouter(prefix="/api/posts", tags=["posts"])


@router.get("", response_model=list[PostResponse])
async def get_posts(db: DbSession):
    return (await db.scalars(select(models.Post).options(selectinload(models.Post.user)))).all()


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(post: PostCreate, db: DbSession):
    if await db.get(models.User, post.user_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    new_post = models.Post(title=post.title, content=post.content, user_id=post.user_id)
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post, attribute_names=["user"])
    return new_post


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: DbSession):
    return await find_post(db, post_id)


@router.patch("/{post_id}", response_model=PostResponse)
async def update_post(post_id: int, post_update: PostUpdate, db: DbSession):
    post = await find_post(db, post_id)
    updates = post_update.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(post, field, value)
    await db.commit()
    await db.refresh(post)
    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db: DbSession):
    post = await find_post(db, post_id)
    await db.delete(post)
    await db.commit()

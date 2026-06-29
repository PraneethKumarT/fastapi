from fastapi import APIRouter, Request
from sqlalchemy import select
from sqlalchemy.orm import selectinload

import models
from dependencies import DbSession, find_post, templates

router = APIRouter(include_in_schema=False)


@router.get("/", name="home")
@router.get("/posts", name="posts")
async def home(request: Request, db: DbSession):
    posts = (await db.scalars(select(models.Post).options(selectinload(models.Post.user)))).all()
    return templates.TemplateResponse(request=request, name="home.html", context={"posts": posts})


@router.get("/post/new", name="new_post")
async def new_post(request: Request, db: DbSession):
    users = (await db.scalars(select(models.User))).all()
    return templates.TemplateResponse(request=request, name="post_form.html", context={"users": users})


@router.get("/post/{post_id}", name="post")
async def post_detail(request: Request, post_id: int, db: DbSession):
    post = await find_post(db, post_id)
    return templates.TemplateResponse(request=request, name="post.html", context={"post": post})

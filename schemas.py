from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: str = Field(min_length=3, max_length=120)



class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=255)

class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=50)
    email: str | None = Field(default=None, min_length=3, max_length=120)
    password: str | None = Field(default=None, min_length=8, max_length=255)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserPublic(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    image_file: str = "default.jpg"


class UserPrivate(UserPublic):
    email: str

class PostBase(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    content: str = Field(min_length=3, max_length=1000)


class PostCreate(PostBase):
    user_id: int

class PostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=100)
    content: str | None = Field(default=None, min_length=3, max_length=1000)

class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    user_id: int
    date_posted: datetime
    author: UserPublic = Field(validation_alias="user")
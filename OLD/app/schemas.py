from pydantic import BaseModel, EmailStr
from datetime import datetime

class Post(BaseModel):
    title: str
    content: str 
    published: bool = True

class PostBase(BaseModel):
    title: str
    content: str 
    published: bool = True

class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: int
    created_at: datetime
    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    class Config:
        orm_mode = True





















    

class Addition(BaseModel):
    a: int = 2
    b: int = 2

class Data(BaseModel):
    data: list[list[float]]
from pydantic import BaseModel, RootModel, EmailStr
from datetime import datetime
from typing import List


# Posts
# ---------------------------------------------------------------


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

# Users
# ---------------------------------------------------------------


class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    
    class Config:
        orm_mode = True


# Authentication
# ---------------------------------------------------------------


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Predictions
# ---------------------------------------------------------------


class PredictionBase(BaseModel):
    x: float
    y: float
    
class Prediction(PredictionBase):
    pass

class Feature(BaseModel):
    x: list[float]

class UpdatedPrediction(BaseModel):
    y: float

class PredictionsList(RootModel):
    root: List[float]
from pydantic import BaseModel, RootModel, EmailStr
from datetime import datetime
from typing import List, Optional
from pydantic.types import conint

import warnings
warnings.filterwarnings("ignore", category=UserWarning)


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
    owner_id: int
    owner: UserOut

    class Config:
        orm_mode = True


# Authentication
# ---------------------------------------------------------------


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str 


class TokenData(BaseModel):
    id: Optional[str] = None


# Votes
# ---------------------------------------------------------------


class Vote(BaseModel):
    post_id: int
    dir: conint(le=1)
    


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
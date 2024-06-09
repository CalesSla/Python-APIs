from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional, List
from random import randrange
import requests
import pickle
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import psycopg2
from  psycopg2.extras import RealDictCursor
import os
import time
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())
from sqlalchemy.orm import Session
from . import models, schemas, utils
from .database import engine, SessionLocal, get_db
from .routers import post, user, other





models.Base.metadata.create_all(bind=engine)

app = FastAPI()

host = os.environ["HOST"]
database = os.environ["DATABASE"]
user_name=  os.environ["USER"]
password = os.environ["PASSWORD"]

while True:
    try:
        conn = psycopg2.connect(host=host, 
                                database=database, 
                                user=user_name, 
                                password=password,
                                cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was successful")
        break
    except Exception as error:
        print("Connectung to database failed")
        print("Error: ", error)
        time.sleep(2)


my_posts = [{"title": "title of post 1", "content": "content of post 1", "id": 1},
            {"title": "favorite foods", "content": "I like pizza", "id": 2}]

def find_post(id):
    for p in my_posts:
        if p['id'] == id:
            return p
        
def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i

app.include_router(post.router)
app.include_router(user.router)
app.include_router(other.router)

@app.get("/")
def root():
    return {"message": "Hello World"}





from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
import pickle
import numpy as np
from typing import Optional
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
load_dotenv()
import os
import time
from sqlalchemy.orm import Session
from . import models
from .database import engine, get_db


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True

class FeatureData(BaseModel):
    x: list[float]


while True:
    try:
        conn = psycopg2.connect(host="localhost", 
                                database="fastapi", 
                                user="postgres", 
                                password=os.getenv("dbpassword"),
                                cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was successful!")
        break
    except Exception as error:
        print("Connecting to database failed")
        print("Error: ", error)
        time.sleep(2)



my_posts = [{"title": "title of post 1",
             "content": "content of post 1",
             "id": 1},
             {"title": "favorite foods",
              "content": "I like pizza",
              "id": 2}
            ]


def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p
        

def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p["id"] == id:
            return i


@app.get("/")
def root():
    return {"message": "Hello World!!!!"}


@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"data": posts}


@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * 
    #                     FROM posts
    #                     """)
    # posts = cursor.fetchall()
    posts = db.query(models.Post).all()
    return {"data": posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post, db: Session = Depends(get_db)):
    # cursor.execute("""
    #                 INSERT INTO posts
    #                 (title, content, published)
    #                 VALUES (%s, %s, %s)
    #                 RETURNING *
    #                 """,
    #                 (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()
    new_post = models.Post(title=post.title,
                           content=post.content,
                           published=post.published)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"data": new_post}


@app.post("/predict", status_code=status.HTTP_201_CREATED)
def predict(data: FeatureData):
    data = data.dict()
    features = np.array([data["x"]]).reshape(-1,1)
    model_path = "app/trainedModels/trained_linreg_model.pkl"
    with open(model_path, 'rb') as file:
        loaded_model = pickle.load(file)
    prediction = loaded_model.predict(features)
    prediction = prediction.flatten().tolist()
    for i in range(features.shape[0]):
        cursor.execute("""
                        INSERT INTO predictions
                        (x, y)
                        VALUES (%s, %s)
                        ON CONFLICT (x) DO NOTHING
                        RETURNING *
                            """,
                        (int(features[i][0]), float(prediction[i])))
    conn.commit()
    return {"prediction": prediction}


@app.get("/posts/{id}")
def get_post(id: int):
    cursor.execute("""
                    SELECT *
                    FROM posts
                    WHERE id = %s
                    """, (str(id),))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    return {"post_detail": post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute("""
                    DELETE
                    FROM posts
                    WHERE id = %s
                    RETURNING *
                    """, (str(id),))
    deleted_post = cursor.fetchone()
    conn.commit()

    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} does not exist")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    cursor.execute("""
                   UPDATE posts
                   SET title = %s,
                   content = %s,
                   published = %s
                   WHERE id = %s
                   RETURNING *
                   """, (post.title, post.content, post.published, str(id)))
    
    updated_post = cursor.fetchone()
    conn.commit()
    
    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")
    return {"data": updated_post}
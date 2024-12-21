from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
import pickle
import numpy as np
from typing import Optional, List
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
load_dotenv()
import os
import time
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from . import models, schemas
from .database import engine, get_db
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


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


# Posts
# ---------------------------------------------------------------


@app.get("/posts", response_model=List[schemas.Post])
def get_posts(db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * 
    #                     FROM posts
    #                     """)
    # posts = cursor.fetchall()
    posts = db.query(models.Post).all()
    return posts


@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db)):
    # cursor.execute("""
    #                 INSERT INTO posts
    #                 (title, content, published)
    #                 VALUES (%s, %s, %s)
    #                 RETURNING *
    #                 """,
    #                 (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@app.get("/posts/{id}", response_model=schemas.Post)
def get_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute("""
    #                 SELECT *
    #                 FROM posts
    #                 WHERE id = %s
    #                 """, (str(id),))
    # post = cursor.fetchone()

    post = db.query(models.Post).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    return post


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute("""
    #                 DELETE
    #                 FROM posts
    #                 WHERE id = %s
    #                 RETURNING *
    #                 """, (str(id),))
    # deleted_post = cursor.fetchone()
    # conn.commit()
    post = db.query(models.Post).filter(models.Post.id == id)

    if post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} does not exist")
    
    post.delete(synchronize_session=False)
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}", response_model=schemas.Post)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db)):
    # cursor.execute("""
    #                UPDATE posts
    #                SET title = %s,
    #                content = %s,
    #                published = %s
    #                WHERE id = %s
    #                RETURNING *
    #                """, (post.title, post.content, post.published, str(id)))
    
    # updated_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")
    
    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    
    return post_query.first()


# Users
# ---------------------------------------------------------------


@app.post("/users", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session=Depends(get_db)):
    hashed_password = pwd_context.hash(user.password)
    user.password = hashed_password
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# Posts
# ---------------------------------------------------------------


@app.get("/predict", response_model=List[schemas.Prediction])
def get_predictions(db: Session = Depends(get_db)):
    predictions = db.query(models.Predictions).all()
    return predictions


@app.post("/predict", status_code=status.HTTP_201_CREATED, response_model=schemas.PredictionsList)
def predict(data: schemas.Feature, db: Session = Depends(get_db)):
    data = data.dict()
    features = np.array([data["x"]]).reshape(-1,1)
    model_path = "app/trainedModels/trained_linreg_model.pkl"
    with open(model_path, 'rb') as file:
        loaded_model = pickle.load(file)
    prediction = loaded_model.predict(features)
    prediction = prediction.flatten().tolist()
    for i in range(features.shape[0]):
    #     cursor.execute("""
    #                     INSERT INTO predictions
    #                     (x, y)
    #                     VALUES (%s, %s)
    #                     ON CONFLICT (x) DO NOTHING
    #                     RETURNING *
    #                         """,
    #                     (int(features[i][0]), float(prediction[i])))
        stmt = insert(models.Predictions).values(x=int(features[i][0]), y=float(prediction[i]))
        stmt = stmt.on_conflict_do_nothing(index_elements=["x"])
        db.execute(stmt)
    # conn.commit()
    db.commit()
    prediction = schemas.PredictionsList(prediction)
    return prediction


@app.delete("/predict/{x}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prediction(x: int, db: Session = Depends(get_db)):
    prediction = db.query(models.Predictions).filter(models.Predictions.x == x)

    if prediction.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"There is no prediction for x={x}")
    
    prediction.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/predict/{x}", response_model=schemas.Prediction)
def update_prediction(x: int, updated_prediction: schemas.UpdatedPrediction, db: Session = Depends(get_db)):
    update_query = db.query(models.Predictions).filter(models.Predictions.x == x)
    prediction = update_query.first()
    updated_prediction = updated_prediction.dict()
    updated_prediction.update({"x": x})
    if prediction == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"prediction with x: {x} does not exist")
    update_query.update(updated_prediction, synchronize_session=False)
    db.commit()
    return update_query.first()


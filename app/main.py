from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
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

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str 
    published: bool = True

host = os.environ["HOST"]
database = os.environ["DATABASE"]
user=  os.environ["USER"]
password = os.environ["PASSWORD"]

while True:
    try:
        conn = psycopg2.connect(host=host, 
                                database=database, 
                                user=user, 
                                password=password,
                                cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was successful")
        break
    except Exception as error:
        print("Connectung to database failed")
        print("Error: ", error)
        time.sleep(2)


class Addition(BaseModel):
    a: int = 2
    b: int = 2


class Data(BaseModel):
    data: list[list[float]]

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

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/posts")
def get_posts():
    return {"data": my_posts}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    post_dict = post.dict()
    post_dict["id"] = randrange(0, 1000000)
    my_posts.append(post_dict)
    return {"data": post_dict}

@app.post("/add")
def add(added: Addition):
    return{"result": added.a + added.b}

@app.post("/linreg")
def linreg(data: Data):
    with open('linear_regression_model.pkl', 'rb') as file:
        loaded_model = pickle.load(file)
    new_data = data.dict()['data']
    predictions = loaded_model.predict(new_data).flatten()
    return{"result": {"result": predictions.tolist()}}

@app.get("/posts/{id}")
def get_post(id: int, response: Response):
    post = find_post(id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    return {"post_detail": post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    index = find_index_post(id)
    if index is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")
    my_posts.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id: int, post: Post):

    index = find_index_post(id)
    base_url = "http://127.0.0.1:8000"
    post_id = id

    response = dict(requests.get(f"{base_url}/posts/{post_id}").json()['post_detail'])
    print(f"Existing post: {response}")
    if index is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")
    post_dict = post.dict()
    post_dict["id"] = id
    my_posts[index] = post_dict
    print(f"New post: {my_posts[index]}")
    return {"data": post_dict}

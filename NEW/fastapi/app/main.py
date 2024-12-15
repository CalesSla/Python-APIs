from fastapi import FastAPI, Response, status, HTTPException 
from fastapi.params import Body
from pydantic import BaseModel
import pickle
import numpy as np
from typing import Optional
from random import randrange

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None

class FeatureData(BaseModel):
    x: list[float]


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


@app.get("/posts")
def get_posts():
    return {"data": my_posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    post_dict = post.dict()
    post_dict["id"] = randrange(0, 1000000)
    my_posts.append(post_dict)
    return {"data": post_dict}


@app.post("/predict")
def predict(data: FeatureData):
    data = data.dict()
    features = np.array([data["x"]]).reshape(-1,1)
    model_path = "trainedModels/trained_linreg_model.pkl"
    with open(model_path, 'rb') as file:
        loaded_model = pickle.load(file)
    prediction = loaded_model.predict(features)
    prediction = prediction.flatten().tolist()
    return {"prediction": prediction}


@app.get("/posts/{id}")
def get_post(id: int):
    post = find_post(int(id))
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"posti with id: {id} was not found")
    return {"post_detail": post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    index = find_index_post(id)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} does not exist")
    my_posts.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    index = find_index_post(id)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")
    post_dict = post.dict()
    post_dict["id"] = id
    my_posts[index] = post_dict
    return {"data": post_dict}
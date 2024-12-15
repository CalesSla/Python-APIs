from fastapi import FastAPI
from fastapi.params import Body
from pydantic import BaseModel
import pickle
import numpy as np

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str

class FeatureData(BaseModel):
    x: list[float]


@app.get("/")
def root():
    return {"message": "Hello World!!!!"}


@app.get("/posts")
def get_posts():
    return {"data": "This is your posts"}


@app.post("/createposts")
def create_posts(new_post: Post):
    
    return {"data": new_post}


@app.post("/predict")
def predict(data: FeatureData):
    features = np.array([data.x]).reshape(-1,1)
    model_path = "trainedModels/trained_linreg_model.pkl"
    with open(model_path, 'rb') as file:
        loaded_model = pickle.load(file)
    prediction = loaded_model.predict(features)
    prediction = prediction.flatten().tolist()
    return {"prediction": prediction}



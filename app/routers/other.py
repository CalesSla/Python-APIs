from .. import models, schemas, utils
from ..database import get_db
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/add")
def add(added: schemas.Addition):
    return{"result": added.a + added.b}

@router.post("/linreg")
def linreg(data: schemas.Data):
    with open('linear_regression_model.pkl', 'rb') as file:
        loaded_model = pickle.load(file)
    new_data = data.dict()['data']
    predictions = loaded_model.predict(new_data).flatten()
    return{"result": {"result": predictions.tolist()}}
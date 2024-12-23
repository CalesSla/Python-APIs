from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from .. import models, schemas, oauth2
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from ..database import get_db
from typing import List
import pickle
import numpy as np

router = APIRouter(prefix="/predict", tags=["Predictions"])



@router.get("/", response_model=List[schemas.Prediction])
def get_predictions(db: Session = Depends(get_db), 
                    current_user: int = Depends(oauth2.get_current_user)):
    predictions = db.query(models.Predictions).all()
    return predictions


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PredictionsList)
def predict(data: schemas.Feature, 
            db: Session = Depends(get_db), 
            current_user: int = Depends(oauth2.get_current_user)):
    
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


@router.delete("/{x}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prediction(x: int, 
                      db: Session = Depends(get_db), 
                      current_user: int = Depends(oauth2.get_current_user)):
    
    prediction = db.query(models.Predictions).filter(models.Predictions.x == x)

    if prediction.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"There is no prediction for x={x}")
    
    prediction.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{x}", response_model=schemas.Prediction)
def update_prediction(x: int, 
                      updated_prediction: schemas.UpdatedPrediction, 
                      db: Session = Depends(get_db), 
                      current_user: int = Depends(oauth2.get_current_user) ):
    
    update_query = db.query(models.Predictions).filter(models.Predictions.x == x)
    prediction = update_query.first()
    updated_prediction = updated_prediction.dict()
    updated_prediction.update({"x": x})
    if prediction == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"prediction with x: {x} does not exist")
    update_query.update(updated_prediction, synchronize_session=False)
    db.commit()
    return update_query.first()
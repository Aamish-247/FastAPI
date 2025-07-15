from fastapi import FastAPI, Path , Query, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal
import json



app = FastAPI()

class Patient(BaseModel):
    id: Annotated[str, Field(description = "Unique ID of the patient", example="P001")]
    name: Annotated[str, Field(description = "Name of the patient", example="John Doe")]
    age: Annotated[int, Field(description = "Age of the patient", example=30)]
    gender: Annotated[Literal['male','female', 'other'], Field(description="Specify the patient gender")]
    height: Annotated[float, Field( gt=0, description = "Height of the patient in meters", example=175.5)]
    weight: Annotated[float, Field(gt=0, description = "Weight of the patient in kg", example=70.2)]

    @computed_field
    def bmi(self) -> float:
        """Calculate Body Mass Index (BMI)"""
        bmi = round(self.weight / (self.height ** 2), 2)
        return bmi
    
    @computed_field
    def verdict(self) -> str:
        """Determine the health verdict based on BMI"""
        if self.bmi < 18.5:
            return "Underweight"
        elif 18.5 <= self.bmi < 24.9:
            return "Normal weight"
        elif 25 <= self.bmi < 29.9:
            return "Overweight"
        else:
            return "Obesity"
        


def load_data():
    with open('data.json','r') as f:
        data = json.load(f)

    return data

def save_data(data):
    with open('data.json','w') as f:
        json.dump(data , f)

@app.get("/")
def hello():
    return {"message":"Patient Management System API"}

@app.get("/view")
def view():
    data = load_data()
    return data

@app.get("/patient/{patient_id}")
def get_patient(patient_id: str = Path(..., description="The ID of the patient to retrieve", example="P001")):
    data = load_data()
    if patient_id in data:
        return data[patient_id]
    raise  HTTPException(status_code=404, detail="Patient not found")

@app.get("/sorted")
def sorted_patients(sort_by: str = Query(..., description="The field to sort by", example="Height , Age , BMI"), order : str = Query("asc", description="The order to sort by, either 'asc' or 'desc'")):
    data = load_data()

    valid_fields = ['height', 'weight', 'bmi']

    if sort_by.lower() not in valid_fields:
        raise HTTPException(status_code=400, detail="Invalid sort field. Valid fields are: height, weight, bmi")
    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail="Invalid order. Use 'asc' or 'desc'")
    
    sort_order = True if order == 'asc' else False
    sorted_data = sorted(data.values(), key = lambda x: x[sort_by.lower()], reverse= sort_order)
    return sorted_data


@app.post('/create')
def create_patient(patient: Patient):
    data = load_data()

    if patient.id in data:
        raise HTTPException(status_code=400, detail="Patient with this ID already exists")
    
    data[patient.id] = patient.model_dump(exclude={'id'})

    save_data(data)

    return JSONResponse(status_code=201, content={"message": "Patient created successfully"})